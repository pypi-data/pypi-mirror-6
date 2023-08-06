import logging
from django import forms

from models import Place, Review

# Instantiate logger.
logger = logging.getLogger(__name__)


class PlaceForm(forms.ModelForm):
    """
    Fields required to create/update Places.
    """
    class Meta:
        model = Place
        

class PhotoForm(forms.Form):
    """
    Form for Place's photos.
    """
    file = forms.ImageField()
        
        
class ReviewForm(forms.ModelForm):
    """
    Fields required to create/update Reviews.
    """
    class Meta:
        model = Review