from django.contrib import admin
from .models import PerfilUsuario, Libro, Valoracion, Foro, PublicacionForo, Participacion

admin.site.register(PerfilUsuario)


admin.site.register(Libro)


admin.site.register(Valoracion)


admin.site.register(Foro)


admin.site.register(PublicacionForo)

admin.site.register(Participacion)
