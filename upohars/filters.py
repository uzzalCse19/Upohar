import django_filters
from .models import UpoharPost

class UpoharPostFilter(django_filters.FilterSet):
    city = django_filters.CharFilter(lookup_expr='icontains')
    category = django_filters.CharFilter(field_name='category__name', lookup_expr='iexact')
    status = django_filters.CharFilter()
    donor = django_filters.CharFilter(field_name='donor__email', lookup_expr='iexact')

    class Meta:
        model = UpoharPost
        fields = ['city', 'category', 'status', 'donor']
