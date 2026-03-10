# Explicación del Backend: Lógica de la Aplicación

Para poder defender el proyecto de forma excelente, necesitas entender qué sucede "detrás de escena" cuando alguien navega por la página.

A continuación explicamos cómo funciona todo el flujo del Backend en Django y cómo se comunica con la Base de Datos, desde cero y paso a paso.

---

### 1. El corazón del sistema: Los Modelos (Base de Datos)
En el archivo `models.py` es donde ocurre la "magia" para Base de Datos I. En Django, en lugar de escribir código SQL como `CREATE TABLE`, nosotros creamos **Clases de Python**, y el ORM (Mapeador Objeto-Relacional) de Django se encarga de traducirlo a tablas SQL.

**El Problema de la Herencia (Multi-table Inheritance):**
El reto más grande del proyecto era: *"Tenemos Obras, pero una Pintura tiene 'Técnica' y una Escultura tiene 'Peso', ¿cómo metemos eso en la misma base de datos sin dejar cientos de campos en blanco?"*.
- **La Solución:** Creamos una clase Padre llamada `Artwork` (Obra) que tiene los campos comunes: título, precio, fecha de creación y estado (`AVAILABLE`, `RESERVED`, `SOLD`).
- Luego creamos clases Hijas (`Painting`, `Sculpture`, etc.) que **heredan** de `Artwork`.
- **¿Qué hace Django en SQL por debajo?** Crea la tabla `museum_artwork`, y luego crea la tabla `museum_painting`. La tabla `museum_painting` no tiene el título ni el precio, solo tiene la técnica, el soporte, y la **Clave Foránea (Foreign Key)** que vincula esa pintura con el ID de la tabla `museum_artwork`. Django une (hace un `JOIN`) ambas tablas automáticamente cuando un usuario entra a ver el catálogo.

**Automatización de Cálculos en Ventas:**
En el modelo `Sale` (Ventas), sobreescribimos el método `save()`. Esto es un "Trigger" manejado por código Python en lugar de estar dentro del motor de la BD. 
- Cuando un administrador guarda una factura en el sistema, antes de grabarla en la Base de Datos, Django ejecuta nuestro método `save()`. 
- Nuestro método toma el subtotal (ej. $100), calcula el IVA ($16), averigua el % de comisión del artista y calcula la comisión del museo (ej. $5), suma todo y lo guarda en la BD. Así evitamos guardar cálculos estáticos por error.

### 2. El flujo del Sistema: De la URL a la Pantalla
El patrón que usamos es MVT (Modelo-Vista-Template). Este es el viaje de un click:

1. **La URL (`urls.py`):** El usuario escribe `tusitio.com/catalog/` o hace clic en un botón. El archivo `urls.py` es como el recepcionista; ve que la dirección dice `catalog/` y dice: *"¡Ah! Eso le toca atenderlo a la función `catalog`"*. Y manda al usuario ahí.
2. **La Vista (`views.py`):** Aquí está el **cerebro**. La función `catalog(request)` recibe al usuario.
    - Se conecta a la base de datos usando el ORM: `Artwork.objects.all()`. Django traduce eso a `SELECT * FROM museum_artwork;`.
    - Si el usuario eligió un filtro para ver solo fotos de "Van Gogh", la vista hace: `artworks = artworks.filter(artist='Van Gogh')` (que se traduce como `SELECT * WHERE artist = 'Van Gogh'`).
    - Guarda los resultados en una "caja" (un diccionario).
3. **El Template (`.html`):** La vista le manda esa "caja" al HTML. El HTML usa etiquetas especiales (como `{% for artwork in artworks %}`) para recorrer cada obra que sacamos de la BD y pintar una tarjetita bonita en la pantalla por cada una.

### 3. El Flujo de Compra (Paso a Paso)

**A. El Registro (Users / Forms):**
1. Un usuario entra a registrarse. Llena un formulario.
2. Atrás, en `users/views.py`, interceptamos ese formulario.
3. Django crea el usuario en la tabla nativa (`auth_user`). Luego nosotros creamos su `BuyerProfile` (perfil del comprador).
4. El sistema, mediante la librería `random`, genera un código único de letras y números (ej. `AX93BT2`) y se lo guarda a ese perfil en la BD. De inmediato, usa la función `send_mail` para enviar ese código por correo.

**B. La Reserva (La validación cruzada):**
1. El visitante entra al detalle de "La Noche Estrellada" y hunde "Reservar".
2. La base de datos primero revisa la sesión: *"¿Este usuario está logueado como Comprador?"*.
3. Si lo está, le pide el código de seguridad. Cuando el usuario lo ingresa, el backend va a la tabla de `BuyerProfile` y saca el código real.
4. Si `codigo_ingresado == codigo_bd`, entonces creamos un registro en la tabla `Reservation`.
5. Inmediatamente **cambiamos el estado (Update)** de la obra: `artwork.status = 'RESERVED'` y la guardamos en BD. ¡Boom! Ya nadie más puede ver el botón de comprar.

**C. La "Limpieza Mágica" de las 24 horas (Lazy Validation):**
1. En lugar de instalar un cronómetro de servidor costoso para vigilar el tiempo, implementamos una validación condicional en `utils.py`.
2. Cada vez que **cualquier persona** entra a ver el Catálogo o el Home. La vista, antes de hacer el `SELECT` de las obras de arte, llama a `cleanup_expired_reservations()`.
3. Esa función pide la hora actual a Django, le resta 24 horas (`timedelta(hours=24)`), y hace un `SELECT` buscando todas las reservaciones que sean más viejas que esa hora límite.
4. Si encuentra 3 reservas viejas, les borra la reserva (`DELETE`) y le cambia el estatus a la obra poniéndolas en `'AVAILABLE'` de nuevo (`UPDATE`).
5. **Por ende:** Aparenta que el servidor está limpiando constantemente con un reloj cada segundo, pero en realidad, es un truco donde el servidor solo limpia justo antes de que alguien mire. La base de datos se mantiene super optimizada.

### 4. Consultas y Reportes de los Administradores
Cuando un Admin entra a ver "Total de Facturación", ocurre una agregación en la DB.

En SQL Puro, para sumar toda la plata ganada, la profesora esperaría ver esto:
```sql
SELECT SUM(total) FROM museum_sale WHERE date > '2023-01-01';
```

En Django, logramos esa misma consulta con esto (`views.py`):
```python
total_revenue = sales.aggregate(Sum('total'))['total__sum']
```
Django le envía literalmente ese `SUM()` a MySQL/Postgres. Esto es rapidísimo porque el cálculo de las sumas lo hace el Motor de la Base de Datos nativamente (que está hecho para eso), y a Python solo le llega un numerito final como "5000 dólares", evitando que Python y la RAM de la computadora tengan que procesar y sumar 10.000 filas a mano cruzando listas. 

---

**Resumen rápido para defender:**
- Usaron **Django Framework** con el stack MVT (Modelo, Vista, Template).
- La Base de Datos se manipula a través de un **ORM**, lo que evita inyecciones SQL y convierte el código Python en Querys (Consultas SQL) limpias.
- Para los distintos tipos de arte usaron **Herencia Multitabla** en la BD (tablas hijas ligadas a una tabla padre con Claves Foráneas).
- Y todo el sistema de reportes se procesa del lado de la misma base de datos usando **Queryset Aggregation** (las funciones SUM, COUNT nativas de SQL invocadas desde Django).
