import django_filters
from apps.products.models import Product


class ProductFilter(django_filters.FilterSet):
    category = django_filters.NumberFilter(field_name='category__id', lookup_expr='exact')
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    rating_min = django_filters.NumberFilter(field_name='rating', lookup_expr='gte')
    condition = django_filters.ChoiceFilter(choices=Product.CONDITION_CHOICES)
    is_active = django_filters.BooleanFilter(field_name='is_active')
    search = django_filters.CharFilter(method='filter_search')

    class Meta:
        model = Product
        fields = ['category', 'min_price', 'max_price', 'rating_min', 'condition', 'is_active']

    def filter_search(self, queryset, name, value):
        if value:
            return queryset.filter(name__icontains=value) | queryset.filter(description__icontains=value)
        return queryset
