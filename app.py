import streamlit as st
import pandas as pd
import numpy as np
import json
import hashlib
try:
    import pysqlite3 as sqlite3
except ImportError:
    import sqlite3

‎# ایجاد ویژگی version_info برای هر دو حالت
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

‎# تنظیمات صفحه
st.set_page_config(
    page_title="سیستم تحلیل تداخلات دارویی",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

‎# استایل‌های CSS برای طراحی
def load_css():
    st.markdown("""
    <style>
‎    /* پالت رنگی سفارشی */
    :root {
        --primary-ultralight: #F0FFFF;  /* فیروزه‌ای خیلی خیلی روشن */
        --primary-light: #E0F7FA;       /* فیروزه‌ای خیلی روشن */
        --primary: #4DB6AC;             /* فیروزه‌ای اصلی */
        --primary-dark: #00897B;        /* فیروزه‌ای تیره */
        --secondary-light: #FFECB3;     /* نارنجی فسفری خیلی روشن */
        --secondary: #FFB74D;           /* نارنجی فسفری اصلی */
        --secondary-dark: #FF9800;      /* نارنجی فسفری تیره */
    }
    
‎    /* استایل اصلی برنامه */
    .main, .stApp {
        background-color: var(--primary-ultralight) !important;
        font-family: 'Vazir', 'Segoe UI', Tahoma, sans-serif;
    }
    
‎    /* هدر */
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
    
‎    /* کارت محصولات */
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
    
‎    /* دکمه‌ها */
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
    
‎    /* نوار کناری */
    .sidebar .sidebar-content {
        background-color: var(--primary-light) !important;
    }
    
‎    /* کارت‌های ویژه */
    .interaction-card {
        border-left: 5px solid var(--secondary) !important;
    }
    
    .warning-card {
        border-left: 5px solid var(--secondary-dark) !important;
    }
    
‎    /* هایلایت‌ها */
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
    
‎    # اضافه کردن فونت فارسی
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
‎            # ایجاد دایرکتوری اگر وجود ندارد
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
            
‎            # اضافه کردن جدول sessions برای مدیریت نشست‌های کاربری
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
‎            # استفاده از پایگاه داده در حافظه به عنوان جایگزین
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
‎                'بیماری': 'disease',
‎                'گروه آسیب‌پذیر': 'vulnerable_group',
‎                'آزمایش‌های پیشنهادی': 'recommended_tests',
‎                'نکات بالینی': 'clinical_notes',
‎                'تناوب پیشنهادی': 'monitoring_frequency',
‎                'مکمل‌های پیشنهادی': 'recommended_supplements',
‎                'رژیم غذایی حمایتی': 'supportive_diet',
‎                'دوزینگ زنان': 'dosing_women',
‎                'دوزینگ مردان': 'dosing_men',
‎                'دوزینگ سالمندان': 'dosing_elderly',
‎                'دوزینگ کودک (۰–۲ سال)': 'dosing_children_0_2',
‎                'دوزینگ کودک (۲–۱۲ سال)': 'dosing_children_2_12',
‎                'دوزینگ نوجوان (۱۲–۱۸ سال)': 'dosing_teens_12_18',
‎                'دوزینگ افراد چاق': 'dosing_obese',
‎                'دوزینگ زنان باردار و شیرده': 'dosing_pregnant_nursing',
‎                'منبع': 'source'
            }
        elif table_name == 'pregnancy_categories':
            column_mapping = {
‎                'ماده فعال / Compound': 'compound',
‎                'رده بارداری/شیردهی (A–X)': 'pregnancy_category',
‎                'توصیه بالینی / Clinical Advice': 'clinical_advice',
‎                'هشدار مصرف / Use Warning': 'use_warning',
‎                'دوز خطرناک / Toxic Threshold': 'toxic_threshold',
‎                'منابع / Sources': 'sources'
            }
        elif table_name == 'supplement_drug_interactions':
            column_mapping = {
‎                'گروه مکمل / Supplement Group': 'supplement_group',
‎                'ماده فعال / Compound': 'compound',
‎                'داروی درگیر / Interacting Drug': 'interacting_drug',
‎                'شدت / Severity (A–X)': 'severity',
‎                'نوع تداخل / Type': 'interaction_type',
‎                'هشدار بیماری / Condition Alert': 'condition_alert',
‎                'گروه حساس / Risk Group': 'risk_group',
‎                'دوز پیشنهادی / RDA': 'rda',
‎                'تست / Test': 'test',
‎                'رنج نرمال / Normal Range': 'normal_range',
‎                'توصیه بالینی / Clinical Advice': 'clinical_advice',
‎                'منبع / Source': 'source'
            }
        elif table_name == 'supplement_condition_interactions':
            column_mapping = {
‎                'ماده فعال / Compound': 'compound',
‎                'بیماری / Condition': 'condition_disease',
‎                'شدت تداخل (A–X) / Severity': 'severity',
‎                'توصیه بالینی / Clinical Advice': 'clinical_advice',
‎                'مکانیسم / Mechanism': 'mechanism',
‎                'منبع / Source': 'source'
            }
        
        if column_mapping:
            df = df.rename(columns=column_mapping)
        return df
    
    def add_sample_products(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            sample_products = [
‎                ("ویتامین D3 2000 واحد", "ویتامین‌ها", 250000, "مکمل ویتامین D3 با کیفیت بالا", "https://example.com/vitamin-d.jpg", 50),
‎                ("امگا 3 فیش اویل", "اسیدهای چرب", 180000, "کپسول امگا 3 از روغن ماهی", "https://example.com/omega3.jpg", 30),
‎                ("مولتی ویتامین کامل", "مولتی ویتامین", 320000, "مکمل جامع ویتامین‌ها و مواد معدنی", "https://example.com/multivitamin.jpg", 25),
‎                ("منیزیم 400 میلی‌گرم", "مواد معدنی", 150000, "مکمل منیزیم برای سلامت عضلات", "https://example.com/magnesium.jpg", 40),
‎                ("زینک 30 میلی‌گرم", "مواد معدنی", 120000, "مکمل زینک تقویت‌کننده سیستم ایمنی", "https://example.com/zinc.jpg", 35),
‎                ("ویتامین B12 1000 میکروگرم", "ویتامین‌ها", 200000, "مکمل ویتامین B12 برای انرژی", "https://example.com/b12.jpg", 45),
‎                ("آهن بیس‌گلایسینات", "مواد معدنی", 180000, "مکمل آهن با جذب بهینه", "https://example.com/iron.jpg", 20),
‎                ("کلسیم + ویتامین K2", "مواد معدنی", 220000, "ترکیب کلسیم و ویتامین K2", "https://example.com/calcium.jpg", 30),
‎                ("کوآنزیم Q10", "آنتی‌اکسیدان", 380000, "مکمل کوآنزیم Q10 برای انرژی سلولی", "https://example.com/coq10.jpg", 15),
‎                ("پروبیوتیک 50 میلیارد", "پروبیوتیک", 290000, "کپسول پروبیوتیک با 10 گونه باکتری", "https://example.com/probiotic.jpg", 22)
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

‎# بقیه کدهای کلاس‌ها و توابع...
EOF

‎# کلاس تحلیل تداخلات
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
        
        conn = sqlite3.connect(self.db.db_path)
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
        finally:
            conn.close()
        
        return results
    
    def _analyze_supplement_drug_interactions(self, supplements, medications, conn):
        interactions = []
        try:
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
                        interaction = {
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
                        }
                        interactions.append(interaction)
        except Exception as e:
            st.error(f"خطا در تحلیل تداخلات دارویی: {str(e)}")
        return interactions
    
    def _analyze_supplement_condition_interactions(self, supplements, conditions, conn):
        interactions = []
        try:
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
                        interaction = {
                            'supplement': supplement,
                            'condition': condition,
                            'compound': row.get('compound', ''),
                            'severity': row.get('severity', ''),
                            'clinical_advice': row.get('clinical_advice', ''),
                            'mechanism': row.get('mechanism', ''),
                            'source': row.get('source', '')
                        }
                        interactions.append(interaction)
        except Exception as e:
            st.error(f"خطا در تحلیل تداخلات بیماری: {str(e)}")
        return interactions
    
    def _analyze_pregnancy_safety(self, supplements, conn):
        safety_results = []
        try:
            for supplement in supplements:
                query = """
                SELECT * FROM pregnancy_categories 
                WHERE LOWER(compound) LIKE ?
                """
                params = [f'%{supplement.lower()}%']
                df = pd.read_sql_query(query, conn, params=params)
                
                for _, row in df.iterrows():
                    safety = {
                        'supplement': supplement,
                        'compound': row.get('compound', ''),
                        'pregnancy_category': row.get('pregnancy_category', ''),
                        'clinical_advice': row.get('clinical_advice', ''),
                        'use_warning': row.get('use_warning', ''),
                        'toxic_threshold': row.get('toxic_threshold', ''),
                        'sources': row.get('sources', ''),
                        'safety_level': self._get_safety_level(row.get('pregnancy_category', ''))
                    }
                    safety_results.append(safety)
        except Exception as e:
            st.error(f"خطا در تحلیل ایمنی بارداری: {str(e)}")
        return safety_results
    
    def _analyze_disease_recommendations(self, conditions, demographic_data, conn):
        recommendations = []
        try:
            for condition in conditions:
                query = """
                SELECT * FROM diseases_supplements 
                WHERE LOWER(disease) LIKE ?
                """
                params = [f'%{condition.lower()}%']
                df = pd.read_sql_query(query, conn, params=params)
                
                for _, row in df.iterrows():
                    recommendation = {
                        'disease': condition,
                        'vulnerable_group': row.get('vulnerable_group', ''),
                        'recommended_tests': row.get('recommended_tests', ''),
                        'clinical_notes': row.get('clinical_notes', ''),
                        'recommended_supplements': row.get('recommended_supplements', ''),
                        'supportive_diet': row.get('supportive_diet', ''),
                        'monitoring_frequency': row.get('monitoring_frequency', ''),
                        'source': row.get('source', '')
                    }
                    recommendations.append(recommendation)
        except Exception as e:
            st.error(f"خطا در تحلیل توصیه‌های بیماری: {str(e)}")
        return recommendations
    
    def _get_personalized_dosing(self, supplements, demographic_data, conn):
        dosing = {}
        try:
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
        except Exception as e:
            st.error(f"خطا در تعیین دوزاژ: {str(e)}")
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

‎# کلاس تحلیل آزمایش
class LabAnalyzer:
    def __init__(self):
        self.normal_ranges = {
‎            'هموگلوبین': {'min': 12, 'max': 16, 'unit': 'g/dL', 'male_min': 14, 'male_max': 18},
‎            'فریتین': {'min': 15, 'max': 150, 'unit': 'ng/mL', 'male_min': 30, 'male_max': 400},
‎            'ویتامین D': {'min': 30, 'max': 50, 'unit': 'ng/mL'},
            'B12': {'min': 200, 'max': 900, 'unit': 'pg/mL'},
‎            'فولات': {'min': 3, 'max': 17, 'unit': 'ng/mL'},
            'TSH': {'min': 0.4, 'max': 4.0, 'unit': 'mIU/L'},
‎            'کلسیم': {'min': 8.5, 'max': 10.5, 'unit': 'mg/dL'},
‎            'منیزیم': {'min': 1.7, 'max': 2.3, 'unit': 'mg/dL'},
‎            'روی': {'min': 70, 'max': 120, 'unit': 'µg/dL'},
‎            'آهن': {'min': 60, 'max': 170, 'unit': 'µg/dL'}
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

‎# کلاس احراز هویت
class AuthManager:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, phone, first_name, last_name, password):
        try:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            password_hash = self.hash_password(password)
            cursor.execute("""
            INSERT INTO users (phone, first_name, last_name, password_hash)
            VALUES (?, ?, ?, ?)
            """, (phone, first_name, last_name, password_hash))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
        except Exception:
            return False
    
    def login_user(self, phone, password):
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        password_hash = self.hash_password(password)
        cursor.execute("""
        SELECT id, first_name, last_name FROM users 
        WHERE phone = ? AND password_hash = ?
        """, (phone, password_hash))
        result = cursor.fetchone()
        conn.close()
        if result:
            return {
                'success': True,
                'user_id': result[0],
                'first_name': result[1],
                'last_name': result[2]
            }
        else:
            return {'success': False}

‎# کلاس فروشگاه آنلاین
class OnlineShop:
    def __init__(self, db_manager):
        self.db = db_manager
        self.zarinpal_merchant = "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
        self.zarinpal_callback_url = "http://localhost:8501/verify"
    
    def get_products(self):
        conn = sqlite3.connect(self.db.db_path)
        query = """
        SELECT * FROM products WHERE active = TRUE ORDER BY category, name
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
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
        conn = sqlite3.connect(self.db.db_path)
        for product_id, quantity in st.session_state.cart.items():
            query = "SELECT * FROM products WHERE id = ?"
            product = pd.read_sql_query(query, conn, params=[product_id])
            if not product.empty:
                item = product.iloc[0].to_dict()
                item['quantity'] = quantity
                item['total_price'] = item['price'] * quantity
                cart_items.append(item)
        conn.close()
        return cart_items
    
    def calculate_total(self):
        cart_items = self.get_cart_items()
        return sum(item['total_price'] for item in cart_items)

‎# کلاس رابط کاربری اصلی
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
    
    def run(self):
        load_css()
        self.render_header()
        
        if st.session_state.logged_in:
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
    
    def render_main_menu(self):
        with st.sidebar:
            st.success(f"خوش آمدید {st.session_state.user_data['first_name']}")
            menu_option = st.selectbox(
‎                "انتخاب بخش",
‎                ["تحلیل تداخلات", "فروشگاه مکمل‌ها", "سبد خرید", "تاریخچه آنالیزها"]
            )
            if st.button("خروج"):
                st.session_state.logged_in = False
                st.session_state.user_data = {}
                st.rerun()
        
        if menu_option == "تحلیل تداخلات":
            self.render_analysis_section()
        elif menu_option == "فروشگاه مکمل‌ها":
            self.render_shop_section()
        elif menu_option == "سبد خرید":
            self.render_cart_section()
        elif menu_option == "تاریخچه آنالیزها":
            self.render_history_section()
    
    def render_analysis_section(self):
        st.header("🔬 تحلیل تداخلات دارویی")
        demographic_data = self.render_demographic_form()
        lab_data = self.render_lab_section()
        supplements_data = self.render_supplements_section()
        
        if st.button("🔍 شروع تحلیل", key="analyze_btn", use_container_width=True):
            if supplements_data['supplements']:
                with st.spinner("در حال تحلیل..."):
                    interaction_results = self.interaction_analyzer.analyze_interactions(
                        supplements_data['supplements'],
                        supplements_data['medications'],
                        supplements_data['conditions'],
                        demographic_data
                    )
                    lab_results = self.lab_analyzer.analyze_lab_results(lab_data, demographic_data)
                    st.session_state.analysis_results = {
                        'interactions': interaction_results,
                        'lab_analysis': lab_results,
                        'demographic': demographic_data,
                        'timestamp': datetime.now()
                    }
                    self.render_analysis_results()
            else:
                st.error("لطفاً حداقل یک مکمل را انتخاب کنید!")
    
    def render_demographic_form(self):
        st.markdown('<div class="demographic-form">', unsafe_allow_html=True)
        st.subheader("🧑‍⚕️ اطلاعات دموگرافیک")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            age = st.number_input("سن", min_value=0, max_value=120, value=30)
            gender = st.selectbox("جنسیت", ["مرد", "زن"])
            weight = st.number_input("وزن (کیلوگرم)", min_value=1.0, max_value=300.0, value=70.0)
        with col2:
            height = st.number_input("قد (سانتی‌متر)", min_value=50, max_value=250, value=170)
            if gender == "زن":
                is_pregnant = st.checkbox("آیا باردار هستید؟")
                is_breastfeeding = st.checkbox("آیا شیرده هستید؟")
            else:
                is_pregnant = False
                is_breastfeeding = False
        with col3:
            activity_level = st.selectbox("میزان فعالیت", ["کم", "متوسط", "زیاد", "ورزشکار"])
            smoking = st.selectbox("مصرف سیگار", ["خیر", "گاهی", "روزانه"])
            alcohol = st.selectbox("مصرف الکل", ["خیر", "گاهی", "منظم"])
        
        bmi = weight / ((height/100) ** 2)
        bmi_category = self.get_bmi_category(bmi)
        st.info(f"شاخص توده بدنی (BMI): {bmi:.1f} - {bmi_category}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        return {
            'age': age, 'gender': gender, 'weight': weight, 'height': height,
            'is_pregnant': is_pregnant, 'is_breastfeeding': is_breastfeeding,
            'activity_level': activity_level, 'smoking': smoking, 'alcohol': alcohol,
            'bmi': bmi, 'bmi_category': bmi_category
        }
    
    def get_bmi_category(self, bmi):
        if bmi < 18.5:
            return "کم‌وزن"
        elif bmi < 25:
            return "طبیعی"
        elif bmi < 30:
            return "اضافه‌وزن"
        else:
            return "چاق"
    
    def render_lab_section(self):
        st.subheader("📋 نتایج آزمایش")
        col1, col2 = st.columns(2)
        lab_data = {}
        
        with col1:
            st.markdown("**آزمایش‌های خونی:**")
            hb = st.number_input("هموگلوبین (g/dL)", value=0.0, key="hb")
            if hb > 0: lab_data['هموگلوبین'] = hb
            ferritin = st.number_input("فریتین (ng/mL)", value=0.0, key="ferritin")
            if ferritin > 0: lab_data['فریتین'] = ferritin
            b12 = st.number_input("ویتامین B12 (pg/mL)", value=0.0, key="b12")
            if b12 > 0: lab_data['B12'] = b12
        
        with col2:
            st.markdown("**آزمایش‌های هورمونی و معدنی:**")
            vit_d = st.number_input("ویتامین D (ng/mL)", value=0.0, key="vit_d")
            if vit_d > 0: lab_data['ویتامین D'] = vit_d
            tsh = st.number_input("TSH (mIU/L)", value=0.0, key="tsh")
            if tsh > 0: lab_data['TSH'] = tsh
            calcium = st.number_input("کلسیم (mg/dL)", value=0.0, key="calcium")
            if calcium > 0: lab_data['کلسیم'] = calcium
        
        return lab_data
    
    def render_supplements_section(self):
        st.subheader("💊 مکمل‌ها و داروها")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**مکمل‌های مصرفی:**")
            supplements = st.multiselect(
‎                "انتخاب مکمل‌ها",
‎                ["ویتامین D", "ویتامین B12", "آهن", "کلسیم", "منیزیم", "روی", "امگا 3",
‎                 "مولتی ویتامین", "فولیک اسید", "ویتامین C", "کوآنزیم Q10", "پروبیوتیک",
                 "NAC", "زینک", "سلنیوم", "کروم", "L-Arginine", "Curcumin", "Green Tea Extract"]
            )
            custom_supplement = st.text_input("مکمل دیگر (اختیاری)")
            if custom_supplement:
                supplements.append(custom_supplement)
        
        with col2:
            st.markdown("**داروهای مصرفی:**")
            medications = st.multiselect(
‎                "انتخاب داروها",
‎                ["وارفارین", "آسپرین", "متفورمین", "لووتیروکسین", "امپرازول",
‎                 "آتورواستاتین", "لیزینوپریل", "آمیودارون", "Nifedipine", "Sildenafil",
                 "SSRIs", "MAOIs", "Tramadol", "Iron", "Calcium", "Tetracycline"]
            )
            custom_medication = st.text_input("داروی دیگر (اختیاری)")
            if custom_medication:
                medications.append(custom_medication)
        
        st.markdown("**بیماری‌های زمینه‌ای:**")
        conditions = st.multiselect(
‎            "انتخاب بیماری‌ها",
‎            ["دیابت", "فشار خون بالا", "بیماری قلبی", "بیماری کلیوی", "بیماری کبدی",
‎             "کم‌کاری تیروئید", "پرکاری تیروئید", "آسم", "صرع", "افسردگی", "Epilepsy",
             "Hypertension", "Liver disease", "Kidney failure", "Hemochromatosis", "G6PD Deficiency"]
        )
        
        return {
            'supplements': supplements,
            'medications': medications,
            'conditions': conditions
        }
    
    def render_analysis_results(self):
        if not st.session_state.analysis_results:
            return
        
        results = st.session_state.analysis_results
        st.markdown('<div class="analysis-result">', unsafe_allow_html=True)
        st.header("📊 نتایج تحلیل جامع")
        
        self.render_severity_summary(results['interactions']['severity_summary'])
        
        if results['interactions']['supplement_drug_interactions']:
            self.render_supplement_drug_interactions(results['interactions']['supplement_drug_interactions'])
        
        if results['interactions']['supplement_condition_interactions']:
            self.render_supplement_condition_interactions(results['interactions']['supplement_condition_interactions'])
        
        if results['interactions']['pregnancy_safety']:
            self.render_pregnancy_safety_results(results['interactions']['pregnancy_safety'])
        
        if results['interactions']['disease_recommendations']:
            self.render_disease_recommendations(results['interactions']['disease_recommendations'])
        
        if results['interactions']['personalized_dosing']:
            self.render_personalized_dosing(results['interactions']['personalized_dosing'])
        
        if results['lab_analysis']['deficiencies'] or results['lab_analysis']['excesses']:
            self.render_lab_analysis_results(results['lab_analysis'])
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def render_severity_summary(self, severity_summary):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("تداخلات شدید", severity_summary['high'], delta=None)
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("تداخلات متوسط", severity_summary['medium'], delta=None)
            st.markdown('</div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("تداخلات خفیف", severity_summary['low'], delta=None)
            st.markdown('</div>', unsafe_allow_html=True)
    
    def render_supplement_drug_interactions(self, interactions):
        st.subheader("⚠️ تداخلات مکمل-دارو")
        for interaction in interactions:
            severity_class = "interaction-card" if interaction['severity'] in ['X', 'D'] else "warning-card"
            st.markdown(f"""
            <div class="{severity_class}">
                <h4>🚨 {interaction['supplement']} + {interaction['drug']}</h4>
                <p><strong>ماده فعال:</strong> {interaction['compound']}</p>
                <p><strong>شدت تداخل:</strong> {interaction['severity']}</p>
                <p><strong>نوع تداخل:</strong> {interaction['interaction_type']}</p>
                <p><strong>توصیه بالینی:</strong> {interaction['clinical_advice']}</p>
                {f"<p><strong>گروه حساس:</strong> {interaction['risk_group']}</p>" if interaction['risk_group'] else ""}
                {f"<p><strong>هشدار بیماری:</strong> {interaction['condition_alert']}</p>" if interaction['condition_alert'] else ""}
                <p><strong>منبع:</strong> {interaction['source']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    def render_supplement_condition_interactions(self, interactions):
        st.subheader("🏥 تداخلات مکمل-بیماری")
        for interaction in interactions:
            severity_class = "disease-card" if interaction['severity'] in ['X', 'D'] else "warning-card"
            st.markdown(f"""
            <div class="{severity_class}">
                <h4>🩺 {interaction['supplement']} + {interaction['condition']}</h4>
                <p><strong>ماده فعال:</strong> {interaction['compound']}</p>
                <p><strong>شدت تداخل:</strong> {interaction['severity']}</p>
                <p><strong>مکانیسم:</strong> {interaction['mechanism']}</p>
                <p><strong>توصیه بالینی:</strong> {interaction['clinical_advice']}</p>
                <p><strong>منبع:</strong> {interaction['source']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    def render_pregnancy_safety_results(self, pregnancy_results):
        st.subheader("🤱 تحلیل ایمنی بارداری و شیردهی")
        for safety in pregnancy_results:
            safety_class = "interaction-card" if safety['safety_level'] in ['خطرناک', 'ممنوع مطلق'] else "pregnancy-card"
            st.markdown(f"""
            <div class="{safety_class}">
                <h4>👶 {safety['supplement']} ({safety['compound']})</h4>
                <p><strong>رده بارداری:</strong> {safety['pregnancy_category']}</p>
                <p><strong>سطح ایمنی:</strong> {safety['safety_level']}</p>
                <p><strong>توصیه بالینی:</strong> {safety['clinical_advice']}</p>
                {f"<p><strong>هشدار مصرف:</strong> {safety['use_warning']}</p>" if safety['use_warning'] else ""}
                {f"<p><strong>دوز خطرناک:</strong> {safety['toxic_threshold']}</p>" if safety['toxic_threshold'] else ""}
                <p><strong>منابع:</strong> {safety['sources']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    def render_disease_recommendations(self, recommendations):
        st.subheader("🏥 توصیه‌های مکمل بر اساس بیماری")
        for rec in recommendations:
            st.markdown(f"""
            <div class="disease-card">
                <h4>🩺 {rec['disease']}</h4>
                {f"<p><strong>گروه آسیب‌پذیر:</strong> {rec['vulnerable_group']}</p>" if rec['vulnerable_group'] else ""}
                {f"<p><strong>آزمایش‌های پیشنهادی:</strong> {rec['recommended_tests']}</p>" if rec['recommended_tests'] else ""}
                {f"<p><strong>مکمل‌های پیشنهادی:</strong> {rec['recommended_supplements']}</p>" if rec['recommended_supplements'] else ""}
                {f"<p><strong>رژیم غذایی حمایتی:</strong> {rec['supportive_diet']}</p>" if rec['supportive_diet'] else ""}
                {f"<p><strong>تناوب پایش:</strong> {rec['monitoring_frequency']}</p>" if rec['monitoring_frequency'] else ""}
                {f"<p><strong>نکات بالینی:</strong> {rec['clinical_notes']}</p>" if rec['clinical_notes'] else ""}
                <p><strong>منبع:</strong> {rec['source']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    def render_personalized_dosing(self, dosing):
        st.subheader("💊 دوزاژ شخصی‌سازی‌شده")
        for supplement, dosing_info in dosing.items():
            st.markdown(f"""
            <div class="safe-card">
                <h4>💉 {supplement}</h4>
                <p><strong>دوز پیشنهادی:</strong> {dosing_info['recommended']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    def render_lab_analysis_results(self, lab_analysis):
        st.subheader("🧪 تحلیل آزمایش‌ها")
        if lab_analysis['deficiencies']:
            st.markdown("**🔻 کمبودهای شناسایی‌شده:**")
            for deficiency in lab_analysis['deficiencies']:
                severity_color = {'شدید': '#FF6B6B', 'متوسط': '#FFE66D', 'خفیف': '#4ECDC4'}
                color = severity_color.get(deficiency['severity'], '#888888')
                st.markdown(f"""
                <div class="interaction-card" style="border-left-color: {color}">
                    <strong>{deficiency['test']}</strong><br>
‎                    مقدار: {deficiency['value']} (محدوده طبیعی: {deficiency['normal_range']})<br>
‎                    شدت کمبود: {deficiency['severity']}
                </div>
                """, unsafe_allow_html=True)
        
        if lab_analysis['excesses']:
            st.markdown("**🔺 مقادیر اضافی شناسایی‌شده:**")
            for excess in lab_analysis['excesses']:
                st.markdown(f"""
                <div class="warning-card">
                    <strong>{excess['test']}</strong><br>
‎                    مقدار: {excess['value']} (محدوده طبیعی: {excess['normal_range']})<br>
‎                    شدت اضافی: {excess['severity']}
                </div>
                """, unsafe_allow_html=True)
        
        if lab_analysis['recommendations']:
            st.markdown("**📋 توصیه‌های درمانی:**")
            for rec in lab_analysis['recommendations']:
                st.markdown(f"• {rec}")
    
    def render_shop_section(self):
        st.header("🛍️ فروشگاه مکمل‌ها", anchor="shop")
        
‎        # جستجوی محصولات
        search_query = st.text_input("جستجوی محصولات", placeholder="نام مکمل مورد نظر را وارد کنید...")
        
        products = self.shop.get_products()
        
        if search_query:
            products = [p for p in products if search_query.lower() in p['name'].lower()]
        
        if not products:
            st.warning("محصولی یافت نشد!")
            return
        
‎        # دسته‌بندی‌ها
        categories = ["همه محصولات"] + sorted(list(set(p['category'] for p in products if p['category'])))
        selected_category = st.selectbox("دسته‌بندی", categories, index=0)
        
        if selected_category != "همه محصولات":
            products = [p for p in products if p['category'] == selected_category]
        
‎        # نمایش محصولات
        cols = st.columns(3)
        for idx, product in enumerate(products):
            with cols[idx % 3]:
                st.markdown(f"""
                <div class="product-card">
                    <div style="text-align: center; margin-bottom: 1rem;">
                        <img src="{product.get('image_url', 'https://via.placeholder.com/200x150?text=Supplement')}" 
                             width="100%" style="border-radius: 8px;">
                    </div>
                    <h4 style="margin-bottom: 0.5rem;">{product['name']}</h4>
                    <p style="color: #555; font-size: 0.9rem; margin-bottom: 0.8rem;">
                        {product['description'][:60]}...
                    </p>
                    <div class="price-tag">
                        {product['price']:,} تومان
                    </div>
                    <div style="margin-top: 0.5rem; font-size: 0.8rem; color: #666;">
‎                        موجودی: {product['stock']} عدد
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if product['stock'] > 0:
                    if st.button("➕ افزودن به سبد", key=f"add_{product['id']}"):
                        self.shop.add_to_cart(product['id'])
                        st.success(f"{product['name']} به سبد خرید اضافه شد!")
                        st.rerun()
                else:
                    st.error("موجود نیست")
    
    def render_cart_section(self):
        st.header("🛒 سبد خرید شما", anchor="cart")
        
        cart_items = self.shop.get_cart_items()
        
        if not cart_items:
            st.info("سبد خرید شما خالی است")
            st.markdown("[به فروشگاه بروید](#shop)")
            return
        
        total = 0
        for item in cart_items:
            cols = st.columns([1, 3, 2, 2, 1])
            
            with cols[0]:
                st.image(item.get('image_url', 'https://via.placeholder.com/80?text=Product'), width=60)
            
            with cols[1]:
                st.markdown(f"**{item['name']}**")
                st.caption(item['category'])
            
            with cols[2]:
                st.markdown(f"**تعداد:** {item['quantity']}")
            
            with cols[3]:
                st.markdown(f"**قیمت:** {item['total_price']:,} تومان")
            
            with cols[4]:
                if st.button("❌", key=f"remove_{item['id']}"):
                    del st.session_state.cart[item['id']]
                    st.rerun()
            
            st.divider()
            total += item['total_price']
        
‎        # خلاصه پرداخت
        st.markdown(f"""
        <div style="background-color: var(--primary-light); padding: 1.5rem; border-radius: 10px;">
            <div style="display: flex; justify-content: space-between; font-size: 1.1rem;">
                <span>جمع کل:</span>
                <span style="font-weight: bold;">{total:,} تومان</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
‎        # دکمه پرداخت
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("[ادامه خرید](#shop)")
        with col2:
            if st.button("💳 پرداخت نهایی", type="primary", use_container_width=True):
                st.success("پرداخت با موفقیت انجام شد! (نمونه آزمایشی)")
                st.session_state.cart = {}
                st.rerun()
    
    def render_history_section(self):
        st.header("📈 تاریخچه آنالیزها")
        if st.session_state.analysis_results:
            st.subheader("آخرین آنالیز")
            timestamp = st.session_state.analysis_results.get('timestamp')
            if timestamp:
                st.info(f"زمان آنالیز: {timestamp.strftime('%Y/%m/%d %H:%M')}")
            
            interactions = st.session_state.analysis_results.get('interactions', {})
            severity_summary = interactions.get('severity_summary', {})
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("تداخلات شدید", severity_summary.get('high', 0))
            with col2:
                st.metric("تداخلات متوسط", severity_summary.get('medium', 0))
            with col3:
                st.metric("تداخلات خفیف", severity_summary.get('low', 0))
            
            if st.button("مشاهده جزئیات کامل", use_container_width=True):
                self.render_analysis_results()
        else:
            st.info("هنوز آنالیزی انجام نداده‌اید.")
            st.markdown("""
‎            ### 🔍 نحوه استفاده از سیستم:
‎            1. **اطلاعات دموگرافیک:** سن، جنس، وزن و قد خود را وارد کنید
‎            2. **نتایج آزمایش:** مقادیر آزمایش‌های خونی خود را وارد کنید (اختیاری)
‎            3. **مکمل‌ها و داروها:** مکمل‌ها و داروهای مصرفی خود را انتخاب کنید
‎            4. **بیماری‌ها:** بیماری‌های زمینه‌ای خود را انتخاب کنید
‎            5. **تحلیل:** روی دکمه "شروع تحلیل" کلیک کنید
‎            سیستم تداخلات احتمالی را بررسی کرده و توصیه‌های مناسب ارائه می‌دهد.
            """)

‎# تابع اصلی برای اجرای برنامه
def main():
    app = SupplementAnalysisUI()
    app.run()

if __name__ == "__main__":
    main()
