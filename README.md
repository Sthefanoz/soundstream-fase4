# SoundStream - Fase 4 Proyecto Integrador

Plataforma de streaming de musica construida sobre la base de datos real de la
Fase 3 (`SoundStreamDB` en SQL Server). Backend Django, frontend HTML/CSS/JS
con animaciones de scroll, fotos y portadas reales descargadas desde la API
publica de Deezer, y preview de audio de 30s para cada cancion.

**Materia:** ITIZ-2201 Base de Datos II - Fase 4.

---

## Stack

- **Backend**: Python 3.12, Django 5, mssql-django 1.7+, pyodbc
- **Base de datos**: SQL Server (esquemas `Catalogo` y `Operacion` de Fase 3)
- **Frontend**: HTML, CSS y JavaScript vanilla (sin librerias externas)
- **API externa**: Deezer publica (sin API key) para fotos, portadas y previews

---

## Requisitos previos

- **Python 3.12** (3.11 tambien funciona).
- **SQL Server** con la base `SoundStreamDB` ya creada (la de Fase 3).
- **ODBC Driver 17 o 18 for SQL Server** instalado.
- Internet (para cargar fotos/portadas/audio desde Deezer).

---

## Instalacion

### 1. Clonar y crear el entorno

```powershell
git clone https://github.com/TU_USUARIO/soundstream-fase4.git
cd soundstream-fase4
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r soundstream\requirements.txt
```

### 2. Aplicar los cambios de base de datos

El archivo `cambios_bd.sql` (en la raiz) agrega columnas necesarias para la
Fase 4 (`rol`, `foto`, `portada`, `preview`), inserta dos canciones de prueba
y marca al administrador.

```powershell
sqlcmd -S "localhost\SQLEXPRESS" -E -C -d SoundStreamDB -i cambios_bd.sql
```

Cambia `localhost\SQLEXPRESS` por **tu** instancia.

### 3. Configurar la conexion a la BD

Edita `soundstream/soundstream/settings.py` en la seccion `DATABASES` y ajusta
`HOST` y la autenticacion segun tu maquina. Algunos ejemplos:

```python
# Autenticacion de Windows en SQL Server Express:
'HOST': r'localhost\SQLEXPRESS',
'OPTIONS': {
    'driver': 'ODBC Driver 17 for SQL Server',
    'trusted_connection': 'yes',
    'extra_params': 'TrustServerCertificate=yes;',
}

# LocalDB con login SQL:
'HOST': r'(localdb)\MSSQLLocalDB',
'USER': 'tu_login',
'PASSWORD': 'tu_password',
'OPTIONS': {
    'driver': 'ODBC Driver 17 for SQL Server',
    'extra_params': 'TrustServerCertificate=yes;',
}
```

### 4. Migrar y rellenar contenido (imagenes y audio)

```powershell
cd soundstream
python manage.py migrate                # crea las tablas de sesiones de Django
python manage.py fotos_artistas         # baja fotos de artistas desde Deezer
python manage.py portadas_albumes       # baja portadas de albumes
python manage.py previews_canciones     # baja previews + corrige duraciones
```

### 5. Arrancar

```powershell
python manage.py runserver
```

Abre `http://127.0.0.1:8000/`.

---

## Login de prueba

- **Administrador** (acceso al panel de gestion del catalogo):
  - email: `sthefanozambrano1@gmail.com`
  - password: la que registraste

- **Usuarios normales** (datos reales de Fase 3 con contrasena demo):
  - email: `michelle.altamirano1@email.com` / password `pass001`
  - email: `josue.chiriboga2@email.com` / password `pass002`
  - email: `camila.simbana3@email.com` / password `pass003`
  - ...y asi el resto: cada usuario `i` usa la contrasena `passNNN` con su
    `idUsuario`.

Si vas a ser admin en tu propia BD, ejecuta:

```sql
UPDATE Operacion.Usuario SET rol='admin' WHERE email='tu_correo@email.com';
```

---

## Funcionalidades

| Pagina                       | Descripcion |
|------------------------------|-------------|
| `/`                          | Hero animado, top canciones (con play) y top artistas |
| `/catalogo/`                 | Buscador de canciones (titulo / artista / album) |
| `/artistas/`                 | Grilla con buscador en vivo |
| `/albumes/`                  | Grilla con buscador en vivo |
| `/usuarios/playlists/publicas/` | Playlists publicas con buscador en vivo |
| `/usuarios/playlists/mias/`  | Mis playlists (requiere login) - CRUD completo |
| `/usuarios/playlists/<id>/`  | Detalle: agregar/quitar canciones con buscador |
| `/suscripciones/`            | Planes (Free, Premium, Familiar) |
| `/suscripciones/contratar/X/`| Pago simulado con validacion de tarjeta (Luhn + MM/AA + CVV) |
| `/operacion/historial/`      | Historial de reproducciones y pagos |
| `/operacion/regalias/`       | Reporte de regalias por artista |
| `/catalogo/gestion/`         | Panel admin: CRUD de Artistas, Albumes y Canciones |

**CRUD operativo sobre SQL Server** (ideal para el video):
- Playlist: crear / editar / eliminar / agregar canciones / quitar canciones.
- Suscripcion y Pago: se crean al contratar un plan.
- Reproduccion: cada play incrementa `numReproducciones` e inserta una fila
  en `Operacion.Reproduccion`.
- Catalogo (solo admin): CRUD completo sobre `Catalogo.Artista`,
  `Catalogo.Album` y `Catalogo.Cancion`.

---

## Tarjeta de prueba para el pago

- Numero: `4242 4242 4242 4242`
- Vence: `12/30`
- CVV: `123`

---

## Comandos utiles

Dentro de `soundstream/` con el venv activado:

```powershell
python manage.py check                  # valida la configuracion
python manage.py runserver              # arranca el servidor
python manage.py migrate                # aplica migraciones de Django
python manage.py fotos_artistas         # baja/actualiza fotos
python manage.py portadas_albumes       # baja/actualiza portadas
python manage.py previews_canciones     # baja/actualiza previews + duracion
```

Cada comando acepta `--solo-vacias` para procesar solo los registros que aun
no tienen dato.

---

## Notas

- Las **fotos, portadas y audio** se sirven desde el CDN de Deezer; sin
  internet se ven los emojis de respaldo y los botones de play no suenan.
- El **pago es simulado**: los datos de tarjeta solo se validan, **no se
  guardan**. Solo se guarda el metodo de pago en `Operacion.Pago`.
- Las contrasenas de `Operacion.Usuario` estan en **texto plano** porque asi
  estaban en los datos de Fase 3; la app respeta ese formato.
