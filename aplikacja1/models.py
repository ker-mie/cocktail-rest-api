from django.db import models

#

class Cocktail(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    count = models.IntegerField()

    def __str__(self):
        return self.name

    def set_count(self, count):
        self.count = count

    def set_double(self):
        self.count = self.count*2

class Ingredient(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    cocktail = models.ManyToManyField(
        Cocktail,
        related_name='ingredients'
    )

    def __str__(self):
        return self.name
