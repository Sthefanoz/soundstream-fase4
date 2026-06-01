/* =============================================================
   SoundStream - Cambios de BD para la Fase 4
   Aplicar sobre la base SoundStreamDB de la Fase 3.

   Uso (PowerShell):
       sqlcmd -S TU_INSTANCIA -E -d SoundStreamDB -i cambios_bd.sql

   Ejemplo:
       sqlcmd -S "localhost\SQLEXPRESS" -E -C -d SoundStreamDB -i cambios_bd.sql
   ============================================================= */

USE SoundStreamDB;
GO

/* -------------------------------------------------------------
   1. CAMBIOS DE ESQUEMA (ALTER TABLE)
   ------------------------------------------------------------- */

-- 1.1 Rol de usuario (distingue admin del resto).
IF COL_LENGTH('Operacion.Usuario', 'rol') IS NULL
BEGIN
    ALTER TABLE Operacion.Usuario
        ADD rol NVARCHAR(20) NOT NULL
        CONSTRAINT DF_Usuario_rol DEFAULT 'usuario';
END
GO

-- 1.2 URL de la foto de cada artista.
IF COL_LENGTH('Catalogo.Artista', 'foto') IS NULL
BEGIN
    ALTER TABLE Catalogo.Artista
        ADD foto NVARCHAR(500) NULL;
END
GO

-- 1.3 URL de la portada de cada album.
IF COL_LENGTH('Catalogo.Album', 'portada') IS NULL
BEGIN
    ALTER TABLE Catalogo.Album
        ADD portada NVARCHAR(500) NULL;
END
GO

-- 1.4 URL de la preview de audio (30s) de cada cancion.
IF COL_LENGTH('Catalogo.Cancion', 'preview') IS NULL
BEGIN
    ALTER TABLE Catalogo.Cancion
        ADD preview NVARCHAR(500) NULL;
END
GO


/* -------------------------------------------------------------
   2. DATOS DE EJEMPLO ANADIDOS EN FASE 4
   ------------------------------------------------------------- */

-- 2.1 Dos canciones nuevas en el album Thriller de Michael Jackson.
DECLARE @idAlbumThriller INT;
SELECT @idAlbumThriller = a.idAlbum
  FROM Catalogo.Album a
  JOIN Catalogo.Artista ar ON ar.idArtista = a.idArtista
 WHERE a.titulo = 'Thriller'
   AND ar.nombreArtistico = 'Michael Jackson';

IF @idAlbumThriller IS NOT NULL
BEGIN
    IF NOT EXISTS (SELECT 1 FROM Catalogo.Cancion
                    WHERE titulo = 'Beat It' AND idAlbum = @idAlbumThriller)
    BEGIN
        INSERT INTO Catalogo.Cancion (titulo, duracion, calidadAudio, numReproducciones, idAlbum)
        VALUES ('Beat It', '00:04:18', '320kbps', 0, @idAlbumThriller);
    END

    IF NOT EXISTS (SELECT 1 FROM Catalogo.Cancion
                    WHERE titulo = 'Billie Jean' AND idAlbum = @idAlbumThriller)
    BEGIN
        INSERT INTO Catalogo.Cancion (titulo, duracion, calidadAudio, numReproducciones, idAlbum)
        VALUES ('Billie Jean', '00:04:54', '320kbps', 0, @idAlbumThriller);
    END
END
GO


/* -------------------------------------------------------------
   3. ADMINISTRADOR
   -------------------------------------------------------------
   Marca como admin al usuario que vaya a manejar el panel.
   Por defecto va por email para que sea portable entre BDs.
   Cambia el correo por el del admin de tu equipo.
   ------------------------------------------------------------- */

UPDATE Operacion.Usuario
   SET rol = 'admin'
 WHERE email = 'sthefanozambrano1@gmail.com';
GO


/* -------------------------------------------------------------
   4. SIGUIENTE PASO (NO ES SQL)
   -------------------------------------------------------------
   Las columnas foto / portada / preview se rellenan ejecutando,
   dentro de soundstream/ y con el venv activado:

       python manage.py migrate
       python manage.py fotos_artistas
       python manage.py portadas_albumes
       python manage.py previews_canciones

   Esas tres tareas usan la API publica de Deezer y necesitan
   conexion a internet.
   ------------------------------------------------------------- */
