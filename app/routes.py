from flask import Blueprint, request, jsonify, redirect, url_for
from .models import Product
from . import db, logger  
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
    logger.log('INFO', 'Fetching all products')
    products = db.session.query(Product).all()
    logger.log('INFO', 'Products retrieved', count=len(products))
    return jsonify([product_to_dict(p) for p in products]), 200

@bp.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    logger.log('INFO', 'Fetching product', product_id=product_id)
    product = db.session.get(Product, product_id)
    if not product:
        logger.log('WARNING', 'Product not found', product_id=product_id)
        return jsonify({"error": "not found"}), 404
    return jsonify(product_to_dict(product)), 200

@bp.route("/products", methods=["POST"])
def create_product():
    data = request.json
    logger.log('INFO', 'Creating product', product_name=data.get('name'))
    
    try:
        p = Product(
            name=data.get("name"),
            description=data.get("description", ""),
            price=float(data.get("price", 0)),
            quantity=int(data.get("quantity", 0))
        )
        db.session.add(p)
        db.session.commit()
        
        logger.log('INFO', 'Product created', product_id=p.id, product_name=p.name)
        return jsonify(product_to_dict(p)), 201
        
    except Exception as e:
        logger.log('ERROR', 'Failed to create product', error=str(e))
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@bp.route("/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    data = request.json
    logger.log('INFO', 'Updating product', product_id=product_id)
    
    product = db.session.get(Product, product_id)
    if not product:
        logger.log('WARNING', 'Product not found for update', product_id=product_id)
        return jsonify({"error": "not found"}), 404
    
    try:
        for k in ["name", "description", "price", "quantity"]:
            if k in data:
                setattr(product, k, data[k])
        db.session.commit()
        
        logger.log('INFO', 'Product updated', product_id=product_id)
        return jsonify(product_to_dict(product)), 200
        
    except Exception as e:
        logger.log('ERROR', 'Failed to update product', product_id=product_id, error=str(e))
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@bp.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    logger.log('INFO', 'Deleting product', product_id=product_id)
    
    product = db.session.get(Product, product_id)
    if not product:
        logger.log('WARNING', 'Product not found for deletion', product_id=product_id)
        return jsonify({"error":"not found"}), 404
    
    try:
        db.session.delete(product)
        db.session.commit()
        
        logger.log('INFO', 'Product deleted', product_id=product_id)
        return "", 200
        
    except Exception as e:
        logger.log('ERROR', 'Failed to delete product', product_id=product_id, error=str(e))
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

@bp.route('/')
def home():
    return redirect(url_for('api.get_products'))

@bp.route("/admin/setup", methods=["POST"])
def admin_setup():
    from flask import current_app
    import sqlalchemy

    admin_token = request.headers.get("X-ADMIN-TOKEN")
    if admin_token != current_app.config.get("ADMIN_SECRET", "mysecret"):
        logger.log('WARNING', 'Unauthorized admin setup attempt', 
                   remote_addr=request.remote_addr)
        return jsonify({"error": "Unauthorized"}), 403

    try:
        logger.log('INFO', 'Starting database setup')
        
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
        
        logger.log('INFO', 'Database setup completed successfully')
        return jsonify({"message": " Database setup completed successfully!"}), 200

    except Exception as e:
        logger.log('ERROR', 'Database setup failed', error=str(e))
        db.session.rollback()
        return jsonify({"error": str(e)}), 500