"""
Comando: python manage.py previews_canciones [--solo-vacias]

Descarga la preview de audio (30s) de cada cancion desde la API publica de
Deezer y la guarda en Catalogo.Cancion.preview. Tambien corrige la duracion
(Catalogo.Cancion.duracion) con la duracion real que reporta Deezer.
No requiere API key.
"""

import json
import unicodedata
import urllib.parse
import urllib.request
from datetime import time

from django.core.management.base import BaseCommand
from django.db.models import Q

from apps.catalogo.models import Cancion


def normaliza(texto):
    t = unicodedata.normalize('NFD', texto or '')
    t = ''.join(c for c in t if unicodedata.category(c) != 'Mn')
    return t.lower().strip()


def buscar_track(titulo, artista):
    consultas = [
        f'artist:"{artista}" track:"{titulo}"',
        f'track:"{titulo}"',
        f'{artista} {titulo}',
    ]
    for consulta in consultas:
        url = 'https://api.deezer.com/search/track?' + urllib.parse.urlencode(
            {'q': consulta, 'limit': 5})
        try:
            with urllib.request.urlopen(url, timeout=15) as resp:
                resultados = json.load(resp).get('data', [])
        except Exception:
            resultados = []
        if resultados:
            return next(
                (t for t in resultados if normaliza(t['title']) == normaliza(titulo)),
                resultados[0])
    return None


class Command(BaseCommand):
    help = 'Descarga previews de audio y corrige duraciones desde Deezer.'

    def add_arguments(self, parser):
        parser.add_argument('--solo-vacias', action='store_true',
                            help='Solo procesa canciones que aun no tienen preview.')

    def handle(self, *args, **opts):
        qs = Cancion.objects.select_related('album__artista').order_by('titulo')
        if opts['solo_vacias']:
            qs = qs.filter(Q(preview__isnull=True) | Q(preview=''))

        ok = fallidos = 0
        for cancion in qs:
            track = buscar_track(cancion.titulo, cancion.album.artista.nombre)
            if not track or not track.get('preview'):
                fallidos += 1
                self.stdout.write(self.style.WARNING(f'  sin preview: {cancion.titulo}'))
                continue

            cancion.preview = track['preview']
            segundos = int(track.get('duration') or 0)
            if 0 < segundos < 3600:
                cancion.duracion = time(0, segundos // 60, segundos % 60)
            cancion.save(update_fields=['preview', 'duracion'])
            ok += 1
            self.stdout.write(f'  OK  {cancion.titulo}  ({cancion.album.artista.nombre})')

        self.stdout.write(self.style.SUCCESS(f'Listo: {ok} con preview, {fallidos} sin preview.'))
