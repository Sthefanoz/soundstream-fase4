# SoundStream - Fase 4 Proyecto Integrador

Plataforma de streaming de musica con backend Django + SQL Server y frontend
con animaciones de scroll premium (Intersection Observer, parallax, counter
animado, efecto Apple scroll-video opcional).

## Stack

- **Backend**: Python 3.11+, Django 5, mssql-django, pyodbc
- **Base de datos**: SQL Server (esquemas `Catalogo` y `Operacion`)
- **Frontend**: HTML5, CSS3, JavaScript vanilla (sin librerias externas)
- **Tipografias**: Google Fonts (Inter + Space Grotesk)

## Estructura

```
soundstream/
├── manage.py
├── requirements.txt
├── soundstream/             # config del proyecto
│   ├── settings.py          # conexion SQL Server aqui
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── catalogo/            # esquema Catalogo (Artista, Album, Cancion)
│   ├── operacion/           # esquema Operacion (Reproduccion, Regalia, Pago, Suscripcion)
│   ├── usuarios/            # PerfilUsuario + Playlist + PlaylistCancion
│   └── web/                 # vistas publicas con scroll animations
├── templates/web/           # 13 plantillas HTML extendiendo base.html
├── static/
│   ├── css/main.css         # tema oscuro premium
│   ├── js/scroll.js         # IntersectionObserver, counter, parallax, scroll-video
│   └── assets/              # tus imagenes y videos aqui
└── fixtures/
    └── sample_data.json     # datos de prueba Fase 3 (artistas, canciones, etc.)
```

## 1. Instalacion

```powershell
cd soundstream
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Si pyodbc da problemas en Windows, instala primero el driver ODBC:
https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server

## 2. Configurar SQL Server

1. Crea la base de datos en SQL Server (si no existe ya de Fase 3):

   ```sql
   CREATE DATABASE SoundStreamDB;
   GO
   USE SoundStreamDB;
   CREATE SCHEMA Catalogo;
   CREATE SCHEMA Operacion;
   GO
   ```

2. Abre `soundstream/settings.py` y ajusta `DATABASES`:

   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'mssql',
           'NAME': 'SoundStreamDB',
           'USER': 'sa',
           'PASSWORD': 'TuPassword123',
           'HOST': 'localhost',     # o 'localhost\\SQLEXPRESS'
           'PORT': '1433',
           'OPTIONS': {'driver': 'ODBC Driver 17 for SQL Server'},
       }
   }
   ```

   Si usas autenticacion de Windows, deja `USER` y `PASSWORD` vacios y agrega
   `'Trusted_Connection': 'yes'` dentro de OPTIONS.

3. **Modo desarrollo rapido (sin SQL Server)**: en `settings.py` comenta el bloque
   anterior y descomenta el de SQLite. La web funciona igual para probar el front.

## 3. Migraciones

```powershell
python manage.py makemigrations catalogo operacion usuarios web
python manage.py migrate
```

Las migraciones crean automaticamente las tablas en los esquemas
`Catalogo.Artista`, `Catalogo.Album`, `Catalogo.Cancion`,
`Operacion.Suscripcion`, `Operacion.Pago`, `Operacion.Reproduccion`,
`Operacion.Regalia`, `Operacion.PerfilUsuario`, `Operacion.Playlist`,
`Operacion.PlaylistCancion`.

## 4. Cargar datos de prueba (Fase 3)

```powershell
python manage.py seed
```

Esto carga `fixtures/sample_data.json` (6 artistas, 8 albumes, 17 canciones,
3 usuarios demo, suscripciones, pagos, reproducciones y regalias) y asigna
contrasena `soundstream2026` a los usuarios `ana`, `carlos` y `lucia`.

Tambien puedes crear un superusuario propio:

```powershell
python manage.py createsuperuser
```

## 5. Arrancar el servidor

```powershell
python manage.py runserver
```

Abre `http://127.0.0.1:8000/` en tu navegador.

## 6. Funcionalidades probables

| URL                              | Descripcion |
|----------------------------------|-------------|
| `/`                              | Hero animado + top canciones + stats con counter + parallax |
| `/catalogo/`                     | Listado y busqueda de canciones |
| `/artistas/`                     | Grid de artistas con efecto reveal |
| `/albumes/`                      | Grid de albumes |
| `/catalogo/artistas/1/`          | Detalle de artista + discografia |
| `/catalogo/albumes/1/`           | Detalle de album + tracklist |
| `/usuarios/playlists/publicas/`  | Playlists publicas de la comunidad |
| `/usuarios/playlists/mias/`      | Mis playlists (requiere login) |
| `/suscripciones/`                | Planes Free/Premium/Familiar |
| `/operacion/historial/`          | Historial reproducciones y pagos aprobados |
| `/operacion/regalias/calcular/`  | Calcular regalias del mes (CRUD ejemplo) |
| `/contacto/`                     | Formulario de contacto |
| `/login/` y `/usuarios/registro/`| Auth |
| `/admin/`                        | Panel admin Django (CRUD completo) |

## 7. Probar reproducciones (CRUD)

1. Inicia sesion como `ana` / `soundstream2026`.
2. En `/catalogo/` haz click en el boton ▶ de cualquier cancion.
3. Se incrementa el campo `Reproducciones` en `Catalogo.Cancion` y se inserta
   un registro en `Operacion.Reproduccion` con timestamp.
4. Despues entra a `/operacion/historial/` y veras la cancion en tu historial.
5. Llama a `/operacion/regalias/calcular/` para que se calculen las regalias
   del mes actual en `Operacion.Regalia` (tarifa 0.004 USD/play).

## 8. Activar el efecto Apple scroll-video

1. Coloca tu video en `static/assets/hero.mp4` (recomendado 10-20s en H.264).
2. En `templates/web/inicio.html` cambia la primera condicional:
   `{% if False %}` -> `{% if True %}`.
3. Recarga el inicio. El video avanzara fotograma a fotograma con el scroll.

Si va muy rapido o lento, ajusta `height: 500vh` en `.scroll-video-hero`
dentro de `static/css/main.css` (300vh = rapido, 700vh = lento).

## 9. Animaciones de scroll incluidas

- **Reveal** fade-up/left/right/scale al entrar en viewport
- **Stagger** delays escalonados en grids
- **Counter** animado de 0 al numero real (50M, 50k, 100k)
- **Parallax** sutil en orbes decorativos y texto de fondo
- **Nav** que se condensa con backdrop-filter al hacer scroll
- **Hover** elevation y play-button revealed en cards
- **Equalizer** animado en el hero
- **Smooth scroll** nativo (scroll-behavior CSS)
- **Scroll-video** efecto Apple (opcional con video)

Todo respeta `prefers-reduced-motion` y se adapta a movil.

## 10. Datos que faltan / placeholders

Los siguientes datos son de ejemplo y debes sustituirlos con los tuyos:

- `BRAND.email` en `apps/web/context_processors.py`
- URLs de redes sociales en el mismo archivo
- Fotos de artistas y portadas de albumes (campo `foto` y `portada`)
- Video del hero (`static/assets/hero.mp4`)
- Logo (`static/assets/logo.png`)

Cumple Fase 4: backend Django + SQL Server con CRUD, frontend animado, datos reales de Fase 3.
