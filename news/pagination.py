from core.pagination import CursorPaginationWithCount


class TimeStampCursorPagination(CursorPaginationWithCount):
    ordering = '-timestamp'
    page_size = 20


class SortCursorPagination(CursorPaginationWithCount):
    ordering = 'sort'
    page_size = 30
