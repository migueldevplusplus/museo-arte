# 🗄️ Modelado de Base de Datos — Museo de Arte Contemporáneo

Este documento explica cómo se implementó el modelado de la base de datos usando Django ORM con MySQL.

---

## Visión General

El proyecto usa **Django ORM** para definir los modelos. Django traduce automáticamente las clases Python en tablas MySQL mediante migraciones. La base de datos se llama `museum_db`.

El diseño utiliza **herencia multi-tabla (multi-table inheritance)** de Django para modelar la especialización de obras de arte por género. Cada tipo de obra (Pintura, Escultura, Fotografía, Cerámica, Orfebrería) hereda de un modelo base `Artwork`, creando tablas separadas con sus atributos específicos.

## Entidades implementadas formateadas manualmente versión clases BD:


## USUARIO

* id_usuario (PK)
* username
* password
* email
* is_buyer
* is_employee
* date_joined

---

## BUYER_PROFILE

* id_buyer_profile (PK)
* user_id (FK → Usuario)
* credit_card_number
* security_code
* shipping_address

---

## GENERO

* id_genero (PK)
* name

Géneros registrados: Pintura, Escultura, Fotografía, Cerámica, Orfebrería.

---

## ARTISTA

* id_artista (PK)
* name
* biography
* birth_date
* nationality
* photo

---

## OBRA (modelo base)

* id_obra (PK)
* title
* artist_id (FK → Artista)
* genre_id (FK → Genero)
* price
* creation_date
* photo
* status

---

## PINTURA (hereda de Obra)

* artwork_ptr_id (PK, FK → Obra)
* technique (óleo, acrílico, acuarela)
* support (lienzo, madera, papel)
* height
* width

---

## ESCULTURA (hereda de Obra)

* artwork_ptr_id (PK, FK → Obra)
* material
* weight
* height
* width
* depth

---

## FOTOGRAFÍA (hereda de Obra)

* artwork_ptr_id (PK, FK → Obra)
* photo_type (digital, analógica)
* camera
* technique (blanco y negro, color)
* height
* width

---

## CERÁMICA (hereda de Obra)

* artwork_ptr_id (PK, FK → Obra)
* material
* technique
* glaze_type
* height
* width

---

## ORFEBRERÍA (hereda de Obra)

* artwork_ptr_id (PK, FK → Obra)
* material (oro, plata, bronce, cobre)
* object_type (anillo, collar, pulsera)
* weight
* gemstones

---

## MEMBRESIA

* id_membresia (PK)
* buyer_profile_id (FK → BuyerProfile)
* start_date
* amount

---

## VENTA

* id_venta (PK)
* artwork_id (FK UNIQUE → Obra)
* buyer_id (FK → Usuario)
* processed_by (FK → Usuario)
* date
* subtotal
* iva
* commission
* total

---

# Relaciones del MER

Usuario 1 —— 1 BuyerProfile
BuyerProfile 1 —— N Membresia
Artista N —— M Genero
Artista 1 —— N Obra
Genero 1 —— N Obra
Pintura 1 —— 1 Obra (herencia multi-tabla)
Escultura 1 —— 1 Obra (herencia multi-tabla)
Fotografía 1 —— 1 Obra (herencia multi-tabla)
Cerámica 1 —— 1 Obra (herencia multi-tabla)
Orfebrería 1 —— 1 Obra (herencia multi-tabla)
Obra 1 —— 1 Venta
Usuario 1 —— N Venta (como comprador)
Usuario 1 —— N Venta (como empleado que procesa)

---

### Diagrama de Relaciones (ER)

```mermaid
erDiagram
    User ||--o| BuyerProfile : "tiene"
    BuyerProfile ||--o{ Membership : "tiene"
    User ||--o{ Sale : "compra"
    User ||--o{ Sale : "procesa"
    Artist }o--o{ Genre : "pertenece a"
    Artist ||--o{ Artwork : "crea"
    Genre ||--o{ Artwork : "clasifica"
    Artwork ||--o| Painting : "especializa"
    Artwork ||--o| Sculpture : "especializa"
    Artwork ||--o| Photography : "especializa"
    Artwork ||--o| Ceramic : "especializa"
    Artwork ||--o| Goldsmithing : "especializa"
    Artwork ||--o| Sale : "se vende en"
```

---

## App `users` — Archivo: `users/models.py`

### Tabla `User` (extiende `AbstractUser` de Django)

Hereda todos los campos de Django (username, password, email, etc.) y agrega:

| Campo | Tipo Django | Tipo MySQL | Descripción |
|-------|------------|------------|-------------|
| `is_buyer` | `BooleanField(default=False)` | `TINYINT(1)` | ¿Es comprador? |
| `is_employee` | `BooleanField(default=False)` | `TINYINT(1)` | ¿Es empleado del museo? |

**¿Por qué `AbstractUser`?** Permite usar el sistema de autenticación de Django (login, logout, permisos) sin crear un sistema desde cero. Los flags `is_buyer` e `is_employee` diferencian los roles.

**Configuración requerida** en `settings.py`:
```python
AUTH_USER_MODEL = 'users.User'
```

### Tabla `BuyerProfile`

| Campo | Tipo Django | Tipo MySQL | Descripción |
|-------|------------|------------|-------------|
| `user` | `OneToOneField(User)` | `INT FK UNIQUE` | Relación 1:1 con User |
| `credit_card_number` | `CharField(max_length=19)` | `VARCHAR(19)` | Número de tarjeta (demo) |
| `security_code` | `CharField(max_length=10)` | `VARCHAR(10)` | Código de seguridad generado |
| `shipping_address` | `TextField` | `TEXT` | Dirección de envío |

**Relación:** `OneToOneField` → Un usuario tiene exactamente un perfil de comprador. Si se elimina el User, se elimina el perfil (`on_delete=CASCADE`).

**Acceso en código:**
```python
# Desde el usuario al perfil:
request.user.buyer_profile.credit_card_number

# Desde el perfil al usuario:
profile.user.username
```

---

## App `museum` — Archivo: `museum/models.py`

### Tabla `Genre`

| Campo | Tipo Django | Tipo MySQL | Descripción |
|-------|------------|------------|-------------|
| `id` | Auto (PK) | `INT AUTO_INCREMENT` | Clave primaria |
| `name` | `CharField(max_length=100)` | `VARCHAR(100)` | Nombre del género |

### Tabla `Artist`

| Campo | Tipo Django | Tipo MySQL | Descripción |
|-------|------------|------------|-------------|
| `id` | Auto (PK) | `INT AUTO_INCREMENT` | Clave primaria |
| `name` | `CharField(max_length=200)` | `VARCHAR(200)` | Nombre |
| `biography` | `TextField` | `TEXT` | Biografía |
| `birth_date` | `DateField(null=True)` | `DATE NULL` | Fecha de nacimiento |
| `nationality` | `CharField(max_length=100)` | `VARCHAR(100)` | Nacionalidad |
| `photo` | `ImageField(upload_to='artists/')` | `VARCHAR(100)` | Ruta de imagen |
| `genres` | `ManyToManyField(Genre)` | Tabla intermedia | Géneros del artista |

**Relación M:N (Artist ↔ Genre):**
Django crea automáticamente una tabla intermedia `museum_artist_genres` con dos FK:
```sql
-- Tabla generada automáticamente:
CREATE TABLE museum_artist_genres (
    id INT AUTO_INCREMENT PRIMARY KEY,
    artist_id INT REFERENCES museum_artist(id),
    genre_id INT REFERENCES museum_genre(id)
);
```

**Acceso en código:**
```python
# Géneros de un artista:
artist.genres.all()

# Artistas de un género (gracias a related_name='artists'):
genre.artists.all()
```

### Tabla `Artwork` (modelo base)

| Campo | Tipo Django | Tipo MySQL | Descripción |
|-------|------------|------------|-------------|
| `id` | Auto (PK) | `INT AUTO_INCREMENT` | Clave primaria |
| `title` | `CharField(max_length=200)` | `VARCHAR(200)` | Título de la obra |
| `artist` | `ForeignKey(Artist)` | `INT FK` | Artista creador |
| `genre` | `ForeignKey(Genre, null=True)` | `INT FK NULL` | Género de la obra |
| `price` | `DecimalField(10, 2)` | `DECIMAL(10,2)` | Precio en USD |
| `creation_date` | `DateField` | `DATE` | Fecha de creación |
| `photo` | `ImageField(upload_to='artworks/')` | `VARCHAR(100)` | Imagen de la obra |
| `status` | `CharField(choices=...)` | `VARCHAR(20)` | Estado actual |

**Campo `status` — Máquina de estados:**
```
AVAILABLE  →  RESERVED  →  SOLD
(Disponible)  (Reservada)  (Vendida)
```
- Un comprador puede reservar una obra → cambia a `RESERVED`
- Un empleado finaliza la venta desde el admin → cambia a `SOLD`

**Relaciones FK:**
- `artist`: `on_delete=CASCADE` → Si se elimina el artista, se eliminan sus obras
- `genre`: `on_delete=SET_NULL` → Si se elimina el género, la obra queda sin género (no se borra)

### Tablas Especializadas (Herencia Multi-Tabla)

Django implementa la especialización mediante **multi-table inheritance**: cada modelo hijo crea su propia tabla con un `OneToOneField` automático (`artwork_ptr_id`) hacia la tabla padre `museum_artwork`.

#### Tabla `Painting` (Pintura)

| Campo | Tipo Django | Tipo MySQL | Descripción |
|-------|------------|------------|-------------|
| `artwork_ptr` | Auto (PK, FK → Artwork) | `INT PK FK` | Referencia al Artwork base |
| `technique` | `CharField(choices=...)` | `VARCHAR(50)` | Técnica: óleo, acrílico, acuarela |
| `support` | `CharField(choices=...)` | `VARCHAR(50)` | Soporte: lienzo, madera, papel |
| `height` | `DecimalField(8, 2)` | `DECIMAL(8,2)` | Altura en cm |
| `width` | `DecimalField(8, 2)` | `DECIMAL(8,2)` | Ancho en cm |

#### Tabla `Sculpture` (Escultura)

| Campo | Tipo Django | Tipo MySQL | Descripción |
|-------|------------|------------|-------------|
| `artwork_ptr` | Auto (PK, FK → Artwork) | `INT PK FK` | Referencia al Artwork base |
| `material` | `CharField(max_length=100)` | `VARCHAR(100)` | Material de la escultura |
| `weight` | `DecimalField(8, 2)` | `DECIMAL(8,2)` | Peso en kg |
| `height` | `DecimalField(8, 2)` | `DECIMAL(8,2)` | Altura en cm |
| `width` | `DecimalField(8, 2)` | `DECIMAL(8,2)` | Ancho en cm |
| `depth` | `DecimalField(8, 2)` | `DECIMAL(8,2)` | Profundidad en cm |

#### Tabla `Photography` (Fotografía)

| Campo | Tipo Django | Tipo MySQL | Descripción |
|-------|------------|------------|-------------|
| `artwork_ptr` | Auto (PK, FK → Artwork) | `INT PK FK` | Referencia al Artwork base |
| `photo_type` | `CharField(choices=...)` | `VARCHAR(50)` | Tipo: digital, analógica |
| `camera` | `CharField(max_length=200)` | `VARCHAR(200)` | Cámara utilizada |
| `technique` | `CharField(choices=...)` | `VARCHAR(50)` | Técnica: B&N, color |
| `height` | `DecimalField(8, 2)` | `DECIMAL(8,2)` | Altura en cm |
| `width` | `DecimalField(8, 2)` | `DECIMAL(8,2)` | Ancho en cm |

#### Tabla `Ceramic` (Cerámica)

| Campo | Tipo Django | Tipo MySQL | Descripción |
|-------|------------|------------|-------------|
| `artwork_ptr` | Auto (PK, FK → Artwork) | `INT PK FK` | Referencia al Artwork base |
| `material` | `CharField(max_length=100)` | `VARCHAR(100)` | Material |
| `technique` | `CharField(max_length=100)` | `VARCHAR(100)` | Técnica cerámica |
| `glaze_type` | `CharField(max_length=100)` | `VARCHAR(100)` | Tipo de esmalte |
| `height` | `DecimalField(8, 2)` | `DECIMAL(8,2)` | Altura en cm |
| `width` | `DecimalField(8, 2)` | `DECIMAL(8,2)` | Ancho en cm |

#### Tabla `Goldsmithing` (Orfebrería)

| Campo | Tipo Django | Tipo MySQL | Descripción |
|-------|------------|------------|-------------|
| `artwork_ptr` | Auto (PK, FK → Artwork) | `INT PK FK` | Referencia al Artwork base |
| `material` | `CharField(choices=...)` | `VARCHAR(50)` | Material: oro, plata, bronce, cobre |
| `object_type` | `CharField(choices=...)` | `VARCHAR(50)` | Tipo: anillo, collar, pulsera |
| `weight` | `DecimalField(8, 2)` | `DECIMAL(8,2)` | Peso en gramos |
| `gemstones` | `CharField(max_length=200)` | `VARCHAR(200)` | Piedras preciosas (opcional) |

**¿Cómo funciona la herencia multi-tabla?**
```python
# Crear una pintura (crea registro en museum_artwork Y museum_painting):
painting = Painting.objects.create(
    title="Guernica",
    artist=picasso,
    genre=pintura,
    price=15000000,
    creation_date="1937-01-01",
    technique="oil",
    support="canvas",
    height=349,
    width=776,
)

# Acceder desde Artwork base a la especialización:
artwork = Artwork.objects.get(pk=1)
specific = artwork.get_specific_instance()  # Retorna la instancia Painting
fields = specific.get_detail_fields()       # Lista de (etiqueta, valor) en español
```

### Tabla `Membership`

| Campo | Tipo Django | Tipo MySQL | Descripción |
|-------|------------|------------|-------------|
| `id` | Auto (PK) | `INT AUTO_INCREMENT` | Clave primaria |
| `buyer_profile` | `ForeignKey(BuyerProfile)` | `INT FK` | Perfil del comprador |
| `start_date` | `DateField(auto_now_add=True)` | `DATE` | Fecha de inicio (auto) |
| `amount` | `DecimalField(6, 2, default=10)` | `DECIMAL(6,2)` | Monto pagado |

**Relación:** Un comprador puede tener varias membresías (`1:N`).

### Tabla `Sale`

| Campo | Tipo Django | Tipo MySQL | Descripción |
|-------|------------|------------|-------------|
| `id` | Auto (PK) | `INT AUTO_INCREMENT` | Clave primaria |
| `artwork` | `OneToOneField(Artwork)` | `INT FK UNIQUE` | Obra vendida (1:1) |
| `buyer` | `ForeignKey(User)` | `INT FK` | Comprador |
| `date` | `DateTimeField(default=now)` | `DATETIME` | Fecha de venta |
| `subtotal` | `DecimalField(12, 2)` | `DECIMAL(12,2)` | Precio de la obra |
| `iva` | `DecimalField(12, 2)` | `DECIMAL(12,2)` | 16% IVA |
| `commission` | `DecimalField(12, 2)` | `DECIMAL(12,2)` | 10% comisión del museo |
| `total` | `DecimalField(12, 2)` | `DECIMAL(12,2)` | subtotal + IVA |
| `processed_by` | `ForeignKey(User, null=True)` | `INT FK NULL` | Empleado que procesó |

**Lógica de cálculo** (en `save()` y en `SaleAdmin`):
```python
subtotal = artwork.price
iva = subtotal * 0.16        # 16%
commission = subtotal * 0.10  # 10%
total = subtotal + iva
```

**Relación `OneToOneField` con Artwork:** Una obra solo puede venderse una vez.

---

## Cómo Hacer Cambios

### Agregar un campo a un modelo existente

1. Edita el archivo `models.py` correspondiente:
   ```python
   class Artwork(models.Model):
       # ... campos existentes ...
       description = models.TextField(blank=True, default='')  # NUEVO
   ```

2. Crea y aplica la migración:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

### Crear un nuevo modelo

1. Agrega la clase en `models.py`:
   ```python
   class Exhibition(models.Model):
       name = models.CharField(max_length=200)
       start_date = models.DateField()
       artworks = models.ManyToManyField(Artwork)
   ```

2. Regístralo en `admin.py`:
   ```python
   from .models import Exhibition
   admin.site.register(Exhibition)
   ```

3. Crea y aplica migraciones:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

### Modificar un campo existente

1. Cambia el campo en `models.py`
2. Ejecuta `makemigrations` → Django detecta el cambio automáticamente
3. Ejecuta `migrate` → Aplica el `ALTER TABLE` en MySQL

### Eliminar un campo o modelo

1. Elimina del código
2. `makemigrations` → genera migración con `RemoveField` o `DeleteModel`
3. `migrate` → aplica `DROP COLUMN` o `DROP TABLE`

> **⚠️ Importante:** Nunca modifiques las tablas directamente en MySQL. Siempre usa migraciones de Django para mantener la sincronización.

---

## Resumen de Tablas MySQL Generadas

| Tabla MySQL | Modelo Django | App |
|-------------|--------------|-----|
| `users_user` | `User` | users |
| `users_buyerprofile` | `BuyerProfile` | users |
| `museum_genre` | `Genre` | museum |
| `museum_artist` | `Artist` | museum |
| `museum_artist_genres` | *(tabla M:N automática)* | museum |
| `museum_artwork` | `Artwork` (base) | museum |
| `museum_painting` | `Painting` | museum |
| `museum_sculpture` | `Sculpture` | museum |
| `museum_photography` | `Photography` | museum |
| `museum_ceramic` | `Ceramic` | museum |
| `museum_goldsmithing` | `Goldsmithing` | museum |
| `museum_membership` | `Membership` | museum |
| `museum_sale` | `Sale` | museum |

Django también genera tablas internas: `auth_group`, `auth_permission`, `django_session`, `django_content_type`, `django_migrations`, etc.
