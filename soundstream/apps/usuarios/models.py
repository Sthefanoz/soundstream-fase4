"""
Esquema 'Operacion': Usuario, Playlist y la tabla puente Cancion_Playlist.
managed = False -> mapean a las tablas reales de Fase 3.
La autenticacion del sitio se hace contra Operacion.Usuario (ver auth.py).
"""

from django.db import models

from apps.catalogo.models import Cancion


class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True, db_column='idUsuario')
    primer_nombre = models.CharField(max_length=50, db_column='primerNombre')
    primer_apellido = models.CharField(max_length=50, db_column='primerApellido')
    email = models.CharField(max_length=120, db_column='email')
    password = models.CharField(max_length=255, db_column='password')
    pais = models.CharField(max_length=50, blank=True, null=True, db_column='pais')
    fecha_registro = models.DateField(null=True, blank=True, db_column='fechaRegistro')
    estado_cuenta = models.CharField(max_length=20, blank=True, null=True,
                                     default='Activo', db_column='estadoCuenta')
    rol = models.CharField(max_length=20, default='usuario', db_column='rol')

    class Meta:
        managed = False
        db_table = '[Operacion].[Usuario]'
        ordering = ['primer_nombre', 'primer_apellido']

    def __str__(self):
        return self.nombre_completo

    @property
    def nombre_completo(self):
        return f'{self.primer_nombre} {self.primer_apellido}'

    @property
    def es_admin(self):
        return (self.rol or '').lower() == 'admin'


class Playlist(models.Model):
    VISIBILIDAD = [
        ('publica', 'Publica'),
        ('privada', 'Privada'),
    ]

    id_playlist = models.AutoField(primary_key=True, db_column='idPlaylist')
    nombre = models.CharField(max_length=120, db_column='nombre')
    descripcion = models.CharField(max_length=255, blank=True, null=True, db_column='descripcion')
    tipo_visibilidad = models.CharField(max_length=20, choices=VISIBILIDAD,
                                        default='publica', db_column='tipoVisibilidad')
    usuario = models.ForeignKey(Usuario, on_delete=models.DO_NOTHING,
                                db_column='idUsuario', related_name='playlists')

    class Meta:
        managed = False
        db_table = '[Operacion].[Playlist]'
        ordering = ['-id_playlist']

    def __str__(self):
        return self.nombre

    @property
    def es_publica(self):
        return (self.tipo_visibilidad or '').lower() == 'publica'

    @property
    def canciones(self):
        """Canciones de la playlist (a traves de la tabla puente)."""
        return Cancion.objects.filter(
            id_cancion__in=CancionPlaylist.objects
            .filter(playlist=self).values('cancion')
        ).select_related('album__artista')


class CancionPlaylist(models.Model):
    """
    Tabla puente Operacion.Cancion_Playlist (PK compuesta idCancion+idPlaylist).
    Django no soporta PK compuesta: usamos idCancion como pk y filtramos siempre
    por playlist, asi cada fila tiene idCancion unico dentro de una playlist.
    """
    cancion = models.ForeignKey(Cancion, on_delete=models.DO_NOTHING,
                                db_column='idCancion', primary_key=True, related_name='+')
    playlist = models.ForeignKey(Playlist, on_delete=models.DO_NOTHING,
                                 db_column='idPlaylist', related_name='canciones_rel')

    class Meta:
        managed = False
        db_table = '[Operacion].[Cancion_Playlist]'
        unique_together = (('cancion', 'playlist'),)
