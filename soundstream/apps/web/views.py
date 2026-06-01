"""
Vistas publicas con animaciones de scroll. Datos REALES de SQL Server.
Login/Logout usan la auth propia (apps.usuarios.auth) contra Operacion.Usuario.
"""

from datetime import timedelta
from decimal import Decimal

from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.shortcuts import redirect, render
from django.utils import timezone

from apps.catalogo.models import Artista, Album, Cancion
from apps.operacion.models import Suscripcion, Pago
from apps.usuarios.auth import (autenticar, login_usuario, logout_usuario,
                                usuario_required, get_usuario)
from .forms import ContratarForm


PLANES_INFO = {
    'free': {'nombre': 'Free', 'precio': Decimal('0.00')},
    'premium': {'nombre': 'Premium', 'precio': Decimal('9.99')},
    'familiar': {'nombre': 'Familiar', 'precio': Decimal('14.99')},
}


def inicio(request):
    top_artistas = (Artista.objects
                    .annotate(plays=Sum('albumes__canciones__num_reproducciones'))
                    .order_by('-plays')[:6])
    nuevos_albumes = (Album.objects
                      .select_related('artista')
                      .order_by('-fecha_lanzamiento')[:8])
    top_canciones = (Cancion.objects
                     .select_related('album__artista')
                     .order_by('-num_reproducciones')[:10])
    return render(request, 'web/inicio.html', {
        'top_artistas': top_artistas,
        'nuevos_albumes': nuevos_albumes,
        'top_canciones': top_canciones,
    })


def catalogo(request):
    query = request.GET.get('q', '').strip()
    qs = Cancion.objects.select_related('album__artista')
    if query:
        qs = qs.filter(
            Q(titulo__icontains=query)
            | Q(album__artista__nombre__icontains=query)
            | Q(album__titulo__icontains=query))
    canciones = qs.order_by('-num_reproducciones')[:60]
    return render(request, 'web/catalogo.html', {
        'canciones': canciones,
        'query': query,
    })


def artistas(request):
    artistas_qs = (Artista.objects
                   .select_related('discografica')
                   .annotate(total_albumes=Count('albumes'))
                   .order_by('nombre'))
    return render(request, 'web/artistas.html', {'artistas': artistas_qs})


def albumes(request):
    albumes_qs = (Album.objects
                  .select_related('artista')
                  .annotate(total_canciones=Count('canciones'))
                  .order_by('-fecha_lanzamiento'))
    return render(request, 'web/albumes.html', {'albumes': albumes_qs})


def suscripciones(request):
    planes = [
        {
            'codigo': 'FREE', 'nombre': 'Free',
            'precio': '0', 'periodo': 'siempre',
            'features': [
                'Acceso al catalogo completo',
                'Calidad estandar 128 kbps',
                'Con anuncios cada 3 canciones',
                'Saltos limitados (6/hora)',
                'Sin descargas offline',
            ],
            'destacado': False,
        },
        {
            'codigo': 'PREMIUM', 'nombre': 'Premium',
            'precio': '9.99', 'periodo': '/mes',
            'features': [
                'Sin anuncios',
                'Calidad 320 kbps + FLAC lossless',
                'Saltos ilimitados',
                'Descarga offline',
                'Letras sincronizadas',
            ],
            'destacado': True,
        },
        {
            'codigo': 'FAMILIAR', 'nombre': 'Familiar',
            'precio': '14.99', 'periodo': '/mes',
            'features': [
                'Hasta 6 cuentas Premium',
                'Control parental',
                'Playlists colaborativas',
                'Calidad FLAC en todas las cuentas',
                'Soporte prioritario',
            ],
            'destacado': False,
        },
    ]
    return render(request, 'web/suscripciones.html', {'planes': planes})


def contacto(request):
    enviado = False
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        email = request.POST.get('email', '').strip()
        mensaje = request.POST.get('mensaje', '').strip()
        if nombre and email and mensaje:
            messages.success(request, 'Mensaje enviado. Te responderemos en 24h.')
            enviado = True
        else:
            messages.error(request, 'Completa todos los campos.')
    return render(request, 'web/contacto.html', {'enviado': enviado})


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        usuario = autenticar(email, password)
        if usuario is not None:
            login_usuario(request, usuario)
            messages.success(request, f'Bienvenido, {usuario.primer_nombre}.')
            return redirect('web:inicio')
        messages.error(request, 'Correo o contrasena incorrectos.')
    return render(request, 'web/login.html')


def logout_view(request):
    logout_usuario(request)
    messages.success(request, 'Sesion cerrada.')
    return redirect('web:inicio')


@usuario_required
def contratar_plan(request, plan):
    """Contrata un plan para el usuario logueado: crea Suscripcion (+ Pago si es de pago)."""
    info = PLANES_INFO.get(plan.lower())
    if not info:
        messages.error(request, 'Plan no valido.')
        return redirect('web:suscripciones')

    usuario = get_usuario(request)
    es_pago = info['precio'] > 0
    form = None

    if request.method == 'POST':
        if es_pago:
            form = ContratarForm(request.POST)
            if not form.is_valid():
                messages.error(request, 'Revisa los datos de pago.')
                return render(request, 'web/contratar.html',
                              {'plan': plan.lower(), 'info': info, 'form': form})
            metodo = form.cleaned_data['metodo_pago']
        else:
            metodo = None

        hoy = timezone.localdate()
        # Vence la suscripcion activa anterior (un solo plan activo a la vez).
        Suscripcion.objects.filter(usuario=usuario, estado='Activa').update(estado='Vencida')
        suscripcion = Suscripcion.objects.create(
            usuario=usuario,
            tipo_plan=info['nombre'],
            fecha_inicio=hoy,
            fecha_fin=hoy + timedelta(days=30),
            estado='Activa',
        )
        # Con managed=False, segun la version de mssql-django/Python, el insert
        # no siempre devuelve el PK autogenerado. Si falta, lo recuperamos.
        if not suscripcion.pk:
            suscripcion = (Suscripcion.objects
                           .filter(usuario=usuario, estado='Activa',
                                   tipo_plan=info['nombre'], fecha_inicio=hoy)
                           .order_by('-id_suscripcion').first())
        if es_pago:
            Pago.objects.create(
                suscripcion=suscripcion,
                monto=info['precio'],
                fecha_pago=timezone.now(),
                metodo_pago=metodo,
                resultado='Aprobado',
            )
            messages.success(request, f'Pago aprobado. Plan {info["nombre"]} activado.')
        else:
            messages.success(request, 'Plan Free activado.')
        return redirect('operacion:historial')

    if es_pago:
        form = ContratarForm()
    return render(request, 'web/contratar.html',
                  {'plan': plan.lower(), 'info': info, 'form': form})
