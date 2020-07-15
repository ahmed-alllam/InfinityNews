from rest_framework.pagination import CursorPagination


class TimeStampCursorPagination(CursorPagination):
    ordering = '-timestamp'
    page_size = 25


class PriorityCursorPagination(CursorPagination):
    ordering = 'priority'
    page_size = 30
