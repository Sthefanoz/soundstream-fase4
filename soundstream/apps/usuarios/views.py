"""
Registro de Usuario y CRUD completo de Playlist (Operacion.Playlist) +
gestion de canciones en la playlist (Operacion.Cancion_Playlist).
"""

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from apps.catalogo.models import Cancion
from .auth import get_usuario, login_usuario, usuario_required
from .forms import RegistroForm, PlaylistForm
from .models import Playlist, CancionPlaylist


def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login_usuario(request, usuario)
            messages.success(request, 'Cuenta creada. Bienvenido a SoundStream.')
            return redirect('web:inicio')
    else:
        form = RegistroForm()
    return render(request, 'web/registro.html', {'form': form})


@usuario_required
def mis_playlists(request):
    playlists = Playlist.objects.filter(usuario=get_usuario(request))
    return render(request, 'web/playlists.html', {
        'playlists': playlists,
        'es_propio': True,
    })


def playlists_publicas(request):
    playlists = (Playlist.objects
                 .filter(tipo_visibilidad='publica')
                 .select_related('usuario')[:30])
    return render(request, 'web/playlists.html', {
        'playlists': playlists,
        'es_propio': False,
    })


@usuario_required
def crear_playlist(request):
    if request.method == 'POST':
        form = PlaylistForm(request.POST)
        if form.is_valid():
            playlist = form.save(commit=False)
            playlist.usuario = get_usuario(request)
            playlist.save()
            messages.success(request, f'Playlist "{playlist.nombre}" creada.')
            return redirect('usuarios:detalle_playlist', playlist_id=playlist.id_playlist)
    else:
        form = PlaylistForm()
    return render(request, 'web/playlist_form.html', {'form': form})


@usuario_required
def editar_playlist(request, playlist_id):
    playlist = get_object_or_404(Playlist, pk=playlist_id, usuario=get_usuario(request))
    if request.method == 'POST':
        form = PlaylistForm(request.POST, instance=playlist)
        if form.is_valid():
            form.save()
            messages.success(request, f'Playlist "{playlist.nombre}" actualizada.')
            return redirect('usuarios:mis_playlists')
    else:
        form = PlaylistForm(instance=playlist)
    return render(request, 'web/playlist_form.html', {
        'form': form,
        'playlist': playlist,
    })


@usuario_required
@require_http_methods(['POST'])
def eliminar_playlist(request, playlist_id):
    playlist = get_object_or_404(Playlist, pk=playlist_id, usuario=get_usuario(request))
    nombre = playlist.nombre
    # managed=False no aplica cascade: primero limpiamos la tabla puente.
    CancionPlaylist.objects.filter(playlist=playlist).delete()
    playlist.delete()
    messages.success(request, f'Playlist "{nombre}" eliminada.')
    return redirect('usuarios:mis_playlists')


@usuario_required
def detalle_playlist(request, playlist_id):
    playlist = get_object_or_404(Playlist, pk=playlist_id, usuario=get_usuario(request))
    ids_actuales = list(
        CancionPlaylist.objects.filter(playlist=playlist).values_list('cancion', flat=True))
    canciones = (Cancion.objects
                 .filter(id_cancion__in=ids_actuales)
                 .select_related('album__artista'))
    disponibles = (Cancion.objects
                   .exclude(id_cancion__in=ids_actuales)
                   .select_related('album__artista')
                   .order_by('titulo'))
    return render(request, 'web/playlist_detalle.html', {
        'playlist': playlist,
        'canciones': canciones,
        'disponibles': disponibles,
    })


@usuario_required
@require_http_methods(['POST'])
def agregar_cancion(request, playlist_id):
    playlist = get_object_or_404(Playlist, pk=playlist_id, usuario=get_usuario(request))
    cancion = get_object_or_404(Cancion, pk=request.POST.get('cancion_id'))
    if not CancionPlaylist.objects.filter(playlist=playlist, cancion=cancion).exists():
        CancionPlaylist.objects.create(playlist=playlist, cancion=cancion)
        messages.success(request, f'"{cancion.titulo}" agregada a la playlist.')
    return redirect('usuarios:detalle_playlist', playlist_id=playlist.id_playlist)


@usuario_required
@require_http_methods(['POST'])
def quitar_cancion(request, playlist_id, cancion_id):
    playlist = get_object_or_404(Playlist, pk=playlist_id, usuario=get_usuario(request))
    CancionPlaylist.objects.filter(playlist=playlist, cancion_id=cancion_id).delete()
    messages.success(request, 'Cancion quitada de la playlist.')
    return redirect('usuarios:detalle_playlist', playlist_id=playlist.id_playlist)
