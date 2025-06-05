from django.urls import path
from . import views

urlpatterns = [
    path('', views.startpage, name='startpage'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('buscar/', views.buscar_libros, name='buscar_libros'),
    path('crear_libro/', views.crear_libro, name='crear_libro'),
    path('crear_foro/', views.crear_foro, name='crear_foro'),
    path('foro/<int:id>', views.foro, name='foro'),
    path('authentication', views.login_register_view, name='authentication'),
    path('libro/<int:libro_id>/', views.detalle_libro, name='detalle_libro'),
    path('agregar-a-lista/', views.agregar_a_lista, name='agregar_a_lista'),
    path('mis-libros/leidos/', views.libros_leidos, name='libros_leidos'),
    path('mis-libros/por-leer/', views.libros_por_leer, name='libros_por_leer'),
    path('salir_foro/<int:foro_id>/', views.salir_foro, name='salir_foro'),
    path('foro/<int:foro_id>/buscar_usuarios/', views.buscar_usuarios_para_foro, name='buscar_usuarios_para_foro'),
    path('foro/<int:foro_id>/agregar_participante/', views.agregar_participante_foro, name='agregar_participante_foro'),
]
