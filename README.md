# 🏋️ NEW LIFE GYM — Sistema de Gestión Web

**Versión 2.0** | Febrero 2026

Sistema web completo para la gestión integral del gimnasio New Life Gym, desarrollado con Flask y PostgreSQL (Neon). Incluye sitio público, panel de administración con CRUD completo e imágenes personalizadas almacenadas en base de datos.

---

## 📋 Descripción del Proyecto

New Life Gym es una plataforma web moderna y funcional que permite gestionar todas las operaciones del gimnasio desde un panel de administración seguro, mientras ofrece a los clientes una experiencia visual atractiva con vídeos de fondo, galería interactiva y tienda de productos.

### ✅ Funcionalidades Incluidas

**Sitio Público**
- Página de inicio con hero a pantalla completa con vídeo `.mp4` de fondo
- Páginas interiores con hero de vídeo independiente por página
- Membresías con planes y beneficios dinámicos desde la BD
- Tienda de suplementos con imágenes reales
- Página de entrenadores con fotos personalizadas desde la BD
- Galería interactiva con lightbox (fotos ampliadas al hacer clic)
- Página de compra exitosa para membresías y productos
- Páginas de error 404 y 500 personalizadas
- Diseño 100% responsive (móvil, tablet, escritorio)

**Panel de Administración**
- Login seguro con sesión Flask
- Dashboard con estadísticas en tiempo real
- CRUD completo: Miembros, Membresías, Planes, Entrenadores, Productos
- Subida de imágenes personalizadas para entrenadores y productos
- Imágenes almacenadas como BYTEA en PostgreSQL (Neon), sin archivos locales
- Cambio de plan de membresía desde el dashboard

---

## 🗂️ Estructura del Proyecto

```
NEW_LIFE_GYM/
│
├── app.py                        # Lógica principal Flask + rutas + BD
│
├── templates/
│   ├── home.html                 # Página de inicio (hero con vídeo)
│   ├── membresias.html           # Planes de membresía
│   ├── tienda.html               # Tienda de suplementos
│   ├── entrenadores.html         # Equipo de entrenadores
│   ├── galeria.html              # Galería de instalaciones
│   ├── compra_exitosa.html       # Confirmación de compra
│   ├── login.html                # Acceso al panel admin
│   ├── dashboard.html            # Panel de administración
│   ├── crear_miembro.html
│   ├── editar_miembro.html
│   ├── crear_membresia.html
│   ├── cambiar_plan.html
│   ├── crear_plan.html
│   ├── editar_plan.html
│   ├── crear_entrenador.html     # Con subida de foto
│   ├── editar_entrenador.html    # Con reemplazo de foto
│   ├── crear_producto.html       # Con subida de imagen
│   ├── editar_producto.html      # Con reemplazo de imagen
│   ├── 404.html
│   └── 500.html
│
├── static/
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   └── script.js
│   ├── images/
│   │   ├── logo.png              # Logo del gimnasio
│   │   ├── gym-hero.jpg          # Fallback de fondo (páginas sin vídeo)
│   │   ├── gym1.jpg              # Galería foto 1
│   │   ├── gym2.jpg              # Galería foto 2
│   │   ├── gym3.jpg              # Galería foto 3
│   │   ├── gym4.jpg              # Galería foto 4
│   │   ├── gym5.jpg              # Galería foto 5
│   │   └── gym6.jpg              # Galería foto 6
│   └── videos/
│       ├── gym-hero.mp4          # Vídeo hero — Inicio
│       ├── hero-membresias.mp4   # Vídeo hero — Membresías
│       ├── hero-tienda.mp4       # Vídeo hero — Tienda
│       ├── hero-entrenadores.mp4 # Vídeo hero — Entrenadores
│       └── hero-galeria.mp4      # Vídeo hero — Galería
│
└── requirements.txt
```

> **Nota sobre los vídeos:** Si algún archivo `.mp4` no está presente, el hero de esa página muestra un fondo oscuro con el overlay y el texto centrado. No rompe la página.

---

## 🗄️ Base de Datos (PostgreSQL — Neon)

La aplicación usa **PostgreSQL** alojado en [Neon](https://neon.tech). La función `init_db()` se ejecuta al arrancar la app y crea automáticamente las tablas si no existen.

### Tablas

| Tabla | Descripción |
|---|---|
| `miembro` | Datos personales de los socios |
| `plan` | Planes de membresía (con imagen BYTEA) |
| `membresia` | Relación miembro–plan con fechas y estado |
| `entrenador` | Entrenadores con foto almacenada en BD (BYTEA) |
| `producto` | Productos de la tienda con imagen en BD (BYTEA) |

Las imágenes de entrenadores y productos se sirven directamente desde la BD:

```
/imagen/entrenador/<id>
/imagen/producto/<id>
```

---

## 🗺️ Rutas del Sitio

### Públicas

| Ruta | Descripción |
|---|---|
| `/` | Redirige a `/home` |
| `/home` | Página principal con hero de vídeo |
| `/membresias` | Planes disponibles |
| `/tienda` | Catálogo de productos |
| `/entrenadores` | Perfiles del equipo |
| `/galeria` | Fotos de las instalaciones |
| `/comprar_membresia/<id>` | POST — procesa compra de membresía |
| `/comprar_producto/<id>` | POST — procesa compra de producto |

### Administración

| Ruta | Descripción |
|---|---|
| `/admin` | Página de login |
| `/admin/login` | POST — autenticación |
| `/admin/dashboard` | Panel principal |
| `/admin/logout` | Cerrar sesión |
| `/admin/miembro/crear` | Nuevo miembro |
| `/admin/miembro/editar/<id>` | Editar miembro |
| `/admin/miembro/eliminar/<id>` | Eliminar miembro |
| `/admin/membresia/crear` | Nueva membresía |
| `/admin/membresia/cambiar-plan/<id>` | Cambiar plan por miembro |
| `/admin/membresia/cambiar-plan-desde-membresia/<id>` | Cambiar plan por membresía |
| `/admin/membresia/eliminar/<id>` | Cancelar membresía |
| `/admin/plan/crear` | Nuevo plan (con imagen) |
| `/admin/plan/editar/<id>` | Editar plan (con imagen) |
| `/admin/plan/eliminar/<id>` | Desactivar plan |
| `/admin/entrenador/crear` | Nuevo entrenador (con foto) |
| `/admin/entrenador/editar/<id>` | Editar entrenador (con foto) |
| `/admin/entrenador/eliminar/<id>` | Eliminar entrenador |
| `/admin/producto/crear` | Nuevo producto (con imagen) |
| `/admin/producto/editar/<id>` | Editar producto (con imagen) |
| `/admin/producto/eliminar/<id>` | Eliminar producto |

---

## 🚀 Instalación y Ejecución

### Prerrequisitos

- Python 3.8 o superior
- pip

### 1. Clonar o descargar el proyecto

```bash
git clone [url-del-repositorio]
cd NEW_LIFE_GYM
```

### 2. Crear entorno virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecutar

```bash
python app.py
```

La aplicación estará disponible en **http://localhost:5000**

La base de datos se inicializa automáticamente al arrancar. Si las tablas ya existen, no se modifican.

### Producción (Gunicorn)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

---

## 🔐 Acceso Administrativo

| Campo | Valor |
|---|---|
| URL | `/admin` |
| Usuario | `admin` |
| Contraseña | `newlife2026` |

---

## 💻 Tecnologías

| Capa | Tecnología |
|---|---|
| Backend | Python 3 + Flask 3.0 |
| Base de datos | PostgreSQL (Neon) + psycopg2 |
| Templates | Jinja2 |
| Frontend | HTML5 + CSS3 + JavaScript (Vanilla) |
| Imágenes en BD | BYTEA (PostgreSQL) |
| Vídeos de fondo | HTML5 `<video>` autoplay/muted/loop |

---

## 🎨 Paleta de Colores

```css
--primary-color:   #ff0000   /* Rojo principal */
--secondary-color: #1a1a1a   /* Negro secundario */
--accent-color:    #ff3333   /* Rojo acento hover */
--bg-dark:         #ffffff   /* Fondo general */
--card-bg:         #ffffff   /* Fondo de tarjetas */
```

---

## 📁 Dependencias Python

```
Flask==3.0.0
Werkzeug==3.0.1
Jinja2==3.1.2
psycopg2-binary
```

---

## 📞 Contacto del Gimnasio

- **Gimnasio:** New Life Gym
- **Ubicación:** Pasto, Nariño
- **Teléfono:** (555) 123-4567
- **Email:** info@newlifegym.com

---

*New Life Gym © 2026 — Todos los derechos reservados*