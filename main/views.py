from .models import Libro, Foro, PublicacionForo, PerfilUsuario, Valoracion, Participacion
from django.db.models import Q, Avg
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import LibroForm, ForoForm, PublicacionForoForm
from django.utils.timezone import now
import uuid
from django.contrib.auth.models import User
from django.contrib import messages

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from django.utils import timezone


def login_register_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'login':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')  
            else:
                messages.error(request, 'Credenciales incorrectas')

        elif action == 'register':
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')

            if User.objects.filter(username=username).exists():
                messages.error(request, 'El usuario ya existe')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)

                # Crea perfil del usuario si aplica
                PerfilUsuario.objects.create(user=user)

                login(request, user)
                return redirect('dashboard')

    return render(request, 'login.html')




@login_required
def crear_foro(request):
    if request.method == 'POST':
        form = ForoForm(request.POST, user=request.user)
        if form.is_valid():
            foro = form.save(commit=False)
            foro.creador = request.user
            foro.save()
            form.save_m2m()

            # Aprobar automáticamente al creador del foro
            Participacion.objects.get_or_create(
                foro=foro,
                usuario=request.user,
                aprobado=True
            )

            # Aprobar automáticamente a los participantes seleccionados
            for participante in form.cleaned_data['participantes']:
                Participacion.objects.get_or_create(
                    foro=foro,
                    usuario=participante,
                    aprobado=True
                )

            return redirect('dashboard')
    else:
        form = ForoForm(user=request.user)

    return render(request, 'crear_foro.html', {'form': form})





@login_required
def crear_libro(request):
    if request.method == 'POST':
        form = LibroForm(request.POST, request.FILES)
        if form.is_valid():
            libro = form.save(commit=False)
            libro.usuario = request.user
            libro.save()
            return redirect('dashboard')  
    else:
        form = LibroForm()
    
    return render(request, 'crear_libro.html', {'form': form})




def buscar_libros(request):
    query = request.GET.get('q')  
    resultados = []
    titulo = "Libros que coinciden con tu búsqueda"

    if query:
        resultados = Libro.objects.filter(
            Q(titulo_del_libro__icontains=query) |
            Q(genero__icontains=query) |
            Q(autor__icontains=query)
        )

    leidos = []
    por_leer = []
    if request.user.is_authenticated:
        perfil, created = PerfilUsuario.objects.get_or_create(user=request.user)
        leidos = perfil.libros_leidos.all()
        por_leer = perfil.libros_por_leer.all()

    promedios_estrellas = {}

    for libro in resultados:
        promedio = Valoracion.objects.filter(libro=libro).aggregate(Avg('puntuacion'))['puntuacion__avg']
        if promedio is None:
            promedio = 0.0
        else:
            promedio = float(promedio)
        promedios_estrellas[libro.id] = promedio

    return render(request, 'book_list.html', {
        'titulo' : titulo,
        'books': resultados,
        'query': query,
        'leidos': leidos,
        'por_leer': por_leer,
        'promedios_estrellas': promedios_estrellas,
    })




@csrf_exempt
@require_POST
@login_required
def agregar_a_lista(request):
    try:
        data = json.loads(request.body)
        libro_id = data.get('book_id')
        lista = data.get('lista')
        libro = Libro.objects.get(id=libro_id)
        perfil = request.user.perfilusuario
        if lista == 'leidos':
            perfil.libros_por_leer.remove(libro)
            perfil.libros_leidos.add(libro)
        elif lista == 'por_leer':
            perfil.libros_leidos.remove(libro)
            perfil.libros_por_leer.add(libro)
        else:
            return JsonResponse({'error': 'Lista no válida'}, status=400)

        return JsonResponse({'status': 'ok'})
    except Libro.DoesNotExist:
        return JsonResponse({'error': 'Libro no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)



def startpage(request):
    return render(request, 'startpage.html')

@login_required
def dashboard(request):
    foros_usuario = Foro.objects.filter(participacion__usuario=request.user, participacion__aprobado=True)
    return render(request, 'dashboard.html', {
        'foros_usuario' : foros_usuario
    })

@login_required
def salir_foro(request, foro_id):
    foro = get_object_or_404(Foro, id=foro_id)
    participacion = Participacion.objects.filter(foro=foro, usuario=request.user)

    if participacion.exists():
        participacion.delete()

        # Si no quedan participaciones aprobadas...
        if not Participacion.objects.filter(foro=foro, aprobado=True).exists():
            # Borra el resto de participaciones no
            Participacion.objects.filter(foro=foro).delete()
            foro.delete()

    return redirect('dashboard')


@login_required
def libros_leidos(request):
    perfil = request.user.perfilusuario
    books = perfil.libros_leidos.all()


    promedios_estrellas = {}

    for libro in books:
        promedio = Valoracion.objects.filter(libro=libro).aggregate(Avg('puntuacion'))['puntuacion__avg']
        if promedio is None:
            promedio = 0.0
        else:
            promedio = float(promedio)
        promedios_estrellas[libro.id] = promedio

    return render(request, 'book_list.html', {
        'books': books,
        'titulo': 'Tus libros leídos',
        'leidos': books,
        'por_leer': [],  
        'promedios_estrellas': promedios_estrellas,
    })

@login_required
def libros_por_leer(request):
    perfil = request.user.perfilusuario
    books = perfil.libros_por_leer.all()

    promedios_estrellas = {}

    for libro in books:
        promedio = Valoracion.objects.filter(libro=libro).aggregate(Avg('puntuacion'))['puntuacion__avg']
        if promedio is None:
            promedio = 0.0
        else:
            promedio = float(promedio)
        promedios_estrellas[libro.id] = promedio

    return render(request, 'book_list.html', {
        'books': books,
        'titulo': 'Tus libros por leer',
        'leidos': [], 
        'por_leer': books,
        'promedios_estrellas': promedios_estrellas,
    })




@login_required
def foro(request, id):
    foro = get_object_or_404(Foro, id=id)
    publicaciones_foro = PublicacionForo.objects.filter(foro=foro).order_by('fecha')

    if request.method == 'POST':
        form = PublicacionForoForm(request.POST)
        if form.is_valid():
            publicacion = form.save(commit=False)
            publicacion.id_publicacion = str(uuid.uuid4())
            publicacion.usuario = request.user
            publicacion.foro = foro
            publicacion.fecha = now().date()
            publicacion.save()
            return redirect('foro', id=foro.id)  # Asumiendo que la URL se llama 'foro'
    else:
        form = PublicacionForoForm()

    return render(request, 'foro.html', {
        'foro': foro,
        'mensajes': publicaciones_foro,
        'form': form,
    })


@login_required
def buscar_usuarios_para_foro(request, foro_id):
    foro = get_object_or_404(Foro, id=foro_id)
    q = request.GET.get('q', '')
    participantes_ids = foro.participantes.values_list('id', flat=True)
    usuarios = User.objects.filter(username__icontains=q).exclude(id__in=participantes_ids)[:10]
    results = [{'id': u.id, 'text': u.username} for u in usuarios]
    return JsonResponse({'results': results})

@login_required
@require_POST
def agregar_participante_foro(request, foro_id):
    foro = get_object_or_404(Foro, id=foro_id)
    usuario_id = request.POST.get('usuario_id')
    if not usuario_id:
        return JsonResponse({'error': 'No se proporcionó usuario'}, status=400)
    try:
        usuario = User.objects.get(id=usuario_id)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Usuario no encontrado'}, status=404)

    # Evitar duplicados (si usas through, crear Participacion)
    from .models import Participacion
    if Participacion.objects.filter(foro=foro, usuario=usuario).exists():
        return JsonResponse({'error': 'Usuario ya es participante'}, status=400)

    Participacion.objects.create(foro=foro, usuario=usuario, aprobado=True)
    return JsonResponse({'success': True})



@login_required
def solicitar_participacion(request, foro_id):
    foro = get_object_or_404(Foro, id=foro_id)
    Participacion.objects.get_or_create(foro=foro, usuario=request.user, aprobado=False)
    return redirect('detalle_foro', foro.id)

@login_required
def gestionar_participantes(request, foro_id):
    foro = get_object_or_404(Foro, id=foro_id)
    if foro.creador != request.user:
        return redirect('detalle_foro', foro.id)

    solicitudes = Participacion.objects.filter(foro=foro, aprobado=False)

    if request.method == 'POST':
        user_id = request.POST.get('usuario_id')
        accion = request.POST.get('accion')
        participacion = get_object_or_404(Participacion, foro=foro, usuario_id=user_id)
        if accion == 'aceptar':
            participacion.aprobado = True
            participacion.save()
        elif accion == 'rechazar':
            participacion.delete()

    return render(request, 'gestionar_participantes.html', {'foro': foro, 'solicitudes': solicitudes})




@login_required
def detalle_libro(request, libro_id):
    libro = get_object_or_404(Libro, pk=libro_id)
    valoraciones = Valoracion.objects.filter(libro=libro).order_by('-fecha')
    promedio = valoraciones.aggregate(Avg('puntuacion'))['puntuacion__avg'] or 0

    # Calcular porcentaje para cada estrella (1 a 5)
    estrellas = []
    for i in range(1, 6):
        diff = promedio - (i - 1)
        if diff >= 1:
            estrellas.append(100)  # Estrella llena
        elif diff > 0:
            estrellas.append(round(diff * 100))  # Parcial proporcional
        else:
            estrellas.append(0)  # Vacía

    valoracion_usuario = Valoracion.objects.filter(libro=libro, usuario=request.user).first()

    if request.method == 'POST':
        try:
            puntuacion = float(request.POST.get('puntuacion', 0))
            if puntuacion < 0: puntuacion = 0
            if puntuacion > 5: puntuacion = 5
        except (ValueError, TypeError):
            puntuacion = 0

        comentario = request.POST.get('comentario', '').strip()

        if valoracion_usuario:
            valoracion_usuario.puntuacion = puntuacion
            valoracion_usuario.comentario = comentario
            valoracion_usuario.fecha = timezone.now()
            valoracion_usuario.save()
        else:
            Valoracion.objects.create(
                puntuacion=puntuacion,
                comentario=comentario,
                usuario=request.user,
                libro=libro,
                fecha=timezone.now()
            )

        return redirect('dashboard')

    return render(request, 'detalle_libro.html', {
        'libro': libro,
        'valoraciones': valoraciones,
        'promedio': promedio,
        'estrellas': estrellas,
        'valoracion_usuario': valoracion_usuario,  # <- Añadido
    })
