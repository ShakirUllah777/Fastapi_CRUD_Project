from fastapi import FastAPI, HTTPException, Depends, status
from model import Product, UserCreate, UserResponse
from database import session, engine
import database_model
from sqlalchemy.orm import Session
from security import hash_password, verify_password, create_access_token
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from auth import get_current_user , get_current_admin


app = FastAPI()

database_model.Base.metadata.create_all(bind=engine)
# -------------------- Dummy Products to add first  --------------------

products= [
    Product(id=1, name="Laptop", description="Best laptop in Pakistan", price=22),
    Product(id=2, name="Phone", description="Best phone in Pakistan", price=22),
    Product(id=3, name="Windows Laptop", description="Best windows laptop", price=22),
]

# -------------------- DB DEPENDENCY --------------------
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
# -------------------- USER REGISTRATION --------------------
@app.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(database_model.User).filter(
        database_model.User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = database_model.User(
        email=user.email,
        hashed_password=hash_password(user.password),
        role="user"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# -------------------- LOGIN --------------------
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(database_model.User).filter(database_model.User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token(
        data={"sub": user.email, "role": user.role},
        expires_delta=timedelta(minutes=30)
    )

    return {"access_token": access_token, "token_type": "bearer"}


# -------------------- PRODUCTS (PROTECTED) --------------------

@app.get("/products")
def get_all_products(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return db.query(database_model.Product).all()


@app.get("/products/{product_id}")
def get_product_by_id(
    product_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    product = db.query(database_model.Product).filter(
        database_model.Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


@app.post("/products")
def add_product(product: Product, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You are not allowed to add products")
    
    db.add(database_model.Product(**product.model_dump()))
    db.commit()
    db.refresh(product)
    return product



@app.put("/products/{product_id}")
def update_product(
    product_id: int,
    product: Product,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)  # <-- ADMIN ONLY
):
    db_product = db.query(database_model.Product).filter(
        database_model.Product.id == product_id
    ).first()

    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    db_product.name = product.name
    db_product.description = product.description
    db_product.price = product.price
    db.commit()

    return {"message": "Product updated successfully"}


@app.delete("/products/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin)
):
    db_product = db.query(database_model.Product).filter(
        database_model.Product.id == product_id
    ).first()

    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(db_product)
    db.commit()

    return {"message": "Product deleted successfully"}