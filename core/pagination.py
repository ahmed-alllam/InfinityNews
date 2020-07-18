from collections import OrderedDict

from rest_framework.pagination import CursorPagination
from rest_framework.response import Response


class CursorPaginationWithCount(CursorPagination):
    def paginate_queryset(self, queryset, request, view=None):
        self.get_count(queryset)
        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))

    def get_paginated_response_schema(self, schema):
        return {
            'type': 'object',
            'properties': {
                'count': {
                    'type': 'int',
                    'nullable': True
                },
                'next': {
                    'type': 'string',
                    'nullable': True,
                },
                'previous': {
                    'type': 'string',
                    'nullable': True,
                },
                'results': schema,
            },
        }

    def get_count(self, queryset):
        self.count = queryset.count()
