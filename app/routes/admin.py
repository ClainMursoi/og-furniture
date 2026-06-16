from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from app import db
from app.models.product import Product
from app.models.order import Order
from werkzeug.utils import secure_filename
from uuid import uuid4
import os

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Hardcoded Admin Password (Change this in production)
ADMIN_PASSWORD = "admin123"


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash("Login successful!", "success")
            return redirect(url_for('admin.dashboard'))
        else:
            flash("Incorrect password!", "danger")
    return render_template('admin/login.html')


@admin_bp.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    flash("Logged out successfully.", "info")
    return redirect(url_for('admin.login'))


@admin_bp.route('/dashboard')
def dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    total_orders = Order.query.count()
    total_products = Product.query.count()
    
    return render_template('admin/dashboard.html', 
                         orders=recent_orders,
                         total_orders=total_orders,
                         total_products=total_products)


@admin_bp.route('/orders')
def orders():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=orders)


@admin_bp.route('/products', methods=['GET', 'POST'])
def products():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    
    if request.method == 'POST':
        try:
            # Handle multiple images
            image_files = request.files.getlist('images')
            image_urls = []
            
            upload_folder = current_app.config.get('UPLOAD_FOLDER') or os.path.join(current_app.static_folder, 'uploads')
            if not os.path.isabs(upload_folder):
                upload_folder = os.path.abspath(upload_folder)
            os.makedirs(upload_folder, exist_ok=True)

            for image in image_files:
                if image and image.filename:
                    filename = secure_filename(image.filename)
                    unique_filename = f"{uuid4().hex}_{filename}"
                    upload_path = os.path.join(upload_folder, unique_filename)
                    image.save(upload_path)
                    image_urls.append(unique_filename)
            
            # Limit to maximum 4 images
            image_urls = image_urls[:4]
            
            product = Product(
                name=request.form['name'],
                price=float(request.form['price']),
                description=request.form['description'],
                category=request.form.get('category', ''),
                images=image_urls,
                stock=int(request.form.get('stock', 10))
            )
            
            db.session.add(product)
            db.session.commit()
            flash("Product added successfully with images!", "success")
            
        except Exception as e:
            db.session.rollback()
            flash(f"Error adding product: {str(e)}", "danger")
    
    products = Product.query.all()
    return render_template('admin/products.html', products=products)


@admin_bp.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin.login'))
    
    try:
        product = Product.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()
        flash(f"Product '{product.name}' deleted successfully.", "success")
    except Exception as e:
        db.session.rollback()
        flash("Error deleting product.", "danger")
    
    return redirect(url_for('admin.products'))


@admin_bp.route('/update_status/<int:order_id>', methods=['POST'])
def update_status(order_id):
    if not session.get('admin_logged_in'):
        flash("Please login first", "danger")
        return redirect(url_for('admin.login'))
    
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    
    if new_status in ['Pending', 'Paid', 'Processing', 'Shipped', 'Delivered']:
        order.status = new_status
        db.session.commit()
        flash(f"Order status updated to {new_status}", "success")
    else:
        flash("Invalid status selected", "danger")
    
    return redirect(url_for('admin.orders'))