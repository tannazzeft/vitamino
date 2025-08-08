from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
import os
import requests

router = APIRouter()

ZARINPAL_REQ = "https://api.zarinpal.com/pg/v4/payment/request.json"
ZARINPAL_START = "https://www.zarinpal.com/pg/StartPay/"
ZARINPAL_VERIFY = "https://api.zarinpal.com/pg/v4/payment/verify.json"
MERCHANT = os.getenv("ZARINPAL_MERCHANT", "TEST_MERCHANT_ID")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

class CheckoutModel(BaseModel):
    user_id: str
    items: list  # [{product_id: int, qty: int}, ...]
    total: int
    description: str = "پرداخت در Vitamino"

@router.post("/checkout")
def checkout(data: CheckoutModel):
    # اینجا میتونیم سفارش را در orders ثبت کنیم (با وضعیت pending)
    # سپس درخواست به زرین‌پال ارسال می‌کنیم
    req_payload = {
        "merchant_id": MERCHANT,
        "amount": data.total,
        "description": data.description,
        "callback_url": f"{BASE_URL}/payment/verify"
    }
    headers = {"accept": "application/json", "content-type": "application/json"}
    resp = requests.post(ZARINPAL_REQ, json=req_payload, headers=headers).json()
    if "data" in resp and resp["data"].get("authority"):
        authority = resp["data"]["authority"]
        return {"payment_url": f"{ZARINPAL_START}{authority}", "authority": authority}
    else:
        raise HTTPException(status_code=400, detail="خطا در ایجاد تراکنش")

@router.get("/verify")
def verify(request: Request, Authority: str = None, Status: str = None):
    # زرین‌پال با پارامترهای Authority و Status برمی‌گرداند
    if Status != "OK":
        return {"status": "پرداخت لغو شد"}
    payload = {"merchant_id": MERCHANT, "authority": Authority, "amount": request.query_params.get("amount", 0)}
    headers = {"accept": "application/json", "content-type": "application/json"}
    resp = requests.post(ZARINPAL_VERIFY, json=payload, headers=headers).json()
    # بررسی کد پاسخ (در نسخه‌ای که استفاده می‌کنی ممکن است متفاوت باشد)
    if "data" in resp and resp["data"].get("code") == 100:
        return {"status": "پرداخت موفق"}
    return {"status": "پرداخت ناموفق", "response": resp}
