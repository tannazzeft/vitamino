from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import sqlite3
import uuid

# لود متغیرهای محیطی
load_dotenv()

# ایجاد برنامه FastAPI
app = FastAPI(title="Vitamino Shop")

# تنظیمات CORS برای توسعه
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# سرویس دهی فایل‌های استاتیک از پوشه static
app.mount("/", StaticFiles(directory="static", html=True), name="static")

# --- مسیرهای API ---

@app.get("/ping")
def ping():
    return {"status": "ok"}

@app.get("/shop/products")
def get_products():
    """لیست محصولات را از دیتابیس برمی‌گرداند"""
    try:
        # اتصال به دیتابیس
        db_path = os.getenv("DB_PATH", "output(2)(1) 2.sqlite")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # دریافت محصولات
        cursor.execute("SELECT id, title, price, description FROM products")
        products = [
            {
                "id": row[0],
                "title": row[1],
                "price": row[2],
                "description": row[3] or ""
            }
            for row in cursor.fetchall()
        ]
        
        conn.close()
        return {"products": products}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.post("/payment/checkout")
def create_checkout(checkout_data: dict):
    """ایجاد لینک پرداخت برای سبد خرید"""
    try:
        # در نسخه واقعی باید به درگاه پرداخت متصل شوید
        # این یک پیاده‌سازی نمونه است
        
        # ایجاد لینک پرداخت ساختگی
        payment_id = str(uuid.uuid4())[:8]
        
        return {
            "payment_url": f"https://vitamino-pay.com/{payment_id}",
            "message": "Payment initiated"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment error: {str(e)}")

# --- رویدادهای برنامه ---

@app.on_event("startup")
def startup():
    """ایجاد جداول در دیتابیس در صورت عدم وجود"""
    try:
        db_path = os.getenv("DB_PATH", "output(2)(1) 2.sqlite")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # ایجاد جدول محصولات (اگر وجود ندارد)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            price INTEGER NOT NULL,
            description TEXT,
            image_url TEXT
        )
        """)
        
        # درج داده‌های نمونه (فقط برای توسعه)
        cursor.execute("SELECT COUNT(*) FROM products")
        count = cursor.fetchone()[0]
        
        if count == 0:
            sample_products = [
                ("ویتامین C", 50000, "تقویت سیستم ایمنی بدن", "/static/vitamin-c.jpg"),
                ("ویتامین D", 60000, "تقویت استخوان‌ها و دندان‌ها", "/static/vitamin-d.jpg"),
                ("امگا 3", 70000, "تقویت قلب و مغز", "/static/omega3.jpg"),
                ("زینک", 40000, "تقویت سیستم ایمنی و رشد مو", "/static/zinc.jpg"),
            ]
            cursor.executemany(
                "INSERT INTO products (title, price, description, image_url) VALUES (?, ?, ?, ?)",
                sample_products
            )
            conn.commit()
        
        conn.close()
        print("✅ Database initialized successfully")
    
    except Exception as e:
        print(f"❌ Database initialization failed: {str(e)}")
