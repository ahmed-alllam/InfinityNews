from rest_framework.pagination import CursorPagination


class TimeStampCursorPagination(CursorPagination):
    ordering = '-timestamp'


class PriorityCursorPagination(CursorPagination):
    ordering = 'priority'
