متوجه شدم. شما فایل دیتابیس با نام خاصی دارید و فایل‌های CSV در پوشه data قرار دارند. برای اینکه برنامه بتواند این فایل‌ها را پیدا کند، باید تغییرات زیر را اعمال کنیم:

```python
import streamlit as st
import pandas as pd
import numpy as np
import json
import hashlib
try:
    import pysqlite3 as sqlite3
except ImportError:
    import sqlite3

# ایجاد ویژگی version_info برای هر دو حالت
if not hasattr(sqlite3, 'sqlite_version_info'):
    sqlite3.sqlite_version_info = tuple(map(int, sqlite3.sqlite_version.split('.')))
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re
from typing import Dict, List, Tuple, Any, Optional
import base64
from io import BytesIO
import requests
import os
from pathlib import Path

# تنظیمات صفحه
st.set_page_config(
    page_title="سیستم تحلیل تداخلات دارویی",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# استایل‌های CSS برای طراحی
def load_css():
    st.markdown("""
    <style>
    /* پالت رنگی سفارشی */
    :root {
        --primary-ultralight: #F0FFFF;  /* فیروزه‌ای خیلی خیلی روشن */
        --primary-light: #E0F7FA;       /* فیروزه‌ای خیلی روشن */
        --primary: #4DB6AC;             /* فیروزه‌ای اصلی */
        --primary-dark: #00897B;        /* فیروزه‌ای تیره */
        --secondary-light: #FFECB3;     /* نارنجی فسفری خیلی روشن */
        --secondary: #FFB74D;           /* نارنجی فسفری اصلی */
        --secondary-dark: #FF9800;      /* نارنجی فسفری تیره */
    }
    
    /* استایل اصلی برنامه */
    .main, .stApp {
        background-color: var(--primary-ultralight) !important;
        font-family: 'Vazir', 'Segoe UI', Tahoma, sans-serif;
    }
    
    /* هدر */
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
    
    /* کارت محصولات */
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
    
    /* دکمه‌ها */
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
    
    /* نوار کناری */
    .sidebar .sidebar-content {
        background-color: var(--primary-light) !important;
    }
    
    /* کارت‌های ویژه */
    .interaction-card {
        border-left: 5px solid var(--secondary) !important;
    }
    
    .warning-card {
        border-left: 5px solid var(--secondary-dark) !important;
    }
    
    /* هایلایت‌ها */
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
    
    .warning-card {
        background: white;
        border-left: 5px solid #FFE66D;
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
    """, unsafe_allow_html=True)
    
    # اضافه کردن فونت فارسی
    st.markdown("""
    <link href='https://fonts.googleapis.com/css2?family=Vazir:wght@300;400;500;700&display=swap' rel='stylesheet'>
    """, unsafe_allow_html=True)

class DatabaseManager:
    def __init__(self, db_path: str = "output(2)(1).sqlite") -> None:
        """Initialize database with thread safety support"""
        self.db_path = db_path  # ذخیره مسیر دیتابیس
        self.data_dir: Path = Path("data/")
        self._ensure_data_dir()
        self.init_database()
        self.load_all_csv_data()  # بارگذاری خودکار داده‌های CSV
    
    def _ensure_data_dir(self) -> None:
        """Create data directory if not exists"""
        os.makedirs(self.data_dir, exist_ok=True)
    
    def init_database(self):
        try:
            # ایجاد دایرکتوری اگر وجود ندارد
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone TEXT UNIQUE NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                demographic_data TEXT,
                supplements TEXT,
                medications TEXT,
                conditions TEXT,
                results TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """)
            
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS diseases_supplements (
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
            )
            """)
            
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS pregnancy_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                compound TEXT,
                pregnancy_category TEXT,
                clinical_advice TEXT,
                use_warning TEXT,
                toxic_threshold TEXT,
                sources TEXT
            )
            """)
            
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS supplement_drug_interactions (
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
            )
            """)
            
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS supplement_condition_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                compound TEXT,
                condition_disease TEXT,
                severity TEXT,
                clinical_advice TEXT,
                mechanism TEXT,
                source TEXT
            )
            """)
            
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                price INTEGER,
                description TEXT,
                image_url TEXT,
                stock INTEGER DEFAULT 0,
                active BOOLEAN DEFAULT TRUE
            )
            """)
            
            # اضافه کردن جدول sessions برای مدیریت نشست‌های کاربری
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """)
            
            conn.commit()
            conn.close()
            st.success("✅ پایگاه داده با موفقیت راه‌اندازی شد!")
        except Exception as e:
            st.error(f"خطا در راه‌اندازی پایگاه داده: {str(e)}")
            # استفاده از پایگاه داده در حافظه به عنوان جایگزین
            st.info("از پایگاه داده موقت در حافظه استفاده می‌شود")
            self.db_path = ":memory:"
    
    def load_all_csv_data(self):
        try:
            conn = sqlite3.connect(self.db_path)
            csv_mappings = {
                'sheet1.csv': 'diseases_supplements',
                'sheet2.csv': 'pregnancy_categories',
                'sheet3.csv': 'supplement_drug_interactions',
                'sheet4.csv': 'supplement_condition_interactions'
            }
            
            loaded_files = 0
            for csv_file, table_name in csv_mappings.items():
                file_path = self.data_dir / csv_file
                if file_path.exists():
                    df = None
                    encodings = ['utf-8-sig', 'utf-8', 'cp1256', 'iso-8859-1', 'windows-1256']
                    for encoding in encodings:
                        try:
                            df = pd.read_csv(file_path, encoding=encoding)
                            break
                        except (UnicodeDecodeError, UnicodeError):
                            continue
                    
                    if df is not None and not df.empty:
                        df = df.dropna(how='all', axis=1)
                        df = df.dropna(how='all', axis=0)
                        df.columns = df.columns.str.strip()
                        df = self._standardize_column_names(df, table_name)
                        df.to_sql(table_name, conn, if_exists='replace', index=False)
                        loaded_files += 1
                        st.success(f"✅ فایل {csv_file} با موفقیت بارگذاری شد!")
            
            conn.close()
            if loaded_files > 0:
                st.success(f"✅ {loaded_files} فایل CSV با موفقیت بارگذاری شد!")
            else:
                st.warning("⚠️ هیچ فایل CSV قابل خواندنی یافت نشد!")
        except Exception as e:
            st.error(f"خطا در بارگذاری داده‌ها: {str(e)}")
    
    def _standardize_column_names(self, df, table_name):
        column_mapping = {}
        if table_name == 'diseases_supplements':
            column_mapping = {
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
                'منبع': 'source'
            }
        elif table_name == 'pregnancy_categories':
            column_mapping = {
                'ماده فعال / Compound': 'compound',
                'رده بارداری/شیردهی (A–X)': 'pregnancy_category',
                'توصیه بالینی / Clinical Advice': 'clinical_advice',
                'هشدار مصرف / Use Warning': 'use_warning',
                'دوز خطرناک / Toxic Threshold': 'toxic_threshold',
                'منابع / Sources': 'sources'
            }
        elif table_name == 'supplement_drug_interactions':
            column_mapping = {
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
                'منبع / Source': 'source'
            }
        elif table_name == 'supplement_condition_interactions':
            column_mapping = {
                'ماده فعال / Compound': 'compound',
                'بیماری / Condition': 'condition_disease',
                'شدت تداخل (A–X) / Severity': 'severity',
                'توصیه بالینی / Clinical Advice': 'clinical_advice',
                'مکانیسم / Mechanism': 'mechanism',
                'منبع / Source': 'source'
            }
        
        if column_mapping:
            df = df.rename(columns=column_mapping)
        return df
    
    def add_sample_products(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
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
            conn.close()
            st.success("✅ محصولات نمونه با موفقیت اضافه شدند!")
        except Exception as e:
            st.error(f"خطا در افزودن محصولات نمونه: {str(e)}")

# بقیه کد بدون تغییر می‌ماند...
# فقط مطمئن شوید که تمام کلاس‌ها و توابع قبلی در اینجا کپی شده‌اند

# کلاس تحلیل تداخلات
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
        
        try:
            conn = sqlite3.connect(self.db.db_path)
            results['supplement_drug_interactions'] = self._analyze_supplement_drug_interactions(supplements, medications, conn)
            results['supplement_condition_interactions'] = self._analyze_supplement_condition_interactions(supplements, conditions, conn)
            
            if demographic_data.get('is_pregnant') or demographic_data.get('is_breastfeeding'):
                results['pregnancy_safety'] = self._analyze_pregnancy_safety(supplements, conn)
            
            results['disease_recommendations'] = self._analyze_disease_recommendations(conditions, demographic_data, conn)
            results['personalized_dosing'] = self._get_personalized_dosing(supplements, demographic_data, conn)
            results['severity_summary'] = self._calculate_severity_summary(results)
            conn.close()
        except Exception as e:
            st.error(f"خطا در تحلیل تداخلات: {str(e)}")
        
        return results
    
    # بقیه متدهای این کلاس بدون تغییر...

# کلاس تحلیل آزمایش
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
    
    # بقیه متدهای این کلاس بدون تغییر...

# کلاس احراز هویت
class AuthManager:
    def __init__(self, db_manager):
        self.db = db_manager
    
    # بقیه متدهای این کلاس بدون تغییر...

# کلاس فروشگاه آنلاین
class OnlineShop:
    def __init__(self, db_manager):
        self.db = db_manager
        self.zarinpal_merchant = "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
        self.zarinpal_callback_url = "http://localhost:8501/verify"
    
    # بقیه متدهای این کلاس بدون تغییر...

# کلاس رابط کاربری اصلی
class SupplementAnalysisUI:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.interaction_analyzer = InteractionAnalyzer(self.db_manager)
        self.lab_analyzer = LabAnalyzer()
        self.auth_manager = AuthManager(self.db_manager)
        self.shop = OnlineShop(self.db_manager)
        self.db_manager.add_sample_products()
        
        if 'logged_in' not in st.session_state:
            st.session_state.logged_in = False
        if 'user_data' not in st.session_state:
            st.session_state.user_data = {}
        if 'analysis_results' not in st.session_state:
            st.session_state.analysis_results = {}
        if 'cart' not in st.session_state:
            st.session_state.cart = {}
    
    # بقیه متدهای این کلاس بدون تغییر...

# تابع اصلی برای اجرای برنامه
def main():
    app = SupplementAnalysisUI()
    app.run()

if __name__ == "__main__":
    main()
```

**تغییرات اصلی اعمال شده:**

1. **مسیر دیتابیس**: تغییر مسیر پیش‌فرض دیتابیس به `"output(2)(1).sqlite"` که فایل دیتابیس شماست.

2. **بارگذاری خودکار CSV**: افزودن `self.load_all_csv_data()` در constructor کلاس `DatabaseManager` تا داده‌های CSV به صورت خودکار بارگذاری شوند.

3. **پیام‌های اطلاع‌رسانی**: اضافه کردن پیام‌های موفقیت برای هر فایل CSV که با موفقیت بارگذاری می‌شود.

4. **مدیریت خطا**: حفظ سیستم مدیریت خطا برای مواردی که فایل‌های CSV پیدا نشوند یا مشکلی در خواندن آنها وجود داشته باشد.

اکنون برنامه باید بتواند:
- به فایل دیتابیس `output(2)(1).sqlite` متصل شود
- فایل‌های CSV را از پوشه `data` بارگذاری کند (sheet1.csv, sheet2.csv, sheet3.csv, sheet4.csv)
- در صورت عدم وجود فایل‌های CSV، پیام هشدار مناسب نمایش دهد

اگر فایل‌های CSV شما نام‌های متفاوتی دارند یا در مسیر دیگری قرار دارند، لطفاً نام و مسیر آنها را اعلام کنید تا تغییرات لازم را اعمال کنم.
