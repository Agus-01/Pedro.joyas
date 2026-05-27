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
        'name': 'Pulsera Dorada',
        'description': 'Pulsera de estilo ancho y moderno.',
        'category': 'pulseras',
        'category_label': 'Pulseras',
        'price': 110000.00,
        'image': '/static/images/WhatsApp Image 2026-05-23 at 20.25.57.jpeg',
        'sizes': ['S', 'M', 'L'],
        'stocks': [5, 10, 5],
    },
    {
        'name': 'Pulsera Lux',
        'description': 'Pulsera sólida con acabado premium.',
        'category': 'pulseras',
        'category_label': 'Pulseras',
        'price': 110000.00,
        'image': '/static/images/WhatsApp Image 2026-05-23 at 20.26.05.jpeg',
        'sizes': ['S', 'M', 'L'],
        'stocks': [6, 6, 6],
    },
    {
        'name': 'Collar Trenza',
        'description': 'Cadena trenzada con brillo dorado.',
        'category': 'collares',
        'category_label': 'Collares',
        'price': 120000.00,
        'image': '/static/images/WhatsApp Image 2026-05-23 at 20.25.56.jpeg',
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
