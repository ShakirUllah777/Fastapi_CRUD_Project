from fastapi import FastAPI, HTTPException , Depends
from model import Product
from database import session , engine
import database_model
from sqlalchemy.orm import Session


app = FastAPI()

database_model.Base.metadata.create_all(bind=engine)

products= [
    Product(id=1, name="Laptop", description="Best laptop in Pakistan", price=22),
    Product(id=2, name="Phone", description="Best phone in Pakistan", price=22),
    Product(id=3, name="Windows Laptop", description="Best windows laptop", price=22),
]

def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()

def init_db():
    db = session()
    count = db.query(database_model.Product).count
    if count == 0:
        for product in products:
            db.add(database_model.Product(**product.model_dump()))
        db.commit()

init_db()

# Get all products
@app.get("/products")
def get_all_products(db: Session = Depends(get_db)):
    db_products = db.query(database_model.Product).all()
    return db_products



# Get product by ID
@app.get("/products/{product_id}")
def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
    db_product = db.query(database_model.Product).filter(database_model.Product.id == product_id).first()
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product


# Add new product
@app.post("/products")
def add_product(product: Product, db: Session = Depends(get_db)):
    db.add(database_model.Product(**product.model_dump()))
    db.commit()
    return product


# Update product
@app.put("/products/{product_id}")
def update_product(product_id: int, product: Product , db: Session = Depends(get_db)):
    db_product = db.query(database_model.Product).filter(database_model.Product.id == product_id).first()
    if db_product:
        db_product.name = product.name
        db_product.description = product.description
        db_product.price = product.price
        db.commit()
        return "Product updated"
    else:
        return "No Product Found!"


# Delete product
@app.delete("/products/{product_id}")
def delete_product(product_id: int , db: Session = Depends(get_db)):
    db_product = db.query(database_model.Product).filter(database_model.Product.id == product_id).first()
    if db_product:
        db.delete(db_product)
        db.commit()
        return "Product Deleted SuccesFully!"
    else:
        return "Product not Found!"


