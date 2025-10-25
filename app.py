import streamlit as st
import pandas as pd
import numpy as np
import json
import bcrypt  # تغییر: اضافه کردن bcrypt
try:
    import pysqlite3 as sqlite3
except ImportError:
    import sqlite3
import requests
from bs4 import BeautifulSoup
import googletrans
from googletrans import Translator
import xml.etree.ElementTree as ET
import time
import random
from functools import lru_cache
import bleach
from tenacity import retry, stop_after_attempt, wait_fixed
from contextlib import contextmanager
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re
from typing import Dict, List, Tuple, Any, Optional
import base64
from io import BytesIO
import os
from pathlib import Path

# تنظیمات صفحه
st.set_page_config(
    page_title="سیستم تحلیل تداخلات دارویی",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Create a translator instance
translator = Translator()

# Global requests session for better performance
session = requests.Session()

@lru_cache(maxsize=1000)
def translate_to_persian(text):
    try:
        return translator.translate(text, dest='fa').text
    except:
        return text

@contextmanager
def get_db_connection(db_path):
    conn = sqlite3.connect(db_path)
    try:
        yield conn
    finally:
        conn.close()

# استایل‌های CSS برای طراحی
def load_css():
    st.markdown("""
    <style>
    :root {
        --primary-ultralight: #F0FFFF;
        --primary-light: #E0F7FA;
        --primary: #4DB6AC;
        --primary-dark: #00897B;
        --secondary-light: #FFECB3;
        --secondary: #FFB74D;
        --secondary-dark: #FF9800;
    }
    .main, .stApp {
        background-color: var(--primary-ultralight) !important;
        font-family: 'Vazirmatn', 'Segoe UI', Tahoma, sans-serif;  /* تغییر: استفاده از Vazirmatn */
    }
    .header-container {
        background: linear-gradient(135deg, var(--primary), var(--primary-dark)) !important;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .header-title {
        color: white;
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .product-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 0.5rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        border: 1px solid var(--primary-light);
    }
    .product-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.12);
        border-color: var(--secondary-light);
    }
    .price-tag {
        background-color: var(--secondary);
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin-top: 0.5rem;
        font-size: 0.9rem;
    }
    .stButton>button {
        background: linear-gradient(135deg, var(--primary), var(--primary-dark)) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.5rem 1.8rem !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2) !important;
        background: linear-gradient(135deg, var(--primary-dark), var(--primary)) !important;
    }
    .sidebar .sidebar-content {
        background-color: var(--primary-light) !important;
    }
    .interaction-card {
        border-left: 5px solid var(--secondary) !important;
    }
    .warning-card {
        border-left: 5px solid var(--secondary-dark) !important;
    }
    .highlight {
        background-color: var(--secondary-light);
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
    }
    .header-subtitle {
        color: #f0ffff;
        font-size: 1.2rem;
        text-align: center;
        margin-top: 0.5rem;
    }
    .safe-card {
        background: white;
        border-left: 5px solid #4ECDC4;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-top: 3px solid #20B2AA;
    }
    .pregnancy-card {
        background: white;
        border-left: 5px solid #FF69B4;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .disease-card {
        background: white;
        border-left: 5px solid #9932CC;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .analysis-result {
        background: linear-gradient(135deg, #f8fff8, #f0ffff);
        border-radius: 15px;
        padding: 2rem;
        margin: 2rem 0;
        border: 1px solid #20B2AA;
    }
    .demographic-form {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .shop-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
        border: 1px solid #e0e0e0;
    }
    </style>
    <link href='https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;700&display=swap' rel='stylesheet'>  <!-- تغییر: استفاده از Vazirmatn -->
    """, unsafe_allow_html=True)

class OnlineSearch:
    def __init__(self):
        self.sources = {
            'pubmed': 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={}&retmode=json&retmax=5',
            'drugs.com': 'https://www.drugs.com/search.php?searchterm={}',
            'webmd': 'https://www.webmd.com/search/search_results/default.aspx?query={}'
        }

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def search_pubmed(self, query):
        try:
            url = self.sources['pubmed'].format(query.replace(' ', '+'))
            response = session.get(url)
            response.raise_for_status()
            data = response.json()

            results = []
            if 'esearchresult' in data and 'idlist' in data['esearchresult']:
                for article_id in data['esearchresult']['idlist'][:3]:
                    summary_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={article_id}&retmode=json"
                    summary_response = session.get(summary_url)
                    summary_response.raise_for_status()
                    summary_data = summary_response.json()

                    if 'result' in summary_data and article_id in summary_data['result']:
                        article = summary_data['result'][article_id]
                        title = article.get('title', 'No title available')
                        pub_date = article.get('pubdate', 'Unknown date')
                        authors = article.get('authors', [])
                        author_list = ", ".join([author['name'] for author in authors]) if authors else "Unknown authors"

                        title_persian = translate_to_persian(title)

                        results.append({
                            'title': title,
                            'title_persian': title_persian,
                            'pub_date': pub_date,
                            'authors': author_list,
                            'source': 'PubMed',
                            'url': f'https://pubmed.ncbi.nlm.nih.gov/{article_id}/'
                        })
            return results
        except Exception as e:
            st.error(f"خطا در جستجوی PubMed: {str(e)}. لطفاً بعداً امتحان کنید.")
            return []

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def search_drugs_com(self, query):
        try:
            url = self.sources['drugs.com'].format(query.replace(' ', '+'))
            response = session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            results = []
            for result in soup.select('.ddc-search-results .ddc-list-item')[:3]:
                title_elem = result.select_one('.ddc-list-item-title')
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    url_path = title_elem.get('href', '')

                    title_persian = translate_to_persian(title)

                    results.append({
                        'title': title,
                        'title_persian': title_persian,
                        'source': 'Drugs.com',
                        'url': f'https://www.drugs.com{url_path}' if url_path.startswith('/') else url_path
                    })
            return results
        except Exception as e:
            st.error(f"خطا در جستجوی Drugs.com: {str(e)}. لطفاً بعداً امتحان کنید.")
            return []

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    def search_webmd(self, query):
        try:
            url = self.sources['webmd'].format(query.replace(' ', '+'))
            response = session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            results = []
            for result in soup.select('.search-results .result')[:3]:
                title_elem = result.select_one('h3 a')
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    url_path = title_elem.get('href', '')

                    title_persian = translate_to_persian(title)

                    results.append({
                        'title': title,
                        'title_persian': title_persian,
                        'source': 'WebMD',
                        'url': f'https://www.webmd.com{url_path}' if url_path.startswith('/') else url_path
                    })
            return results
        except Exception as e:
            st.error(f"خطا در جستجوی WebMD: {str(e)}. لطفاً بعداً امتحان کنید.")
            return []

    def search_all(self, query):
        st.info(f"جستجو برای: {query}")
        results = []
        results.extend(self.search_pubmed(query))
        results.extend(self.search_drugs_com(query))
        results.extend(self.search_webmd(query))
        return results

class AdminManager:
    def __init__(self, db_manager):
        self.db = db_manager

    def get_about_us(self):
        with get_db_connection(self.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM site_settings WHERE key = 'about_us'")
            result = cursor.fetchone()
            return result[0] if result else "این سایت زیر نظر دکتر داروساز اداره می‌شود و از غذادارو مجوز دارد."

    def update_about_us(self, content):
        with get_db_connection(self.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO site_settings (key, value) VALUES ('about_us', ?)",
                (content,)
            )
            conn.commit()

    def get_contact_info(self):
        with get_db_connection(self.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT key, value FROM site_settings WHERE key IN ('pharmacy_address', 'pharmacy_phone', 'support_email')")
            results = cursor.fetchall()

        contact_info = {'pharmacy_address': '', 'pharmacy_phone': '', 'support_email': ''}
        for key, value in results:
            contact_info[key] = value
        return contact_info

    def update_contact_info(self, address, phone, email):
        with get_db_connection(self.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO site_settings (key, value) VALUES ('pharmacy_address', ?)",
                (address,)
            )
            cursor.execute(
                "INSERT OR REPLACE INTO site_settings (key, value) VALUES ('pharmacy_phone', ?)",
                (phone,)
            )
            cursor.execute(
                "INSERT OR REPLACE INTO site_settings (key, value) VALUES ('support_email', ?)",
                (email,)
            )
            conn.commit()

class DatabaseManager:
    def __init__(self, db_path: str = "/tmp/vitamino.sqlite") -> None:
        self.db_path = "output(2)(1).sqlite"
        self.data_dir: Path = Path("data/")
        self._ensure_data_dir()
        try:
            self.init_database()
            self.load_all_csv_data()
            self.add_sample_products()
        except Exception as e:
            st.error(f"خطا در راه‌اندازی پایگاه داده: {str(e)}")
            self.db_path = ":memory:"
            self.init_database()
            self.load_all_csv_data()

    def _ensure_data_dir(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def init_database(self):
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            try:
                tables = [
                    """CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        phone TEXT UNIQUE NOT NULL,
                        first_name TEXT NOT NULL,
                        last_name TEXT NOT NULL,
                        password_hash TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_admin INTEGER DEFAULT 0  -- اضافه کردن ستون is_admin
                    )""",
                    """CREATE TABLE IF NOT EXISTS analyses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        demographic_data TEXT,
                        supplements TEXT,
                        medications TEXT,
                        conditions TEXT,
                        results TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )""",
                    """CREATE TABLE IF NOT EXISTS diseases_supplements (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        disease TEXT,
                        vulnerable_group TEXT,
                        recommended_tests TEXT,
                        clinical_notes TEXT,
                        monitoring_frequency TEXT,
                        recommended_supplements TEXT,
                        supportive_diet TEXT,
                        dosing_women TEXT,
                        dosing_men TEXT,
                        dosing_elderly TEXT,
                        dosing_children_0_2 TEXT,
                        dosing_children_2_12 TEXT,
                        dosing_teens_12_18 TEXT,
                        dosing_obese TEXT,
                        dosing_pregnant_nursing TEXT,
                        source TEXT
                    )""",
                    """CREATE TABLE IF NOT EXISTS pregnancy_categories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        compound TEXT,
                        pregnancy_category TEXT,
                        clinical_advice TEXT,
                        use_warning TEXT,
                        toxic_threshold TEXT,
                        sources TEXT
                    )""",
                    """CREATE TABLE IF NOT EXISTS supplement_drug_interactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        supplement_group TEXT,
                        compound TEXT,
                        interacting_drug TEXT,
                        severity TEXT,
                        interaction_type TEXT,
                        condition_alert TEXT,
                        risk_group TEXT,
                        rda TEXT,
                        test TEXT,
                        normal_range TEXT,
                        clinical_advice TEXT,
                        source TEXT
                    )""",
                    """CREATE TABLE IF NOT EXISTS supplement_condition_interactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        compound TEXT,
                        condition_disease TEXT,
                        severity TEXT,
                        clinical_advice TEXT,
                        mechanism TEXT,
                        source TEXT
                    )""",
                    """CREATE TABLE IF NOT EXISTS products (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        category TEXT,
                        price INTEGER,
                        description TEXT,
                        image_url TEXT,
                        stock INTEGER DEFAULT 0,
                        active BOOLEAN DEFAULT TRUE
                    )""",
                    """CREATE TABLE IF NOT EXISTS sessions (
                        session_id TEXT PRIMARY KEY,
                        user_id INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )""",
                    """CREATE TABLE IF NOT EXISTS site_settings (
                        key TEXT PRIMARY KEY,
                        value TEXT
                    )""",
                    """CREATE TABLE IF NOT EXISTS product_categories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        description TEXT
                    )""",
                    """CREATE TABLE IF NOT EXISTS product_discounts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        product_id INTEGER,
                        discount_percent INTEGER,
                        start_date TIMESTAMP,
                        end_date TIMESTAMP,
                        FOREIGN KEY (product_id) REFERENCES products (id)
                    )""",
                    """CREATE TABLE IF NOT EXISTS related_products (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        product_id INTEGER,
                        related_product_id INTEGER,
                        FOREIGN KEY (product_id) REFERENCES products (id),
                        FOREIGN KEY (related_product_id) REFERENCES products (id)
                    )"""
                ]

                for table_query in tables:
                    cursor.execute(table_query)

                # بررسی و اضافه کردن ستون is_admin برای دیتابیس‌های موجود
                cursor.execute("PRAGMA table_info(users)")
                columns = [col[1] for col in cursor.fetchall()]
                if 'is_admin' not in columns:
                    cursor.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")
                    print("ستون is_admin به جدول users اضافه شد.")

                cursor.execute(
                    "INSERT OR IGNORE INTO site_settings (key, value) VALUES ('about_us', ?)",
                    ("این سایت زیر نظر دکتر داروساز اداره می‌شود و از غذادارو مجوز دارد.",)
                )

                conn.commit()
                st.success("✅ پایگاه داده با موفقیت راه‌اندازی شد!")
            except Exception as e:
                st.error(f"خطا در راه‌اندازی پایگاه داده: {str(e)}")
                raise

    def load_all_csv_data(self):
        """🔧 اصلاح‌شده: همه فایل‌های CSV موجود رو می‌خونه"""
        with get_db_connection(self.db_path) as conn:
            # همه فایل‌های CSV توی پوشه data رو پیدا می‌کنه
            csv_files = list(self.data_dir.glob("*.csv"))

            if not csv_files:
                st.warning("⚠️ هیچ فایل CSV در پوشه data/ یافت نشد")
                return

            loaded_files = 0
            for csv_file in csv_files:
                csv_name = csv_file.name
                table_name = csv_name.replace('.csv', '')

                try:
                    st.info(f"📂 در حال بارگذاری: {csv_name}")
                    df = pd.read_csv(csv_file, encoding='utf-8-sig')

                    if df.empty:
                        st.warning(f"⚠️ {csv_name} خالی است")
                        continue

                    # پاک کردن ردیف/ستون‌های خالی
                    df = df.dropna(how='all', axis=1)
                    df = df.dropna(how='all', axis=0)
                    df.columns = df.columns.str.strip()

                    # نام ستون‌ها رو استاندارد می‌کنه
                    df = self._standardize_column_names(df, table_name)

                    # ذخیره توی دیتابیس
                    df.to_sql(table_name, conn, if_exists='replace', index=False)
                    loaded_files += 1
                    st.success(f"✅ {csv_name} با موفقیت بارگذاری شد ({len(df)} ردیف)")

                except Exception as e:
                    st.error(f"❌ خطا در {csv_name}: {str(e)}")

            st.success(f"🎉 {loaded_files} فایل CSV با موفقیت بارگذاری شد!")
    def _standardize_column_names(self, df, table_name):
        """🔧 همه ستون‌های فارسی رو به انگلیسی تبدیل می‌کنه"""
        # دیکشنری کامل برای همه ستون‌های ممکن
        all_mappings = {
            # sheet1 - diseases_supplements
            'بیماری': 'disease',
            'گروه آسیب‌پذیر': 'vulnerable_group',
            'آزمایش‌های پیشنهادی': 'recommended_tests',
            'نکات بالینی': 'clinical_notes',
            'تناوب پیشنهادی': 'monitoring_frequency',
            'مکمل‌های پیشنهادی': 'recommended_supplements',
            'رژیم غذایی حمایتی': 'supportive_diet',
            'دوزینگ زنان': 'dosing_women',
            'دوزینگ مردان': 'dosing_men',
            'دوزینگ سالمندان': 'dosing_elderly',
            'دوزینگ کودک (۰–۲ سال)': 'dosing_children_0_2',
            'دوزینگ کودک (۲–۱۲ سال)': 'dosing_children_2_12',
            'دوزینگ نوجوان (۱۲–۱۸ سال)': 'dosing_teens_12_18',
            'دوزینگ افراد چاق': 'dosing_obese',
            'دوزینگ زنان باردار و شیرده': 'dosing_pregnant_nursing',

            # sheet2 - pregnancy_categories
            'ماده فعال / Compound': 'compound',
            'رده بارداری/شیردهی (A–X)': 'pregnancy_category',
            'توصیه بالینی / Clinical Advice': 'clinical_advice',
            'هشدار مصرف / Use Warning': 'use_warning',
            'دوز خطرناک / Toxic Threshold': 'toxic_threshold',
            'منابع / Sources': 'sources',

            # sheet3 - supplement_drug_interactions
            'گروه مکمل / Supplement Group': 'supplement_group',
            'ماده فعال / Compound': 'compound',
            'داروی درگیر / Interacting Drug': 'interacting_drug',
            'شدت / Severity (A–X)': 'severity',
            'نوع تداخل / Type': 'interaction_type',
            'هشدار بیماری / Condition Alert': 'condition_alert',
            'گروه حساس / Risk Group': 'risk_group',
            'دوز پیشنهادی / RDA': 'rda',
            'تست / Test': 'test',
            'رنج نرمال / Normal Range': 'normal_range',
            'توصیه بالینی / Clinical Advice': 'clinical_advice',

            # sheet4 - supplement_condition_interactions
            'ماده فعال / Compound': 'compound',
            'بیماری / Condition': 'condition_disease',
            'شدت تداخل (A–X) / Severity': 'severity',
            'توصیه بالینی / Clinical Advice': 'clinical_advice',
            'مکانیسم / Mechanism': 'mechanism',

            # عمومی
            'منبع': 'source',
            'منابع': 'source'
        }

        # همه ستون‌های فارسی رو تبدیل می‌کنه
        df.columns = [all_mappings.get(col, col) for col in df.columns]
        return df
    def add_sample_products(self):
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products'")
            if not cursor.fetchone():
                st.error("جدول products وجود ندارد!")
                return

            sample_products = [
                ("ویتامین D3 2000 واحد", "ویتامین‌ها", 250000, "مکمل ویتامین D3 با کیفیت بالا", "https://example.com/vitamin-d.jpg", 50),
                ("امگا 3 فیش اویل", "اسیدهای چرب", 180000, "کپسول امگا 3 از روغن ماهی", "https://example.com/omega3.jpg", 30),
                ("مولتی ویتامین کامل", "مولتی ویتامین", 320000, "مکمل جامع ویتامین‌ها و مواد معدنی", "https://example.com/multivitamin.jpg", 25),
                ("منیزیم 400 میلی‌گرم", "مواد معدنی", 150000, "مکمل منیزیم برای سلامت عضلات", "https://example.com/magnesium.jpg", 40),
                ("زینک 30 میلی‌گرم", "مواد معدنی", 120000, "مکمل زینک تقویت‌کننده سیستم ایمنی", "https://example.com/zinc.jpg", 35),
                ("ویتامین B12 1000 میکروگرم", "ویتامین‌ها", 200000, "مکمل ویتامین B12 برای انرژی", "https://example.com/b12.jpg", 45),
                ("آهن بیس‌گلایسینات", "مواد معدنی", 180000, "مکمل آهن با جذب بهینه", "https://example.com/iron.jpg", 20),
                ("کلسیم + ویتامین K2", "مواد معدنی", 220000, "ترکیب کلسیم و ویتامین K2", "https://example.com/calcium.jpg", 30),
                ("کوآنزیم Q10", "آنتی‌اکسیدان", 380000, "مکمل کوآنزیم Q10 برای انرژی سلولی", "https://example.com/coq10.jpg", 15),
                ("پروبیوتیک 50 میلیارد", "پروبیوتیک", 290000, "کپسول پروبیوتیک با 10 گونه باکتری", "https://example.com/probiotic.jpg", 22)
            ]

            cursor.executemany("""
            INSERT OR IGNORE INTO products (name, category, price, description, image_url, stock)
            VALUES (?, ?, ?, ?, ?, ?)
            """, sample_products)
            conn.commit()
            st.success("✅ محصولات نمونه با موفقیت اضافه شدند!")

class InteractionAnalyzer:
    def __init__(self, db_manager):
        self.db = db_manager

    def analyze_interactions(self, supplements, medications, conditions, demographic_data):
        results = {
            'supplement_drug_interactions': [],
            'supplement_condition_interactions': [],
            'pregnancy_safety': [],
            'disease_recommendations': [],
            'severity_summary': {'high': 0, 'medium': 0, 'low': 0},
            'personalized_dosing': {}
        }

        with get_db_connection(self.db.db_path) as conn:
            try:
                results['supplement_drug_interactions'] = self._analyze_supplement_drug_interactions(supplements, medications, conn)
                results['supplement_condition_interactions'] = self._analyze_supplement_condition_interactions(supplements, conditions, conn)
                if demographic_data.get('is_pregnant') or demographic_data.get('is_breastfeeding'):
                    results['pregnancy_safety'] = self._analyze_pregnancy_safety(supplements, conn)
                results['disease_recommendations'] = self._analyze_disease_recommendations(conditions, demographic_data, conn)
                results['personalized_dosing'] = self._get_personalized_dosing(supplements, demographic_data, conn)
                results['severity_summary'] = self._calculate_severity_summary(results)
            except Exception as e:
                st.error(f"خطا در تحلیل تداخلات: {str(e)}")
        return results

    def _analyze_supplement_drug_interactions(self, supplements, medications, conn):
        interactions = []
        for supplement in supplements:
            for medication in medications:
                query = """
                SELECT * FROM supplement_drug_interactions
                WHERE (LOWER(compound) LIKE ? OR LOWER(supplement_group) LIKE ?)
                AND LOWER(interacting_drug) LIKE ?
                """
                params = [f'%{supplement.lower()}%', f'%{supplement.lower()}%', f'%{medication.lower()}%']
                df = pd.read_sql_query(query, conn, params=params)

                for _, row in df.iterrows():
                    interactions.append({
                        'supplement': supplement,
                        'drug': medication,
                        'compound': row.get('compound', ''),
                        'severity': row.get('severity', ''),
                        'interaction_type': row.get('interaction_type', ''),
                        'clinical_advice': row.get('clinical_advice', ''),
                        'risk_group': row.get('risk_group', ''),
                        'source': row.get('source', ''),
                        'condition_alert': row.get('condition_alert', ''),
                        'normal_range': row.get('normal_range', ''),
                        'test': row.get('test', '')
                    })
        return interactions

    def _analyze_supplement_condition_interactions(self, supplements, conditions, conn):
        interactions = []
        for supplement in supplements:
            for condition in conditions:
                query = """
                SELECT * FROM supplement_condition_interactions
                WHERE LOWER(compound) LIKE ?
                AND LOWER(condition_disease) LIKE ?
                """
                params = [f'%{supplement.lower()}%', f'%{condition.lower()}%']
                df = pd.read_sql_query(query, conn, params=params)

                for _, row in df.iterrows():
                    interactions.append({
                        'supplement': supplement,
                        'condition': condition,
                        'compound': row.get('compound', ''),
                        'severity': row.get('severity', ''),
                        'clinical_advice': row.get('clinical_advice', ''),
                        'mechanism': row.get('mechanism', ''),
                        'source': row.get('source', '')
                    })
        return interactions

    def _analyze_pregnancy_safety(self, supplements, conn):
        safety_results = []
        for supplement in supplements:
            query = """
            SELECT * FROM pregnancy_categories
            WHERE LOWER(compound) LIKE ?
            """
            params = [f'%{supplement.lower()}%']
            df = pd.read_sql_query(query, conn, params=params)

            for _, row in df.iterrows():
                safety_results.append({
                    'supplement': supplement,
                    'compound': row.get('compound', ''),
                    'pregnancy_category': row.get('pregnancy_category', ''),
                    'clinical_advice': row.get('clinical_advice', ''),
                    'use_warning': row.get('use_warning', ''),
                    'toxic_threshold': row.get('toxic_threshold', ''),
                    'sources': row.get('sources', ''),
                    'safety_level': self._get_safety_level(row.get('pregnancy_category', ''))
                })
        return safety_results

    def _analyze_disease_recommendations(self, conditions, demographic_data, conn):
        recommendations = []
        for condition in conditions:
            query = """
            SELECT * FROM diseases_supplements
            WHERE LOWER(disease) LIKE ?
            """
            params = [f'%{condition.lower()}%']
            df = pd.read_sql_query(query, conn, params=params)

            for _, row in df.iterrows():
                recommendations.append({
                    'disease': condition,
                    'vulnerable_group': row.get('vulnerable_group', ''),
                    'recommended_tests': row.get('recommended_tests', ''),
                    'clinical_notes': row.get('clinical_notes', ''),
                    'recommended_supplements': row.get('recommended_supplements', ''),
                    'supportive_diet': row.get('supportive_diet', ''),
                    'monitoring_frequency': row.get('monitoring_frequency', ''),
                    'source': row.get('source', '')
                })
        return recommendations

    def _get_personalized_dosing(self, supplements, demographic_data, conn):
        dosing = {}
        query = """
        SELECT * FROM diseases_supplements
        WHERE recommended_supplements IS NOT NULL
        """
        df = pd.read_sql_query(query, conn)

        age = demographic_data.get('age', 30)
        gender = demographic_data.get('gender', 'مرد')
        is_pregnant = demographic_data.get('is_pregnant', False)
        is_obese = demographic_data.get('bmi', 25) > 30

        for supplement in supplements:
            supplement_dosing = {}
            for _, row in df.iterrows():
                if supplement.lower() in str(row.get('recommended_supplements', '')).lower():
                    if is_pregnant or demographic_data.get('is_breastfeeding', False):
                        supplement_dosing['recommended'] = row.get('dosing_pregnant_nursing', '')
                    elif age >= 65:
                        supplement_dosing['recommended'] = row.get('dosing_elderly', '')
                    elif age < 2:
                        supplement_dosing['recommended'] = row.get('dosing_children_0_2', '')
                    elif age < 12:
                        supplement_dosing['recommended'] = row.get('dosing_children_2_12', '')
                    elif age < 18:
                        supplement_dosing['recommended'] = row.get('dosing_teens_12_18', '')
                    elif is_obese:
                        supplement_dosing['recommended'] = row.get('dosing_obese', '')
                    elif gender == 'زن':
                        supplement_dosing['recommended'] = row.get('dosing_women', '')
                    else:
                        supplement_dosing['recommended'] = row.get('dosing_men', '')
                    if supplement_dosing['recommended']:
                        break
            if supplement_dosing:
                dosing[supplement] = supplement_dosing
        return dosing

    def _get_safety_level(self, category):
        category = str(category).upper()
        if category in ['A']:
            return 'ایمن'
        elif category in ['B']:
            return 'احتمالاً ایمن'
        elif category in ['C']:
            return 'احتیاط لازم'
        elif category in ['D']:
            return 'خطرناک'
        elif category in ['X']:
            return 'ممنوع مطلق'
        else:
            return 'نامشخص'

    def _calculate_severity_summary(self, results):
        summary = {'high': 0, 'medium': 0, 'low': 0}
        for key, items in results.items():
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict):
                        severity = item.get('severity', '').upper()
                        if severity in ['X', 'D']:
                            summary['high'] += 1
                        elif severity in ['C']:
                            summary['medium'] += 1
                        elif severity in ['A', 'B']:
                            summary['low'] += 1
        return summary

class LabAnalyzer:
    def __init__(self):
        self.normal_ranges = {
            'هموگلوبین': {'min': 12, 'max': 16, 'unit': 'g/dL', 'male_min': 14, 'male_max': 18},
            'فریتین': {'min': 15, 'max': 150, 'unit': 'ng/mL', 'male_min': 30, 'male_max': 400},
            'ویتامین D': {'min': 30, 'max': 50, 'unit': 'ng/mL'},
            'B12': {'min': 200, 'max': 900, 'unit': 'pg/mL'},
            'فولات': {'min': 3, 'max': 17, 'unit': 'ng/mL'},
            'TSH': {'min': 0.4, 'max': 4.0, 'unit': 'mIU/L'},
            'کلسیم': {'min': 8.5, 'max': 10.5, 'unit': 'mg/dL'},
            'منیزیم': {'min': 1.7, 'max': 2.3, 'unit': 'mg/dL'},
            'روی': {'min': 70, 'max': 120, 'unit': 'µg/dL'},
            'آهن': {'min': 60, 'max': 170, 'unit': 'µg/dL'}
        }

    def analyze_lab_results(self, lab_data, demographic_data):
        analysis = {
            'deficiencies': [],
            'excesses': [],
            'normal': [],
            'recommendations': []
        }
        gender = demographic_data.get('gender', 'مرد')
        for test_name, value in lab_data.items():
            if test_name in self.normal_ranges:
                normal_range = self.normal_ranges[test_name]
                min_val = normal_range.get(f'{gender.lower()}_min', normal_range['min'])
                max_val = normal_range.get(f'{gender.lower()}_max', normal_range['max'])
                if value < min_val:
                    severity = self._calculate_deficiency_severity(value, min_val)
                    analysis['deficiencies'].append({
                        'test': test_name,
                        'value': value,
                        'normal_range': f"{min_val}-{max_val} {normal_range['unit']}",
                        'severity': severity
                    })
                elif value > max_val:
                    severity = self._calculate_excess_severity(value, max_val)
                    analysis['excesses'].append({
                        'test': test_name,
                        'value': value,
                        'normal_range': f"{min_val}-{max_val} {normal_range['unit']}",
                        'severity': severity
                    })
                else:
                    analysis['normal'].append({
                        'test': test_name,
                        'value': value,
                        'normal_range': f"{min_val}-{max_val} {normal_range['unit']}"
                    })
        analysis['recommendations'] = self._generate_lab_recommendations(analysis)
        return analysis

    def _calculate_deficiency_severity(self, value, min_normal):
        deficit_percentage = ((min_normal - value) / min_normal) * 100
        if deficit_percentage >= 50:
            return 'شدید'
        elif deficit_percentage >= 25:
            return 'متوسط'
        else:
            return 'خفیف'

    def _calculate_excess_severity(self, value, max_normal):
        excess_percentage = ((value - max_normal) / max_normal) * 100
        if excess_percentage >= 50:
            return 'شدید'
        elif excess_percentage >= 25:
            return 'متوسط'
        else:
            return 'خفیف'

    def _generate_lab_recommendations(self, analysis):
        recommendations = []
        for deficiency in analysis['deficiencies']:
            test = deficiency['test']
            severity = deficiency['severity']
            if test == 'ویتامین D':
                if severity == 'شدید':
                    recommendations.append("💊 ویتامین D3: 4000 واحد روزانه به مدت 3 ماه")
                elif severity == 'متوسط':
                    recommendations.append("💊 ویتامین D3: 2000 واحد روزانه به مدت 2 ماه")
                else:
                    recommendations.append("💊 ویتامین D3: 1000 واحد روزانه")
            elif test == 'هموگلوبین':
                recommendations.append("🔍 بررسی علت کم‌خونی و مصرف مکمل مناسب")
                recommendations.append("🥩 افزایش مصرف غذاهای غنی از آهن")
            elif test == 'B12':
                if severity == 'شدید':
                    recommendations.append("💉 B12: 2000 میکروگرم روزانه یا تزریق")
                else:
                    recommendations.append("💊 B12: 1000 میکروگرم روزانه")
            elif test == 'فریتین':
                recommendations.append("🔬 بررسی آهن سرم و TIBC")
                recommendations.append("💊 آهن: 30-60 میلی‌گرم روزانه با ویتامین C")
        if analysis['deficiencies']:
            recommendations.append("🏥 مراجعه به پزشک برای بررسی بیشتر")
            recommendations.append("🔄 تکرار آزمایش‌ها پس از 2-3 ماه")
        return recommendations

class AuthManager:
    def __init__(self, db_manager):
        self.db = db_manager
        with get_db_connection(self.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            if not cursor.fetchone():
                st.error("جدول users وجود ندارد!")
                raise Exception("Users table not found")

    def hash_password(self, password):
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def register_user(self, phone, first_name, last_name, password):
        with get_db_connection(self.db.db_path) as conn:
            cursor = conn.cursor()
            try:
                password_hash = self.hash_password(password)
                cursor.execute("""
                INSERT INTO users (phone, first_name, last_name, password_hash)
                VALUES (?, ?, ?, ?)
                """, (phone, first_name, last_name, password_hash))
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False
            except Exception:
                return False

    def login_user(self, phone, password):
        with get_db_connection(self.db.db_path) as conn:
            cursor = conn.cursor()
            password_hash = self.hash_password(password)
            cursor.execute("""
            SELECT id, first_name, last_name, is_admin FROM users
            WHERE phone = ? AND password_hash = ?
            """, (phone, password_hash))
            result = cursor.fetchone()
            if result:
                return {
                    'success': True,
                    'user_id': result[0],
                    'first_name': result[1],
                    'last_name': result[2],
                    'is_admin': result[3] if len(result) > 3 else False
                }
        return {'success': False}

class OnlineShop:
    def __init__(self, db_manager):
        self.db = db_manager
        self.zarinpal_merchant = "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
        self.zarinpal_callback_url = "http://localhost:8501/verify"

    def get_products(self, include_inactive=False):
        with get_db_connection(self.db.db_path) as conn:
            query = "SELECT * FROM products WHERE active = TRUE ORDER BY category, name" if not include_inactive else "SELECT * FROM products ORDER BY category, name"
            df = pd.read_sql_query(query, conn)
        return df.to_dict('records')

    def add_to_cart(self, product_id, quantity=1):
        if 'cart' not in st.session_state:
            st.session_state.cart = {}
        if product_id in st.session_state.cart:
            st.session_state.cart[product_id] += quantity
        else:
            st.session_state.cart[product_id] = quantity
        return True

    def get_cart_items(self):
        if 'cart' not in st.session_state:
            return []
        cart_items = []
        with get_db_connection(self.db.db_path) as conn:
            for product_id, quantity in st.session_state.cart.items():
                query = "SELECT * FROM products WHERE id = ?"
                product = pd.read_sql_query(query, conn, params=[product_id])
                if not product.empty:
                    item = product.iloc[0].to_dict()
                    item['quantity'] = quantity
                    item['total_price'] = item['price'] * quantity
                    cart_items.append(item)
        return cart_items

    def calculate_total(self):
        cart_items = self.get_cart_items()
        return sum(item['total_price'] for item in cart_items)

    def get_product_recommendations(self, product_id):
        with get_db_connection(self.db.db_path) as conn:
            query = """
            SELECT p.* FROM products p
            JOIN related_products rp ON p.id = rp.related_product_id
            WHERE rp.product_id = ? AND p.active = TRUE
            LIMIT 3
            """
            df = pd.read_sql_query(query, conn, params=[product_id])
        return df.to_dict('records')

    def get_discount_price(self, product_id):
        with get_db_connection(self.db.db_path) as conn:
            query = """
            SELECT discount_percent FROM product_discounts
            WHERE product_id = ? AND date('now') BETWEEN start_date AND end_date
            """
            cursor = conn.cursor()
            cursor.execute(query, (product_id,))
            result = cursor.fetchone()
        return result[0] if result else 0

class SupplementAnalysisUI:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.interaction_analyzer = InteractionAnalyzer(self.db_manager)
        self.lab_analyzer = LabAnalyzer()
        self.auth_manager = AuthManager(self.db_manager)
        self.shop = OnlineShop(self.db_manager)
        self.online_search = OnlineSearch()
        self.admin_manager = AdminManager(self.db_manager)

        if 'logged_in' not in st.session_state:
            st.session_state.logged_in = False
        if 'user_data' not in st.session_state:
            st.session_state.user_data = {}
        if 'analysis_results' not in st.session_state:
            st.session_state.analysis_results = {}
        if 'cart' not in st.session_state:
            st.session_state.cart = {}
        if 'selected_product' not in st.session_state:
            st.session_state.selected_product = None
        if 'cart_updated' not in st.session_state:
            st.session_state.cart_updated = False

    def run(self):
        load_css()
        self.render_header()

        if st.session_state.logged_in:
            if st.session_state.user_data.get('is_admin', False):
                self.render_admin_section()
            self.render_main_menu()
        else:
            self.render_auth_section()

    def render_header(self):
        st.markdown("""
        <div class="header-container">
            <h1 class="header-title">🔬 سیستم تحلیل تداخلات دارویی و مکمل‌ها</h1>
            <p class="header-subtitle">تحلیل هوشمند و ایمن مکمل‌های غذایی بر اساس وضعیت سلامت فردی</p>
        </div>
        """, unsafe_allow_html=True)

    def render_auth_section(self):
        tab1, tab2 = st.tabs(["ورود", "ثبت‌نام"])
        with tab1:
            st.markdown('<div class="demographic-form">', unsafe_allow_html=True)
            st.subheader("ورود به سیستم")
            phone = st.text_input("شماره همراه", placeholder="09123456789")
            password = st.text_input("رمز عبور", type="password")
            if st.button("ورود", key="login_btn"):
                if phone and password:
                    result = self.auth_manager.login_user(phone, password)
                    if result['success']:
                        st.session_state.logged_in = True
                        st.session_state.user_data = result
                        st.success("ورود موفقیت‌آمیز بود!")
                        st.rerun()
                    else:
                        st.error("شماره همراه یا رمز عبور اشتباه است!")
                else:
                    st.error("لطفاً تمام فیلدها را پر کنید!")
            st.markdown('</div>', unsafe_allow_html=True)

        with tab2:
            st.markdown('<div class="demographic-form">', unsafe_allow_html=True)
            st.subheader("ثبت‌نام در سیستم")
            first_name = st.text_input("نام")
            last_name = st.text_input("نام خانوادگی")
            phone_reg = st.text_input("شماره همراه", placeholder="09123456789", key="phone_reg")
            password_reg = st.text_input("رمز عبور", type="password", key="password_reg")
            password_confirm = st.text_input("تأیید رمز عبور", type="password")
            if st.button("ثبت‌نام", key="register_btn"):
                if all([first_name, last_name, phone_reg, password_reg, password_confirm]):
                    if password_reg == password_confirm:
                        if self.auth_manager.register_user(phone_reg, first_name, last_name, password_reg):
                            st.success("ثبت‌نام با موفقیت انجام شد!")
                        else:
                            st.error("خطا در ثبت‌نام!")
                    else:
                        st.error("رمز عبور و تأیید آن یکسان نیستند!")
                else:
                    st.error("لطفاً تمام فیلدها را پر کنید!")
            st.markdown('</div>', unsafe_allow_html=True)

    def render_admin_section(self):
        if st.sidebar.checkbox("مدیریت سایت", key="admin_toggle"):
            st.sidebar.subheader("مدیریت سایت")
            admin_option = st.sidebar.selectbox(
                "انتخاب بخش مدیریت",
                ["ویرایش درباره ما", "ویرایش اطلاعات تماس", "مدیریت محصولات"]
            )
            if admin_option == "ویرایش درباره ما":
                self.render_about_us_editor()
            elif admin_option == "ویرایش اطلاعات تماس":
                self.render_contact_info_editor()
            elif admin_option == "مدیریت محصولات":
                self.render_product_manager()

    def render_about_us_editor(self):
        st.header("ویرایش بخش درباره ما")
        st.markdown('<div class="demographic-form">', unsafe_allow_html=True)
        current_about_us = self.admin_manager.get_about_us()
        new_about_us = st.text_area("متن درباره ما", value=current_about_us, height=300)
        if st.button("ذخیره تغییرات"):
            self.admin_manager.update_about_us(new_about_us)
            st.success("تغییرات با موفقیت ذخیره شد!")
        st.markdown('</div>', unsafe_allow_html=True)

    def render_contact_info_editor(self):
        st.header("ویرایش اطلاعات تماس")
        st.markdown('<div class="demographic-form">', unsafe_allow_html=True)
        contact_info = self.admin_manager.get_contact_info()
        address = st.text_input("آدرس داروخانه", value=contact_info['pharmacy_address'])
        phone = st.text_input("شماره تلفن", value=contact_info['pharmacy_phone'])
        email = st.text_input("ایمیل پشتیبانی", value=contact_info['support_email'])
        if st.button("ذخیره تغییرات"):
            self.admin_manager.update_contact_info(address, phone, email)
            st.success("تغییرات با موفقیت ذخیره شد!")
        st.markdown('</div>', unsafe_allow_html=True)

    def save_product(self, product_id, name, category, price, description, image_url, stock, discount):
        if not all([name, category, price, description, stock]):
            st.error("لطفاً تمام فیلدهای مورد نیاز را پر کنید!")
            return

        name = bleach.clean(name)
        description = bleach.clean(description)

        with get_db_connection(self.db_manager.db_path) as conn:
            cursor = conn.cursor()
            try:
                if product_id > 0:
                    cursor.execute("""
                    UPDATE products
                    SET name=?, category=?, price=?, description=?, image_url=?, stock=?
                    WHERE id=?
                    """, (name, category, price, description, image_url, stock, product_id))
                    cursor.execute("DELETE FROM product_discounts WHERE product_id=?", (product_id,))
                    if discount > 0:
                        cursor.execute("""
                        INSERT INTO product_discounts (product_id, discount_percent, start_date, end_date)
                        VALUES (?, ?, DATE('now'), DATE('now', '+30 days'))
                        """, (product_id, discount))
                else:
                    cursor.execute("""
                    INSERT INTO products (name, category, price, description, image_url, stock)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """, (name, category, price, description, image_url, stock))
                    product_id = cursor.lastrowid
                    if discount > 0:
                        cursor.execute("""
                        INSERT INTO product_discounts (product_id, discount_percent, start_date, end_date)
                        VALUES (?, ?, DATE('now'), DATE('now', '+30 days'))
                        """, (product_id, discount))
                conn.commit()
                st.success("محصول با موفقیت ذخیره شد!")
            except Exception as e:
                st.error(f"خطا در ذخیره محصول: {str(e)}")

    def delete_product(self, product_id):
        with get_db_connection(self.db_manager.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
                cursor.execute("DELETE FROM product_discounts WHERE product_id=?", (product_id,))
                conn.commit()
                st.success("محصول با موفقیت حذف شد!")
            except Exception as e:
                st.error(f"خطا در حذف محصول: {str(e)}")

    def render_product_manager(self):
        st.header("مدیریت محصولات")
        with st.form("product_form"):
            st.subheader("افزودن/ویرایش محصول")
            product_id = st.number_input("ID محصول (برای ویرایش موجود)", min_value=0, value=0)
            name = st.text_input("نام محصول")
            category = st.text_input("دسته‌بندی")
            price = st.number_input("قیمت (تومان)", min_value=0, value=0)
            description = st.text_area("توضیحات محصول")
            image_url = st.text_input("URL تصویر محصول")
            stock = st.number_input("موجودی", min_value=0, value=0)
            discount = st.number_input("تخفیف (%)", min_value=0, max_value=100, value=0)
            submitted = st.form_submit_button("ذخیره محصول")
            if submitted:
                self.save_product(product_id, name, category, price, description, image_url, stock, discount)

        st.subheader("محصولات موجود")
        products = self.shop.get_products(include_inactive=True)
        for product in products:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{product['name']}** - {product['price']:,} تومان")
                st.caption(product['description'][:100] + "...")
            with col2:
                if st.button("ویرایش", key=f"edit_{product['id']}"):
                    st.session_state.selected_product = product['id']
                    st.rerun()
            with col3:
                if st.button("حذف", key=f"delete_{product['id']}"):
                    self.delete_product(product['id'])
                    st.rerun()

    def render_main_menu(self):
        st.sidebar.title("منو")
        menu = st.sidebar.selectbox(
            "انتخاب بخش",
            ["تحلیل مکمل‌ها", "نتایج قبلی", "فروشگاه", "جستجوی آنلاین"]
        )

        if menu == "تحلیل مکمل‌ها":
            self.render_supplement_analysis()
        elif menu == "نتایج قبلی":
            self.render_history()
        elif menu == "فروشگاه":
            self.render_shop()
        elif menu == "جستجوی آنلاین":
            self.render_online_search()

    def render_supplement_analysis(self):
        st.header("تحلیل مکمل‌ها و تداخلات دارویی")
        st.markdown('<div class="demographic-form">', unsafe_allow_html=True)

        with st.form("demographic_form"):
            st.subheader("اطلاعات دموگرافیک")
            age = st.number_input("سن", min_value=0, max_value=120, value=30)
            gender = st.selectbox("جنسیت", ["مرد", "زن"])
            is_pregnant = st.checkbox("باردار هستم")
            is_breastfeeding = st.checkbox("شیرده هستم")
            weight = st.number_input("وزن (کیلوگرم)", min_value=0, value=70)
            height = st.number_input("قد (سانتیمتر)", min_value=0, value=170)
            bmi = weight / ((height / 100) ** 2)
            st.write(f"شاخص توده بدنی (BMI): {bmi:.1f}")

            submitted_demographic = st.form_submit_button("ذخیره اطلاعات دموگرافیک")
            if submitted_demographic:
                st.session_state.demographic_data = {
                    'age': age,
                    'gender': gender,
                    'is_pregnant': is_pregnant,
                    'is_breastfeeding': is_breastfeeding,
                    'bmi': bmi
                }
                st.success("اطلاعات دموگرافیک ذخیره شد!")

        with st.form("analysis_form"):
            st.subheader("ورود اطلاعات")
            supplements = st.text_area("مکمل‌ها (هر خط یک مکمل)", placeholder="مثال: ویتامین D\nامگا 3").splitlines()
            medications = st.text_area("داروها (هر خط یک دارو)", placeholder="مثال: آسپرین\nمتفورمین").splitlines()
            conditions = st.text_area("بیماری‌ها/وضعیت‌ها (هر خط یک مورد)", placeholder="مثال: دیابت\nفشار خون").splitlines()
            lab_results = {}
            lab_section = st.expander("ورود نتایج آزمایش (اختیاری)")
            with lab_section:
                for test in self.lab_analyzer.normal_ranges.keys():
                    value = st.number_input(f"{test} (مقدار)", value=0.0, step=0.1)
                    if value > 0:
                        lab_results[test] = value

            submitted = st.form_submit_button("تحلیل")
            if submitted:
                if st.session_state.demographic_data:
                    demographic_data = st.session_state.demographic_data
                else:
                    demographic_data = {'age': 30, 'gender': 'مرد', 'is_pregnant': False, 'is_breastfeeding': False, 'bmi': 25}

                supplements = [s.strip() for s in supplements if s.strip()]
                medications = [m.strip() for m in medications if m.strip()]
                conditions = [c.strip() for c in conditions if c.strip()]

                if supplements or medications or conditions or lab_results:
                    results = self.interaction_analyzer.analyze_interactions(supplements, medications, conditions, demographic_data)
                    lab_analysis = self.lab_analyzer.analyze_lab_results(lab_results, demographic_data)
                    st.session_state.analysis_results = {
                        'interaction_results': results,
                        'lab_results': lab_analysis
                    }
                    st.success("تحلیل با موفقیت انجام شد!")
                    self.render_analysis_results()
                else:
                    st.error("لطفاً حداقل یک مورد (مکمل، دارو، بیماری یا آزمایش) وارد کنید!")

        st.markdown('</div>', unsafe_allow_html=True)

    def render_analysis_results(self):
        if 'analysis_results' in st.session_state:
            st.header("نتایج تحلیل")
            st.markdown('<div class="analysis-result">', unsafe_allow_html=True)

            results = st.session_state.analysis_results
            interaction_results = results.get('interaction_results', {})
            lab_results = results.get('lab_results', {})

            # نمایش تداخلات مکمل-دارو
            if interaction_results.get('supplement_drug_interactions'):
                st.subheader("تداخلات مکمل-دارو")
                for interaction in interaction_results['supplement_drug_interactions']:
                    with st.expander(f"{interaction['supplement']} و {interaction['drug']}"):
                        st.markdown('<div class="interaction-card">', unsafe_allow_html=True)
                        st.write(f"**شدت:** {interaction['severity']}")
                        st.write(f"**نوع تداخل:** {interaction['interaction_type']}")
                        st.write(f"**توصیه بالینی:** {interaction['clinical_advice']}")
                        st.write(f"**گروه حساس:** {interaction['risk_group']}")
                        st.write(f"**منبع:** {interaction['source']}")
                        st.markdown('</div>', unsafe_allow_html=True)

            # نمایش تداخلات مکمل-بیماری
            if interaction_results.get('supplement_condition_interactions'):
                st.subheader("تداخلات مکمل-بیماری")
                for interaction in interaction_results['supplement_condition_interactions']:
                    with st.expander(f"{interaction['supplement']} و {interaction['condition']}"):
                        st.markdown('<div class="disease-card">', unsafe_allow_html=True)
                        st.write(f"**شدت:** {interaction['severity']}")
                        st.write(f"**توصیه بالینی:** {interaction['clinical_advice']}")
                        st.write(f"**مکانیسم:** {interaction['mechanism']}")
                        st.write(f"**منبع:** {interaction['source']}")
                        st.markdown('</div>', unsafe_allow_html=True)

            # نمایش ایمنی بارداری
            if interaction_results.get('pregnancy_safety'):
                st.subheader("ایمنی در بارداری")
                for safety in interaction_results['pregnancy_safety']:
                    with st.expander(f"{safety['supplement']}"):
                        st.markdown('<div class="pregnancy-card">', unsafe_allow_html=True)
                        st.write(f"**رده بارداری:** {safety['pregnancy_category']}")
                        st.write(f"**سطح ایمنی:** {safety['safety_level']}")
                        st.write(f"**توصیه بالینی:** {safety['clinical_advice']}")
                        st.write(f"**هشدار مصرف:** {safety['use_warning']}")
                        st.write(f"**آستانه سمی:** {safety['toxic_threshold']}")
                        st.write(f"**منابع:** {safety['sources']}")
                        st.markdown('</div>', unsafe_allow_html=True)

            # نمایش توصیه‌های بیماری
            if interaction_results.get('disease_recommendations'):
                st.subheader("توصیه‌های بیماری")
                for rec in interaction_results['disease_recommendations']:
                    with st.expander(f"{rec['disease']}"):
                        st.markdown('<div class="disease-card">', unsafe_allow_html=True)
                        st.write(f"**گروه آسیب‌پذیر:** {rec['vulnerable_group']}")
                        st.write(f"**آزمایش‌های پیشنهادی:** {rec['recommended_tests']}")
                        st.write(f"**نکات بالینی:** {rec['clinical_notes']}")
                        st.write(f"**مکمل‌های پیشنهادی:** {rec['recommended_supplements']}")
                        st.write(f"**رژیم غذایی حمایتی:** {rec['supportive_diet']}")
                        st.write(f"**تناوب نظارت:** {rec['monitoring_frequency']}")
                        st.write(f"**منبع:** {rec['source']}")
                        st.markdown('</div>', unsafe_allow_html=True)

            # نمایش دوزینگ شخصی‌سازی‌شده
            if interaction_results.get('personalized_dosing'):
                st.subheader("دوزینگ شخصی‌سازی‌شده")
                for supp, dosing in interaction_results['personalized_dosing'].items():
                    st.write(f"**{supp}:** {dosing['recommended']}")

            # نمایش خلاصه شدت
            st.subheader("خلاصه شدت تداخلات")
            severity_summary = interaction_results.get('severity_summary', {})
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("بالا", severity_summary.get('high', 0))
                st.markdown('</div>', unsafe_allow_html=True)
            with col2:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("متوسط", severity_summary.get('medium', 0))
                st.markdown('</div>', unsafe_allow_html=True)
            with col3:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("پایین", severity_summary.get('low', 0))
                st.markdown('</div>', unsafe_allow_html=True)

            # نمایش نتایج آزمایش
            if lab_results.get('deficiencies') or lab_results.get('excesses') or lab_results.get('normal'):
                st.subheader("نتایج آزمایش")
                if lab_results.get('deficiencies'):
                    st.subheader("کمبودها")
                    for defic in lab_results['deficiencies']:
                        st.write(f"**{defic['test']}:** {defic['value']} (رنج نرمال: {defic['normal_range']}, شدت: {defic['severity']})")
                if lab_results.get('excesses'):
                    st.subheader("افزایش‌ها")
                    for excess in lab_results['excesses']:
                        st.write(f"**{excess['test']}:** {excess['value']} (رنج نرمال: {excess['normal_range']}, شدت: {excess['severity']})")
                if lab_results.get('normal'):
                    st.subheader("نرمال")
                    for normal in lab_results['normal']:
                        st.write(f"**{normal['test']}:** {normal['value']} (رنج نرمال: {normal['normal_range']})")
                if lab_results.get('recommendations'):
                    st.subheader("توصیه‌ها")
                    for rec in lab_results['recommendations']:
                        st.write(rec)

            st.markdown('</div>', unsafe_allow_html=True)

    def render_history(self):
        st.header("تاریخچه تحلیل‌ها")
        with get_db_connection(self.db_manager.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT results FROM analyses WHERE user_id = ?", (st.session_state.user_data['user_id'],))
            results = cursor.fetchall()
            if results:
                for result in results:
                    st.json(json.loads(result[0]))
            else:
                st.info("هیچ تحلیل قبلی یافت نشد.")

    def render_shop(self):
        st.header("فروشگاه آنلاین مکمل‌ها")
        st.markdown('<div class="shop-card">', unsafe_allow_html=True)
        products = self.shop.get_products()
        for product in products:
            with st.expander(f"{product['name']} - {product['price']:,} تومان"):
                st.image(product['image_url'], width=200)
                st.write(f"**دسته‌بندی:** {product['category']}")
                st.write(f"**توضیحات:** {product['description']}")
                st.write(f"**موجودی:** {product['stock']}")
                discount = self.shop.get_discount_price(product['id'])
                if discount > 0:
                    discounted_price = product['price'] * (1 - discount / 100)
                    st.write(f"**تخفیف:** {discount}%")
                    st.write(f"**قیمت با تخفیف:** {discounted_price:,.0f} تومان")
                if st.button("افزودن به سبد خرید", key=f"add_to_cart_{product['id']}"):
                    self.shop.add_to_cart(product['id'])
                    st.success("محصول به سبد خرید اضافه شد!")
                recommendations = self.shop.get_product_recommendations(product['id'])
                if recommendations:
                    st.subheader("محصولات مرتبط")
                    for rec in recommendations:
                        st.write(f"- {rec['name']} ({rec['price']:,} تومان)")

        st.subheader("سبد خرید")
        cart_items = self.shop.get_cart_items()
        if cart_items:
            for item in cart_items:
                st.write(f"**{item['name']}** x {item['quantity']} = {item['total_price']:,} تومان")
            total = self.shop.calculate_total()
            st.write(f"**جمع کل:** {total:,} تومان")
            if st.button("پرداخت"):
                self.process_payment(total)
        else:
            st.write("سبد خرید خالی است.")
        st.markdown('</div>', unsafe_allow_html=True)

    def process_payment(self, amount):
        st.warning("پرداخت آنلاین در حال حاضر فقط به صورت نمایشی است!")
        st.write(f"مبلغ قابل پرداخت: {amount:,} تومان")
        payment_url = f"https://www.zarinpal.com/pg/StartPay/{self.shop.zarinpal_merchant}/{amount}"
        st.write(f"لینک پرداخت نمایشی: {payment_url}")
        if st.button("تأیید پرداخت (نمایش)") and st.session_state.cart:
            st.success("پرداخت با موفقیت انجام شد (نمایش)!")
            st.session_state.cart = {}
            st.rerun()

    def render_online_search(self):
        st.header("جستجوی آنلاین")
        query = st.text_input("عبارت جستجو")
        if st.button("جستجو"):
            if query:
                results = self.online_search.search_all(query)
                if results:
                    for result in results:
                        with st.expander(f"{result['title_persian']} ({result['source']})"):
                            st.write(f"**عنوان اصلی:** {result['title']}")
                            st.write(f"**منبع:** {result['source']}")
                            st.write(f"**لینک:** [برو به منبع]({result['url']})")
                            if 'pub_date' in result:
                                st.write(f"**تاریخ انتشار:** {result['pub_date']}")
                            if 'authors' in result:
                                st.write(f"**نویسندگان:** {result['authors']}")
                else:
                    st.warning("هیچ نتیجه‌ای یافت نشد.")
            else:
                st.error("لطفاً عبارت جستجو را وارد کنید!")

if __name__ == "__main__":
    app = SupplementAnalysisUI()
    app.run()
