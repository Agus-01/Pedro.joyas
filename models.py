from datetime import datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(100), nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    phone         = db.Column(db.String(30))
    address       = db.Column(db.String(300))
    city          = db.Column(db.String(100))
    province      = db.Column(db.String(100))
    zip_code      = db.Column(db.String(20))
    is_admin      = db.Column(db.Boolean, default=False, nullable=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    orders = db.relationship('Order', backref='user', lazy=True)

    def set_password(self, bcrypt, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, bcrypt, password):
        return bcrypt.check_password_hash(self.password_hash, password)


class Product(db.Model):
    __tablename__ = 'products'

    id             = db.Column(db.Integer, primary_key=True)
    name           = db.Column(db.String(100), nullable=False)
    description    = db.Column(db.Text)
    category       = db.Column(db.String(50), nullable=False, index=True)
    category_label = db.Column(db.String(50), nullable=False)
    price          = db.Column(db.Float, nullable=False)
    original_price = db.Column(db.Float)
    image          = db.Column(db.String(300))
    active         = db.Column(db.Boolean, default=True, nullable=False)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    variants = db.relationship(
        'ProductVariant',
        backref='product',
        lazy=True,
        cascade='all, delete-orphan',
    )

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'category_label': self.category_label,
            'price': self.price,
            'original_price': self.original_price,
            'image': self.image,
            'active': self.active,
            'variants': [v.to_dict() for v in self.variants],
        }


class ProductVariant(db.Model):
    __tablename__ = 'product_variants'

    id         = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    size       = db.Column(db.String(50), nullable=False)
    stock      = db.Column(db.Integer, default=0, nullable=False)

    def to_dict(self):
        return {'id': self.id, 'size': self.size, 'stock': self.stock}


class Order(db.Model):
    __tablename__ = 'orders'

    id                = db.Column(db.String(20), primary_key=True)
    user_id           = db.Column(db.Integer, db.ForeignKey('users.id'))
    buyer_name        = db.Column(db.String(100), nullable=False)
    buyer_email       = db.Column(db.String(100), nullable=False)
    buyer_dni         = db.Column(db.String(20), nullable=False)
    buyer_phone       = db.Column(db.String(30))
    shipping_address  = db.Column(db.String(300))
    shipping_city     = db.Column(db.String(100))
    shipping_province = db.Column(db.String(100))
    shipping_zip      = db.Column(db.String(20))
    payment_method    = db.Column(db.String(50), default='mercadopago')
    items             = db.Column(db.JSON, nullable=False)
    total             = db.Column(db.Float, nullable=False)
    created_at        = db.Column(db.DateTime, default=datetime.utcnow)
    payment_status    = db.Column(db.String(50), default='pending')
    shipping_status   = db.Column(db.String(50), default='pending')
    mp_payment_id     = db.Column(db.String(100))
    notes             = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'buyer_name': self.buyer_name,
            'buyer_email': self.buyer_email,
            'buyer_phone': self.buyer_phone,
            'shipping_address': self.shipping_address,
            'shipping_city': self.shipping_city,
            'shipping_province': self.shipping_province,
            'payment_method': self.payment_method,
            'items': self.items,
            'total': self.total,
            'created_at': self.created_at.strftime('%d/%m/%Y %H:%M'),
            'payment_status': self.payment_status,
            'shipping_status': self.shipping_status,
        }
