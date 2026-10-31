from rest_framework.test import APITestCase
from rest_framework import status
from aplikacja1.models import Cocktail
from django.contrib.auth import get_user_model

User = get_user_model()


class CocktailTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="admin_test",
            password="Test12345!"
        )


    def test_lista_koktajli(self):
        response = self.client.get("/api/cocktails/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data["results"], list)
        self.assertEqual(response.data["count"], 0)


    def test_dodawanie_koktajlu(self):
        self.client.force_authenticate(user=self.admin)
        dane = {
            "name": "TestowyDrink",
            "count": 5
        }

        response = self.client.post("/api/cocktails/", dane, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Cocktail.objects.count(), 1)


    def test_bledne_dane(self):
        self.client.force_authenticate(user=self.admin)
        dane = {
            "name": "A",
            "count": -5
        }
        response = self.client.post("/api/cocktails/", dane, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Cocktail.objects.count(), 0)
        self.assertIn("name", response.data)
        self.assertIn("count", response.data)


    def test_szczegoly_koktajlu(self):

        koktajl = Cocktail.objects.create(
            name="Mojito",
            count=5
        )
        response = self.client.get(f"/api/cocktails/{koktajl.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("name", response.data)


    def test_patch_koktajlu(self):
        self.client.force_authenticate(user=self.admin)

        koktajl = Cocktail.objects.create(
            name="Mojito",
            count=5
        )
        response = self.client.patch(
            f"/api/cocktails/{koktajl.id}/",{"count": 10},format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 10)


    def test_delete_koktaj(self):
        self.client.force_authenticate(user=self.admin)

        koktajl = Cocktail.objects.create(
            name="Mojito",
            count=5
        )

        response = self.client.delete(
            f"/api/cocktails/{koktajl.id}/"
        )

        self.assertEqual(response.status_code, 204)
        self.assertEqual(Cocktail.objects.count(), 0)


    def test_nieistniejacy_koktajl(self):
        response = self.client.get(
            f"/api/cocktails/{999999}/")
        self.assertEqual(response.status_code, 404)


    def test_niedozwolona_metoda(self):
        response = self.client.delete(f"/api/cocktails/")
        self.assertEqual(response.status_code, 405)


    def test_zwykly_uzytkownik_nie_moze_usunac(self):
        user = User.objects.create_user(
            username="jan",
            password="12345"
        )

        coctail_ob = Cocktail.objects.create(
            name="Mojito",
            count=5
        )

        self.client.force_authenticate(user=user)

        response = self.client.delete(
            f"/api/cocktails/{coctail_ob.pk}/"
        )

        self.assertEqual(response.status_code, 403)

        self.assertTrue(
            Cocktail.objects.filter(pk=coctail_ob.pk).exists()
        )


    def test_niezalogowany_nie_moze_dodac(self):
        dane = {
            "name": "Mojito",
            "count": 5
        }

        response = self.client.post(
            "/api/cocktails/",
            dane,
            format="json"
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Cocktail.objects.count(), 0)


    def test_bledny_max_count(self):
        response = self.client.get("/api/cocktails/?max_count=abc")

        self.assertEqual(response.status_code, 400)
        self.assertIn("max_count", response.data)


    def test_rejestracja(self):
        dane = {
            "username": "nowy",
            "password": "Haslo12345!"
        }

        response = self.client.post("/api/register/", dane, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["username"], "nowy")
        self.assertNotIn("password", response.data)
        self.assertTrue(
            User.objects.get(username="nowy").check_password("Haslo12345!")
        )


    def test_rejestracja_slabe_haslo(self):
        dane = {
            "username": "nowy",
            "password": "1"
        }

        response = self.client.post("/api/register/", dane, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("password", response.data)
        self.assertFalse(User.objects.filter(username="nowy").exists())


    def test_rejestracja_zajety_login(self):
        dane = {
            "username": "admin_test",
            "password": "Haslo12345!"
        }

        response = self.client.post("/api/register/", dane, format="json")

        self.assertEqual(response.status_code, 400)
        self.assertIn("username", response.data)
