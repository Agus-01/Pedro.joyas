import os

from models import Product, ProductVariant, User, db

DISCOUNT = 0.20

ADMIN_EMAIL = 'agustincarbone22@gmail.com'
ADMIN_NAME = 'Administrador'

# Productos iniciales (imágenes que ya tenés en static/images)
INITIAL_PRODUCTS = [
   {
        'name': 'Anillo TODO PASA',
        'description': 'Un manifiesto de elegancia y actitud. Este anillo premium destaca por su grabado de alta precisión y un diseño robusto que se adapta a cualquier estilo con distinción única.',
        'category': 'anillos',
        'category_label': 'Anillos',
        'price': 56250.00,
        'image': '/static/images/anillo1.jpeg',
        'sizes': ['12', '14', '16', '18'],
        'stocks': [10, 10, 10, 10],
    },
    
    
    
    {
        'name': 'Anillo ROLEX grabado',
        'description': 'Inspirado en la estética de la alta relojería. Combina un imponente relieve texturizado con un grabado interno impecable, ideal para quienes buscan una presencia fuerte y sofisticada.',
        'category': 'anillos',
        'category_label': 'Anillos',
        'price': 56250.00,
        'image': '/static/images/anillo3.jpeg',
        'sizes': ['12', '14', '16', '18'],
        'stocks': [8, 8, 8, 8],
    },
    {
        'name': 'Anillo Trebol',
        'description': 'Sofisticación y amuleto en una sola pieza. Su diseño estilizado rinde homenaje a la buena fortuna, con acabados delicados que lo convierten en el accesorio perfecto para el día a día.',
        'category': 'anillos',
        'category_label': 'Anillos',
        'price': 56250.00,
        'image': '/static/images/anillo4.jpeg',
        'sizes': ['12', '14', '16', '18'],
        'stocks': [8, 8, 8, 8],
    },

    {
        'name': 'Anillo 79',
        'description': 'Un anillopractico y elegante, con un diseño de líneas limpias y un acabado pulido que refleja la luz de manera sutil.',
        'category': 'anillos',
        'category_label': 'Anillos',
        'price': 56250.00,
        'image': '/static/images/anillo5.jpeg',
        'sizes': ['12', '14', '16', '18'],
        'stocks': [8, 8, 8, 8],
    },

    {
        'name': 'Anillo ROLEX Articulado',
        'description': 'Un anillo que combina la elegancia de la alta joyería con la innovación del diseño articulado. Su estructura flexible se adapta cómodamente al dedo, mientras que su acabado pulido y detalles grabados lo convierten en una pieza de lujo imprescindible.',
        'category': 'anillos',
        'category_label': 'Anillos',
        'price': 81250.00,
        'image': '/static/images/rolexa.jpeg',
        'sizes': ['12', '14', '16', '18'],
        'stocks': [8, 8, 8, 8],
    },

    {
        'name': 'Anillo Rolex grueso',
        'description': 'La máxima expresión del lujo contemporáneo. Una pieza exclusiva de Pedro Joyas, diseñada con líneas sofisticadas y un pulido espejo que captura la luz desde cualquier ángulo.',
        'category': 'anillos',
        'category_label': 'Anillos',
        'price': 56250.00,
        'image': '/static/images/anillos.jpeg',
        'sizes': ['12', '14', '16', '18'],
        'stocks': [8, 8, 8, 8],
    },

    {
        'name': 'Anillo 32',
        'description': 'Un anillo con un diseño poco común, en el que un 32 está grabado en el centro. Cuenta con líneas limpias y un acabado pulido que refleja la luz de manera sutil.',
        'category': 'anillos',
        'category_label': 'Anillos',
        'price': 56250.00,
        'image': '/static/images/32.jpeg',
        'sizes': ['12', '14', '16', '18'],
        'stocks': [8, 8, 8, 8],
    },

    {
        'name': 'Anillo Piedra roja',
        'description': 'Un anillo con una piedra roja en el centro, rodeada de un diseño elegante y sofisticado. La piedra roja aporta un toque de color vibrante, mientras que el diseño pulido y detallado lo convierte en una pieza de lujo imprescindible.',
        'category': 'anillos',
        'category_label': 'Anillos',
        'price': 56250.00,
        'image': '/static/images/piedras.jpg',
        'sizes': ['12', '14', '16', '18'],
        'stocks': [8, 8, 8, 8],
    },

    
    {
        'name': 'Anillo Cleopatra',
        'description': 'Este anillo Cleopatra demuestra la máxima expresión del lujo contemporáneo. Es una pieza exclusiva de Pedro Joyas, diseñada con líneas sofisticadas y un pulido espejo que captura la luz desde cualquier ángulo.',
        'category': 'anillos',
        'category_label': 'Anillos',
        'price': 56250.00,
        'image': '/static/images/cleopatra.jpg',
        'sizes': ['12', '14', '16', '18'],
        'stocks': [8, 8, 8, 8],
    },




    # --- PULSERAS (Precio final limpio basado en el valor superior) ---
    {
        'name': 'Pulsera cedusa',
        'description': 'Una pieza imponente que no pasa desapercibida. Su tramado ancho y eslabones macizos ofrecen un diseño moderno, pensado para resaltar la muñeca con un brillo dorado sublime.',
        'category': 'pulseras',
        'category_label': 'Pulseras',
        'price': 118750.00,
        'image': '/static/images/WhatsApp Image 2026-05-23 at 20.25.57.jpeg',
        'sizes': ['S', 'M', 'L'],
        'stocks': [5, 10, 5],
    },
    {
        'name': 'Pulsera peruano',
        'description': 'Tradición y vanguardia unidas en un tejido compacto y resistente. Esta pulsera de peso ideal cuenta con un cierre de seguridad premium, combinando confort y estilo de manera impecable.',
        'category': 'pulseras',
        'category_label': 'Pulseras',
        'price': 75000.00,
        'image': '/static/images/peruana.jpeg',
        'sizes': ['S', 'M', 'L'],
        'stocks': [6, 6, 6],
    },
    {
        'name': 'Pulsera Juliana',
        'description': 'Delicadeza y distinción en su máxima pureza. Sus eslabones curvos fluyen con un movimiento natural y elegante, convirtiéndola en una joya versátil indispensable para cualquier ocasión.',
        'category': 'pulseras',
        'category_label': 'Pulseras',
        'price': 62500.00,
        'image': '/static/images/juliana.jpeg',
        'sizes': ['S', 'M', 'L'],
        'stocks': [6, 6, 6],
    },
    {
        'name': 'Pulsera Tourbillon',
        'description': 'El equilibrio perfecto entre dinamismo y lujo. Destaca por su característico entrelazado helicoidal que genera un juego visual único de luces y sombras con cada movimiento de tu mano.',
        'category': 'pulseras',
        'category_label': 'Pulseras',
        'price': 75000.00,
        'image': '/static/images/tourbillon.jpeg',
        'sizes': ['S', 'M', 'L'],
        'stocks': [6, 6, 6],
    },

    # --- CADENAS / COLLARES (Precio de referencia superior como único precio) ---
    {
        'name': 'Cadena Tourbillon',
        'description': 'Un clásico que jamás pasa de moda. Esta cadena presenta un eslabonado trenzado de gran grosor que se asienta de forma impecable en el cuello, derrochando prestancia y categoría.',
        'category': 'collares',
        'category_label': 'Collares',
        'price': 118750.00,
        'image': '/static/images/cadenatoutbillon.jpg',
        'sizes': ['40cm', '45cm', '50cm'],
        'stocks': [4, 4, 4],
    },
    {
        'name': 'Cadena JULIANA',
        'description': 'Sutil, brillante y cautivadora. Sus eslabones pulidos simétricamente garantizan un reflejo dorado constante, siendo la opción ideal tanto para lucir sola como para acompañar con tus dijes favoritos.',
        'category': 'collares',
        'category_label': 'Collares',
        'price':118750.00,
        'image': '/static/images/cadena juliana.jpeg',
        'sizes': ['40cm', '45cm', '50cm'],
        'stocks': [4, 4, 4],
    },
    {
        'name': 'Cadena GROUMET',
        'description': 'Fuerza y carácter tradicional. Confeccionada con eslabones planos entrelazados con precisión milimétrica, es la cadena ideal para quienes buscan una joya imponente, duradera y de gran presencia.',
        'category': 'collares',
        'category_label': 'Collares',
        'price': 137500.00,
        'image': '/static/images/grumet.jpeg',
        'sizes': ['40cm', '45cm', '50cm'],
        'stocks': [4, 4, 4],
    }, 
    {
        'name': 'Cadena FORCET',
        'description': 'Elegancia geométrica en estado puro. Su diseño de eslabones rectangulares pulidos a mano aporta una estética limpia, minimalista y de altísima costura que realza cualquier outfit.',
        'category': 'collares',
        'category_label': 'Collares',
        'price': 118750.00,
        'image': '/static/images/Forcet.jpg',
        'sizes': ['40cm', '45cm', '50cm'],
        'stocks': [4, 4, 4],
    },

{
        'name': 'Cadena Paris',
        'description': 'Un diseño que evoca la sofisticación parisina con un toque moderno. Sus eslabones redondeados y pulidos a mano crean un brillo suave y elegante, convirtiéndola en la opción perfecta para quienes buscan una pieza versátil y con estilo atemporal.',
        'category': 'collares',
        'category_label': 'Collares',
        'price': 118750.00,
        'image': '/static/images/paris.jpeg',
        'sizes': ['40cm', '45cm', '50cm'],
        'stocks': [4, 4, 4],
    },


    # --- COMBOS ---
    {
        'name': 'Combo Tourbillon',
        'description': 'La sofisticación definitiva en un solo set. Combina una cadena de caída perfecta con una pieza complementaria seleccionada minuciosamente para lograr una armonía visual deslumbrante.',
        'category': 'combos',
        'category_label': 'Combo',
        'price': 187500.00,
        'image': '/static/images/combotourbillon.jpeg',
        'sizes': ['Único'],
        'stocks': [3],
    },
    {
        'name': 'Combo Triple GROUMET',
        'description': 'El set definitivo para los amantes de las joyas con personalidad. Un imponente conjunto que lleva el clásico estilo Grumet a su máximo nivel de ostentación, combinando tres piezas de brillo salvaje.',
        'category': 'combos',
        'category_label': 'Combo',
        'price': 187500.00,
        'image': '/static/images/combo-2.jpg',
        'sizes': ['Único'],
        'stocks': [3],
    },

    {
        'name': 'Combo Paris',
        'description': 'Un set exclusivo que combina piezas icónicas para crear un look incomparable con un toque de sofisticación parisina. Cada pieza ha sido seleccionada para complementar a la perfección, ofreciendo un equilibrio entre elegancia y modernidad.',
        'category': 'combos',
        'category_label': 'Combo',
        'price': 162500.00,
        'image': '/static/images/combopais.jpeg',
        'sizes': ['Único'],
        'stocks': [3],
    },

    {
        'name': 'Combo Juliana',
        'description': 'Algo mas simple pero elegante capaz de destacar en cualquier ocasión y ademas con una clase que desborda poder.',
        'category': 'combos',
        'category_label': 'Combo',
        'price': 162500.00,
        'image': '/static/images/combojuliana.jpeg',
        'sizes': ['Único'],
        'stocks': [3],
    },
]


def seed_products(force=False):
    """Carga el catálogo. Con force=True reemplaza todos los productos."""
    if force:
        ProductVariant.query.delete()
        Product.query.delete()
        db.session.commit()
    elif Product.query.count() > 0:
        return 0

    created = 0
    for item in INITIAL_PRODUCTS:
        product = Product(
            name=item['name'],
            description=item['description'],
            category=item['category'],
            category_label=item['category_label'],
            original_price=item['price'],
            price=round(item['price'] * (1 - DISCOUNT), 2),
            image=item['image'],
            active=True,
        )
        db.session.add(product)
        db.session.flush()

        stocks = item.get('stocks') or [10] * len(item['sizes'])
        for i, size in enumerate(item['sizes']):
            stock = stocks[i] if i < len(stocks) else 10
            db.session.add(
                ProductVariant(product_id=product.id, size=size, stock=stock)
            )
        created += 1

    db.session.commit()
    return created


def seed_admin(bcrypt):
    admin_password = os.environ.get('ADMIN_PASSWORD', 'admin1234')
    user = User.query.filter_by(email=ADMIN_EMAIL).first()
    if user:
        if not user.is_admin:
            user.is_admin = True
            db.session.commit()
        return False

    user = User(name=ADMIN_NAME, email=ADMIN_EMAIL, is_admin=True)
    user.set_password(bcrypt, admin_password)
    db.session.add(user)
    db.session.commit()
    return True


def sync_catalog(bcrypt):
    """Reemplaza el catálogo con INITIAL_PRODUCTS sin borrar usuarios ni pedidos."""
    db.create_all()
    products_added = seed_products(force=True)
    admin_added = seed_admin(bcrypt)
    return {
        'products_seeded': products_added,
        'users': User.query.count(),
        'products': Product.query.count(),
        'variants': ProductVariant.query.count(),
    }


def init_database(bcrypt, reset=False, sync_products=False):
    """Crea tablas y carga datos iniciales si están vacías."""
    if reset:
        db.drop_all()

    db.create_all()
    if sync_products:
        products_added = seed_products(force=True)
    else:
        products_added = seed_products()
    admin_added = seed_admin(bcrypt)

    return {
        'reset': reset,
        'sync_products': sync_products,
        'products_seeded': products_added,
        'admin_seeded': admin_added,
        'users': User.query.count(),
        'products': Product.query.count(),
        'variants': ProductVariant.query.count(),
    }
