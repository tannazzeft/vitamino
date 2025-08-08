from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db import get_conn, insert_sample_products_if_empty

router = APIRouter()

class AddProductModel(BaseModel):
    sku: str
    title: str
    description: str
    price: int
    stock: int

@router.get("/products")
def list_products():
    conn = get_conn()
    insert_sample_products_if_empty(conn)
    cur = conn.cursor()
    cur.execute("SELECT id, sku, title, description, price, stock, image FROM products")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return {"products": rows}

@router.get("/products/{product_id}")
def get_product(product_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, sku, title, description, price, stock, image FROM products WHERE id=?", (product_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="محصول یافت نشد")
    return dict(row)

# Admin-like route to add a product (later protect it)
@router.post("/products")
def add_product(p: AddProductModel):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO products (sku, title, description, price, stock, image) VALUES (?, ?, ?, ?, ?, ?)",
                (p.sku, p.title, p.description, p.price, p.stock, ""))
    conn.commit()
    conn.close()
    return {"message": "محصول اضافه شد"}
