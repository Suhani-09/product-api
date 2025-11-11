from flask import Blueprint, request, jsonify, redirect, url_for
from .models import Product
from . import db
import os

bp = Blueprint('api', __name__)

def product_to_dict(p):
    return {
        "id": p.id,
        "name": p.name,
        "description": p.description,
        "price": p.price,
        "quantity": p.quantity,
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "updated_at": p.updated_at.isoformat() if p.updated_at else None,
    }

@bp.route("/products", methods=["GET"])
def get_products():
    products = db.session.query(Product).all()
    return jsonify([product_to_dict(p) for p in products]), 200

@bp.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({"error": "not found"}), 404
    return jsonify(product_to_dict(product)), 200

@bp.route("/products", methods=["POST"])
def create_product():
    data = request.json
    p = Product(
        name=data.get("name"),
        description=data.get("description", ""),
        price=float(data.get("price", 0)),
        quantity=int(data.get("quantity", 0))
    )
    db.session.add(p)
    db.session.commit()
    return jsonify(product_to_dict(p)), 201

@bp.route("/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    data = request.json
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({"error": "not found"}), 404
    for k in ["name", "description", "price", "quantity"]:
        if k in data:
            setattr(product, k, data[k])
    db.session.commit()
    return jsonify(product_to_dict(product)), 200

@bp.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({"error":"not found"}), 404
    db.session.delete(product)
    db.session.commit()
    return "", 200

@bp.route('/')
def home():
    return redirect(url_for('api.get_products'))

@bp.route("/admin/setup", methods=["POST"])
def admin_setup():
    from flask import current_app
    import sqlalchemy

    admin_token = request.headers.get("X-ADMIN-TOKEN")
    if admin_token != current_app.config.get("ADMIN_SECRET", "mysecret"):
        return jsonify({"error": "Unauthorized"}), 403

    try:
        db.create_all()

        db.session.execute(sqlalchemy.text("""
            CREATE OR REPLACE FUNCTION update_timestamp()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = NOW();
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """))

       
        db.session.execute(sqlalchemy.text("""
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM information_schema.tables WHERE table_name = 'product'
                ) THEN
                    DROP TRIGGER IF EXISTS set_updated_at ON product;
                    CREATE TRIGGER set_updated_at
                    BEFORE UPDATE ON product
                    FOR EACH ROW
                    EXECUTE FUNCTION update_timestamp();
                END IF;
            END;
            $$;
        """))

        db.session.commit()
        return jsonify({"message": "✅ Database setup completed successfully!"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
