import django_filters

from .models import Movies


class MovieFilter(django_filters.FilterSet):
    title = django_filters.CharFilter()

    class Meta:
        model = Movies
        fields = ['title']
