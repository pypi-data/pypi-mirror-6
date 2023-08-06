from django.contrib import admin

from models import Place, Rating, Photo, Review


class PlaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'city', 'country', 'created_at', 'created_by', 'active')
    search_fields = ('name', 'address', 'city', 'country', 'created_by__email')
    list_filter = ('active',)
admin.site.register(Place, PlaceAdmin)


class RatingAdmin(admin.ModelAdmin):
    list_display = ('place', 'average', 'reviews', 'relative')
    search_fields = ('place__name',)
admin.site.register(Rating, RatingAdmin)


class PhotoAdmin(admin.ModelAdmin):
    list_display = ('place', 'file', 'added_at', 'added_by')
    search_fields = ('place__name', 'added_by__email')
admin.site.register(Photo, PhotoAdmin)


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('place', 'user', 'date', 'rating', 'photo')
    search_fields = ('place__name', 'user__email', 'comment')
    list_filter = ('rating',)
admin.site.register(Review, ReviewAdmin)