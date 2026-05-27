import os

from models import Product, ProductVariant, User, db

DISCOUNT = 0.20

ADMIN_EMAIL = 'admin@pedrojoyas.com'
ADMIN_NAME = 'Administrador'

# Productos iniciales (imágenes que ya tenés en static/images)
INITIAL_PRODUCTS = [
    {
        'name': 'Anillo TODO PASA',
        'description': 'Anillo premium con grabado distintivo.',
        'category': 'anillos',
        'category_label': 'Anillos',
        'price': 45000.00,
        'image': '/static/images/anillo1.jpeg',
        'sizes': ['12', '14', '16', '18'],
        'stocks': [10, 10, 10, 10],
    },
    {
        'name': 'Anillo Colección',
        'description': 'Diseño exclusivo de la colección Pedro Joyas.',
        'category': 'anillos',
        'category_label': 'Anillos',
        'price': 45000.00,
        'image': '/static/images/anillos.jpeg',
        'sizes': ['12', '14', '16', '18'],
        'stocks': [8, 8, 8, 8],
    },

    {
        'name': 'Anillo ROLEX grabado',
        'description': 'Diseño simple de la colección Pedro Joyas.',
        'category': 'anillos',
        'category_label': 'Anillos',
        'price': 45000.00,
        'image': '/static/images/anillo3.jpg',
        'sizes': ['12', '14', '16', '18'],
        'stocks': [8, 8, 8, 8],
    },

    {
        'name': 'Anillo Trebol',
        'description': 'Diseño de trebol de la colección Pedro Joyas.',
        'category': 'anillos',
        'category_label': 'Anillos',
        'price': 45000.00,
        'image': '/static/images/anillo4.jpg',
        'sizes': ['12', '14', '16', '18'],
        'stocks': [8, 8, 8, 8],
    },

    {
        'name': 'Pulsera cedusa',
        'description': 'Pulsera de estilo ancho y moderno.',
        'category': 'pulseras',
        'category_label': 'Pulseras',
        'price': 95000.00,
        'image': '/static/images/WhatsApp Image 2026-05-23 at 20.25.57.jpeg',
        'sizes': ['S', 'M', 'L'],
        'stocks': [5, 10, 5],
    },
    {
        'name': 'Pulsera peruano',
        'description': 'Pulsera sólida con acabado premium.',
        'category': 'pulseras',
        'category_label': 'Pulseras',
        'price': 60000.00,
        'image': '/static/images/peruana.jpeg',
        'sizes': ['S', 'M', 'L'],
        'stocks': [6, 6, 6],
    },

    {
        'name': 'Pulsera Juliana',
        'description': 'Pulsera sólida con acabado premium.',
        'category': 'pulseras',
        'category_label': 'Pulseras',
        'price': 50000.00,
        'image': '/static/images/juliana.jpeg',
        'sizes': ['S', 'M', 'L'],
        'stocks': [6, 6, 6],
    },

    {
        'name': 'Pulsera Tourbillon',
        'description': 'Pulsera sólida con acabado premium.',
        'category': 'pulseras',
        'category_label': 'Pulseras',
        'price': 60000.00,
        'image': '/static/images/tourbillon.jpeg',
        'sizes': ['S', 'M', 'L'],
        'stocks': [6, 6, 6],
    },

    {
        'name': 'Collar TORBILLON',
        'description': 'Cadena trenzada con brillo dorado.',
        'category': 'collares',
        'category_label': 'Collares',
        'price': 110000.00,
        'image': '/static/images/cadenatourbillon.jpeg',
        'sizes': ['40cm', '45cm', '50cm'],
        'stocks': [4, 4, 4],
    },

    {
        'name': 'Collar JULIANA',
        'description': 'Cadena trenzada con brillo dorado.',
        'category': 'collares',
        'category_label': 'Collares',
        'price': 90000.00,
        'image': '/static/images/cadenajuliana.jpeg',
        'sizes': ['40cm', '45cm', '50cm'],
        'stocks': [4, 4, 4],
    },

    {
        'name': 'Collar GRUMET',
        'description': 'Cadena trenzada con brillo dorado.',
        'category': 'collares',
        'category_label': 'Collares',
        'price': 110000.00,
        'image': '/static/images/cadenagrumet.jpeg',
        'sizes': ['40cm', '45cm', '50cm'],
        'stocks': [4, 4, 4],
    }, 

    {
        'name': 'Collar FORCET',
        'description': 'Cadena trenzada con brillo dorado.',
        'category': 'collares',
        'category_label': 'Collares',
        'price': 90000.00,
        'image': '/static/images/cadenaforcet.jpeg',
        'sizes': ['40cm', '45cm', '50cm'],
        'stocks': [4, 4, 4],
    },

    {
        'name': 'Combo Elegance',
        'description': 'Set con cadena y pieza de lujo.',
        'category': 'combos',
        'category_label': 'Combo',
        'price': 220000.00,
        'image': '/static/images/WhatsApp Image 2026-05-23 at 20.26.05 (1).jpeg',
        'sizes': ['Único'],
        'stocks': [3],
    },

    {
        'name': 'Combo Triple GRUMET',
        'description': 'Set con cadena y pieza de lujo.',
        'category': 'combos',
        'category_label': 'Combo',
        'price': 150000.00,
        'image': '/static/images/combo-2.jpeg',
        'sizes': ['Único'],
        'stocks': [3],
    },
]


def seed_products():
    if Product.query.count() > 0:
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


def init_database(bcrypt, reset=False):
    """Crea tablas y carga datos iniciales si están vacías."""
    if reset:
        db.drop_all()

    db.create_all()
    products_added = seed_products()
    admin_added = seed_admin(bcrypt)

    return {
        'reset': reset,
        'products_seeded': products_added,
        'admin_seeded': admin_added,
        'users': User.query.count(),
        'products': Product.query.count(),
        'variants': ProductVariant.query.count(),
    }
