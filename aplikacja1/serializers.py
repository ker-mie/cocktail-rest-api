
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from aplikacja1.models import Cocktail, Ingredient

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

User = get_user_model()

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ["id", "name"]


class CocktailSerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        max_length=100,
        validators=[
            UniqueValidator(
                queryset=Cocktail.objects.all(),
                message="Koktajl o tej nazwie już istnieje."
            )
        ]
    )

    ingredients = IngredientSerializer(many=True, read_only=True)

    ingredient_ids = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        many=True,
        write_only=True,
        source="ingredients",
        required=False
    )

    def validate_count(self, value):
        if value < 0:
            raise serializers.ValidationError(
                "count nie może być ujemne"
            )
        return value

    def validate_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError(
                "nazwa musi zawierać przynajmniej 3 znaki"
            )
        return value

    def validate(self, data):
        name = data.get("name")
        count = data.get("count")

        if self.instance is not None:
            if name is None:
                name = self.instance.name
            if count is None:
                count = self.instance.count

        if name and name.lower() == "mojito" and count == 0:
            raise serializers.ValidationError("Błędne dane")

        return data

    class Meta:
        model = Cocktail
        fields = [
            "id",
            "name",
            "count",
            "ingredients",
            "ingredient_ids"
        ]


class RegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["username", "password"]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def validate(self, data):
        user = User(username=data.get("username"))
        try:
            validate_password(data.get("password"), user)
        except DjangoValidationError as e:
            raise serializers.ValidationError({"password": list(e.messages)})
        return data

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
