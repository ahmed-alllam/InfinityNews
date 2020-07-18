from core.pagination import CursorPaginationWithCount


class TimeStampCursorPagination(CursorPaginationWithCount):
    ordering = '-timestamp'
    page_size = 25


class PriorityCursorPagination(CursorPaginationWithCount):
    ordering = 'priority'
    page_size = 30
