import sqlite3
from pathlib import Path
import os
from datetime import datetime

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    fullname TEXT,
    phone TEXT UNIQUE,
    password TEXT,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT UNIQUE,
    title TEXT,
    description TEXT,
    price INTEGER,
    stock INTEGER,
    image TEXT
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    total INTEGER,
    status TEXT,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    product_id INTEGER,
    qty INTEGER,
    price INTEGER
);
"""

def get_conn(db_path=None):
    db_path = db_path or os.getenv("DB_PATH", "output(2)(1).sqlite")
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path=None):
    db_path = db_path or os.getenv("DB_PATH", "output(2)(1).sqlite")
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.executescript(SCHEMA_SQL)
    conn.commit()
    conn.close()

def insert_sample_products_if_empty(conn):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(1) as c FROM products")
    r = cur.fetchone()
    if r and r[0] == 0:
        sample = [
            ("SKU001", "مکمل الف", "توضیح مکمل الف", 120000, 10, ""),
            ("SKU002", "مکمل ب", "توضیح مکمل ب", 85000, 20, ""),
            ("SKU003", "مکمل ج", "توضیح مکمل ج", 200000, 5, ""),
        ]
        cur.executemany("INSERT INTO products (sku,title,description,price,stock,image) VALUES (?, ?, ?, ?, ?, ?)", sample)
        conn.commit()
