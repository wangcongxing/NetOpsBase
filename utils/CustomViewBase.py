# Base类，将增删改查方法重写
# !/usr/bin/env python
# -*- coding:utf-8 -*-

from utils import APIResponseResult
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from rest_framework import filters
from django_filters import rest_framework
from django_filters.rest_framework import DjangoFilterBackend


# 设置分页
class LargeResultsSetPagination(PageNumberPagination):
    page_size = 10  # 每页显示多少条
    page_size_query_param = 'limit'  # URL中每页显示条数的参数
    page_query_param = 'page'  # URL中页码的参数
    max_page_size = 200  # 最大页码数限制


class CustomViewBase(viewsets.ModelViewSet):
    # 注意不是列表（只能有一个分页模式）
    #pagination_class = PageNumberPagination
    # 自定义分页模式，不要写在base类中，如需要单独配置，请在views中通过继承的方式重写
    pagination_class = LargeResultsSetPagination
    # filter_class = ServerFilter
    # queryset = ''
    # serializer_class = ''
    # permission_classes = ()
    # filter_fields = ()
    # search_fields = ()
    filter_backends = (rest_framework.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return APIResponseResult.APIResponse(0, 'success', results=serializer.data, http_status=status.HTTP_200_OK,
                                             headers=headers)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return APIResponseResult.APIResponse(0, 'success',
                                                 results=serializer.data,
                                                 http_status=status.HTTP_200_OK, **{"count": len(queryset)})

            # return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return APIResponseResult.APIResponse(0, 'success', results=serializer.data, http_status=status.HTTP_200_OK, )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return APIResponseResult.APIResponse(0, 'success', results=serializer.data, http_status=status.HTTP_200_OK, )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return APIResponseResult.APIResponse(0, 'success', results=serializer.data, http_status=status.HTTP_200_OK, )

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return APIResponseResult.APIResponse(0, 'success',
                                             http_status=status.HTTP_200_OK, )

    # 批量删除
    @action(methods=['delete'], detail=False, url_path='multiple_delete')
    def multiple_delete(self, request, *args, **kwargs):
        delete_id = request.data.get("deleteid", "")
        list_ids = list(filter(None, delete_id.split(',')))
        list_ids = [int(x) for x in list_ids if x.split()]
        self.queryset.model.objects.filter(id__in=list_ids).delete()
        return APIResponseResult.APIResponse(0, "删除成功", results=list_ids)
