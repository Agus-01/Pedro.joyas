# Tienda de Joyería

Proyecto Flask con catálogo de anillos, pulseras, collares y combos, plus carrito de compra y checkout.

## Despliegue en Render

### 1. Crea un repositorio Git

Si aún no tienes tu proyecto en Git, inicializa uno y súbelo a GitHub:

```bash
cd "c:\Users\agust\OneDrive\Escritorio\Pagina wed"
git init
git add .
git commit -m "Primer deploy" 
# Luego crea un repositorio en GitHub y empuja al remoto
```

### 2. Crea cuenta en Render

- Ve a `https://render.com`
- Regístrate o inicia sesión
- Conecta tu cuenta de GitHub

### 3. Crea un nuevo Web Service

- Elige `New +` > `Web Service`
- Selecciona tu repositorio
- Branch: `main` o el branch donde subiste el proyecto

### 4. Configura la app

- `Build Command`: `pip install -r requirements.txt`
- `Start Command`: `gunicorn app:app`
- `Environment` > `Add Environment Variable`
  - `MP_ACCESS_TOKEN` con tu token de Mercado Pago

### 5. Despliega

Render hará el deploy automático y te dará una URL pública.

## Archivos importantes

- `app.py` → backend Flask y rutas
- `templates/index.html` → página principal
- `static/css/styles.css` → estilos
- `static/js/main.js` → lógica del carrito y filtros
- `Procfile` → comando de inicio para Render
- `.env.example` → configuración local de Mercado Pago

## Uso local

1. Copia `.env.example` a `.env`
2. Agrega `MP_ACCESS_TOKEN` y `ADMIN_PASSWORD` si querés cambiar la clave del admin
3. Instala dependencias:

```bash
python -m pip install -r requirements.txt
```

4. Crea la base de datos (productos, talles/stock y usuario admin):

```bash
python init_db.py
```

Para empezar de cero (borra pedidos y datos):

```bash
python init_db.py --reset
```

5. Ejecuta la tienda:

```bash
python app.py
```

6. Abre `http://127.0.0.1:5000`

### Base de datos

| Tabla | Contenido |
| ----- | --------- |
| `users` | Clientes registrados y administrador |
| `products` | Catálogo de joyas |
| `product_variants` | Talle/medida y stock por producto |
| `orders` | Pedidos y pagos |

- Archivo SQLite: `jewelry_store.db`
- Admin por defecto: `admin@pedrojoyas.com` / contraseña de `ADMIN_PASSWORD`
- Panel: `http://127.0.0.1:5000/admin/login`
