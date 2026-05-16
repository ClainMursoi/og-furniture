from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from app import db
from app.models.product import Product
from app.models.order import Order

customer_bp = Blueprint('customer', __name__, url_prefix='/')


@customer_bp.route('/')
def index():
    products = Product.query.all()
    return render_template('customer/index.html', products=products)


@customer_bp.route('/cart')
def cart():
    return render_template('customer/cart.html')


@customer_bp.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            order = Order(
                customer_name=data['name'],
                phone=data['phone'],
                location=data['location'],
                items=data['items'],
                total_amount=data['total']
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