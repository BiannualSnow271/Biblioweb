from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    foto_perfil = models.ImageField(upload_to='perfiles/', blank=True, null=True)

    libros_leidos = models.ManyToManyField('Libro', related_name='usuarios_que_leyeron', blank=True)
    libros_por_leer = models.ManyToManyField('Libro', related_name='usuarios_que_quieren_leer', blank=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"

class Libro(models.Model):
    titulo_del_libro = models.CharField(max_length=255)
    autor = models.CharField(max_length=100)
    genero = models.CharField(max_length=50)
    resumen = models.TextField(max_length=255)
    foto_perfil = models.ImageField(upload_to='portadas_libros/', blank=True, null=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.titulo_del_libro}"

class Valoracion(models.Model):
    puntuacion = models.FloatField()
    comentario = models.CharField(max_length=255, blank=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE)
    fecha = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.usuario.username} rated {self.libro} - {self.puntuacion}"

class Foro(models.Model):
    creador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='foros_creados', null=True)
    titulo_del_foro = models.CharField(max_length=255)
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE)
    participantes = models.ManyToManyField(User, through='Participacion', related_name='foros_participando')

    def __str__(self):
        return f"Foro: {self.titulo_del_foro}"

class Participacion(models.Model):
    foro = models.ForeignKey(Foro, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    aprobado = models.BooleanField(default=True)

    class Meta:
        unique_together = ('foro', 'usuario')

    def __str__(self):
        return f"{self.usuario} en {self.foro} (Aprobado: {self.aprobado})"

class PublicacionForo(models.Model):
    id_publicacion = models.CharField(max_length=255, primary_key=True)
    mensaje = models.TextField()
    fecha = models.DateField()
    foro = models.ForeignKey(Foro, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.usuario.username} - {self.fecha}"
