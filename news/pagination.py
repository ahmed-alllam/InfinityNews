from core.pagination import CursorPaginationWithCount


class TimeStampCursorPagination(CursorPaginationWithCount):
    ordering = '-timestamp'
    page_size = 25


class SortCursorPagination(CursorPaginationWithCount):
    ordering = 'sort'
    page_size = 30
