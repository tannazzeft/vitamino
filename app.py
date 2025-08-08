# app.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import sqlite3
from passlib.hash import bcrypt
import uuid
import requests

app = FastAPI()

DB_PATH = "output(2)(1).sqlite"

# ------ Models ------
class UserRegister(BaseModel):
    fullname: str
    phone: str
    password: str

class UserLogin(BaseModel):
    phone: str
    password: str

class PaymentRequest(BaseModel):
    amount: int
    description: str

# ------ DB helper ------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ------ Auth Routes ------
@app.post("/register")
def register(user: UserRegister):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE phone=?", (user.phone,))
    if cur.fetchone():
        raise HTTPException(status_code=400, detail="این شماره قبلاً ثبت شده است.")

    hashed_password = bcrypt.hash(user.password)
    user_id = str(uuid.uuid4())
    cur.execute("INSERT INTO users (id, fullname, phone, password) VALUES (?, ?, ?, ?)",
                (user_id, user.fullname, user.phone, hashed_password))
    conn.commit()
    conn.close()
    return {"message": "ثبت‌نام با موفقیت انجام شد."}

@app.post("/login")
def login(user: UserLogin):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE phone=?", (user.phone,))
    db_user = cur.fetchone()
    conn.close()

    if not db_user or not bcrypt.verify(user.password, db_user["password"]):
        raise HTTPException(status_code=400, detail="شماره یا رمز اشتباه است.")

    return {"message": "ورود موفقیت‌آمیز", "user_id": db_user["id"]}

# ------ Payment Routes ------
ZARINPAL_MERCHANT = "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"  # اینو بعداً با کد واقعی جایگزین کن
ZARINPAL_REQUEST_URL = "https://api.zarinpal.com/pg/v4/payment/request.json"
ZARINPAL_START_URL = "https://www.zarinpal.com/pg/StartPay/"
ZARINPAL_VERIFY_URL = "https://api.zarinpal.com/pg/v4/payment/verify.json"

@app.post("/payment/request")
def payment_request(data: PaymentRequest):
    req_data = {
        "merchant_id": ZARINPAL_MERCHANT,
        "amount": data.amount,
        "description": data.description,
        "callback_url": "http://localhost:8000/payment/verify"
    }
    headers = {"accept": "application/json", "content-type": "application/json"}
    response = requests.post(ZARINPAL_REQUEST_URL, json=req_data, headers=headers).json()

    if "data" in response and response["data"].get("authority"):
        authority = response["data"]["authority"]
        return {"payment_url": f"{ZARINPAL_START_URL}{authority}"}
    else:
        raise HTTPException(status_code=400, detail="خطا در ایجاد تراکنش")

@app.get("/payment/verify")
def payment_verify(authority: str, Status: str):
    if Status != "OK":
        return {"status": "پرداخت لغو شد"}

    req_data = {
        "merchant_id": ZARINPAL_MERCHANT,
        "amount": 1000,  # مبلغ واقعی تراکنش
        "authority": authority
    }
    headers = {"accept": "application/json", "content-type": "application/json"}
    response = requests.post(ZARINPAL_VERIFY_URL, json=req_data, headers=headers).json()

    if "data" in response and response["data"].get("code") == 100:
        return {"status": "پرداخت موفقیت‌آمیز"}
    else:
        return {"status": "پرداخت ناموفق"}
