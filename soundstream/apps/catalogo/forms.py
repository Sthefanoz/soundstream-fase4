"""
Formularios del panel de administracion para el CRUD del catalogo.
Las FK (discografica/artista/album) son obligatorias porque las columnas
idDiscografica/idArtista/idAlbum son NOT NULL en la BD de Fase 3.
"""

from django import forms

from .models import Artista, Album, Cancion


class ArtistaForm(forms.ModelForm):
    class Meta:
        model = Artista
        fields = ('nombre', 'biografia', 'foto', 'discografica')
        labels = {
            'nombre': 'Nombre artistico',
            'biografia': 'Biografia',
            'foto': 'URL de la foto',
            'discografica': 'Discografica',
        }
        widgets = {
            'biografia': forms.Textarea(attrs={'rows': 4}),
            'foto': forms.TextInput(attrs={'placeholder': 'https://...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['discografica'].required = True


class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ('titulo', 'fecha_lanzamiento', 'portada', 'artista')
        labels = {
            'titulo': 'Titulo',
            'fecha_lanzamiento': 'Fecha de lanzamiento',
            'portada': 'URL de la portada',
            'artista': 'Artista',
        }
        widgets = {
            'fecha_lanzamiento': forms.DateInput(attrs={'type': 'date'}),
            'portada': forms.TextInput(attrs={'placeholder': 'https://...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['artista'].required = True


class CancionForm(forms.ModelForm):
    CALIDADES = [('320kbps', '320 kbps'), ('FLAC', 'FLAC'), ('128kbps', '128 kbps')]

    calidad_audio = forms.ChoiceField(choices=CALIDADES, label='Calidad de audio')

    class Meta:
        model = Cancion
        fields = ('titulo', 'duracion', 'calidad_audio', 'album')
        labels = {
            'titulo': 'Titulo',
            'duracion': 'Duracion (HH:MM:SS)',
            'album': 'Album',
        }
        widgets = {
            'duracion': forms.TimeInput(attrs={'placeholder': '00:03:45'}, format='%H:%M:%S'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['album'].required = True
        self.fields['duracion'].input_formats = ['%H:%M:%S', '%H:%M']
