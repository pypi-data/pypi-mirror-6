import logging
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http.response import HttpResponse, HttpResponseForbidden
from django.template import Context
from django.template.loader import get_template
from django.utils.translation import ugettext as _
from yapi.authentication import ApiKeyAuthentication, SessionAuthentication
from yapi.decorators import authentication_classes, permission_classes
from yapi.permissions import IsStaff
from yapi.resource import Resource
from yapi.response import HTTPStatus, Response
from yutils.email import EmailMessage

from serializers import PlaceSerializer, PhotoSerializer, ReviewSerializer
from yplaces.forms import PlaceForm, PhotoForm, ReviewForm
from yplaces.models import Place, Photo, Review

# Instantiate logger.
logger = logging.getLogger(__name__)


class PlacesHandler(Resource):
    """
    API endpoint handler.
    """
    # HTTP methods allowed.
    allowed_methods = ['POST', 'GET']
    
    @authentication_classes([SessionAuthentication, ApiKeyAuthentication])
    def post(self, request):
        """
        Process POST request.
        """
        # Add additional required info regarding the user that created this Place.
        request.data['created_by'] = request.auth['user'].pk
        
        # Populate form with provided data.
        form = PlaceForm(request.data)
        
        # Create new instance.
        try:
            new_instance = form.save()
            
            # If Place was added by a 'regular' user, notify admin that it is pending aproval.
            if not request.auth['user'].is_staff:
                try:
                    # Email variables.
                    d = Context({ 'place': new_instance, 'host_url': settings.HOST_URL })
                    
                    # Render plaintext email template.
                    plaintext = get_template('yplaces/email/place_added.txt')
                    text_content = plaintext.render(d)
                    
                    # Render HTML email template.
                    html = get_template('yplaces/email/place_added.html')
                    html_content = html.render(d)
                    
                    # Email options.
                    subject = _('Place Added')
                    from_email = settings.YPLACES['email_from']
                    to = settings.YPLACES['admin_emails']
                    
                    # Build message and send.
                    email = EmailMessage(sender=from_email,
                                        recipients=to,
                                        subject=subject,
                                        text_content=text_content,
                                        html_content=html_content,
                                        tags=['Place Added'])
                    result = email.send()
                    
                    # Check if email wasn't sent.
                    if not result['sent']:
                        logger.warning('Email Not Sent! Result: ' + str(result['result']))
                        raise
                except:
                    logger.warning('Unable to send email', exc_info=1)
            
            # Return.
            return Response(request=request,
                            data=new_instance,
                            serializer=PlaceSerializer,
                            status=HTTPStatus.SUCCESS_201_CREATED)
            
        # Form didn't validate!
        except ValueError:
            return Response(request=request,
                            data={ 'message': 'Invalid parameters', 'parameters': form.errors },
                            serializer=None,
                            status=HTTPStatus.CLIENT_ERROR_400_BAD_REQUEST)
    
    def get(self, request):
        """
        Process GET request.
        """
        # Lets start with all.
        results = Place.objects.all()
        
        #
        # Filters
        #
        filters = {}
        
        # **************** IMPORTANT ***************
        # Only show full listing (i.e. inactive places) to staff users.
        # ******************************************
        if not request.user or not request.user.is_staff:
            results = results.filter(active=True)
        # If staff, can filter by active status.
        elif request.user and request.user.is_staff:
            try:
                active = request.GET['active']
                if active != '':
                    ['true', 'false'].index(active)
                    active = (active.lower() == 'true')
                    results = results.filter(active=active)
                    filters['active'] = active
            except KeyError:
                pass
            except ValueError:
                return Response(request=request,
                                data={ 'message': 'Invalid parameters', 'parameters': { 'active': ['Invalid value'] } },
                                serializer=None,
                                status=HTTPStatus.CLIENT_ERROR_400_BAD_REQUEST)
        
        ###
        # Optionally, pagination can be disabled and results returned in single response.
        try:
            pagination = request.GET['pagination']
            ['true', 'false'].index(pagination)
            pagination = (pagination.lower() == 'true')
        except KeyError:
            pagination = True
        except ValueError:
            return Response(request=request,
                            data={ 'message': 'Invalid parameters', 'parameters': { 'pagination': ['Invalid value'] } },
                            serializer=None,
                            status=HTTPStatus.CLIENT_ERROR_400_BAD_REQUEST)
        
        ###
        # Radius search.
        latLng = request.GET.get('latLng', None)
        
        # If coordinates are provided...
        if latLng:
            
            # Validate latitude/longitude pair.
            try:
                latLng = [float(i) for i in latLng.split(',')]
                if len(latLng) != 2:
                    raise ValueError
                latLng = (latLng[0], latLng[1])
            except ValueError:
                return Response(request=request,
                                data={ 'message': 'Invalid parameters', 'parameters': { 'latLng': ['Invalid value'] } },
                                serializer=None,
                                status=HTTPStatus.CLIENT_ERROR_400_BAD_REQUEST)
            
            # If no radius is provided, default to 0.5
            radius = request.GET.get('radius', 0.5)
            
            # Validate radius.
            try:
                radius = float(radius)
            except ValueError:
                return Response(request=request,
                                data={ 'message': 'Invalid parameters', 'parameters': { 'radius': ['Invalid value'] } },
                                serializer=None,
                                status=HTTPStatus.CLIENT_ERROR_400_BAD_REQUEST)
                
            # Filter results by radius search.
            filters['latLng'] = request.GET.get('latLng', None)
            filters['radius'] = radius
            results = Place.search_radius(latLng=latLng, radius=radius, querySet=results)

        ###
        # Name.
        try:
            name = request.GET['name']
            if name != '':
                results = results.filter(Q(name__icontains=name))
                filters['name'] = name
        except KeyError:
            pass
        
        #
        # Return.
        #
        return Response(request=request,
                        data=results,
                        filters=filters,
                        serializer=PlaceSerializer,
                        pagination=pagination,
                        status=HTTPStatus.SUCCESS_200_OK)
        
        
class PlaceIdHandler(Resource):
    """
    API endpoint handler.
    """
    
    # HTTP methods allowed.
    allowed_methods = ['GET', 'PUT']
    
    def get(self, request, pk):
        """
        Process GET request.
        """
        # Check if instance with given ID exists.
        try:
            instance = Place.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return HttpResponse(status=HTTPStatus.CLIENT_ERROR_404_NOT_FOUND)
        
        # **************** IMPORTANT ***************
        # Only show inactive places to _staff_ users.
        # ******************************************
        if not instance.active and (not request.user or not request.user.is_staff):
            return HttpResponse(status=HTTPStatus.CLIENT_ERROR_404_NOT_FOUND)
        
        # Return.
        return Response(request=request,
                        data=instance,
                        serializer=PlaceSerializer,
                        status=HTTPStatus.SUCCESS_200_OK)
    
    @authentication_classes([SessionAuthentication, ApiKeyAuthentication])
    @permission_classes([IsStaff])
    def put(self, request, pk):
        """
        Process PUT request.
        """
        # Check if instance with given ID exists.
        try:
            instance = Place.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return HttpResponse(status=HTTPStatus.CLIENT_ERROR_404_NOT_FOUND)
        
        # Add additional required info regarding the user that created this Place.
        # IMPORTANT:
        # Remember that this instance already exists, so basically we want to keep this field value untouched.
        request.data['created_by'] = instance.created_by.pk
        
        # Populate form with provided data, for given instance.
        form = PlaceForm(request.data, instance=instance)
        
        # Update.
        try:
            form.save()
            return Response(request=request,
                            data=instance,
                            serializer=PlaceSerializer,
                            status=HTTPStatus.SUCCESS_200_OK)
            
        # Form didn't validate!
        except ValueError:
            return Response(request=request,
                            data={ 'message': 'Invalid parameters', 'parameters': form.errors },
                            serializer=None,
                            status=HTTPStatus.CLIENT_ERROR_400_BAD_REQUEST)


class PhotosHandler(Resource):
    """
    API endpoint handler.
    """
    # HTTP methods allowed.
    allowed_methods = ['POST', 'GET']
    
    @authentication_classes([SessionAuthentication, ApiKeyAuthentication])
    def post(self, request, pk):
        """
        Process POST request.
        """
        # Check if (active) Place with given ID exists.
        try:
            place = Place.objects.get(pk=pk, active=True)
        except ObjectDoesNotExist:
            return HttpResponse(status=HTTPStatus.CLIENT_ERROR_404_NOT_FOUND)
        
        # Add user and place IDs to data.
        request.data['added_by'] = request.auth['user'].pk
        request.data['place'] = place.pk
        
        # Populate form with provided data.
        form = PhotoForm(request.POST, request.FILES)
        
        # Provided data is valid.
        if form.is_valid():
            
            # Save photo.
            try:
                photo = Photo.new(place=place, photo_file=form.cleaned_data['file'], user=request.auth['user'])
            except IOError:
                return Response(request=request,
                            data={ 'message': 'Error uploading place photo #1' },
                            serializer=None,
                            status=HTTPStatus.SERVER_ERROR_500_INTERNAL_SERVER_ERROR)    
            
            # Return.
            return Response(request=request,
                            data=photo,
                            serializer=PhotoSerializer,
                            status=HTTPStatus.SUCCESS_201_CREATED)
        
        # Form didn't validate!
        else:
            return Response(request=request,
                            data={ 'message': 'Invalid parameters', 'parameters': form.errors },
                            serializer=None,
                            status=HTTPStatus.CLIENT_ERROR_400_BAD_REQUEST)
    
    def get(self, request, pk):
        """
        Process GET request.
        """
        # Check if Place with given ID exists.
        try:
            place = Place.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return HttpResponse(status=HTTPStatus.CLIENT_ERROR_404_NOT_FOUND)
        
        # **************** IMPORTANT ***************
        # Only _staff_ users can access stuff of inactive places.
        # ******************************************
        if not place.active and (not request.user or not request.user.is_staff):
            return HttpResponse(status=HTTPStatus.CLIENT_ERROR_404_NOT_FOUND)
        
        # Lets start with all.
        results = place.photo_set.all()
        
        #
        # Return.
        #
        return Response(request=request,
                        data=results,
                        serializer=PhotoSerializer,
                        status=HTTPStatus.SUCCESS_200_OK)


class PhotoIdHandler(Resource):
    """
    API endpoint handler.
    """
    
    # HTTP methods allowed.
    allowed_methods = ['GET', 'DELETE']
    
    def get(self, request, pk, photo_pk):
        """
        Process GET request.
        """
        # Check if instance with given ID for given Place ID exists. 
        try:
            place = Place.objects.get(pk=pk)
            instance = Photo.objects.get(pk=photo_pk, place=place)
        except ObjectDoesNotExist:
            return HttpResponse(status=HTTPStatus.CLIENT_ERROR_404_NOT_FOUND)
        
        # **************** IMPORTANT ***************
        # Only _staff_ users can access stuff of inactive places.
        # ******************************************
        if not place.active and (not request.user or not request.user.is_staff):
            return HttpResponse(status=HTTPStatus.CLIENT_ERROR_404_NOT_FOUND)
        
        # Return.
        return Response(request=request,
                        data=instance,
                        serializer=PhotoSerializer,
                        status=HTTPStatus.SUCCESS_200_OK)
        
    @authentication_classes([SessionAuthentication, ApiKeyAuthentication])
    @permission_classes([IsStaff])
    def delete(self, request, pk, photo_pk):
        """
        Process DELETE request.
        """
        # Check if instance with given ID for given Place ID exists. 
        try:
            place = Place.objects.get(pk=pk)
            instance = Photo.objects.get(pk=photo_pk, place=place)
        except ObjectDoesNotExist:
            return HttpResponse(status=HTTPStatus.CLIENT_ERROR_404_NOT_FOUND)
        
        # Proceed...
        instance.destroy()
        return HttpResponse(status=HTTPStatus.SUCCESS_204_NO_CONTENT)

            
class ReviewsHandler(Resource):
    """
    API endpoint handler.
    """
    # HTTP methods allowed.
    allowed_methods = ['POST', 'GET']
    
    @authentication_classes([SessionAuthentication, ApiKeyAuthentication])
    def post(self, request, pk):
        """
        Process POST request.
        """
        # Check if (active) Place with given ID exists.
        try:
            place = Place.objects.get(pk=pk, active=True)
        except ObjectDoesNotExist:
            return HttpResponse(status=HTTPStatus.CLIENT_ERROR_404_NOT_FOUND)
        
        ############################
        # a) Review without photo. #
        ############################
        
        # No file, fetch YAPI parsed payload.
        if len(request.FILES) == 0:
            
            # Add user and place IDs to data.
            request.data['user'] = request.auth['user'].pk
            request.data['place'] = place.pk
            
            # Populate form with provided data.
            form = ReviewForm(request.data)
            
            # Create new instance.
            try:
                new_instance = form.save()
                return Response(request=request,
                                data=new_instance,
                                serializer=ReviewSerializer,
                                status=HTTPStatus.SUCCESS_201_CREATED)
                
            # Form didn't validate!
            except ValueError:
                return Response(request=request,
                                data={ 'message': 'Invalid parameters', 'parameters': form.errors },
                                serializer=None,
                                status=HTTPStatus.CLIENT_ERROR_400_BAD_REQUEST)
         
        ###########################
        # b) Review _WITH_ photo. #
        ###########################
        else:
            
            # Add user and place IDs to data.
            request.POST['user'] = request.auth['user'].pk
            request.POST['place'] = place.pk
            
            # Populate forms with provided data.
            review_form = ReviewForm(request.POST)
            photo_form = PhotoForm(request.POST, request.FILES)
            
            # Provided data is valid.
            if review_form.is_valid() and photo_form.is_valid():
                
                # Save photo.
                try:
                    photo = Photo.new(place=place, photo_file=photo_form.cleaned_data['file'], user=request.auth['user'])
                    
                    # Create review.
                    review = review_form.save()
                    
                    # Link photo.
                    review.photo = photo
                    review.save()
                    
                    # Return.
                    return Response(request=request,
                                    data=review,
                                    serializer=ReviewSerializer,
                                    status=HTTPStatus.SUCCESS_201_CREATED)
                    
                except IOError:
                    return Response(request=request,
                                data={ 'message': 'Error creating review #1' },
                                serializer=None,
                                status=HTTPStatus.SERVER_ERROR_500_INTERNAL_SERVER_ERROR)
            
            # Forms didn't validate!
            else:
                return Response(request=request,
                                data={ 'message': 'Invalid parameters', 'parameters': review_form.errors },
                                serializer=None,
                                status=HTTPStatus.CLIENT_ERROR_400_BAD_REQUEST)
    
    def get(self, request, pk):
        """
        Process GET request.
        """
        # Check if Place with given ID exists.
        try:
            place = Place.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return HttpResponse(status=HTTPStatus.CLIENT_ERROR_404_NOT_FOUND)
        
        # **************** IMPORTANT ***************
        # Only _staff_ users can access stuff of inactive places.
        # ******************************************
        if not place.active and (not request.user or not request.user.is_staff):
            return HttpResponse(status=HTTPStatus.CLIENT_ERROR_404_NOT_FOUND)
        
        # Lets start with all.
        results = place.review_set.all()
        
        #
        # Return.
        #
        return Response(request=request,
                        data=results,
                        serializer=ReviewSerializer,
                        status=HTTPStatus.SUCCESS_200_OK)
        
        
class ReviewIdHandler(Resource):
    """
    API endpoint handler.
    """
    
    # HTTP methods allowed.
    allowed_methods = ['GET', 'DELETE']
    
    def get(self, request, pk, review_pk):
        """
        Process GET request.
        """
        # Check if instance with given ID for given Place ID exists. 
        try:
            place = Place.objects.get(pk=pk)
            instance = Review.objects.get(pk=review_pk, place=place)
        except ObjectDoesNotExist:
            return HttpResponse(status=HTTPStatus.CLIENT_ERROR_404_NOT_FOUND)
        
        # **************** IMPORTANT ***************
        # Only _staff_ users can access stuff of inactive places.
        # ******************************************
        if not place.active and (not request.user or not request.user.is_staff):
            return HttpResponse(status=HTTPStatus.CLIENT_ERROR_404_NOT_FOUND)
        
        # Return.
        return Response(request=request,
                        data=instance,
                        serializer=ReviewSerializer,
                        status=HTTPStatus.SUCCESS_200_OK)
    
    @authentication_classes([SessionAuthentication, ApiKeyAuthentication])
    def delete(self, request, pk, review_pk):
        """
        Process DELETE request.
        """
        # Check if instance with given ID for given Place ID exists.
        try:
            place = Place.objects.get(pk=pk)
            instance = Review.objects.get(pk=review_pk, place=place)
        except ObjectDoesNotExist:
            return HttpResponse(status=HTTPStatus.CLIENT_ERROR_404_NOT_FOUND)
        
        # **************** IMPORTANT ***************
        # Only _staff_ users can access stuff of inactive places.
        # ******************************************
        if not place.active and (not request.user or not request.user.is_staff):
            return HttpResponse(status=HTTPStatus.CLIENT_ERROR_404_NOT_FOUND)
        
        # Check if Review belongs to user.
        elif instance.user != request.auth['user']:
            return HttpResponseForbidden()
        
        # Proceed...
        else:
            instance.destroy()
            return HttpResponse(status=HTTPStatus.SUCCESS_204_NO_CONTENT)