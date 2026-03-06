# 🎨 Museo de Arte Contemporáneo — Sistema de Venta de Obras

Aplicación web desarrollada con **Django** y **MySQL** para la gestión y venta de obras de arte de un museo.

*IMPORTANTE*: Los detalles de la implementación de la base de datos está en **modelado_bd.md** ;)

## Requisitos Previos

- **Python 3.12+**
- **pip** (incluido con Python)

---

## 🛠️ Guía de Instalación Paso a Paso

Sigue estas instrucciones al pie de la letra para configurar el proyecto en tu PC sin errores de entorno o de base de datos. 

> **Nota importante:** Nuestra base de datos está en la nube (Aiven), por lo que **NO necesitas instalar XAMPP ni MySQL localmente**.

### 1. Preparar Windows y Python (Obligatorio)
Si es la primera vez que programas en Python en tu PC, Windows suele bloquear algunas cosas. Sigue esto para evitar errores:
1. **Instala Python:** Descárgalo desde [python.org](https://www.python.org/downloads/) (Evita la Microsoft Store).
2. **El paso crítico:** Durante la instalación, marca la casilla **"Add Python to PATH"**.
3. **Desactiva los bloqueos de Windows:**
   - Escribe en el buscador de Windows **"Administrar alias de ejecución de la aplicación"** (*Manage app execution aliases*).
   - Busca los que digan "Python" o "App Installer" y **desactívalos**.

### 2. Entorno Virtual y Permisos
Abre una terminal en VS Code dentro de la carpeta del proyecto.

1. **Crea el entorno virtual:**
   ```powershell
   python -m venv venv
   ```

2. **Arregla el bloqueo de PowerShell:** Si te sale un error rojo al intentar activar el entorno (`PSSecurityException`), abre **PowerShell como Administrador** en Windows y corre este comando una sola vez (presiona `S` para confirmar):
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

3. **Activa el entorno:** (Debes ver un `(venv)` al inicio de tu terminal).
   ```powershell
   .\venv\Scripts\activate
   ```

### 3. Instalar Dependencias

Con el entorno `(venv)` activo, instala las librerías necesarias para el proyecto:

```powershell
pip install django mysqlclient pillow
```

### 4. Configurar la Base de Datos (Nube)

Para evitar problemas de DNS o bloqueos por el router de la universidad/casa, asegúrate de que el archivo `settings.py` tenga el bloque `DATABASES` configurado **exactamente así**, usando la IP directa y habilitando SSL:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'defaultdb',
        'USER': 'avnadmin',
        'PASSWORD': 'AVNS_A74Wlpf8KvAmRiSTpqy',
        'HOST': '165.232.179.238',  # Usamos la IP directa para evitar errores DNS
        'PORT': '14529',
        'OPTIONS': {
            'ssl': {'ca': None},    # Obligatorio para conectar con Aiven Cloud
        },
    }
}
```

### 5. Lanzar el Proyecto

Finalmente, aplica los cambios de la base de datos y enciende el servidor local:

1. **Sincroniza la base de datos:**
   ```powershell
   python manage.py migrate
   ```

2. **Inicia el servidor:**
   ```powershell
   python manage.py runserver
   ```

Visita `http://127.0.0.1:8000/` en tu navegador para ver el proyecto corriendo. 🎉

---

## 📂 Estructura del Proyecto

```text
museo-arte/
├── core/                   # Configuración principal de Django
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── __init__.py
├── museum/                 # App principal (catálogo, ventas, reportes)
│   ├── admin.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   └── migrations/
├── templates/              # Plantillas HTML
│   ├── base.html
│   ├── museum/
│   └── users/
├── users/                  # App de autenticación (registro, login)
│   ├── admin.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   └── migrations/
├── .gitignore
├── db_dump.sql             # Respaldo SQL de la base de datos
├── documentation.md        # Documentación general
├── manage.py
├── modelado_bd.md          # Detalles del modelado de la BD
├── README.md               # Este archivo
├── requirements.txt        # Dependencias de Python
├── seed_data.py            # Script para insertar datos de prueba
└── write_catalog.py        # Script auxiliar
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
- **Base de Datos:** MySQL (Aiven Cloud)
- **Frontend:** Bootstrap 5, HTML5
- **Lenguaje:** Python 3.12+
