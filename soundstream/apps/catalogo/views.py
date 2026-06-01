"""
Vistas de Catalogo:
- Publicas: detalle de artista/album y registro de reproduccion.
- Panel admin (solo rol 'admin'): CRUD de Artista, Album y Cancion.
"""

from datetime import time

from django.contrib import messages
from django.db import IntegrityError
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from apps.usuarios.auth import get_usuario, admin_required
from .forms import ArtistaForm, AlbumForm, CancionForm
from .models import Artista, Album, Cancion


# ----------------------------------------------------------------------------
# Vistas publicas
# ----------------------------------------------------------------------------
def detalle_artista(request, pk):
    artista = get_object_or_404(Artista.objects.select_related('discografica'), pk=pk)
    albumes = artista.albumes.prefetch_related('canciones')
    return render(request, 'web/artista_detalle.html', {
        'artista': artista,
        'albumes': albumes,
    })


def detalle_album(request, pk):
    album = get_object_or_404(Album.objects.select_related('artista'), pk=pk)
    canciones = album.canciones.all()
    return render(request, 'web/album_detalle.html', {
        'album': album,
        'canciones': canciones,
    })


@require_http_methods(['POST'])
def reproducir_cancion(request, pk):
    """CRUD: incrementa numReproducciones e inserta una Reproduccion real."""
    from apps.operacion.models import Reproduccion

    usuario = get_usuario(request)
    if usuario is None:
        return JsonResponse({'ok': False, 'error': 'login'}, status=401)

    cancion = get_object_or_404(Cancion, pk=pk)
    cancion.num_reproducciones = (cancion.num_reproducciones or 0) + 1
    cancion.save(update_fields=['num_reproducciones'])

    Reproduccion.objects.create(
        usuario=usuario,
        cancion=cancion,
        fecha=timezone.now(),
        tiempo_escuchado=cancion.duracion or time(0, 3, 0),
        pais_origen=(usuario.pais or 'Ecuador'),
    )

    return JsonResponse({
        'ok': True,
        'cancion': cancion.titulo,
        'reproducciones': cancion.num_reproducciones,
    })


# ----------------------------------------------------------------------------
# Panel de administracion (solo admin)
# ----------------------------------------------------------------------------
@admin_required
def gestion_panel(request):
    return render(request, 'web/gestion_panel.html', {
        'n_artistas': Artista.objects.count(),
        'n_albumes': Album.objects.count(),
        'n_canciones': Cancion.objects.count(),
    })


@admin_required
def gestion_artistas(request):
    q = request.GET.get('q', '').strip()
    artistas = Artista.objects.select_related('discografica')
    if q:
        artistas = artistas.filter(
            Q(nombre__icontains=q) | Q(discografica__nombre__icontains=q))
    filas = [{
        'pk': a.id_artista,
        'campos': [a.nombre, a.discografica.nombre if a.discografica else '-',
                   a.albumes.count()],
    } for a in artistas]
    return render(request, 'web/gestion_lista.html', {
        'titulo': 'Artistas', 'singular': 'artista', 'q': q,
        'columnas': ['Nombre', 'Discografica', 'Albumes'],
        'filas': filas,
        'url_nuevo': 'catalogo:artista_nuevo',
        'url_editar': 'catalogo:artista_editar',
        'url_eliminar': 'catalogo:artista_eliminar',
    })


@admin_required
def artista_form(request, pk=None):
    instancia = get_object_or_404(Artista, pk=pk) if pk else None
    if request.method == 'POST':
        form = ArtistaForm(request.POST, instance=instancia)
        if form.is_valid():
            form.save()
            messages.success(request, 'Artista guardado correctamente.')
            return redirect('catalogo:gestion_artistas')
    else:
        form = ArtistaForm(instance=instancia)
    return render(request, 'web/gestion_form.html', {
        'form': form, 'titulo': 'artista', 'es_edicion': instancia is not None,
        'url_volver': 'catalogo:gestion_artistas',
    })


@admin_required
@require_http_methods(['POST'])
def artista_eliminar(request, pk):
    artista = get_object_or_404(Artista, pk=pk)
    try:
        artista.delete()
        messages.success(request, 'Artista eliminado.')
    except IntegrityError:
        messages.error(request, 'No se puede eliminar: el artista tiene albumes u otros datos asociados.')
    return redirect('catalogo:gestion_artistas')


@admin_required
def gestion_albumes(request):
    q = request.GET.get('q', '').strip()
    albumes = Album.objects.select_related('artista')
    if q:
        albumes = albumes.filter(
            Q(titulo__icontains=q) | Q(artista__nombre__icontains=q))
    filas = [{
        'pk': al.id_album,
        'campos': [al.titulo, al.artista.nombre, al.anio, al.canciones.count()],
    } for al in albumes]
    return render(request, 'web/gestion_lista.html', {
        'titulo': 'Albumes', 'singular': 'album', 'q': q,
        'columnas': ['Titulo', 'Artista', 'Anio', 'Canciones'],
        'filas': filas,
        'url_nuevo': 'catalogo:album_nuevo',
        'url_editar': 'catalogo:album_editar',
        'url_eliminar': 'catalogo:album_eliminar',
    })


@admin_required
def album_form(request, pk=None):
    instancia = get_object_or_404(Album, pk=pk) if pk else None
    if request.method == 'POST':
        form = AlbumForm(request.POST, instance=instancia)
        if form.is_valid():
            form.save()
            messages.success(request, 'Album guardado correctamente.')
            return redirect('catalogo:gestion_albumes')
    else:
        form = AlbumForm(instance=instancia)
    return render(request, 'web/gestion_form.html', {
        'form': form, 'titulo': 'album', 'es_edicion': instancia is not None,
        'url_volver': 'catalogo:gestion_albumes',
    })


@admin_required
@require_http_methods(['POST'])
def album_eliminar(request, pk):
    album = get_object_or_404(Album, pk=pk)
    try:
        album.delete()
        messages.success(request, 'Album eliminado.')
    except IntegrityError:
        messages.error(request, 'No se puede eliminar: el album tiene canciones asociadas.')
    return redirect('catalogo:gestion_albumes')


@admin_required
def gestion_canciones(request):
    q = request.GET.get('q', '').strip()
    canciones = Cancion.objects.select_related('album__artista')
    if q:
        canciones = canciones.filter(
            Q(titulo__icontains=q) | Q(album__titulo__icontains=q)
            | Q(album__artista__nombre__icontains=q))
    canciones = canciones[:200]
    filas = [{
        'pk': c.id_cancion,
        'campos': [c.titulo, c.album.titulo, c.album.artista.nombre,
                   c.calidad_audio, c.num_reproducciones],
    } for c in canciones]
    return render(request, 'web/gestion_lista.html', {
        'titulo': 'Canciones', 'singular': 'cancion', 'q': q,
        'columnas': ['Titulo', 'Album', 'Artista', 'Calidad', 'Reproducciones'],
        'filas': filas,
        'url_nuevo': 'catalogo:cancion_nuevo',
        'url_editar': 'catalogo:cancion_editar',
        'url_eliminar': 'catalogo:cancion_eliminar',
    })


@admin_required
def cancion_form(request, pk=None):
    instancia = get_object_or_404(Cancion, pk=pk) if pk else None
    if request.method == 'POST':
        form = CancionForm(request.POST, instance=instancia)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cancion guardada correctamente.')
            return redirect('catalogo:gestion_canciones')
    else:
        form = CancionForm(instance=instancia)
    return render(request, 'web/gestion_form.html', {
        'form': form, 'titulo': 'cancion', 'es_edicion': instancia is not None,
        'url_volver': 'catalogo:gestion_canciones',
    })


@admin_required
@require_http_methods(['POST'])
def cancion_eliminar(request, pk):
    cancion = get_object_or_404(Cancion, pk=pk)
    try:
        cancion.delete()
        messages.success(request, 'Cancion eliminada.')
    except IntegrityError:
        messages.error(request, 'No se puede eliminar: la cancion tiene reproducciones u otros datos asociados.')
    return redirect('catalogo:gestion_canciones')
