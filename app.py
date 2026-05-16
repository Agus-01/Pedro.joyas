import os
import uuid
from flask import Flask, jsonify, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jewelry_store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

MP_ACCESS_TOKEN = os.environ.get('MP_ACCESS_TOKEN', '').strip()
MP_API_URL = 'https://api.mercadopago.com/checkout/preferences'

# Database model for orders
class Order(db.Model):
    id = db.Column(db.String(20), primary_key=True)
    buyer_name = db.Column(db.String(100), nullable=False)
    buyer_email = db.Column(db.String(100), nullable=False)
    buyer_dni = db.Column(db.String(20), nullable=False)
    payment_method = db.Column(db.String(50), default='mercadopago')
    items = db.Column(db.JSON, nullable=False)
    total = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    payment_status = db.Column(db.String(50), default='pending')

    def to_dict(self):
        return {
            'id': self.id,
            'buyer_name': self.buyer_name,
            'buyer_email': self.buyer_email,
            'buyer_dni': self.buyer_dni,
            'payment_method': self.payment_method,
            'items': self.items,
            'total': self.total,
            'created_at': self.created_at.isoformat(),
            'payment_status': self.payment_status
        }

# Create tables
with app.app_context():
    db.create_all()


products = [
    {'id': 1, 'category': 'anillos', 'category_label': 'Anillos', 'name': 'Anillo TODO PASA', 'description': 'Anillo premium con grabado distintivo.', 'price': 45000.00, 'image': '/static/images/ring-todo-pasa.jpg'},
    {'id': 2, 'category': 'anillos', 'category_label': 'Anillos', 'name': 'Anillo Oval', 'description': 'Anillo con diseño oval elegante.', 'price': 45000.00, 'image': '/static/images/ring-oval.jpg'},
    {'id': 3, 'category': 'anillos', 'category_label': 'Anillos', 'name': 'Anillo Corona', 'description': 'Anillo con estilo clásico y superior.', 'price': 45000.00, 'image': '/static/images/ring-crown.jpg'},
    {'id': 4, 'category': 'anillos', 'category_label': 'Anillos', 'name': 'Anillo Número 32', 'description': 'Anillo con diseño numerado de colección.', 'price': 45000.00, 'image': '/static/images/ring-32.jpg'},
    {'id': 5, 'category': 'anillos', 'category_label': 'Anillos', 'name': 'Anillo Stone', 'description': 'Anillo con piedra roja vibrante.', 'price': 65.00, 'image': '/static/images/ring-redstone.jpg'},
    {'id': 6, 'category': 'pulseras', 'category_label': 'Pulseras', 'name': 'Pulsera Dorada', 'description': 'Pulsera de estilo ancho y moderno.', 'price': 110000.00, 'image': '/static/images/pulsera-band.jpg'},
    {'id': 7, 'category': 'pulseras', 'category_label': 'Pulseras', 'name': 'Pulsera Lux', 'description': 'Pulsera sólida con acabado premium.', 'price': 110000.00, 'image': '/static/images/pulsera-band2.jpg'},
    {'id': 8, 'category': 'collares', 'category_label': 'Collares', 'name': 'Collar Trenza', 'description': 'Cadena trenzada con brillo dorado.', 'price': 120.00, 'image': '/static/images/necklace-1.jpg'},
    {'id': 9, 'category': 'collares', 'category_label': 'Collares', 'name': 'Collar Clásico', 'description': 'Cadena clásica para uso diario.', 'price': 140.00, 'image': '/static/images/necklace-2.jpg'},
    {'id': 10, 'category': 'combos', 'category_label': 'Combo', 'name': 'Combo Elegance', 'description': 'Set con cadena y pieza de lujo.', 'price': 220.00, 'image': '/static/images/combo-1.jpg'},
    {'id': 11, 'category': 'combos', 'category_label': 'Combo', 'name': 'Combo Brillante', 'description': 'Set especial con diseño distintivo.', 'price': 245.00, 'image': '/static/images/combo-2.jpg'}
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/products')
def api_products():
    return jsonify(products)

@app.route('/api/checkout', methods=['POST'])
def api_checkout():
    data = request.get_json() or {}
    buyer_name = data.get('buyerName', '').strip()
    buyer_email = data.get('buyerEmail', '').strip()
    buyer_dni = data.get('buyerDni', '').strip()
    payment_method = data.get('paymentMethod', 'mercadopago')
    items = data.get('items', [])

    if not buyer_name or not buyer_email or not buyer_dni or not items:
        return jsonify({'message': 'Datos incompletos para procesar la compra.'}), 400

    order_id = uuid.uuid4().hex[:10]
    total = sum(item.get('unit_price', 0) * item.get('quantity', 1) for item in items)
    prepared_items = [
        {
            'title': item['title'],
            'quantity': item['quantity'],
            'unit_price': item['unit_price'],
            'total': item['unit_price'] * item['quantity']
        }
        for item in items
    ]

    # Create and save order to database
    order = Order(
        id=order_id,
        buyer_name=buyer_name,
        buyer_email=buyer_email,
        buyer_dni=buyer_dni,
        payment_method=payment_method,
        items=prepared_items,
        total=total,
        payment_status='pending'
    )
    
    try:
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error al guardar la orden: {str(e)}'}), 500

    invoice_url = url_for('invoice', order_id=order_id, _external=True)

    if payment_method == 'mercadopago':
        if not MP_ACCESS_TOKEN:
            return jsonify({'message': 'No se encontró la variable MP_ACCESS_TOKEN en el servidor.'}), 500

        preference = {
            'payer': {
                'name': buyer_name,
                'email': buyer_email,
                'identification': {
                    'type': 'DNI',
                    'number': buyer_dni
                }
            },
            'items': [
                {
                    'title': item['title'],
                    'quantity': item['quantity'],
                    'unit_price': item['unit_price']
                } for item in items
            ],
            'external_reference': order_id,
            'back_urls': {
                'success': invoice_url,
                'pending': invoice_url,
                'failure': invoice_url
            },
            'auto_return': 'approved'
        }

        response = requests.post(
            MP_API_URL,
            headers={'Authorization': f'Bearer {MP_ACCESS_TOKEN}'},
            json=preference,
            timeout=15
        )

        if response.status_code != 201 and response.status_code != 200:
            return jsonify({'message': 'Error al crear la preferencia de Mercado Pago.'}), 502

        payment_data = response.json()
        return jsonify({
            'payment_url': payment_data.get('init_point'),
            'invoice_url': invoice_url,
            'order_id': order_id
        })

    return jsonify({
        'payment_url': invoice_url,
        'invoice_url': invoice_url,
        'order_id': order_id
    })

@app.route('/factura/<order_id>')
def invoice(order_id):
    order = Order.query.get(order_id)
    if not order:
        return 'Orden no encontrada', 404
    return render_template('invoice.html', order=order)

@app.route('/usuarios', methods=['GET'])
def get_usuarios():
    usuarios = [
        {'id': 1, 'nombre': 'Alice'},
        {'id': 2, 'nombre': 'Bob'},
        {'id': 3, 'nombre': 'Carlos'}
    ]
    return jsonify({'usuarios': usuarios})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
