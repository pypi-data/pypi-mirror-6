import Image
import logging
import os
from django.core.urlresolvers import reverse
from django.db import models
from django.conf import settings
from django.utils.text import slugify

from utils import Geo

# Instantiate logger.
logger = logging.getLogger(__name__)


class Place(models.Model):
    """
    Place.
    """
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    postal_code = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    latitude = models.FloatField()
    longitude = models.FloatField()
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=50, blank=True)
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    active = models.BooleanField(default=False)
    
    def __unicode__(self):
        """
        String representation of the model instance.
        """
        return self.name
    
    def get_absolute_url(self):
        """
        Used to create sitemap.xml
        """
        return reverse('yplaces:slug', args=[self.pk, slugify(self.name)])
    
    def get_rating(self):
        """
        Returns the Place's rating.
        """
        if hasattr(self, 'rating'):
            return self.rating
        else:
            return None
        
    def refresh_rating(self):
        """
        Calculates Place's rating.
        """
        # No Place rating details, create.
        if not hasattr(self, 'rating'):
            rating = Rating(place=self)
        # Else, fetch Place's rating.
        else:
            rating = self.rating
            
        # Calculate Place's rating.
        reviews = 0
        total_ratings = 0
        for review in self.review_set.all():
            reviews += 1
            total_ratings += review.rating
        
        # Update Rating.
        if reviews > 0:
            rating.average = float(total_ratings) / reviews
            rating.reviews = reviews
            
            # Calculate relative rating.
            rating.relative = (rating.average*rating.reviews)/len(Place.objects.filter(active=True))
            
            # Shave.
            rating.save()
        
        # Return rating.
        return self
    
    @staticmethod
    def search_radius(latLng, radius, querySet=None):
        """
        Searches for Places that are in a given radius of the provided coordinates.
        
        Args:
            latLng: Latitude and longitude.
            radius: Radius.
        """
        # If a query set is provided, use it.
        if querySet:
            places = querySet
        # If not, start with a fresh one, with all Places.
        else:
            places = Place.objects.filter()
        
        # Filter those that fit into the latitude/longitude square limits.
        geo_box = Geo.box(latLng, radius)
        places = places.filter(latitude__range=(geo_box['minLat'], geo_box['maxLat'])).filter(longitude__range=(geo_box['minLon'], geo_box['maxLon']))
        
        # Finally, fetch those that are inside the given radius.
        results = []
        for place in places:
            if Geo.distance(latLng, (place.latitude, place.longitude)) <= radius:
                results.append(place)
        
        # Return.
        return places.filter(pk__in=[place.pk for place in results])
    
    def get_marker_image_url(self):
        """
        Returns the Place's marker image URL.
        """
        return settings.HOST_URL + settings.STATIC_URL + 'yplaces/images/default_place_marker.png'
    
    def get_rating_value(self):
        """
        Return Place's rating.
        """
        rating = self.get_rating()
        if rating:
            return { 'average': float(rating.average), 'reviews': float(rating.reviews) }
        else:
            return { 'average': 0, 'reviews': 0 }


class Rating(models.Model):
    """
    Place's rating, based on reviews average.
    """
    place = models.OneToOneField(Place)
    average = models.FloatField(default=0)
    reviews = models.IntegerField(default=0)
    relative = models.FloatField(default=0)
    
    def __unicode__(self):
        """
        String representation of the model instance.
        """
        return self.place.name
    
    def get_average_percentage(self):
        """
        Returns the Review's rating value in percentage.
        """
        return self.average*100/5


class Photo(models.Model):
    """
    Place's photos.
    """
    place = models.ForeignKey(Place)
    file = models.ImageField(upload_to='yplaces/photos/')
    added_at = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    
    class Meta:
        ordering = ['-added_at']
    
    def __unicode__(self):
        """
        String representation of the instance.
        """
        return self.place.name
    
    @staticmethod
    def new(place, photo_file, user):
        """
        Creates a new photo, saves and resizes it.
        """
        # Save photo.
        photo = Photo(place=place, file=photo_file, added_by=user)
        photo.save()
        
        # Resize image, if necessary, to match maximum width/height.
        try:
            size = 1024, 768
            im = Image.open(photo.file.path)
            im.thumbnail(size, Image.ANTIALIAS)
            im.save(photo.file.path, format='JPEG')
        except IOError:
            photo.destroy() # Delete photo.
            logger.error('Error resizing place photo! User: ' + str(user.email) + ', Place: ' + str(place.name) + ', Place ID: ' + str(place.pk))
            raise
        
        # Return.
        return photo
    
    def destroy(self):
        """
        Deletes Photo model instance and respective file.
        """
        # If there is a Review associated with the Photo, remove that connection first
        # (in order for the Review not be deleted)
        if hasattr(self, 'review'):
            self.review.unlink_photo()
        
        # Delete file.
        os.remove(self.file.path)
        
        # Delete model instance.
        self.delete()


class Review(models.Model):
    """
    User review of a place.
    """
    # Available rating values.
    RATING_VALUES = (
        (1, '*'),
        (2, '* *'),
        (3, '* * *'),
        (4, '* * * *'),
        (5, '* * * * *')
    )
    
    # Fields.
    place = models.ForeignKey(Place)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    date = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(choices=RATING_VALUES)
    comment = models.TextField()
    photo = models.OneToOneField(Photo, blank=True, null=True)
    
    class Meta:
        ordering = ['-date']
    
    def __unicode__(self):
        """
        String representation of the model instance.
        """
        return self.place.name
    
    def save(self, *args, **kwargs):
        """
        Override method to make sure Place's Rating is refreshed whenever a Review is saved.
        """
        super(Review, self).save(*args, **kwargs)
        self.place.refresh_rating()
    
    def destroy(self):
        """
        Deletes the Review and refreshes the Place's rating.
        """
        self.delete()
        self.place.refresh_rating()
        return self
    
    def get_rating_percentage(self):
        """
        Returns the Review's rating value in percentage.
        """
        return self.rating*100/5
    
    def unlink_photo(self):
        """
        If the Review is linked to a Photo, remove this link.
        """
        self.photo = None
        self.save()