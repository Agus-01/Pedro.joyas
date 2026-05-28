import os
import uuid
from flask import Flask, jsonify, render_template, request, url_for, redirect, session, flash
from flask_mail import Mail, Message
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from functools import wraps
import requests
from dotenv import load_dotenv

from database import DISCOUNT, init_database
from models import Order, Product, ProductVariant, User, db

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'pedro-joyas-secret-2026')

# Database
# Por esta configuración inteligente:
db_url = os.environ.get('DATABASE_URL', 'sqlite:///jewelry_store.db')
if db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Auth
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Email
app.config['MAIL_SERVER']         = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT']           = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS']        = True
app.config['MAIL_USERNAME']       = os.environ.get('MAIL_USERNAME', '')
app.config['MAIL_PASSWORD']       = os.environ.get('MAIL_PASSWORD', '')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME', '')
mail = Mail(app)

MP_ACCESS_TOKEN = os.environ.get('MP_ACCESS_TOKEN', '').strip()
MP_API_URL      = 'https://api.mercadopago.com/checkout/preferences'
ALIAS_CBU       = os.environ.get('ALIAS_CBU', 'pedro.joyas')
WHATSAPP_NUMBER = os.environ.get('WHATSAPP_NUMBER', '5491162125672')
OWNER_EMAIL     = os.environ.get('OWNER_EMAIL', 'Pedro.joyaas@gmail.com')
ADMIN_PASSWORD  = os.environ.get('ADMIN_PASSWORD', 'admin1234')

# =========================
#   AUTH
# =========================

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


with app.app_context():
    init_database(bcrypt)


# =========================
#   RUTAS PUBLICAS
# =========================

@app.route('/')
def home():
    return render_template('index.html', user=current_user)


@app.route('/api/products')
def api_products():
    products = Product.query.filter_by(active=True).all()
    return jsonify([p.to_dict() for p in products])


@app.route('/api/checkout', methods=['POST'])
def api_checkout():
    data              = request.get_json() or {}
    buyer_name        = data.get('buyerName', '').strip()
    buyer_email       = data.get('buyerEmail', '').strip()
    buyer_dni         = data.get('buyerDni', '').strip()
    buyer_phone       = data.get('buyerPhone', '').strip()
    shipping_address  = data.get('shippingAddress', '').strip()
    shipping_city     = data.get('shippingCity', '').strip()
    shipping_province = data.get('shippingProvince', '').strip()
    shipping_zip      = data.get('shippingZip', '').strip()
    payment_method    = data.get('paymentMethod', 'mercadopago')
    items             = data.get('items', [])

    if not buyer_name or not buyer_email or not buyer_dni or not items:
        return jsonify({'message': 'Datos incompletos.'}), 400

    # Descontar stock
    for item in items:
        variant_id = item.get('variant_id')
        if variant_id:
            variant = ProductVariant.query.get(variant_id)
            if variant:
                if variant.stock < item.get('quantity', 1):
                    return jsonify({'message': f'Stock insuficiente para {item["title"]}'}), 400
                variant.stock -= item.get('quantity', 1)

    order_id = uuid.uuid4().hex[:10].upper()
    total = sum(item.get('unit_price', 0) * item.get('quantity', 1) for item in items)
    prepared_items = [
        {'title': i['title'], 'quantity': i['quantity'], 'unit_price': i['unit_price'], 'total': i['unit_price'] * i['quantity']}
        for i in items
    ]

    order = Order(
        id=order_id,
        user_id=current_user.id if current_user.is_authenticated else None,
        buyer_name=buyer_name,
        buyer_email=buyer_email,
        buyer_dni=buyer_dni,
        buyer_phone=buyer_phone,
        shipping_address=shipping_address,
        shipping_city=shipping_city,
        shipping_province=shipping_province,
        shipping_zip=shipping_zip,
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
            return jsonify({'message': 'Token de Mercado Pago no configurado.'}), 500

        success_url = invoice_url + '?status=approved'
        pending_url = invoice_url + '?status=pending'
        failure_url = invoice_url + '?status=failure'
        is_local_url = success_url.startswith('http://127.0.0.1') or success_url.startswith('http://localhost')

        preference = {
            'payer': {
                'name': buyer_name,
                'email': buyer_email,
                'identification': {'type': 'DNI', 'number': buyer_dni},
                'phone': {'number': buyer_phone}
            },
            'items': [
                {'title': i['title'], 'quantity': i['quantity'], 'unit_price': float(i['unit_price']), 'currency_id': 'ARS'}
                for i in prepared_items
            ],
            'shipments': {
                'receiver_address': {
                    'street_name': shipping_address,
                    'city_name': shipping_city,
                    'state_name': shipping_province,
                    'zip_code': shipping_zip
                }
            } if shipping_address else {},
            'external_reference': order_id,
            'back_urls': {
                'success': success_url,
                'pending': pending_url,
                'failure': failure_url
            },
            'statement_descriptor': 'Pedro Joyas',
            'payment_methods': {'installments': 12}
        }

        # Mercado Pago rechaza auto_return=approved cuando se usan URLs locales.
        # En producción (Render) sí conviene activarlo.
        if not is_local_url:
            preference['auto_return'] = 'approved'
            preference['notification_url'] = url_for('mp_webhook', _external=True)

        resp = requests.post(MP_API_URL, headers={'Authorization': f'Bearer {MP_ACCESS_TOKEN}'}, json=preference, timeout=15)
        if resp.status_code not in (200, 201):
            try:
                mp_error = resp.json()
            except ValueError:
                mp_error = {'raw': resp.text[:300]}
            return jsonify({
                'message': 'Error al crear preferencia de Mercado Pago.',
                'mp_status': resp.status_code,
                'mp_error': mp_error
            }), 502

        payment_url = resp.json().get('init_point')
        _notify_owner(order, payment_url)
        return jsonify({'payment_url': payment_url, 'invoice_url': invoice_url, 'order_id': order_id})

    _notify_owner(order, None, alias_info={'alias': ALIAS_CBU, 'amount': total, 'reference': order_id})
    return jsonify({'payment_url': None, 'invoice_url': invoice_url, 'order_id': order_id, 'alias': ALIAS_CBU, 'transfer_amount': total})


@app.route('/api/mp-webhook', methods=['POST'])
def mp_webhook():
    data = request.get_json() or {}
    if data.get('type') == 'payment':
        payment_id = str(data.get('data', {}).get('id', ''))
        if payment_id and MP_ACCESS_TOKEN:
            resp = requests.get(f'https://api.mercadopago.com/v1/payments/{payment_id}', headers={'Authorization': f'Bearer {MP_ACCESS_TOKEN}'}, timeout=10)
            if resp.status_code == 200:
                pdata    = resp.json()
                order_id = pdata.get('external_reference', '')
                status   = pdata.get('status', 'pending')
                order    = Order.query.get(order_id)
                if order:
                    order.payment_status = status
                    order.mp_payment_id  = payment_id
                    db.session.commit()
                    if status == 'approved':
                        _notify_owner(order, paid=True)
    return jsonify({'status': 'ok'}), 200


@app.route('/factura/<order_id>')
def invoice(order_id):
    order = Order.query.get(order_id)
    if not order:
        return 'Orden no encontrada', 404
    return render_template('invoice.html', order=order)


# =========================
#   AUTH CLIENTES
# =========================

@app.route('/registro', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        if User.query.filter_by(email=email).first():
            return render_template('auth.html', error='El email ya está registrado.', mode='register')
        user = User(name=name, email=email)
        user.set_password(bcrypt, password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('home'))
    return render_template('auth.html', mode='register')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        user     = User.query.filter_by(email=email).first()
        if user and user.check_password(bcrypt, password):
            login_user(user)
            return redirect(request.args.get('next') or url_for('home'))
        return render_template('auth.html', error='Email o contraseña incorrectos.', mode='login')
    return render_template('auth.html', mode='login')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/api/me')
def api_me():
    if current_user.is_authenticated:
        return jsonify({
            'logged': True,
            'name': current_user.name,
            'email': current_user.email,
            'phone': current_user.phone,
            'address': current_user.address,
            'city': current_user.city,
            'province': current_user.province,
            'zip_code': current_user.zip_code
        })
    return jsonify({'logged': False})


# =========================
#   PANEL ADMIN
# =========================

@app.route('/admin')
@admin_required
def admin_dashboard():
    orders   = Order.query.order_by(Order.created_at.desc()).all()
    products = Product.query.order_by(Product.created_at.desc()).all()
    users    = User.query.filter_by(is_admin=False).order_by(User.created_at.desc()).all()
    stats = {
        'total_orders': len(orders),
        'paid_orders': len([o for o in orders if o.payment_status == 'approved']),
        'total_revenue': sum(o.total for o in orders if o.payment_status == 'approved'),
        'total_products': len(products),
        'total_users': len(users)
    }
    return render_template('admin/dashboard.html', orders=orders, products=products, users=users, stats=stats)


@app.route('/admin/producto/nuevo', methods=['GET', 'POST'])
@admin_required
def admin_product_new():
    if request.method == 'POST':
        sizes  = [s.strip() for s in request.form.get('sizes', '').split(',') if s.strip()]
        stocks = [int(s) for s in request.form.get('stocks', '0').split(',') if s.strip().isdigit()]
        price  = float(request.form.get('price', 0))
        product = Product(
            name=request.form.get('name'),
            description=request.form.get('description'),
            category=request.form.get('category'),
            category_label=request.form.get('category_label'),
            original_price=price,
            price=round(price * (1 - DISCOUNT), 2),
            image=request.form.get('image'),
            active=True
        )
        db.session.add(product)
        db.session.flush()
        for i, size in enumerate(sizes):
            stock = stocks[i] if i < len(stocks) else 0
            db.session.add(ProductVariant(product_id=product.id, size=size, stock=stock))
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/product_form.html', product=None)


@app.route('/admin/producto/<int:pid>/editar', methods=['GET', 'POST'])
@admin_required
def admin_product_edit(pid):
    product = Product.query.get_or_404(pid)
    if request.method == 'POST':
        product.name           = request.form.get('name')
        product.description    = request.form.get('description')
        product.category       = request.form.get('category')
        product.category_label = request.form.get('category_label')
        product.original_price = float(request.form.get('price', 0))
        product.price          = round(product.original_price * (1 - DISCOUNT), 2)
        product.image          = request.form.get('image')
        product.active         = request.form.get('active') == 'on'

        # Actualizar variantes
        for variant in product.variants:
            new_stock = request.form.get(f'stock_{variant.id}')
            if new_stock is not None:
                variant.stock = int(new_stock)

        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/product_form.html', product=product)


@app.route('/admin/producto/<int:pid>/eliminar', methods=['POST'])
@admin_required
def admin_product_delete(pid):
    product = Product.query.get_or_404(pid)
    product.active = False
    db.session.commit()
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/orden/<order_id>/estado', methods=['POST'])
@admin_required
def admin_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    order.shipping_status = request.form.get('shipping_status', order.shipping_status)
    order.payment_status  = request.form.get('payment_status', order.payment_status)
    order.notes           = request.form.get('notes', order.notes)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        from database import ADMIN_EMAIL

        password = request.form.get('password', '').strip()
        user = User.query.filter_by(is_admin=True).first()

        valid = False
        if user and user.check_password(bcrypt, password):
            valid = True
        elif password == ADMIN_PASSWORD.strip():
            valid = True
            if not user:
                user = User(name='Administrador', email=ADMIN_EMAIL, is_admin=True)
                user.set_password(bcrypt, password)
                db.session.add(user)
                db.session.commit()
            elif not user.check_password(bcrypt, password):
                user.set_password(bcrypt, password)
                db.session.commit()

        if valid and user:
            login_user(user)
            return redirect(url_for('admin_dashboard'))

        return render_template('admin/login.html', error='Contraseña incorrecta.')
    return render_template('admin/login.html')


# =========================
#   NOTIFICACIONES
# =========================
# =========================
#   NOTIFICACIONES
# =========================

def _notify_owner(order, payment_url=None, alias_info=None, paid=False):
    items_text = '\n'.join(f"  - {i['title']} x{i['quantity']} = ${i['total']:,.0f}" for i in order.items)
    address = f"{order.shipping_address}, {order.shipping_city}, {order.shipping_province}" if order.shipping_address else 'No especificada'

    # 1. Si el pago está APROBADO, armamos la Factura HTML prolija para el cliente y el dueño
    if paid:
        subject = f'✅ Comprobante de Compra #{order.id} - Pedro Joyas'
        
        # Construimos las filas de la tabla de productos dinámicamente
        tabla_productos_html = ""
        for i in order.items:
            tabla_productos_html += f"""
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #eee;">{i['title']} x{i['quantity']}</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: right;">${i['total']:,.2f}</td>
            </tr>
            """

        # Diseño HTML de la Factura
        html_body = f"""
        <div style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; max-width: 600px; margin: auto; border: 1px solid #e4e4e4; padding: 30px; border-radius: 8px; color: #333;">
            <div style="text-align: center; margin-bottom: 20px;">
                <h1 style="color: #d4af37; margin: 0; font-size: 28px; letter-spacing: 1px;">PEDRO JOYAS</h1>
                <p style="font-size: 12px; color: #777; margin: 5px 0 0 0;">Comprobante Oficial de Pago</p>
            </div>
            
            <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
            
            <p style="font-size: 15px;">¡Hola <b>{order.buyer_name}</b>! Tu pago ha sido procesado con éxito. A continuación te dejamos el detalle de tu compra:</p>
            
            <div style="background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin: 20px 0; font-size: 14px;">
                <b>Número de Orden:</b> #{order.id}<br>
                <b>DNI:</b> {order.buyer_dni}<br>
                <b>Teléfono:</b> {order.buyer_phone}<br>
                <b>Dirección de Envío:</b> {address}<br>
                <b>Método de Pago:</b> Mercado Pago (Aprobado)
            </div>
            
            <h3 style="color: #444; border-bottom: 2px solid #d4af37; padding-bottom: 5px; margin-top: 25px;">Detalle del Pedido</h3>
            <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                <thead>
                    <tr style="background-color: #f5f5f5;">
                        <th style="padding: 10px; text-align: left; font-weight: bold;">Producto</th>
                        <th style="padding: 10px; text-align: right; font-weight: bold;">Total</th>
                    </tr>
                </thead>
                <tbody>
                    {tabla_productos_html}
                </tbody>
            </table>
            
            <div style="text-align: right; margin-top: 20px; font-size: 18px; font-weight: bold; color: #111;">
                Total Abonado: <span style="color: #d4af37;">${order.total:,.2f}</span>
            </div>
            
            <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0 20px 0;">
            
            <p style="font-size: 12px; color: #999; text-align: center; line-height: 1.5; margin: 0;">
                Gracias por confiar en nosotros.<br>
                Si tenés alguna duda con tu pedido, escribinos directamente respondiendo a este correo.<br>
                <b>Pedro Joyas © 2026</b>
            </p>
        </div>
        """
        
        # Enviamos el mail con el HTML renderizado al cliente y a vos (copia)
        if app.config['MAIL_USERNAME']:
            try:
                msg = Message(subject, recipients=[order.buyer_email, OWNER_EMAIL])
                msg.html = html_body
                mail.send(msg)
            except Exception as e:
                print(f"Error enviando mail HTML: {str(e)}")

    # 2. Casos de órdenes pendientes (Texto común clásico como tenías antes)
    else:
        if alias_info:
            subject = f'🛒 Nueva orden #{order.id} - Transferencia - {order.buyer_name}'
            body = f'Nueva orden por transferencia\n\nOrden: #{order.id}\nCliente: {order.buyer_name}\nEmail: {order.buyer_email}\nTeléfono: {order.buyer_phone}\nEnvío: {address}\n\nProductos:\n{items_text}\n\nTOTAL: ${order.total:,.0f}\nAlias: {alias_info["alias"]}\nReferencia: {alias_info["reference"]}'
        else:
            subject = f'🛒 Nueva orden #{order.id} - MP - {order.buyer_name}'
            body = f'Nueva orden con Mercado Pago\n\nOrden: #{order.id}\nCliente: {order.buyer_name}\nEmail: {order.buyer_email}\nTeléfono: {order.buyer_phone}\nEnvío: {address}\n\nProductos:\n{items_text}\n\nTOTAL: ${order.total:,.0f}\nLink MP: {payment_url}'

        if OWNER_EMAIL and app.config['MAIL_USERNAME']:
            try:
                mail.send(Message(subject, recipients=[OWNER_EMAIL], body=body))
            except Exception:
                pass

    # Mantener el envío de logs a WhatsApp que ya tenías
    wa_body = f'PAGO APROBADO\n\nOrden: #{order.id}\nCliente: {order.buyer_name}\nTOTAL: ${order.total:,.0f}' if paid else body
    wa_text = wa_body.replace('\n', '%0A').replace(' ', '%20')[:1000]
    print(f'WA_LINK: https://wa.me/{WHATSAPP_NUMBER}?text={wa_text}')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
