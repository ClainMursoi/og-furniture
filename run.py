from app import create_app, db
from app.models.product import Product
from app.models.order import Order

app = create_app()

# Create tables automatically if they don't exist
with app.app_context():
    db.create_all()
    print("✅ Database tables created successfully!")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)