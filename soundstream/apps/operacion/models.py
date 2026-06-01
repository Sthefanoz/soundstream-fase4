"""
Esquema 'Operacion': Suscripcion, Pago, Reproduccion y Regalia.
managed = False -> mapean a las tablas reales de Fase 3.
"""

from django.db import models

from apps.catalogo.models import Cancion, Artista
from apps.usuarios.models import Usuario


class Suscripcion(models.Model):
    id_suscripcion = models.AutoField(primary_key=True, db_column='idSuscripcion')
    tipo_plan = models.CharField(max_length=30, db_column='tipoPlan')
    fecha_inicio = models.DateField(null=True, blank=True, db_column='fechaInicio')
    fecha_fin = models.DateField(null=True, blank=True, db_column='fechaFin')
    estado = models.CharField(max_length=20, blank=True, null=True, db_column='estado')
    usuario = models.ForeignKey(Usuario, on_delete=models.DO_NOTHING,
                                db_column='idUsuario', related_name='suscripciones')

    class Meta:
        managed = False
        db_table = '[Operacion].[Suscripcion]'
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f'{self.tipo_plan} ({self.estado})'

    @property
    def activa(self):
        return (self.estado or '').lower() == 'activa'


class Pago(models.Model):
    id_pago = models.AutoField(primary_key=True, db_column='idPago')
    monto = models.DecimalField(max_digits=10, decimal_places=2, db_column='monto')
    fecha_pago = models.DateTimeField(null=True, blank=True, db_column='fechaPago')
    metodo_pago = models.CharField(max_length=40, blank=True, null=True, db_column='metodoPago')
    resultado = models.CharField(max_length=20, blank=True, null=True, db_column='resultado')
    suscripcion = models.ForeignKey(Suscripcion, on_delete=models.DO_NOTHING,
                                    db_column='idSuscripcion', related_name='pagos')

    class Meta:
        managed = False
        db_table = '[Operacion].[Pago]'
        ordering = ['-fecha_pago']

    def __str__(self):
        return f'#{self.id_pago} - {self.monto}'

    @property
    def aprobado(self):
        return (self.resultado or '').lower() == 'aprobado'


class Reproduccion(models.Model):
    id_reproduccion = models.AutoField(primary_key=True, db_column='idReproduccion')
    fecha = models.DateTimeField(null=True, blank=True, db_column='fecha')
    tiempo_escuchado = models.TimeField(null=True, blank=True, db_column='tiempoEscuchado')
    pais_origen = models.CharField(max_length=50, blank=True, null=True, db_column='paisOrigen')
    usuario = models.ForeignKey(Usuario, on_delete=models.DO_NOTHING,
                                db_column='idUsuario', related_name='reproducciones')
    cancion = models.ForeignKey(Cancion, on_delete=models.DO_NOTHING,
                                db_column='idCancion', related_name='reproducciones')

    class Meta:
        managed = False
        db_table = '[Operacion].[Reproduccion]'
        ordering = ['-fecha']

    def __str__(self):
        return f'Reproduccion #{self.id_reproduccion}'


class Regalia(models.Model):
    id_regalia = models.AutoField(primary_key=True, db_column='idRegalia')
    monto = models.DecimalField(max_digits=12, decimal_places=4, db_column='monto')
    fecha_calculo = models.DateField(null=True, blank=True, db_column='fechaCalculo')
    reproduccion = models.ForeignKey(Reproduccion, on_delete=models.DO_NOTHING,
                                     db_column='idReproduccion', null=True, blank=True,
                                     related_name='regalias')
    cancion = models.ForeignKey(Cancion, on_delete=models.DO_NOTHING,
                                db_column='idCancion', null=True, blank=True,
                                related_name='regalias')
    artista = models.ForeignKey(Artista, on_delete=models.DO_NOTHING,
                                db_column='idArtista', null=True, blank=True,
                                related_name='regalias')

    class Meta:
        managed = False
        db_table = '[Operacion].[Regalia]'
        ordering = ['-fecha_calculo']

    def __str__(self):
        return f'Regalia #{self.id_regalia} - {self.monto}'
