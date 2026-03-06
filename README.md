
# 🎨 Museo de Arte Contemporáneo — Sistema de Venta de Obras

Aplicación web desarrollada con **Django 6** y **MySQL** para la gestión y venta de obras de arte de un museo.

*IMPORTANTE*: Los detalles de la implementación de la base de datos está en **modelado_bd.md** ;)

## Requisitos Previos

- **Python 3.12+**
- **MySQL 8.0+** (debe estar corriendo)
- **pip** (incluido con Python)

---

## 🚀 Instalación Paso a Paso

### 1. Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd "Proyecto BD1"
```

### 2. Crear un entorno virtual (recomendado)

```bash
python -m venv venv
```

Activar el entorno:

- **Windows:**
  ```bash
  venv\Scripts\activate
  ```
- **macOS/Linux:**
  ```bash
  source venv/bin/activate
  ```

### 3. Instalar las dependencias

```bash
pip install -r requirements.txt
```

> **Nota:** `mysqlclient` requiere tener instaladas las librerías de desarrollo de MySQL en tu sistema. En Windows, usualmente se instala automáticamente. En Linux puedes necesitar: `sudo apt install python3-dev default-libmysqlclient-dev build-essential`

### 4. Configurar la Base de Datos MySQL

#### a) Crear la base de datos

Abre una terminal de MySQL y ejecuta:

```sql
CREATE DATABASE museum_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### b) Configurar las credenciales

Copia el archivo de ejemplo de variables de entorno:

```bash
cp .env.example .env
```

Edita el archivo `.env` con tus credenciales locales:

```
DB_NAME=museum_db
DB_USER=root
DB_PASSWORD=m!guelsql111
DB_HOST=127.0.0.1
DB_PORT=3306
```

#### c) Actualizar `settings.py` (si es necesario)

Abre `core/settings.py` y verifica que la sección `DATABASES` tenga tus credenciales correctas:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'museum_db',
        'USER': 'root',
        'PASSWORD': 'TU_CONTRASEÑA',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
```

### 5. Ejecutar las migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Crear un superusuario (administrador)

```bash
python manage.py createsuperuser
```

Sigue las instrucciones para crear el usuario administrador. Recuerda marcar al usuario como empleado desde el panel de admin.

### 7. Cargar datos de ejemplo (opcional)

```bash
python seed_data.py
```

Esto creará géneros, artistas y obras de arte de ejemplo.

### 8. Ejecutar el servidor de desarrollo

```bash
python manage.py runserver
```

El sitio estará disponible en: **http://127.0.0.1:8000/**

---

## 📂 Estructura del Proyecto

```
Proyecto BD1/
├── core/              # Configuración principal de Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── museum/            # App principal (catálogo, ventas, reportes)
│   ├── models.py      # Genre, Artist, Artwork, Sale, Membership
│   ├── views.py
│   ├── admin.py
│   └── urls.py
├── users/             # App de autenticación (registro, login)
│   ├── models.py      # User, BuyerProfile
│   ├── forms.py
│   ├── views.py
│   └── urls.py
├── templates/         # Plantillas HTML
│   ├── base.html
│   ├── museum/
│   └── users/
├── media/             # Imágenes subidas (artistas, obras)
├── seed_data.py       # Script de datos de ejemplo
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🔑 Funcionalidades

| Rol | Funcionalidad |
|-----|--------------|
| **Visitante** | Ver catálogo, buscar obras por género/artista/precio |
| **Comprador** | Registrarse, recibir código de seguridad, reservar obras |
| **Empleado/Admin** | Finalizar ventas, generar facturas, ver reportes |

---

## 🌐 URLs Principales

| URL | Descripción |
|-----|-------------|
| `/` | Página de inicio |
| `/catalog/` | Catálogo de obras con filtros |
| `/artwork/<id>/` | Detalle de una obra |
| `/artist/<id>/` | Detalle de un artista |
| `/users/register/` | Registro de comprador |
| `/users/login/` | Inicio de sesión |
| `/reports/sales/` | Reporte de ventas (admin) |
| `/reports/memberships/` | Reporte de membresías (admin) |
| `/admin/` | Panel de administración Django |

---

## 🛠 Tecnologías

- **Backend:** Django 6.0.2
- **Base de Datos:** MySQL 8.0+
- **Frontend:** Bootstrap 5, HTML5
- **Lenguaje:** Python 3.12+

