"""
Vistas de operacion: historial del usuario (reproducciones, suscripcion, pagos)
y reporte de regalias por artista (lectura de datos reales).
"""

from django.db.models import Sum, Count
from django.shortcuts import render

from apps.catalogo.models import Artista
from apps.usuarios.auth import get_usuario, usuario_required
from .models import Reproduccion, Pago, Regalia, Suscripcion


@usuario_required
def historial_usuario(request):
    usuario = get_usuario(request)
    reproducciones = (Reproduccion.objects
                      .filter(usuario=usuario)
                      .select_related('cancion__album__artista')[:50])
    suscripcion = (Suscripcion.objects
                   .filter(usuario=usuario)
                   .order_by('-fecha_inicio')
                   .first())
    pagos = (Pago.objects
             .filter(suscripcion__usuario=usuario, resultado='Aprobado')
             .select_related('suscripcion'))
    return render(request, 'web/historial.html', {
        'reproducciones': reproducciones,
        'pagos': pagos,
        'suscripcion': suscripcion,
    })


def reporte_regalias(request):
    """Reporte: total de regalias acumuladas por artista (datos reales)."""
    resultados = (Artista.objects
                  .annotate(total_monto=Sum('regalias__monto'),
                            num_regalias=Count('regalias'))
                  .filter(num_regalias__gt=0)
                  .order_by('-total_monto'))
    total_global = Regalia.objects.aggregate(t=Sum('monto'))['t'] or 0
    return render(request, 'web/regalias.html', {
        'resultados': resultados,
        'total_global': total_global,
    })
