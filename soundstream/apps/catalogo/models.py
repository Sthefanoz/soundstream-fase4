"""
Modelos del esquema 'Catalogo' en SoundStreamDB.
managed = False -> Django NO crea ni migra estas tablas; ya existen (Fase 3).
Cada campo mapea por db_column al nombre real (camelCase) de la tabla.
"""

from django.db import models


class Discografica(models.Model):
    id_discografica = models.AutoField(primary_key=True, db_column='idDiscografica')
    nombre = models.CharField(max_length=50, db_column='nombreDiscografica')
    pais = models.CharField(max_length=30, blank=True, null=True, db_column='pais')
    fecha_fundacion = models.DateField(null=True, blank=True, db_column='fechaFundacion')

    class Meta:
        managed = False
        db_table = '[Catalogo].[Discografica]'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Genero(models.Model):
    id_genero = models.AutoField(primary_key=True, db_column='idGenero')
    nombre = models.CharField(max_length=50, db_column='nombreGenero')

    class Meta:
        managed = False
        db_table = '[Catalogo].[Genero]'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Artista(models.Model):
    id_artista = models.AutoField(primary_key=True, db_column='idArtista')
    nombre = models.CharField(max_length=120, db_column='nombreArtistico')
    biografia = models.TextField(blank=True, null=True, db_column='biografia')
    foto = models.CharField(max_length=500, blank=True, null=True, db_column='foto',
                            help_text='URL de la foto del artista')
    discografica = models.ForeignKey(
        Discografica, on_delete=models.DO_NOTHING, db_column='idDiscografica',
        null=True, blank=True, related_name='artistas')

    class Meta:
        managed = False
        db_table = '[Catalogo].[Artista]'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Album(models.Model):
    id_album = models.AutoField(primary_key=True, db_column='idAlbum')
    titulo = models.CharField(max_length=160, db_column='titulo')
    fecha_lanzamiento = models.DateField(null=True, blank=True, db_column='fechaLanzamiento')
    portada = models.CharField(max_length=500, blank=True, null=True, db_column='portada',
                               help_text='URL de la portada del album')
    artista = models.ForeignKey(
        Artista, on_delete=models.DO_NOTHING, db_column='idArtista',
        related_name='albumes')

    class Meta:
        managed = False
        db_table = '[Catalogo].[Album]'
        ordering = ['-fecha_lanzamiento', 'titulo']

    def __str__(self):
        return self.titulo

    @property
    def anio(self):
        return self.fecha_lanzamiento.year if self.fecha_lanzamiento else ''


class Cancion(models.Model):
    id_cancion = models.AutoField(primary_key=True, db_column='idCancion')
    titulo = models.CharField(max_length=160, db_column='titulo')
    duracion = models.TimeField(null=True, blank=True, db_column='duracion')
    calidad_audio = models.CharField(max_length=20, blank=True, null=True, db_column='calidadAudio')
    num_reproducciones = models.IntegerField(default=0, db_column='numReproducciones')
    preview = models.CharField(max_length=500, blank=True, null=True, db_column='preview',
                               help_text='URL de la preview de audio (30s)')
    album = models.ForeignKey(
        Album, on_delete=models.DO_NOTHING, db_column='idAlbum',
        related_name='canciones')

    class Meta:
        managed = False
        db_table = '[Catalogo].[Cancion]'
        ordering = ['titulo']

    def __str__(self):
        return self.titulo

    @property
    def duracion_mmss(self):
        if not self.duracion:
            return '0:00'
        total = self.duracion.hour * 3600 + self.duracion.minute * 60 + self.duracion.second
        return f'{total // 60}:{total % 60:02d}'

    @property
    def es_flac(self):
        return (self.calidad_audio or '').upper() == 'FLAC'
