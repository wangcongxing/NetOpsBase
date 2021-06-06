
from django_filters import rest_framework as filters
import django_filters
from django_celery_beat.models import PeriodicTask, IntervalSchedule


class PeriodicTaskFilter(filters.FilterSet):
    # 模糊过滤
    name = django_filters.CharFilter(field_name="name", lookup_expr='icontains')
    description = django_filters.CharFilter(field_name="description", lookup_expr='icontains')

    class Meta:
        model = PeriodicTask
        fields = ['name', 'description']