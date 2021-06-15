from django_filters import rest_framework as filters
import django_filters
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from django.contrib.auth.models import User, Group, Permission


class PeriodicTaskFilter(filters.FilterSet):
    # 模糊过滤
    name = django_filters.CharFilter(field_name="name", lookup_expr='icontains')
    description = django_filters.CharFilter(field_name="description", lookup_expr='icontains')

    class Meta:
        model = PeriodicTask
        fields = ['name', 'description']


class UserFilter(filters.FilterSet):
    # 模糊过滤
    username = django_filters.CharFilter(field_name="username", lookup_expr='icontains')
    first_name = django_filters.CharFilter(field_name="first_name", lookup_expr='icontains')
    email = django_filters.CharFilter(field_name="email", lookup_expr='icontains')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'email']
