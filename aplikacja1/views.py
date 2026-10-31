from drf_spectacular.types import OpenApiTypes
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListAPIView
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import PageNumberPagination
from .models import Cocktail
from .serializers import CocktailSerializer
from .permissions import OdczytDlaWszystkichEdycjaDlaAdmina
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer
User = get_user_model()
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
)
from drf_spectacular.types import OpenApiTypes

@extend_schema_view(
    get=extend_schema(
        summary="Pobierz szczegóły koktajlu",
        description="Zwraca koktajl o wskazanym ID. Dostępny dla wszystkich.",
        responses={200: CocktailSerializer},
    ),
    put=extend_schema(
        summary="Zaktualizuj cały koktajl",
        description="Zastępuje dane koktajlu. Wymaga uprawnień administratora.",
        request=CocktailSerializer,
        responses={200: CocktailSerializer},
    ),
    patch=extend_schema(
        summary="Częściowo zaktualizuj koktajl",
        description="Aktualizuje wybrane pola. Wymaga uprawnień administratora.",
        request=CocktailSerializer,
        responses={200: CocktailSerializer},
    ),
    delete=extend_schema(
        summary="Usuń koktajl",
        description="Usuwa koktajl. Wymaga uprawnień administratora.",
        responses={204: None},
    ),
)

@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([OdczytDlaWszystkichEdycjaDlaAdmina])
def cocktail_detail(request, pk):
    koktajl = get_object_or_404(Cocktail, pk=pk)

    if request.method == "GET":
        tlumacz = CocktailSerializer(koktajl)
        return Response(tlumacz.data)
    elif request.method == "DELETE":
        koktajl.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    elif request.method == "PUT":
        tlumacz = CocktailSerializer(koktajl, data=request.data)
        if tlumacz.is_valid():
            tlumacz.save()
            return Response(tlumacz.data,status=status.HTTP_200_OK)
        else:
            return Response(tlumacz.errors,status=status.HTTP_400_BAD_REQUEST)
    elif request.method == "PATCH":
        tlumacz = CocktailSerializer(koktajl,data=request.data,partial=True)
        if tlumacz.is_valid():
            tlumacz.save()
            return Response(tlumacz.data,status=status.HTTP_200_OK)
        else:
            return Response(tlumacz.errors,status=status.HTTP_400_BAD_REQUEST)


class MojPager(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'size'
    max_page_size = 50

@extend_schema_view(
    get=extend_schema(
        summary="Pobierz listę koktajli",
        description="Lista koktajli z filtrowaniem, sortowaniem i paginacją.",
        parameters=[
            OpenApiParameter(name="name", type=str),
            OpenApiParameter(name="min_count", type=int),
            OpenApiParameter(name="max_count", type=int),
            OpenApiParameter(name="count", type=int),
            OpenApiParameter(name="ingredient", type=str),
            OpenApiParameter(
                name="ordering",
                type=str,
                enum=["name", "-name", "count", "-count", "id", "-id"],
            ),
        ],
        responses={200: CocktailSerializer(many=True)},
    ),
    post=extend_schema(
        summary="Dodaj nowy koktajl",
        description="Tworzy nowy koktajl. Wymaga zalogowania.",
        request=CocktailSerializer,
        responses={201: CocktailSerializer},
    ),
)

@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def cocktail_list(request):
    if request.method == "GET":
        ingredient = request.query_params.get("ingredient")
        count = request.query_params.get("count")
        min_count = request.query_params.get("min_count")
        max_count = request.query_params.get("max_count")
        name = request.query_params.get("name")
        cocktails = Cocktail.objects.all()

        if min_count is not None:
            try:
                min_count = int(min_count)
                if min_count < 0:
                    return Response(
                        {"error": "min_count nie może być ujemne"},status=status.HTTP_400_BAD_REQUEST)
                cocktails = cocktails.filter(count__gte=min_count)
            except ValueError:
                return Response({"error":"musi być liczbą calkowita"},status=status.HTTP_400_BAD_REQUEST)

        if max_count is not None:
            try:
                max_count = int(max_count)

                if max_count < 0:
                    raise ValidationError({
                        "max_count": "Liczba nie może być ujemna"
                    })

            except ValueError:
                raise ValidationError({
                    "max_count": "Podaj poprawną liczbę"
                })

            cocktails = cocktails.filter(count__lte=max_count)
        if count is not None:
            try:
                count = int(count)
                cocktails = cocktails.filter(count=count)
            except ValueError:
                return Response({"error": "musi być liczbą calkowita"}, status=status.HTTP_400_BAD_REQUEST)
        if name is not None:
            cocktails = cocktails.filter(name__icontains=name)

        if ingredient is not None:
            cocktails = cocktails.filter(ingredients__name__icontains=ingredient)
        sortowanie = request.query_params.get("ordering", "id")

        dozwolone = ["name", "-name", "count", "-count", "id", "-id"]

        if sortowanie not in dozwolone:
            return Response(
                {"error": "Nieprawidłowe sortowanie"},
                status=status.HTTP_400_BAD_REQUEST
            )

        cocktails = cocktails.distinct()
        cocktails = cocktails.order_by(sortowanie)

        paginator = MojPager()
        strona = paginator.paginate_queryset(cocktails, request)
        serializer = CocktailSerializer(strona, many=True)

        return paginator.get_paginated_response(serializer.data)
    elif request.method == "POST":
        if not request.user.is_authenticated:
            return Response(
                {"error": "Musisz być zalogowany"},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = CocktailSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema(
    methods=["POST"],
    summary="Zarejestruj użytkownika",
    description="Tworzy nowe konto użytkownika.",
    request=RegisterSerializer,
    responses={201: OpenApiTypes.OBJECT},
)

@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()

        return Response(
            {"username": serializer.data["username"]},
            status=status.HTTP_201_CREATED
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )
