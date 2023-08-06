import logging
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import PageNotAnInteger, EmptyPage
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http.response import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils.text import slugify
from django.utils.translation import ugettext as _

from models import Place, Rating, Review

# Instantiate logger.
logger = logging.getLogger(__name__)


def index(request):
    """
    Index page.
    """
    # Page title.
    try:
        title = settings.YPLACES['index_title']
    except KeyError:
        title = 'YPLACES'
        
    # Page description.
    try:
        description = settings.YPLACES['index_description']
    except KeyError:
        description = ''
    
    # Top places.
    top_rating = Rating.objects.all().order_by('-relative')[:5]
    
    # Fetch latest reviews.
    reviews = Review.objects.all().order_by('-date')[:5]    
    
    # Render page.
    return render_to_response('yplaces/index.html',
                              { 'title': title,
                               'description': description,
                               'top_rating': top_rating,
                               'reviews': reviews,
                               'places_api_url': settings.HOST_URL + reverse(settings.YPLACES['api_url_namespace'] + ':yplaces:index') },
                              context_instance=RequestContext(request))


@login_required
def add(request):
    """
    Add new Place.
    """
    return render_to_response('yplaces/edit.html',
                              { 'title': _('Add Place'), 
                                'api_url': settings.HOST_URL + reverse(settings.YPLACES['api_url_namespace'] + ':yplaces:index'),
                                'action': 'POST',
                                'next': reverse('yplaces:index') },
                              context_instance=RequestContext(request))


def search(request):
    """
    Place search.
    """
    # Lets start with all..
    results = Place.objects.filter(active=True).order_by('name')
    
    # Search by name.
    try:
        name = request.GET['name']
        results = results.filter(Q(name__icontains=name))
    except KeyError:
        name = ''
    
    # Search by location.
    try:
        location = request.GET['location']
        results = results.filter(Q(address__icontains=location) | Q(city__icontains=location) | Q(state__icontains=location) | Q(country__icontains=location))
    except KeyError:
        location = ''
        
    # Fetch X items and paginate.
    paginator = Paginator(results, 10)
    try:
        page = request.GET.get('page')
        result_page = paginator.page(page)
        page = int(page)
    # If page is not an integer, deliver first page.
    except PageNotAnInteger:
        page = 1
        result_page = paginator.page(page)
    # If page is out of range (e.g. 9999), deliver last page of results.
    except EmptyPage:
        page = paginator.num_pages
        result_page = paginator.page(page)
    
    # Render page.
    return render_to_response('yplaces/search.html',
                              { 'search_name': name,
                                'search_location': location,
                                'search_results': result_page },
                              context_instance=RequestContext(request))


def place_id(request, pk):
    """
    Checks if the place with given ID exists and, if it does, redirect to the page with respective slug.
    """
    # Check if Place with given ID exists.
    try:
        place = Place.objects.get(pk=pk)
        
        # **************** IMPORTANT ***************
        # Only show inactive places to _staff_ users.
        # ******************************************
        if not place.active and (not request.user or not request.user.is_staff):
            raise Http404
        
        # Redirect to Place slug.
        return HttpResponseRedirect(reverse('yplaces:slug', args=[place.pk, slugify(place.name)]))
    
    # Invalid ID.
    except ObjectDoesNotExist:
        raise Http404


def place_slug(request, pk, slug):
    """
    Returns page for the place with the given ID.
    """
    # Check if Place with given ID exists.
    try:
        place = Place.objects.get(pk=pk)
        
        # **************** IMPORTANT ***************
        # Only show inactive places to _staff_ users.
        # ******************************************
        if not place.active and (not request.user or not request.user.is_staff):
            raise Http404
    
    # Invalid ID.
    except ObjectDoesNotExist:
        raise Http404
    
    # Highlighted Photos.
    photos = [None, None, None]
    no_photos = True
    for idx, photo in enumerate(place.photo_set.all()):
        if idx < 3:
            photos[idx] = photo
            no_photos = False
        else:
            break

    # Render page
    return render_to_response('yplaces/place.html',
                              { 'place': place,
                               'rating': place.get_rating(),
                               'photos': photos, 'no_photos': no_photos,
                               'reviews_api_url': settings.HOST_URL + reverse(settings.YPLACES['api_url_namespace'] + ':yplaces:reviews', args=[place.pk]),
                               'host_url': settings.HOST_URL },
                              context_instance=RequestContext(request))
    

@login_required
def edit(request, pk, slug):
    """
    Edit Place's information.
    """
    # Only staff members.
    if not request.user.is_staff:
        raise Http404
    
    # Fetch Place with given ID.
    try:
        place = Place.objects.get(pk=pk)
    except ObjectDoesNotExist:
        raise Http404
    
    # Render page.
    return render_to_response('yplaces/edit.html',
                              { 'place': place,
                                'title': _('Edit Place'),
                                'api_url': settings.HOST_URL + reverse(settings.YPLACES['api_url_namespace'] + ':yplaces:id', args=[place.pk]),
                                'action': 'PUT' },
                              context_instance=RequestContext(request))

    
def photos(request, pk, slug):
    """
    Renders the Place's photo gallery.
    """
    # Fetch Place with given ID.
    try:
        place = Place.objects.get(pk=pk, active=True)
    except ObjectDoesNotExist:
        raise Http404
    
    # Render page.
    return render_to_response('yplaces/photos.html',
                              { 'place': place,
                               'rating': place.get_rating(),
                               'photos_api_url': settings.HOST_URL + reverse(settings.YPLACES['api_url_namespace'] + ':yplaces:photos', args=[place.pk]) },
                              context_instance=RequestContext(request))