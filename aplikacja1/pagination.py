
from rest_framework.pagination import PageNumberPagination


class CocktailPagination(PageNumberPagination):
    page_size = 5
