from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from app import db
from app.models.product import Product
from app.models.order import Order
import os

customer_bp = Blueprint('customer', __name__, url_prefix='/')


@customer_bp.route('/')
def index():
    products = Product.query.all()
    return render_template('customer/index.html', products=products)


@customer_bp.route('/cart')
def cart():
    return render_template('customer/cart.html')


@customer_bp.route('/test-static')
def test_static():
    """Debug endpoint to test static file serving"""
    from flask import current_app
    uploads = []
    upload_folder = current_app.config.get('UPLOAD_FOLDER', '')
    if os.path.exists(upload_folder):
        uploads = os.listdir(upload_folder)
    
    return jsonify({
        'static_folder': current_app.static_folder,
        'static_url_path': current_app.static_url_path,
        'upload_folder': upload_folder,
        'uploads_exist': os.path.exists(upload_folder),
        'files_in_uploads': uploads[:10],
        'test_url': url_for('static', filename='uploads/test.jpg')
    })


@customer_bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        try:
            data = request.get_json()
            items = data.get('items', [])
            if not isinstance(items, list) or len(items) == 0:
                raise ValueError('Cart is empty or invalid.')

            requested_quantities = {}
            for item in items:
                item_id = int(item.get('id', 0))
                quantity = int(item.get('quantity', 1))
                if item_id <= 0 or quantity < 1:
                    raise ValueError('Invalid cart item.')
                requested_quantities[item_id] = requested_quantities.get(item_id, 0) + quantity

            products = Product.query.filter(Product.id.in_(requested_quantities.keys())).all()
            if len(products) != len(requested_quantities):
                raise ValueError('One or more products are no longer available.')

            for product in products:
                requested = requested_quantities.get(product.id, 0)
                if requested > product.stock:
                    raise ValueError(f'Only {product.stock} item(s) of "{product.name}" are available.')

            # Deduct stock and save the order
            for product in products:
                product.stock -= requested_quantities[product.id]

            order = Order(
                customer_name=data['name'],
                phone=data['phone'],
                location=data['location'],
                items=items,
                total_amount=float(data['total'])
            )

            db.session.add(order)
            db.session.commit()

            return jsonify({
                "success": True,
                "order_number": order.order_number
            })

        except Exception as e:
            db.session.rollback()
            return jsonify({
                "success": False,
                "error": str(e)
            }), 400
    
    # GET request - show checkout page
    return render_template('customer/checkout.html')


@customer_bp.route('/order_success')
def order_success():
    order_number = request.args.get('order_number')
    return render_template('customer/order_success.html', order_number=order_number)


@customer_bp.route('/track', methods=['GET', 'POST'])
def track():
    if request.method == 'POST':
        order_number = request.form.get('order_number')
        order = Order.query.filter_by(order_number=order_number).first()
        return render_template('customer/track.html', order=order, searched=True)
    
    return render_template('customer/track.html', searched=False)


# Optional: Clear cart (for testing)
@customer_bp.route('/clear-cart')
def clear_cart():
    session.pop('cart', None)
    return redirect(url_for('customer.cart'))