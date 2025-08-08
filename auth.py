from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from passlib.hash import bcrypt
import uuid
from db import get_conn
from datetime import datetime

router = APIRouter()

class RegisterModel(BaseModel):
    fullname: str
    phone: str
    password: str

class LoginModel(BaseModel):
    phone: str
    password: str

@router.post("/register")
def register(data: RegisterModel):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE phone = ?", (data.phone,))
    if cur.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="این شماره قبلاً ثبت شده است.")
    user_id = str(uuid.uuid4())
    hashed = bcrypt.hash(data.password)
    now = datetime.utcnow().isoformat()
    cur.execute("INSERT INTO users (id, fullname, phone, password, created_at) VALUES (?, ?, ?, ?, ?)",
                (user_id, data.fullname, data.phone, hashed, now))
    conn.commit()
    conn.close()
    return {"message": "ثبت‌نام با موفقیت انجام شد.", "user_id": user_id}

@router.post("/login")
def login(data: LoginModel):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, password, fullname FROM users WHERE phone = ?", (data.phone,))
    row = cur.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=400, detail="شماره یا رمز اشتباه است.")
    if not bcrypt.verify(data.password, row["password"]):
        raise HTTPException(status_code=400, detail="شماره یا رمز اشتباه است.")
    # برای سادگی جتونی user_id رو برگردونی؛ برای تولید session/token بعدا JWT اضافه می‌کنیم
    return {"message": "ورود موفق", "user_id": row["id"], "fullname": row["fullname"]}
