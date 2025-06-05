from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Libro, PerfilUsuario
from django.urls import reverse
import json

class ListaDeLibrosTest(TestCase):
    def setUp(self):
        # Crear dos usuarios
        self.user1 = User.objects.create_user(username='usuario1', password='test123')
        self.user2 = User.objects.create_user(username='usuario2', password='test123')

        # Crear un libro
        self.libro = Libro.objects.create(
            titulo_del_libro='Libro de prueba',
            autor='Autor',
            genero='Ficción',
            resumen='Resumen del libro',
            usuario=self.user1
        )

        # Crear perfiles (si no se crean automáticamente)
        self.perfil1 = PerfilUsuario.objects.get_or_create(user=self.user1)[0]
        self.perfil2 = PerfilUsuario.objects.get_or_create(user=self.user2)[0]

    def test_agregar_libro_a_lista_solo_afecta_al_usuario_actual(self):
        client = Client()

        # Login como usuario1
        client.login(username='usuario1', password='test123')

        # Llamar a la vista para agregar a "leídos"
        response = client.post(
            reverse('agregar_a_lista'),
            data=json.dumps({'book_id': self.libro.id, 'lista': 'leidos'}),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )

        self.assertEqual(response.status_code, 200)

        # Verificar que el libro está solo en la lista de usuario1
        self.assertIn(self.libro, self.perfil1.libros_leidos.all())
        self.assertNotIn(self.libro, self.perfil2.libros_leidos.all())
        self.assertNotIn(self.libro, self.perfil2.libros_por_leer.all())
