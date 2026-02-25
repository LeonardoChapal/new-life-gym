from flask import Flask, render_template, redirect, url_for, request, flash, session, Response
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tu-clave-secreta-para-demo-2024'

# ========== CONFIGURACIÓN NEON ==========
DATABASE_URL = "postgresql://neondb_owner:npg_BxWG7siKAr6T@ep-weathered-fog-aiqynz6c-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

def get_db_connection():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"Error de conexión: {e}")
        return None

# ========== CREDENCIALES ADMIN ==========
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "newlife2026"

# ========== INICIALIZACIÓN DE TABLAS ==========
def init_db():
    """Crea/migra tablas en Neon la primera vez que arranca la app."""
    conn = get_db_connection()
    if not conn:
        print("No se pudo conectar a Neon para inicializar la DB.")
        return
    try:
        cur = conn.cursor()

        # ── Tabla entrenador ──────────────────────────────────────────────
        cur.execute("""
            CREATE TABLE IF NOT EXISTS entrenador (
                id_entrenador  SERIAL PRIMARY KEY,
                nombre         VARCHAR(200) NOT NULL,
                especialidad   VARCHAR(200),
                experiencia    VARCHAR(100),
                certificaciones TEXT,
                descripcion    TEXT,
                email          VARCHAR(200),
                telefono       VARCHAR(50),
                imagen         BYTEA,
                imagen_mime    VARCHAR(50)
            )
        """)

        # ── Tabla producto ───────────────────────────────────────────────
        cur.execute("""
            CREATE TABLE IF NOT EXISTS producto (
                id_producto SERIAL PRIMARY KEY,
                nombre      VARCHAR(200) NOT NULL,
                categoria   VARCHAR(100),
                precio      NUMERIC(10,2),
                descripcion TEXT,
                stock       BOOLEAN DEFAULT TRUE,
                imagen      BYTEA,
                imagen_mime VARCHAR(50)
            )
        """)

        # ── Columnas imagen en tabla plan (si no existen) ────────────────
        cur.execute("ALTER TABLE plan ADD COLUMN IF NOT EXISTS imagen      BYTEA")
        cur.execute("ALTER TABLE plan ADD COLUMN IF NOT EXISTS imagen_mime VARCHAR(50)")

        conn.commit()

        # ── Poblar entrenadores iniciales ────────────────────────────────
        cur.execute("SELECT COUNT(*) FROM entrenador")
        if cur.fetchone()[0] == 0:
            for e in [
                ("Santiago Reyes",    "Entrenamiento Funcional y CrossFit", "8 años",  "NSCA-CPT, CrossFit Level 2, FMS",          "Especialista en movimientos funcionales y preparación atlética de alto rendimiento.", "santiago.reyes@newlifegym.com", "555-001"),
                ("Valentina Cruz",    "Yoga, Pilates y Bienestar",          "6 años",  "RYT-500, Pilates Mat & Reformer, Mindfulness","Experta en bienestar integral, meditación activa y recuperación funcional.",           "valentina.cruz@newlifegym.com",  "555-002"),
                ("Andrés Castellanos","Musculación, Fuerza y Nutrición",    "10 años", "ACE-CPT, CSCS, Nutrición Deportiva Avanzada","Especialista en hipertrofia, powerlifting y programas de fuerza máxima.",              "andres.cast@newlifegym.com",     "555-003"),
                ("Daniela Vargas",    "HIIT, Cardio y Pérdida de Grasa",   "5 años",  "AFAA-GFI, Spinning Level 3, TRX Certified", "Apasionada del cardio de alta intensidad, pérdida de grasa y resistencia.",           "daniela.vargas@newlifegym.com",  "555-004"),
            ]:
                cur.execute("""
                    INSERT INTO entrenador
                    (nombre, especialidad, experiencia, certificaciones, descripcion, email, telefono)
                    VALUES (%s,%s,%s,%s,%s,%s,%s)
                """, e)

        # ── Poblar productos iniciales ───────────────────────────────────
        cur.execute("SELECT COUNT(*) FROM producto")
        if cur.fetchone()[0] == 0:
            for p in [
                ("Proteína Whey Gold Standard", "Proteínas",    899,  "Proteína de suero de alta calidad, 24g por porción", True),
                ("Creatina Monohidratada",       "Suplementos",  449,  "Creatina pura micronizada, 5g por porción",          True),
                ("Pre-Workout Energía Extrema",  "Pre-Entreno",  599,  "Fórmula con cafeína y beta-alanina",                 True),
                ("BCAA + Glutamina",             "Recuperación", 549,  "Aminoácidos esenciales",                             True),
                ("Multivitamínico Completo",     "Vitaminas",    349,  "Complejo vitamínico diario",                         True),
                ("Shaker Profesional 700ml",     "Accesorios",   149,  "Shaker con compartimentos",                          True),
            ]:
                cur.execute("""
                    INSERT INTO producto (nombre, categoria, precio, descripcion, stock)
                    VALUES (%s,%s,%s,%s,%s)
                """, p)

        conn.commit()
        cur.close()
        conn.close()
        print("Base de datos inicializada correctamente.")
    except Exception as e:
        print(f"Error init_db: {e}")
        try:
            conn.rollback()
            conn.close()
        except:
            pass

# ── Llamar aquí para que funcione también con gunicorn / cualquier WSGI ──
init_db()

# ========== HELPER: leer imagen del request ==========
def leer_imagen(field_name='imagen'):
    archivo = request.files.get(field_name)
    if archivo and archivo.filename:
        datos = archivo.read()
        if datos:
            return datos, archivo.mimetype
    return None, None

# ========== RUTAS DE IMÁGENES ==========

@app.route("/imagen/entrenador/<int:id_entrenador>")
def imagen_entrenador(id_entrenador):
    conn = get_db_connection()
    if not conn:
        return "", 404
    try:
        cur = conn.cursor()
        cur.execute("SELECT imagen, imagen_mime FROM entrenador WHERE id_entrenador = %s", (id_entrenador,))
        row = cur.fetchone()
        cur.close(); conn.close()
        if row and row[0]:
            return Response(bytes(row[0]), mimetype=row[1] or 'image/jpeg')
        return "", 404
    except:
        return "", 404

@app.route("/imagen/plan/<int:id_plan>")
def imagen_plan(id_plan):
    conn = get_db_connection()
    if not conn:
        return "", 404
    try:
        cur = conn.cursor()
        cur.execute("SELECT imagen, imagen_mime FROM plan WHERE id_plan = %s", (id_plan,))
        row = cur.fetchone()
        cur.close(); conn.close()
        if row and row[0]:
            return Response(bytes(row[0]), mimetype=row[1] or 'image/jpeg')
        return "", 404
    except:
        return "", 404

@app.route("/imagen/producto/<int:id_producto>")
def imagen_producto(id_producto):
    conn = get_db_connection()
    if not conn:
        return "", 404
    try:
        cur = conn.cursor()
        cur.execute("SELECT imagen, imagen_mime FROM producto WHERE id_producto = %s", (id_producto,))
        row = cur.fetchone()
        cur.close(); conn.close()
        if row and row[0]:
            return Response(bytes(row[0]), mimetype=row[1] or 'image/jpeg')
        return "", 404
    except:
        return "", 404

# ========== RUTAS PÚBLICAS ==========

@app.route("/")
def index():
    return redirect(url_for("home"))

@app.route("/home")
def home():
    conn = get_db_connection()
    if not conn:
        return render_template("home.html", miembros=[], entrenadores=[])
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT m.nombre, p.nombre AS plan,
                   TO_CHAR(mem.fecha_inicio, 'Month YYYY') AS desde
            FROM miembro m
            JOIN membresia mem ON m.id_miembro = mem.id_miembro
            JOIN plan p ON mem.id_plan = p.id_plan
            WHERE mem.estado = 'activa'
            ORDER BY mem.fecha_inicio DESC LIMIT 8
        """)
        miembros = cur.fetchall()

        cur.execute("""
            SELECT id_entrenador, nombre, especialidad, experiencia,
                   certificaciones, descripcion,
                   (imagen IS NOT NULL) AS imagen
            FROM entrenador LIMIT 2
        """)
        entrenadores = cur.fetchall()

        cur.close(); conn.close()
        return render_template("home.html", miembros=miembros, entrenadores=entrenadores)
    except:
        return render_template("home.html", miembros=[], entrenadores=[])

@app.route("/membresias")
def membresias():
    conn = get_db_connection()
    if not conn:
        return render_template("membresias.html", planes=[])
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT id_plan, nombre, descripcion, precio_mensual,
                   beneficios, duracion_meses, activo,
                   (imagen IS NOT NULL) AS imagen
            FROM plan WHERE activo = TRUE ORDER BY precio_mensual
        """)
        planes = cur.fetchall()
        cur.close(); conn.close()
        return render_template("membresias.html", planes=planes)
    except:
        return render_template("membresias.html", planes=[])

@app.route("/tienda")
def tienda():
    conn = get_db_connection()
    if not conn:
        return render_template("tienda.html", productos=[])
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT id_producto, nombre, categoria, precio, descripcion, stock,
                   (imagen IS NOT NULL) AS imagen
            FROM producto ORDER BY nombre
        """)
        productos = cur.fetchall()
        cur.close(); conn.close()
        return render_template("tienda.html", productos=productos)
    except:
        return render_template("tienda.html", productos=[])

@app.route("/entrenadores")
def entrenadores_page():
    conn = get_db_connection()
    if not conn:
        return render_template("entrenadores.html", entrenadores=[], nombres=[])
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT id_entrenador, nombre, especialidad, experiencia,
                   certificaciones, descripcion, email, telefono,
                   (imagen IS NOT NULL) AS imagen
            FROM entrenador ORDER BY nombre
        """)
        entrenadores = cur.fetchall()
        cur.close(); conn.close()
        # Extraer primeros nombres para los testimonios
        nombres = [e['nombre'].split()[0] for e in entrenadores]
        return render_template("entrenadores.html", entrenadores=entrenadores, nombres=nombres)
    except:
        return render_template("entrenadores.html", entrenadores=[], nombres=[])

@app.route("/galeria")
def galeria():
    imagenes = ["gym1.jpg","gym2.jpg","gym3.jpg","gym4.jpg","gym5.jpg","gym6.jpg"]
    return render_template("galeria.html", imagenes=imagenes)

# ========== COMPRAS ==========

@app.route("/comprar_membresia/<int:plan_id>", methods=["POST"])
def comprar_membresia(plan_id):
    conn = get_db_connection()
    if not conn:
        return redirect(url_for("membresias"))
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('SELECT * FROM plan WHERE id_plan = %s', (plan_id,))
        plan = cur.fetchone()
        cur.close(); conn.close()
        if plan:
            return render_template("compra_exitosa.html", tipo="membresía",
                                   item=plan['nombre'], precio=plan['precio_mensual'],
                                   mensaje="Tu membresía ha sido activada exitosamente.")
    except:
        pass
    return redirect(url_for("membresias"))

@app.route("/comprar_producto/<int:producto_id>", methods=["POST"])
def comprar_producto(producto_id):
    conn = get_db_connection()
    if not conn:
        return redirect(url_for('tienda'))
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('SELECT * FROM producto WHERE id_producto = %s AND stock = TRUE', (producto_id,))
        p = cur.fetchone()
        cur.close(); conn.close()
        if p:
            return render_template("compra_exitosa.html", tipo="producto",
                                   item=p["nombre"], precio=p["precio"],
                                   mensaje="Tu compra ha sido procesada. Pasa a recogerla en recepción.")
    except:
        pass
    return redirect(url_for("tienda"))

# ========== ADMINISTRACIÓN ==========

@app.route("/admin")
def admin_login():
    if session.get('logged_in'):
        return redirect(url_for('admin_dashboard'))
    return render_template("login.html")

@app.route("/admin/login", methods=["POST"])
def admin_login_post():
    if request.form.get('username') == ADMIN_USERNAME and request.form.get('password') == ADMIN_PASSWORD:
        session['logged_in'] = True
        return redirect(url_for('admin_dashboard'))
    flash('Usuario o contraseña incorrectos', 'error')
    return redirect(url_for('admin_login'))

@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('admin_login'))

    conn = get_db_connection()
    if not conn:
        return render_template("dashboard.html", miembros=[], planes=[], membresias=[], productos=[], entrenadores=[])
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("""
            SELECT m.id_miembro, m.nombre, m.email, m.telefono, m.estado,
                   p.nombre AS plan, TO_CHAR(mem.fecha_inicio,'DD/MM/YYYY') AS desde
            FROM miembro m
            LEFT JOIN membresia mem ON m.id_miembro = mem.id_miembro AND mem.estado = 'activa'
            LEFT JOIN plan p ON mem.id_plan = p.id_plan
            ORDER BY m.nombre
        """)
        miembros = cur.fetchall()

        cur.execute('SELECT * FROM plan ORDER BY precio_mensual')
        planes = cur.fetchall()

        cur.execute("""
            SELECT mem.id_membresia, m.nombre AS miembro, p.nombre AS plan,
                   TO_CHAR(mem.fecha_inicio,'DD/MM/YYYY') AS fecha_inicio,
                   TO_CHAR(mem.fecha_fin,'DD/MM/YYYY') AS fecha_fin,
                   mem.estado, mem.monto_pagado
            FROM membresia mem
            JOIN miembro m ON mem.id_miembro = m.id_miembro
            JOIN plan p ON mem.id_plan = p.id_plan
            WHERE mem.estado IN ('activa','vencida')
            ORDER BY mem.fecha_inicio DESC
        """)
        membresias = cur.fetchall()

        cur.execute("""
            SELECT id_producto AS id, id_producto, nombre, categoria, precio, stock,
                   (imagen IS NOT NULL) AS tiene_imagen
            FROM producto ORDER BY nombre
        """)
        productos = cur.fetchall()

        cur.execute("""
            SELECT id_entrenador AS id, id_entrenador, nombre, especialidad,
                   experiencia, certificaciones,
                   (imagen IS NOT NULL) AS tiene_imagen
            FROM entrenador ORDER BY nombre
        """)
        entrenadores = cur.fetchall()

        cur.close(); conn.close()
        return render_template("dashboard.html", miembros=miembros, planes=planes,
                               membresias=membresias, productos=productos, entrenadores=entrenadores)
    except Exception as e:
        print(f"Error dashboard: {e}")
        return render_template("dashboard.html", miembros=[], planes=[], membresias=[], productos=[], entrenadores=[])

@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for('admin_login'))

# ========== CRUD MIEMBROS ==========

@app.route("/admin/miembro/crear", methods=["GET","POST"])
def crear_miembro():
    if not session.get('logged_in'): return redirect(url_for('admin_login'))
    if request.method == "POST":
        conn = get_db_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO miembro (nombre,email,telefono,fecha_nacimiento,direccion,estado)
                    VALUES (%s,%s,%s,%s,%s,'activo')
                """, (request.form.get('nombre'), request.form.get('email'),
                      request.form.get('telefono'), request.form.get('fecha_nacimiento'),
                      request.form.get('direccion')))
                conn.commit(); cur.close(); conn.close()
                flash('Miembro creado exitosamente','success')
                return redirect(url_for('admin_dashboard'))
            except Exception as e:
                flash(f'Error: {e}','error')
    return render_template("crear_miembro.html")

@app.route("/admin/miembro/editar/<int:id_miembro>", methods=["GET","POST"])
def editar_miembro(id_miembro):
    if not session.get('logged_in'): return redirect(url_for('admin_login'))
    conn = get_db_connection()
    if not conn: return redirect(url_for('admin_dashboard'))

    if request.method == "POST":
        try:
            cur = conn.cursor()
            cur.execute("""
                UPDATE miembro SET nombre=%s,email=%s,telefono=%s,
                fecha_nacimiento=%s,direccion=%s,estado=%s WHERE id_miembro=%s
            """, (request.form.get('nombre'), request.form.get('email'),
                  request.form.get('telefono'), request.form.get('fecha_nacimiento'),
                  request.form.get('direccion'), request.form.get('estado'), id_miembro))
            conn.commit(); cur.close(); conn.close()
            flash('Miembro actualizado','success')
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            flash(f'Error: {e}','error')

    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('SELECT * FROM miembro WHERE id_miembro = %s', (id_miembro,))
        miembro = cur.fetchone()
        cur.close(); conn.close()
        return render_template("editar_miembro.html", miembro=miembro)
    except:
        return redirect(url_for('admin_dashboard'))

@app.route("/admin/miembro/eliminar/<int:id_miembro>", methods=["POST"])
def eliminar_miembro(id_miembro):
    if not session.get('logged_in'): return redirect(url_for('admin_login'))
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('DELETE FROM miembro WHERE id_miembro = %s', (id_miembro,))
            conn.commit(); cur.close(); conn.close()
            flash('Miembro eliminado','success')
        except:
            flash('Error: puede tener membresías asociadas','error')
    return redirect(url_for('admin_dashboard'))

# ========== CRUD MEMBRESÍAS ==========

@app.route("/admin/membresia/crear", methods=["GET","POST"])
def crear_membresia():
    if not session.get('logged_in'): return redirect(url_for('admin_login'))
    conn = get_db_connection()
    if not conn: return redirect(url_for('admin_dashboard'))

    if request.method == "POST":
        try:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute('SELECT precio_mensual FROM plan WHERE id_plan = %s', (request.form.get('id_plan'),))
            plan = cur.fetchone()
            meses = int(request.form.get('meses', 1))
            monto = plan['precio_mensual'] * meses
            fecha_inicio = request.form.get('fecha_inicio')
            fecha_fin = (datetime.strptime(fecha_inicio,'%Y-%m-%d') + timedelta(days=30*meses)).date()
            cur.execute("""
                INSERT INTO membresia (id_miembro,id_plan,fecha_inicio,fecha_fin,estado,monto_pagado)
                VALUES (%s,%s,%s,%s,'activa',%s)
            """, (request.form.get('id_miembro'), request.form.get('id_plan'),
                  fecha_inicio, fecha_fin, monto))
            conn.commit(); cur.close(); conn.close()
            flash('Membresía creada','success')
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            flash(f'Error: {e}','error')

    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT id_miembro,nombre FROM miembro WHERE estado='activo' ORDER BY nombre")
        miembros = cur.fetchall()
        cur.execute('SELECT id_plan,nombre,precio_mensual FROM plan WHERE activo=TRUE ORDER BY nombre')
        planes = cur.fetchall()
        cur.close(); conn.close()
        return render_template("crear_membresia.html", miembros=miembros, planes=planes)
    except:
        return redirect(url_for('admin_dashboard'))

@app.route("/admin/membresia/cambiar-plan/<int:id_miembro>", methods=["GET","POST"])
def cambiar_plan_miembro(id_miembro):
    if not session.get('logged_in'): return redirect(url_for('admin_login'))
    conn = get_db_connection()
    if not conn: return redirect(url_for('admin_dashboard'))

    if request.method == "POST":
        try:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute('DELETE FROM membresia WHERE id_miembro=%s AND estado=%s', (id_miembro,'activa'))
            cur.execute('SELECT precio_mensual FROM plan WHERE id_plan=%s', (request.form.get('nuevo_plan'),))
            plan = cur.fetchone()
            meses = int(request.form.get('meses',1))
            monto = plan['precio_mensual'] * meses
            fecha_inicio = datetime.now().date()
            fecha_fin = fecha_inicio + timedelta(days=30*meses)
            cur.execute("""
                INSERT INTO membresia (id_miembro,id_plan,fecha_inicio,fecha_fin,estado,monto_pagado)
                VALUES (%s,%s,%s,%s,'activa',%s)
            """, (id_miembro, request.form.get('nuevo_plan'), fecha_inicio, fecha_fin, monto))
            conn.commit(); cur.close(); conn.close()
            flash('Plan cambiado exitosamente','success')
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            flash(f'Error: {e}','error')

    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute('SELECT * FROM miembro WHERE id_miembro=%s', (id_miembro,))
        miembro = cur.fetchone()
        cur.execute('SELECT * FROM plan WHERE activo=TRUE ORDER BY precio_mensual')
        planes = cur.fetchall()
        cur.close(); conn.close()
        return render_template("cambiar_plan.html", miembro=miembro, planes=planes)
    except:
        return redirect(url_for('admin_dashboard'))

@app.route("/admin/membresia/cambiar-plan-desde-membresia/<int:id_membresia>", methods=["GET","POST"])
def cambiar_plan_desde_membresia(id_membresia):
    if not session.get('logged_in'): return redirect(url_for('admin_login'))
    conn = get_db_connection()
    if not conn: return redirect(url_for('admin_dashboard'))

    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT mem.*, m.nombre AS nombre_miembro, m.email
            FROM membresia mem
            JOIN miembro m ON mem.id_miembro = m.id_miembro
            WHERE mem.id_membresia = %s
        """, (id_membresia,))
        membresia = cur.fetchone()
        if not membresia:
            flash('Membresía no encontrada','error'); conn.close()
            return redirect(url_for('admin_dashboard'))

        id_miembro = membresia['id_miembro']

        if request.method == "POST":
            try:
                cur.execute('DELETE FROM membresia WHERE id_miembro=%s AND estado=%s', (id_miembro,'activa'))
                cur.execute('SELECT precio_mensual FROM plan WHERE id_plan=%s', (request.form.get('nuevo_plan'),))
                plan_data = cur.fetchone()
                if not plan_data:
                    flash('Plan no encontrado','error'); conn.close()
                    return redirect(url_for('admin_dashboard'))
                meses = int(request.form.get('meses',1))
                monto = plan_data['precio_mensual'] * meses
                fecha_inicio = datetime.now().date()
                fecha_fin = fecha_inicio + timedelta(days=30*meses)
                cur.execute("""
                    INSERT INTO membresia (id_miembro,id_plan,fecha_inicio,fecha_fin,estado,monto_pagado)
                    VALUES (%s,%s,%s,%s,'activa',%s)
                """, (id_miembro, request.form.get('nuevo_plan'), fecha_inicio, fecha_fin, monto))
                conn.commit(); cur.close(); conn.close()
                flash('Plan cambiado exitosamente','success')
                return redirect(url_for('admin_dashboard'))
            except Exception as e:
                conn.rollback(); flash(f'Error: {e}','error'); conn.close()
                return redirect(url_for('admin_dashboard'))

        cur.execute('SELECT * FROM plan WHERE activo=TRUE ORDER BY precio_mensual')
        planes = cur.fetchall()
        cur.close(); conn.close()
        miembro = {'id_miembro': id_miembro, 'nombre': membresia['nombre_miembro'], 'email': membresia['email']}
        return render_template("cambiar_plan.html", miembro=miembro, planes=planes)
    except Exception as e:
        if conn: conn.close()
        flash(f'Error: {e}','error')
        return redirect(url_for('admin_dashboard'))

@app.route("/admin/membresia/eliminar/<int:id_membresia>", methods=["POST"])
def eliminar_membresia(id_membresia):
    if not session.get('logged_in'): return redirect(url_for('admin_login'))
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("UPDATE membresia SET estado='cancelada' WHERE id_membresia=%s", (id_membresia,))
            conn.commit(); cur.close(); conn.close()
            flash('Membresía cancelada','success')
        except:
            flash('Error al cancelar','error')
    return redirect(url_for('admin_dashboard'))

# ========== CRUD PLANES ==========

@app.route("/admin/plan/crear", methods=["GET","POST"])
def crear_plan():
    if not session.get('logged_in'): return redirect(url_for('admin_login'))
    if request.method == "POST":
        conn = get_db_connection()
        if conn:
            try:
                imagen_bytes, imagen_mime = leer_imagen()
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO plan
                    (nombre,descripcion,precio_mensual,beneficios,duracion_meses,activo,imagen,imagen_mime)
                    VALUES (%s,%s,%s,%s,%s,TRUE,%s,%s)
                """, (request.form.get('nombre'), request.form.get('descripcion'),
                      request.form.get('precio_mensual'), request.form.get('beneficios'),
                      request.form.get('duracion_meses'), imagen_bytes, imagen_mime))
                conn.commit(); cur.close(); conn.close()
                flash('Plan creado exitosamente','success')
                return redirect(url_for('admin_dashboard'))
            except Exception as e:
                flash(f'Error: {e}','error')
    return render_template("crear_plan.html")

@app.route("/admin/plan/editar/<int:id_plan>", methods=["GET","POST"])
def editar_plan(id_plan):
    if not session.get('logged_in'): return redirect(url_for('admin_login'))
    conn = get_db_connection()
    if not conn: return redirect(url_for('admin_dashboard'))

    if request.method == "POST":
        try:
            imagen_bytes, imagen_mime = leer_imagen()
            activo = request.form.get('activo') == 'on'
            cur = conn.cursor()
            if imagen_bytes:
                cur.execute("""
                    UPDATE plan SET nombre=%s,descripcion=%s,precio_mensual=%s,
                    beneficios=%s,duracion_meses=%s,activo=%s,imagen=%s,imagen_mime=%s
                    WHERE id_plan=%s
                """, (request.form.get('nombre'), request.form.get('descripcion'),
                      request.form.get('precio_mensual'), request.form.get('beneficios'),
                      request.form.get('duracion_meses'), activo,
                      imagen_bytes, imagen_mime, id_plan))
            else:
                cur.execute("""
                    UPDATE plan SET nombre=%s,descripcion=%s,precio_mensual=%s,
                    beneficios=%s,duracion_meses=%s,activo=%s WHERE id_plan=%s
                """, (request.form.get('nombre'), request.form.get('descripcion'),
                      request.form.get('precio_mensual'), request.form.get('beneficios'),
                      request.form.get('duracion_meses'), activo, id_plan))
            conn.commit(); cur.close(); conn.close()
            flash('Plan actualizado','success')
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            flash(f'Error: {e}','error')

    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT id_plan,nombre,descripcion,precio_mensual,beneficios,
                   duracion_meses,activo,(imagen IS NOT NULL) AS imagen
            FROM plan WHERE id_plan=%s
        """, (id_plan,))
        plan = cur.fetchone()
        cur.close(); conn.close()
        return render_template("editar_plan.html", plan=plan)
    except:
        return redirect(url_for('admin_dashboard'))

@app.route("/admin/plan/eliminar/<int:id_plan>", methods=["POST"])
def eliminar_plan(id_plan):
    if not session.get('logged_in'): return redirect(url_for('admin_login'))
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('UPDATE plan SET activo=FALSE WHERE id_plan=%s', (id_plan,))
            conn.commit(); cur.close(); conn.close()
            flash('Plan desactivado','success')
        except:
            flash('Error al desactivar plan','error')
    return redirect(url_for('admin_dashboard'))

# ========== CRUD ENTRENADORES ==========

@app.route("/admin/entrenador/crear", methods=["GET","POST"])
def crear_entrenador():
    if not session.get('logged_in'): return redirect(url_for('admin_login'))
    if request.method == "POST":
        conn = get_db_connection()
        if conn:
            try:
                imagen_bytes, imagen_mime = leer_imagen()
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO entrenador
                    (nombre,especialidad,experiencia,certificaciones,descripcion,email,telefono,imagen,imagen_mime)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, (request.form.get('nombre'), request.form.get('especialidad'),
                      request.form.get('experiencia'), request.form.get('certificaciones',''),
                      request.form.get('descripcion',''), request.form.get('email',''),
                      request.form.get('telefono',''), imagen_bytes, imagen_mime))
                conn.commit(); cur.close(); conn.close()
                flash('Entrenador creado exitosamente','success')
                return redirect(url_for('admin_dashboard'))
            except Exception as e:
                flash(f'Error: {e}','error')
    return render_template("crear_entrenador.html")

@app.route("/admin/entrenador/editar/<int:id_entrenador>", methods=["GET","POST"])
def editar_entrenador(id_entrenador):
    if not session.get('logged_in'): return redirect(url_for('admin_login'))
    conn = get_db_connection()
    if not conn: return redirect(url_for('admin_dashboard'))

    if request.method == "POST":
        try:
            imagen_bytes, imagen_mime = leer_imagen()
            cur = conn.cursor()
            if imagen_bytes:
                cur.execute("""
                    UPDATE entrenador SET nombre=%s,especialidad=%s,experiencia=%s,
                    certificaciones=%s,descripcion=%s,email=%s,telefono=%s,
                    imagen=%s,imagen_mime=%s WHERE id_entrenador=%s
                """, (request.form.get('nombre'), request.form.get('especialidad'),
                      request.form.get('experiencia'), request.form.get('certificaciones',''),
                      request.form.get('descripcion',''), request.form.get('email',''),
                      request.form.get('telefono',''), imagen_bytes, imagen_mime, id_entrenador))
            else:
                cur.execute("""
                    UPDATE entrenador SET nombre=%s,especialidad=%s,experiencia=%s,
                    certificaciones=%s,descripcion=%s,email=%s,telefono=%s
                    WHERE id_entrenador=%s
                """, (request.form.get('nombre'), request.form.get('especialidad'),
                      request.form.get('experiencia'), request.form.get('certificaciones',''),
                      request.form.get('descripcion',''), request.form.get('email',''),
                      request.form.get('telefono',''), id_entrenador))
            conn.commit(); cur.close(); conn.close()
            flash('Entrenador actualizado','success')
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            flash(f'Error: {e}','error')

    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT id_entrenador,nombre,especialidad,experiencia,
                   certificaciones,descripcion,email,telefono,
                   (imagen IS NOT NULL) AS imagen
            FROM entrenador WHERE id_entrenador=%s
        """, (id_entrenador,))
        entrenador = cur.fetchone()
        cur.close(); conn.close()
        if not entrenador:
            flash('Entrenador no encontrado','error')
            return redirect(url_for('admin_dashboard'))
        return render_template("editar_entrenador.html", entrenador=entrenador)
    except:
        return redirect(url_for('admin_dashboard'))

@app.route("/admin/entrenador/eliminar/<int:id_entrenador>", methods=["POST"])
def eliminar_entrenador(id_entrenador):
    if not session.get('logged_in'): return redirect(url_for('admin_login'))
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('DELETE FROM entrenador WHERE id_entrenador=%s', (id_entrenador,))
            conn.commit(); cur.close(); conn.close()
            flash('Entrenador eliminado','success')
        except Exception as e:
            flash(f'Error: {e}','error')
    return redirect(url_for('admin_dashboard'))

# ========== CRUD PRODUCTOS ==========

@app.route("/admin/producto/crear", methods=["GET","POST"])
def crear_producto():
    if not session.get('logged_in'): return redirect(url_for('admin_login'))
    if request.method == "POST":
        conn = get_db_connection()
        if conn:
            try:
                imagen_bytes, imagen_mime = leer_imagen()
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO producto (nombre,categoria,precio,descripcion,stock,imagen,imagen_mime)
                    VALUES (%s,%s,%s,%s,%s,%s,%s)
                """, (request.form.get('nombre'), request.form.get('categoria'),
                      float(request.form.get('precio',0)), request.form.get('descripcion',''),
                      request.form.get('stock') == 'on', imagen_bytes, imagen_mime))
                conn.commit(); cur.close(); conn.close()
                flash('Producto creado exitosamente','success')
                return redirect(url_for('admin_dashboard'))
            except Exception as e:
                flash(f'Error: {e}','error')
    return render_template("crear_producto.html")

@app.route("/admin/producto/editar/<int:id_producto>", methods=["GET","POST"])
def editar_producto(id_producto):
    if not session.get('logged_in'): return redirect(url_for('admin_login'))
    conn = get_db_connection()
    if not conn: return redirect(url_for('admin_dashboard'))

    if request.method == "POST":
        try:
            imagen_bytes, imagen_mime = leer_imagen()
            cur = conn.cursor()
            if imagen_bytes:
                cur.execute("""
                    UPDATE producto SET nombre=%s,categoria=%s,precio=%s,
                    descripcion=%s,stock=%s,imagen=%s,imagen_mime=%s
                    WHERE id_producto=%s
                """, (request.form.get('nombre'), request.form.get('categoria'),
                      float(request.form.get('precio',0)), request.form.get('descripcion',''),
                      request.form.get('stock') == 'on', imagen_bytes, imagen_mime, id_producto))
            else:
                cur.execute("""
                    UPDATE producto SET nombre=%s,categoria=%s,precio=%s,
                    descripcion=%s,stock=%s WHERE id_producto=%s
                """, (request.form.get('nombre'), request.form.get('categoria'),
                      float(request.form.get('precio',0)), request.form.get('descripcion',''),
                      request.form.get('stock') == 'on', id_producto))
            conn.commit(); cur.close(); conn.close()
            flash('Producto actualizado','success')
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            flash(f'Error: {e}','error')

    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT id_producto,nombre,categoria,precio,descripcion,stock,
                   (imagen IS NOT NULL) AS imagen
            FROM producto WHERE id_producto=%s
        """, (id_producto,))
        producto = cur.fetchone()
        cur.close(); conn.close()
        if not producto:
            flash('Producto no encontrado','error')
            return redirect(url_for('admin_dashboard'))
        return render_template("editar_producto.html", producto=producto)
    except:
        return redirect(url_for('admin_dashboard'))

@app.route("/admin/producto/eliminar/<int:id_producto>", methods=["POST"])
def eliminar_producto(id_producto):
    if not session.get('logged_in'): return redirect(url_for('admin_login'))
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute('DELETE FROM producto WHERE id_producto=%s', (id_producto,))
            conn.commit(); cur.close(); conn.close()
            flash('Producto eliminado','success')
        except Exception as e:
            flash(f'Error: {e}','error')
    return redirect(url_for('admin_dashboard'))

# ========== ERRORES ==========

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    return render_template('500.html'), 500

# ========== INICIO ==========
if __name__ == "__main__":
    app.run(debug=True)