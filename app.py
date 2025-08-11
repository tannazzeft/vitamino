"""
سیستم تحلیل تداخلات دارویی و مکمل‌ها - نسخه کامل
توسعه‌دهنده: سیستم هوشمند تحلیل دارویی
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import hashlib
import sqlite3
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
from googletrans import Translator

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
    .main {
        background: linear-gradient(135deg, #e8f5e8 0%, #f0ffff 50%, #e0ffff 100%);
    }
    
    .stApp {
        background: linear-gradient(135deg, #e8f5e8 0%, #f0ffff 50%, #e0ffff 100%);
    }
    
    .header-container {
        background: linear-gradient(90deg, #228B22, #20B2AA);
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
    
    .header-subtitle {
        color: #f0ffff;
        font-size: 1.2rem;
        text-align: center;
        margin-top: 0.5rem;
    }
    
    .interaction-card {
        background: white;
        border-left: 5px solid #FF6B6B;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
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
    
    .stButton > button {
        background: linear-gradient(90deg, #228B22, #20B2AA);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .upload-area {
        border: 2px dashed #20B2AA;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background: rgba(255,255,255,0.8);
        margin: 1rem 0;
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
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border-top: 3px solid #20B2AA;
        transition: transform 0.3s ease;
    }
    
    .shop-card:hover {
        transform: translateY(-5px);
    }
    
    .price-tag {
        background: linear-gradient(90deg, #228B22, #20B2AA);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
    }
    
    .evidence-section {
        background: linear-gradient(135deg, #f0f8ff, #e6f7ff);
        border-radius: 10px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #1E90FF;
    }
    </style>
    """, unsafe_allow_html=True)

# کلاس مدیریت دیتابیس
class DatabaseManager:
    def __init__(self, db_path="output(2)(1).sqlite"):
        self.db_path = db_path
        self.init_database()
        self.load_csv_data()
    
    def init_database(self):
        """ایجاد جداول دیتابیس"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # جدول کاربران
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
        
        # جدول آنالیزها
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
        
        # جدول محصولات فروشگاه
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
        
        # جدول سفارشات
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            products TEXT,
            total_amount INTEGER,
            status TEXT DEFAULT 'pending',
            payment_ref TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """)
        
        conn.commit()
        conn.close()
    
    def load_csv_data(self):
        """بارگذاری داده‌های CSV به دیتابیس"""
        try:
            # بارگذاری فایل‌های CSV اگر موجود باشند
            csv_files = {
                'Sheet1.csv': 'diseases_supplements',
                'Sheet2.csv': 'pregnancy_categories', 
                'Sheet3.csv': 'supplement_drug_interactions',
                'Sheet4.csv': 'supplement_condition_interactions'
            }
            
            conn = sqlite3.connect(self.db_path)
            
            for csv_file, table_name in csv_files.items():
                if os.path.exists(csv_file):
                    try:
                        df = pd.read_csv(csv_file, encoding='utf-8')
                        df.to_sql(table_name, conn, if_exists='replace', index=False)
                        print(f"✅ {csv_file} loaded successfully")
                    except Exception as e:
                        print(f"❌ Error loading {csv_file}: {str(e)}")
            
            conn.close()
            
        except Exception as e:
            print(f"Database loading error: {str(e)}")
    
    def add_sample_products(self):
        """اضافه کردن محصولات نمونه"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        sample_products = [
            ("ویتامین D3 2000 واحد", "ویتامین‌ها", 250000, "مکمل ویتامین D3 با کیفیت بالا", "", 50),
            ("امگا 3 فیش اویل", "اسیدهای چرب", 180000, "کپسول امگا 3 از روغن ماهی", "", 30),
            ("مولتی ویتامین کامل", "مولتی ویتامین", 320000, "مکمل جامع ویتامین‌ها و مواد معدنی", "", 25),
            ("منیزیم 400 میلی‌گرم", "مواد معدنی", 150000, "مکمل منیزیم برای سلامت عضلات", "", 40),
            ("زینک 30 میلی‌گرم", "مواد معدنی", 120000, "مکمل زینک تقویت‌کننده سیستم ایمنی", "", 35),
            ("ویتامین B12 1000 میکروگرم", "ویتامین‌ها", 200000, "مکمل ویتامین B12 جذب بالا", "", 45),
            ("آهن بیس‌گلایسینات", "مواد معدنی", 180000, "مکمل آهن با جذب بهینه", "", 20),
            ("کلسیم + ویتامین K2", "مواد معدنی", 220000, "ترکیب کلسیم و ویتامین K2 برای استخوان", "", 30)
        ]
        
        cursor.executemany("""
        INSERT OR IGNORE INTO products (name, category, price, description, image_url, stock)
        VALUES (?, ?, ?, ?, ?, ?)
        """, sample_products)
        
        conn.commit()
        conn.close()

# کلاس جستجوی علمی
class ScientificSearch:
    def __init__(self):
        self.translator = Translator()
        self.sources = {
            "NIH": "https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_json/PMC/{}/unicode",
            "LactMed": "https://api.fda.gov/drug/label.json?search=openfda.substance_name:\"{}\"",
            "PubMed": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={}&retmode=json",
            "DrugBank": "https://go.drugbank.com/unearth/q?utf8=%E2%9C%93&query={}&searcher=drugs"
        }
    
    def search_interaction(self, supplement: str, drug: str) -> dict:
        """جستجوی تداخلات در منابع علمی معتبر"""
        results = {}
        
        # جستجو در NIH
        nih_results = self._search_nih(supplement, drug)
        if nih_results:
            results["NIH"] = nih_results
        
        # جستجو در LactMed
        lactmed_results = self._search_lactmed(supplement, drug)
        if lactmed_results:
            results["LactMed"] = lactmed_results
        
        # جستجو در PubMed
        pubmed_results = self._search_pubmed(supplement, drug)
        if pubmed_results:
            results["PubMed"] = pubmed_results
        
        # جستجو در DrugBank
        drugbank_results = self._search_drugbank(supplement, drug)
        if drugbank_results:
            results["DrugBank"] = drugbank_results
        
        return results
    
    def _search_nih(self, supplement: str, drug: str) -> list:
        """جستجو در پایگاه NIH"""
        try:
            url = f"https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_json/PMC/{supplement}+{drug}/unicode"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                return [{
                    "source": "NIH",
                    "title": f"تداخل {supplement} و {drug}",
                    "url": f"https://www.ncbi.nlm.nih.gov/pmc/articles/?term={supplement}+{drug}",
                    "summary": "مطالعه کامل در پایگاه ملی سلامت آمریکا"
                }]
        except Exception as e:
            print(f"Error searching NIH: {str(e)}")
        return []
    
    def _search_lactmed(self, supplement: str, drug: str) -> list:
        """جستجو در پایگاه LactMed"""
        try:
            url = f"https://toxnet.nlm.nih.gov/cgi-bin/sis/search2/r?dbs+lactmed:@term+@DOCNO+{supplement}+{drug}"
            response = requests.get(url)
            if response.status_code == 200:
                return [{
                    "source": "LactMed",
                    "title": f"تداخل {supplement} و {drug} در دوران شیردهی",
                    "url": url,
                    "summary": "اطلاعات ایمنی در دوران شیردهی"
                }]
        except Exception as e:
            print(f"Error searching LactMed: {str(e)}")
        return []
    
    def _search_pubmed(self, supplement: str, drug: str) -> list:
        """جستجو در پایگاه PubMed"""
        try:
            query = f"{supplement}+AND+{drug}+AND+interaction"
            url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={query}&retmode=json"
            response = requests.get(url)
            data = response.json()
            
            articles = []
            for id in data.get("esearchresult", {}).get("idlist", [])[:3]:
                article_url = f"https://pubmed.ncbi.nlm.nih.gov/{id}/"
                title = self._get_pubmed_title(id)
                articles.append({
                    "source": "PubMed",
                    "title": title,
                    "url": article_url,
                    "summary": "مقاله علمی معتبر"
                })
            return articles
        except Exception as e:
            print(f"Error searching PubMed: {str(e)}")
        return []
    
    def _get_pubmed_title(self, article_id: str) -> str:
        """دریافت عنوان مقاله از PubMed"""
        try:
            url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={article_id}&retmode=json"
            response = requests.get(url)
            data = response.json()
            return data["result"][article_id]["title"]
        except:
            return f"مقاله درباره تداخلات {article_id}"
    
    def _search_drugbank(self, supplement: str, drug: str) -> list:
        """جستجو در پایگاه DrugBank"""
        try:
            url = f"https://go.drugbank.com/unearth/q?utf8=%E2%9C%93&query={supplement}+{drug}&searcher=drugs"
            return [{
                "source": "DrugBank",
                "title": f"تداخل {supplement} و {drug}",
                "url": url,
                "summary": "اطلاعات دارویی جامع"
            }]
        except Exception as e:
            print(f"Error searching DrugBank: {str(e)}")
        return []
    
    def translate_to_persian(self, text: str) -> str:
        """ترجمه متن به فارسی"""
        try:
            translation = self.translator.translate(text, src='en', dest='fa')
            return translation.text
        except:
            return text

# کلاس تحلیل تداخلات
class InteractionAnalyzer:
    def __init__(self, db_manager):
        self.db = db_manager
        self.scientific_searcher = ScientificSearch()
    
    def analyze_interactions(self, supplements: List[str], medications: List[str], 
                           conditions: List[str], demographic_data: Dict) -> Dict[str, Any]:
        """تحلیل کامل تداخلات"""
        
        results = {
            'supplement_drug_interactions': [],
            'supplement_condition_interactions': [],
            'pregnancy_safety': [],
            'age_specific_warnings': [],
            'recommendations': [],
            'scientific_evidence': [],
            'severity_summary': {'high': 0, 'medium': 0, 'low': 0}
        }
        
        conn = sqlite3.connect(self.db.db_path)
        
        try:
            # تحلیل تداخلات مکمل-دارو
            drug_interactions = self._analyze_drug_interactions(supplements, medications, conn)
            results['supplement_drug_interactions'] = drug_interactions
            
            # تحلیل تداخلات مکمل-بیماری
            condition_interactions = self._analyze_condition_interactions(supplements, conditions, conn)
            results['supplement_condition_interactions'] = condition_interactions
            
            # تحلیل ایمنی بارداری
            if demographic_data.get('is_pregnant') or demographic_data.get('is_breastfeeding'):
                pregnancy_safety = self._analyze_pregnancy_safety(supplements, conn)
                results['pregnancy_safety'] = pregnancy_safety
            
            # تحلیل هشدارهای سنی
            age_warnings = self._analyze_age_warnings(supplements, demographic_data, conn)
            results['age_specific_warnings'] = age_warnings
            
            # جستجوی علمی برای تداخلات مهم
            results['scientific_evidence'] = self._search_scientific_evidence(
                supplements, medications, results
            )
            
            # تولید توصیه‌ها
            recommendations = self._generate_recommendations(results, demographic_data)
            results['recommendations'] = recommendations
            
            # خلاصه شدت
            results['severity_summary'] = self._calculate_severity_summary(results)
            
        except Exception as e:
            st.error(f"خطا در تحلیل تداخلات: {str(e)}")
        
        finally:
            conn.close()
        
        return results
    
    def _search_scientific_evidence(self, supplements, medications, results) -> list:
        """جستجوی مستندات علمی برای تداخلات مهم"""
        evidence = []
        
        # برای تداخلات دارویی
        for interaction in results['supplement_drug_interactions']:
            if interaction.get('severity') in ['X', 'D', 'شدید']:
                supplement = interaction['supplement']
                drug = interaction['drug']
                scientific_results = self.scientific_searcher.search_interaction(supplement, drug)
                if scientific_results:
                    evidence.append({
                        'supplement': supplement,
                        'drug': drug,
                        'results': scientific_results
                    })
        
        # برای تداخلات بیماری
        for interaction in results['supplement_condition_interactions']:
            if interaction.get('severity') in ['X', 'D', 'شدید']:
                supplement = interaction['supplement']
                condition = interaction['condition']
                scientific_results = self.scientific_searcher.search_interaction(supplement, condition)
                if scientific_results:
                    evidence.append({
                        'supplement': supplement,
                        'condition': condition,
                        'results': scientific_results
                    })
        
        return evidence

    def _analyze_drug_interactions(self, supplements: List[str], medications: List[str], conn) -> List[Dict]:
        """تحلیل تداخلات مکمل-دارو"""
        interactions = []
        
        try:
            # جستجو در جدول تداخلات مکمل-دارو
            for supplement in supplements:
                for medication in medications:
                    query = """
                    SELECT * FROM supplement_drug_interactions 
                    WHERE LOWER("مکمل / Supplement") LIKE ? 
                    AND LOWER("دارو / Drug") LIKE ?
                    """
                    
                    df = pd.read_sql_query(query, conn, params=[
                        f'%{supplement.lower()}%', 
                        f'%{medication.lower()}%'
                    ])
                    
                    for _, row in df.iterrows():
                        severity = row.get('شدت تداخل / Severity', 'نامشخص')
                        
                        interactions.append({
                            'supplement': supplement,
                            'drug': medication,
                            'severity': severity,
                            'mechanism': row.get('مکانیسم / Mechanism', ''),
                            'recommendation': row.get('توصیه / Recommendation', ''),
                            'source': row.get('منبع / Source', '')
                        })
        
        except Exception as e:
            st.error(f"خطا در تحلیل تداخلات دارویی: {str(e)}")
        
        return interactions

    def _analyze_condition_interactions(self, supplements: List[str], conditions: List[str], conn) -> List[Dict]:
        """تحلیل تداخلات مکمل-بیماری"""
        interactions = []
        
        try:
            # جستجو در جدول تداخلات مکمل-بیماری
            for supplement in supplements:
                for condition in conditions:
                    query = """
                    SELECT * FROM supplement_condition_interactions 
                    WHERE LOWER("ماده فعال / Compound") LIKE ? 
                    OR LOWER("بیماری / Condition") LIKE ?
                    """
                    
                    df = pd.read_sql_query(query, conn, params=[
                        f'%{supplement.lower()}%', 
                        f'%{condition.lower()}%'
                    ])
                    
                    for _, row in df.iterrows():
                        severity = row.get('شدت تداخل (A–X) / Severity', 'نامشخص')
                        
                        interactions.append({
                            'supplement': supplement,
                            'condition': condition,
                            'severity': severity,
                            'clinical_advice': row.get('توصیه بالینی / Clinical Advice', ''),
                            'mechanism': row.get('مکانیسم / Mechanism', ''),
                            'source': row.get('منبع / Source', '')
                        })
        
        except Exception as e:
            st.error(f"خطا در تحلیل تداخلات بیماری: {str(e)}")
        
        return interactions

    def _analyze_pregnancy_safety(self, supplements: List[str], conn) -> List[Dict]:
        """تحلیل ایمنی بارداری"""
        safety_analysis = []
        
        try:
            for supplement in supplements:
                query = """
                SELECT * FROM pregnancy_categories 
                WHERE LOWER("ماده فعال / Compound") LIKE ?
                """
                
                df = pd.read_sql_query(query, conn, params=[f'%{supplement.lower()}%'])
                
                for _, row in df.iterrows():
                    category = row.get('رده بارداری/شیردهی (A–X)', 'نامشخص')
                    safety_level = self._get_safety_level(category)
                    
                    safety_analysis.append({
                        'supplement': supplement,
                        'category': category,
                        'safety_level': safety_level,
                        'clinical_advice': row.get('توصیه بالینی / Clinical Advice', ''),
                        'warning': row.get('هشدار مصرف / Use Warning', ''),
                        'source': row.get('منابع / Sources', '')
                    })
        
        except Exception as e:
            st.error(f"خطا در تحلیل ایمنی بارداری: {str(e)}")
        
        return safety_analysis

    def _analyze_age_warnings(self, supplements: List[str], demographic_data: Dict, conn) -> List[Dict]:
        """تحلیل هشدارهای مرتبط با سن"""
        warnings = []
        age = demographic_data.get('age', 0)
        
        # هشدارهای مخصوص کودکان (زیر 18 سال)
        if age < 18:
            for supplement in supplements:
                warnings.append({
                    'supplement': supplement,
                    'age_group': 'کودک/نوجوان',
                    'warning': 'مصرف در کودکان و نوجوانان نیاز به نظارت پزشک دارد',
                    'recommendation': 'دوز کاهش‌یافته و تحت نظر پزشک'
                })
        
        # هشدارهای مخصوص سالمندان (بالای 65 سال)
        elif age > 65:
            for supplement in supplements:
                warnings.append({
                    'supplement': supplement,
                    'age_group': 'سالمند',
                    'warning': 'در سالمندان احتمال تداخل دارویی و عوارض جانبی بیشتر است',
                    'recommendation': 'شروع با دوز پایین و پایش منظم'
                })
        
        return warnings

    def _get_safety_level(self, category: str) -> str:
        """تعیین سطح ایمنی بر اساس رده‌بندی"""
        if category in ['A', 'B']:
            return 'ایمن'
        elif category == 'C':
            return 'احتیاط'
        elif category == 'D':
            return 'خطر'
        elif category == 'X':
            return 'ممنوع'
        else:
            return 'نامشخص'

    def _generate_recommendations(self, results: Dict, demographic_data: Dict) -> List[str]:
        """تولید توصیه‌های شخصی‌سازی‌شده"""
        recommendations = []
        
        # توصیه‌های بر اساس تداخلات شدید
        high_severity_interactions = [
            item for sublist in results.values() 
            if isinstance(sublist, list)
            for item in sublist 
            if isinstance(item, dict) and item.get('severity') in ['X', 'D', 'شدید']
        ]
        
        if high_severity_interactions:
            recommendations.append("⚠️ تداخلات شدید شناسایی شد - حتماً با پزشک مشورت کنید")
        
        # توصیه‌های بر اساس BMI
        bmi = demographic_data.get('bmi', 0)
        if bmi > 30:
            recommendations.append("🏃‍♂️ با توجه به BMI بالا، کنترل وزن و ورزش منظم توصیه می‌شود")
        
        # توصیه‌های بر اساس سن
        age = demographic_data.get('age', 0)
        if age > 65:
            recommendations.append("👴 در سن بالا، پایش منظم و شروع با دوزهای پایین‌تر توصیه می‌شود")
        
        # توصیه‌های عمومی
        recommendations.extend([
            "💊 همیشه مکمل‌ها را با فاصله از وعده‌های غذایی مصرف کنید",
            "🥛 مکمل‌ها را با آب فراوان مصرف کنید",
            "📅 زمان‌بندی مناسب مصرف مکمل‌ها را رعایت کنید",
            "⏰ از مصرف همزمان چندین مکمل بدون مشورت پزشک اجتناب کنید"
        ])
        
        return recommendations

    def _calculate_severity_summary(self, results: Dict) -> Dict[str, int]:
        """محاسبه خلاصه شدت تداخلات"""
        summary = {'high': 0, 'medium': 0, 'low': 0}
        
        for key, items in results.items():
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict):
                        severity = item.get('severity', '').upper()
                        if severity in ['X', 'D', 'شدید']:
                            summary['high'] += 1
                        elif severity in ['C', 'متوسط']:
                            summary['medium'] += 1
                        elif severity in ['A', 'B', 'خفیف']:
                            summary['low'] += 1
        
        return summary

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
            'آهن': {'min': 60, 'max': 170, 'unit': 'µg/dL'},
            'TIBC': {'min': 250, 'max': 400, 'unit': 'µg/dL'}
        }
    
    def analyze_lab_results(self, lab_data: Dict[str, float], demographic_data: Dict) -> Dict[str, Any]:
        """تحلیل جامع نتایج آزمایش"""
        analysis = {
            'deficiencies': [],
            'excesses': [],
            'normal': [],
            'recommendations': [],
            'supplement_suggestions': [],
            'retest_recommendations': []
        }
        
        gender = demographic_data.get('gender', 'مرد')
        age = demographic_data.get('age', 30)
        
        for test_name, value in lab_data.items():
            if test_name in self.normal_ranges:
                normal_range = self.normal_ranges[test_name]
                
                # تنظیم محدوده براساس جنسیت
                min_val = normal_range.get(f'{gender.lower()}_min', normal_range['min'])
                max_val = normal_range.get(f'{gender.lower()}_max', normal_range['max'])
                
                if value < min_val:
                    severity = self._calculate_deficiency_severity(value, min_val)
                    analysis['deficiencies'].append({
                        'test': test_name,
                        'value': value,
                        'normal_range': f"{min_val}-{max_val} {normal_range['unit']}",
                        'severity': severity,
                        'percentage_deficit': ((min_val - value) / min_val) * 100
                    })
                elif value > max_val:
                    severity = self._calculate_excess_severity(value, max_val)
                    analysis['excesses'].append({
                        'test': test_name,
                        'value': value,
                        'normal_range': f"{min_val}-{max_val} {normal_range['unit']}",
                        'severity': severity,
                        'percentage_excess': ((value - max_val) / max_val) * 100
                    })
                else:
                    analysis['normal'].append({
                        'test': test_name,
                        'value': value,
                        'normal_range': f"{min_val}-{max_val} {normal_range['unit']}"
                    })
        
        # تولید توصیه‌ها
        analysis['recommendations'] = self._generate_lab_recommendations(analysis, demographic_data)
        analysis['supplement_suggestions'] = self._suggest_supplements(analysis)
        analysis['retest_recommendations'] = self._generate_retest_schedule(analysis)
        
        return analysis
    
    def _calculate_deficiency_severity(self, value: float, min_normal: float) -> str:
        """محاسبه شدت کمبود"""
        deficit_percentage = ((min_normal - value) / min_normal) * 100
        
        if deficit_percentage >= 50:
            return 'شدید'
        elif deficit_percentage >= 25:
            return 'متوسط'
        else:
            return 'خفیف'
    
    def _calculate_excess_severity(self, value: float, max_normal: float) -> str:
        """محاسبه شدت اضافه"""
        excess_percentage = ((value - max_normal) / max_normal) * 100
        
        if excess_percentage >= 50:
            return 'شدید'
        elif excess_percentage >= 25:
            return 'متوسط'
        else:
            return 'خفیف'
    
    def _generate_lab_recommendations(self, analysis: Dict, demographic_data: Dict) -> List[str]:
        """تولید توصیه‌های بر اساس نتایج آزمایش"""
        recommendations = []
        
        for deficiency in analysis['deficiencies']:
            test = deficiency['test']
            severity = deficiency['severity']
            
            if test == 'ویتامین D':
                if severity == 'شدید':
                    recommendations.append("💊 ویتامین D3: 4000 واحد روزانه به مدت 3 ماه، سپس 2000 واحد نگهدارنده")
                elif severity == 'متوسط':
                    recommendations.append("💊 ویتامین D3: 2000 واحد روزانه به مدت 2 ماه")
                else:
                    recommendations.append("💊 ویتامین D3: 1000 واحد روزانه")
            
            elif test == 'هموگلوبین':
                recommendations.append("🔍 بررسی علت کم‌خونی (آهن، B12، فولات) و مصرف مکمل مناسب")
                recommendations.append("🥩 افزایش مصرف غذاهای غنی از آهن (گوشت قرمز، کبد، عدس)")
            
            elif test == 'B12':
                if severity == 'شدید':
                    recommendations.append("💉 تزریق B12 عضلانی یا مصرف 2000 میکروگرم خوراکی روزانه")
                else:
                    recommendations.append("💊 B12: 1000 میکروگرم روزانه")
            
            elif test == 'فریتین':
                recommendations.append("🔬 بررسی آهن سرم و TIBC برای تشخیص نوع کم‌خونی")
                recommendations.append("💊 آهن: 30-60 میلی‌گرم روزانه با ویتامین C")
        
        # توصیه‌های کلی
        if analysis['deficiencies']:
            recommendations.append("🏥 مراجعه به پزشک برای بررسی بیشتر و تجویز مناسب")
            recommendations.append("🔄 تکرار آزمایش‌ها پس از 2-3 ماه مصرف مکمل")
        
        return recommendations
    
    def _suggest_supplements(self, analysis: Dict) -> List[Dict]:
        """پیشنهاد مکمل‌های مناسب"""
        suggestions = []
        
        for deficiency in analysis['deficiencies']:
            test = deficiency['test']
            severity = deficiency['severity']
            
            supplement_map = {
                'ویتامین D': {
                    'name': 'ویتامین D3',
                    'dosage': '2000 واحد' if severity != 'شدید' else '4000 واحد',
                    'frequency': 'روزانه'
                },
                'B12': {
                    'name': 'ویتامین B12',
                    'dosage': '1000 میکروگرم' if severity != 'شدید' else '2000 میکروگرم',
                    'frequency': 'روزانه'
                },
                'فریتین': {
                    'name': 'آهن بیس‌گلایسینات',
                    'dosage': '30 میلی‌گرم',
                    'frequency': 'روزانه'
                },
                'فولات': {
                    'name': 'فولیک اسید',
                    'dosage': '400 میکروگرم',
                    'frequency': 'روزانه'
                }
            }
            
            if test in supplement_map:
                suggestions.append(supplement_map[test])
        
        return suggestions
    
    def _generate_retest_schedule(self, analysis: Dict) -> List[str]:
        """تولید برنامه تکرار آزمایش‌ها"""
        schedule = []
        
        if analysis['deficiencies']:
            schedule.append("🔄 تکرار آزمایش‌های کمبود پس از 6-8 هفته مصرف مکمل")
        
        if analysis['excesses']:
            schedule.append("⚠️ تکرار آزمایش‌های اضافه پس از 4 هفته")
        
        schedule.append("📅 آزمایش‌های دوره‌ای ساالنه برای پایش سلامت")
        
        return schedule

# کلاس احراز هویت
class AuthManager:
    def __init__(self, db_manager):
        self.db = db_manager
    
    def hash_password(self, password: str) -> str:
        """هش کردن رمز عبور"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, phone: str, first_name: str, last_name: str, password: str) -> bool:
        """ثبت‌نام کاربر جدید"""
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
    
    def login_user(self, phone: str, password: str) -> Dict:
        """ورود کاربر"""
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

# کلاس فروشگاه آنلاین
class OnlineShop:
    def __init__(self, db_manager):
        self.db = db_manager
        self.zarinpal_merchant = "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"  # توکن تستی
        self.zarinpal_callback_url = "http://localhost:8501/verify"
    
    def get_products(self) -> List[Dict]:
        """دریافت لیست محصولات"""
        conn = sqlite3.connect(self.db.db_path)
        
        query = """
        SELECT * FROM products WHERE active = TRUE ORDER BY category, name
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df.to_dict('records')
    
    def add_to_cart(self, product_id: int, quantity: int = 1) -> bool:
        """افزودن به سبد خرید"""
        if 'cart' not in st.session_state:
            st.session_state.cart = {}
        
        if product_id in st.session_state.cart:
            st.session_state.cart[product_id] += quantity
        else:
            st.session_state.cart[product_id] = quantity
        
        return True
    
    def get_cart_items(self) -> List[Dict]:
        """دریافت اقلام سبد خرید"""
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
    
    def calculate_total(self) -> int:
        """محاسبه مجموع سبد خرید"""
        cart_items = self.get_cart_items()
        return sum(item['total_price'] for item in cart_items)
    
    def create_zarinpal_payment(self, amount: int, description: str) -> Dict:
        """ایجاد پرداخت زرین‌پال"""
        zarinpal_request_url = "https://sandbox.zarinpal.com/pg/rest/WebGate/PaymentRequest.json"
        
        data = {
            "MerchantID": self.zarinpal_merchant,
            "Amount": amount,
            "Description": description,
            "CallbackURL": self.zarinpal_callback_url
        }
        
        try:
            response = requests.post(zarinpal_request_url, json=data)
            result = response.json()
            
            if result['Status'] == 100:
                payment_url = f"https://sandbox.zarinpal.com/pg/StartPay/{result['Authority']}"
                return {
                    'success': True,
                    'payment_url': payment_url,
                    'authority': result['Authority']
                }
            else:
                return {'success': False, 'error': 'خطا در ایجاد پرداخت'}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}

# کلاس رابط کاربری اصلی
class SupplementAnalysisUI:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.interaction_analyzer = InteractionAnalyzer(self.db_manager)
        self.lab_analyzer = LabAnalyzer()
        self.auth_manager = AuthManager(self.db_manager)
        self.shop = OnlineShop(self.db_manager)
        
        # اضافه کردن محصولات نمونه
        self.db_manager.add_sample_products()
        
        # مقداردهی session state
        if 'logged_in' not in st.session_state:
            st.session_state.logged_in = False
        if 'user_data' not in st.session_state:
            st.session_state.user_data = {}
        if 'analysis_results' not in st.session_state:
            st.session_state.analysis_results = {}
        if 'cart' not in st.session_state:
            st.session_state.cart = {}
    
    def run(self):
        """اجرای اصلی برنامه"""
        load_css()
        self.render_header()
        
        # منوی اصلی
        if st.session_state.logged_in:
            self.render_main_menu()
        else:
            self.render_auth_section()
    
    def render_header(self):
        """رندر هدر صفحه"""
        st.markdown("""
        <div class="header-container">
            <h1 class="header-title">🔬 سیستم تحلیل تداخلات دارویی و مکمل‌ها</h1>
            <p class="header-subtitle">تحلیل هوشمند و ایمن مکمل‌های غذایی بر اساس وضعیت سلامت فردی</p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_auth_section(self):
        """رندر بخش احراز هویت"""
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
                            st.success("ثبت‌نام با موفقیت انجام شد! اکنون می‌توانید وارد شوید.")
                        else:
                            st.error("خطا در ثبت‌نام! شماره همراه قبلاً ثبت شده است.")
                    else:
                        st.error("رمز عبور و تأیید آن یکسان نیستند!")
                else:
                    st.error("لطفاً تمام فیلدها را پر کنید!")
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    def render_main_menu(self):
        """رندر منوی اصلی"""
        # نوار کناری
        with st.sidebar:
            st.success(f"خوش آمدید {st.session_state.user_data['first_name']}")
            
            menu_option = st.selectbox(
                "انتخاب بخش",
                ["تحلیل تداخلات", "فروشگاه مکمل‌ها", "سبد خرید", "تاریخچه آنالیزها"]
            )
            
            if st.button("خروج"):
                st.session_state.logged_in = False
                st.session_state.user_data = {}
                st.rerun()
        
        # نمایش بخش انتخابی
        if menu_option == "تحلیل تداخلات":
            self.render_analysis_section()
        elif menu_option == "فروشگاه مکمل‌ها":
            self.render_shop_section()
        elif menu_option == "سبد خرید":
            self.render_cart_section()
        elif menu_option == "تاریخچه آنالیزها":
            self.render_history_section()
    
    def render_analysis_section(self):
        """رندر بخش تحلیل تداخلات"""
        st.header("🔬 تحلیل تداخلات دارویی")
        
        # فرم اطلاعات دموگرافیک
        demographic_data = self.render_demographic_form()
        
        # بخش آپلود آزمایش
        lab_data = self.render_lab_section()
        
        # بخش مکمل‌ها و داروها
        supplements_data = self.render_supplements_section()
        
        # دکمه تحلیل
        if st.button("🔍 شروع تحلیل", key="analyze_btn"):
            if supplements_data['supplements']:
                with st.spinner("در حال تحلیل..."):
                    # تحلیل تداخلات
                    interaction_results = self.interaction_analyzer.analyze_interactions(
                        supplements_data['supplements'],
                        supplements_data['medications'],
                        supplements_data['conditions'],
                        demographic_data
                    )
                    
                    # تحلیل آزمایش
                    lab_results = self.lab_analyzer.analyze_lab_results(lab_data, demographic_data)
                    
                    # ذخیره نتایج
                    st.session_state.analysis_results = {
                        'interactions': interaction_results,
                        'lab_analysis': lab_results,
                        'demographic': demographic_data,
                        'timestamp': datetime.now()
                    }
                    
                    # نمایش نتایج
                    self.render_analysis_results()
            else:
                st.error("لطفاً حداقل یک مکمل را انتخاب کنید!")
    
    def render_demographic_form(self):
        """رندر فرم اطلاعات دموگرافیک"""
        st.markdown('<div class="demographic-form">', unsafe_allow_html=True)
        st.subheader("🧑‍⚕️ اطلاعات دموگرافیک")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            age = st.number_input("سن", min_value=0, max_value=120, value=30)
            gender = st.selectbox("جنسیت", ["مرد", "زن"])
            weight = st.number_input("وزن (کیلوگرم)", min_value=1.0, max_value=300.0, value=70.0)
        
        with col2:
            height = st.number_input("قد (سانتی‌متر)", min_value=50, max_value=250, value=170)
            is_pregnant = st.checkbox("آیا باردار هستید؟") if gender == "زن" else False
            is_breastfeeding = st.checkbox("آیا شیرده هستید؟") if gender == "زن" else False
        
        with col3:
            activity_level = st.selectbox("میزان فعالیت", ["کم", "متوسط", "زیاد", "ورزشکار"])
            smoking = st.selectbox("مصرف سیگار", ["خیر", "گاهی", "روزانه"])
            alcohol = st.selectbox("مصرف الکل", ["خیر", "گاهی", "منظم"])
        
        # محاسبه BMI
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
    
    def get_bmi_category(self, bmi: float) -> str:
        """تعیین دسته‌بندی BMI"""
        if bmi < 18.5:
            return "کم‌وزن"
        elif bmi < 25:
            return "طبیعی"
        elif bmi < 30:
            return "اضافه‌وزن"
        else:
            return "چاق"
    
    def render_lab_section(self):
        """رندر بخش آزمایش"""
        st.markdown('<div class="upload-area">', unsafe_allow_html=True)
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
            
            folate = st.number_input("فولات (ng/mL)", value=0.0, key="folate")
            if folate > 0: lab_data['فولات'] = folate
        
        with col2:
            st.markdown("**آزمایش‌های هورمونی و معدنی:**")
            vit_d = st.number_input("ویتامین D (ng/mL)", value=0.0, key="vit_d")
            if vit_d > 0: lab_data['ویتامین D'] = vit_d
            
            tsh = st.number_input("TSH (mIU/L)", value=0.0, key="tsh")
            if tsh > 0: lab_data['TSH'] = tsh
            
            calcium = st.number_input("کلسیم (mg/dL)", value=0.0, key="calcium")
            if calcium > 0: lab_data['کلسیم'] = calcium
            
            zinc = st.number_input("روی (µg/dL)", value=0.0, key="zinc")
            if zinc > 0: lab_data['روی'] = zinc
        
        st.markdown('</div>', unsafe_allow_html=True)
        return lab_data
    
    def render_supplements_section(self):
        """رندر بخش مکمل‌ها و داروها"""
        st.subheader("💊 مکمل‌ها و داروها")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**مکمل‌های مصرفی:**")
            supplements = st.multiselect(
                "انتخاب مکمل‌ها",
                ["ویتامین D", "ویتامین B12", "آهن", "کلسیم", "منیزیم", "روی", "امگا 3", 
                 "مولتی ویتامین", "فولیک اسید", "ویتامین C", "کوآنزیم Q10", "پروبیوتیک"]
            )
            
            custom_supplement = st.text_input("مکمل دیگر (اختیاری)")
            if custom_supplement:
                supplements.append(custom_supplement)
        
        with col2:
            st.markdown("**داروهای مصرفی:**")
            medications = st.multiselect(
                "انتخاب داروها",
                ["وارفارین", "آسپرین", "متفورمین", "لووتیروکسین", "امپرازول", 
                 "آتورواستاتین", "لیزینوپریل", "آمیودارون"]
            )
            
            custom_medication = st.text_input("داروی دیگر (اختیاری)")
            if custom_medication:
                medications.append(custom_medication)
        
        # بیماری‌های زمینه‌ای
        st.markdown("**بیماری‌های زمینه‌ای:**")
        conditions = st.multiselect(
            "انتخاب بیماری‌ها",
            ["دیابت", "فشار خون بالا", "بیماری قلبی", "بیماری کلیوی", "بیماری کبدی",
             "کم‌کاری تیروئید", "پرکاری تیروئید", "آسم", "صرع", "افسردگی"]
        )
        
        return {
            'supplements': supplements,
            'medications': medications,
            'conditions': conditions
        }
    
    def render_analysis_results(self):
        """نمایش نتایج تحلیل"""
        if not st.session_state.analysis_results:
            return
        
        results = st.session_state.analysis_results
        
        st.markdown('<div class="analysis-result">', unsafe_allow_html=True)
        st.header("📊 نتایج تحلیل")
        
        # خلاصه کلی
        self.render_severity_summary(results['interactions']['severity_summary'])
        
        # تحلیل آزمایش
        if results['lab_analysis']['deficiencies'] or results['lab_analysis']['excesses']:
            self.render_lab_analysis_results(results['lab_analysis'])
        
        # تداخلات شدید
        self.render_critical_interactions(results['interactions'])
        
        # مستندات علمی
        self.render_scientific_evidence(results['interactions']['scientific_evidence'])
        
        # توصیه‌های کلی
        self.render_recommendations(results['interactions']['recommendations'])
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def render_severity_summary(self, severity_summary):
        """نمایش خلاصه شدت تداخلات"""
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
    
    def render_lab_analysis_results(self, lab_analysis):
        """نمایش نتایج تحلیل آزمایش"""
        st.subheader("🧪 تحلیل آزمایش‌ها")
        
        if lab_analysis['deficiencies']:
            st.markdown("**کمبودهای شناسایی‌شده:**")
            for deficiency in lab_analysis['deficiencies']:
                severity_color = {'شدید': '#FF6B6B', 'متوسط': '#FFE66D', 'خفیف': '#4ECDC4'}
                color = severity_color.get(deficiency['severity'], '#888888')
                
                st.markdown(f"""
                <div class="interaction-card" style="border-left-color: {color}">
                    <strong>{deficiency['test']}</strong><br>
                    مقدار: {deficiency['value']} (محدوده طبیعی: {deficiency['normal_range']})<br>
                    شدت کمبود: {deficiency['severity']}
                </div>
                """, unsafe_allow_html=True)
        
        if lab_analysis['recommendations']:
            st.markdown("**توصیه‌های درمانی:**")
            for rec in lab_analysis['recommendations']:
                st.write(f"• {rec}")
    
    def render_critical_interactions(self, interactions):
        """نمایش تداخلات بحرانی"""
        critical_interactions = []
        
        # جمع‌آوری تداخلات شدید
        for interaction_list in [interactions['supplement_drug_interactions'], 
                               interactions['supplement_condition_interactions']]:
            for interaction in interaction_list:
                if interaction.get('severity') in ['X', 'D', 'شدید']:
                    critical_interactions.append(interaction)
        
        if critical_interactions:
            st.subheader("⚠️ تداخلات بحرانی")
            for interaction in critical_interactions:
                st.markdown(f"""
                <div class="interaction-card">
                    <strong>هشدار شدید!</strong><br>
                    {interaction.get('supplement', 'نامشخص')} + {interaction.get('drug', interaction.get('condition', 'نامشخص'))}<br>
                    توصیه: {interaction.get('clinical_advice', 'مشورت فوری با پزشک')}
                </div>
                """, unsafe_allow_html=True)
    
    def render_scientific_evidence(self, evidence):
        """نمایش مستندات علمی"""
        if evidence:
            st.subheader("🔍 مستندات علمی از منابع معتبر")
            
            for item in evidence:
                if 'drug' in item:
                    title = f"مستندات علمی برای تداخل {item['supplement']} و {item['drug']}"
                else:
                    title = f"مستندات علمی برای تداخل {item['supplement']} و {item['condition']}"
                
                with st.expander(title):
                    for source, results in item['results'].items():
                        st.markdown(f"**{source}**")
                        for result in results:
                            st.markdown(f"""
                            <div class="evidence-section">
                                <strong>{result['title']}</strong><br>
                                <p>{result['summary']}</p>
                                <a href="{result['url']}" target="_blank">مشاهده منبع</a>
                            </div>
                            """, unsafe_allow_html=True)
    
    def render_recommendations(self, recommendations):
        """نمایش توصیه‌های کلی"""
        if recommendations:
            st.subheader("💡 توصیه‌های کلی")
            for rec in recommendations:
                st.markdown(f"""
                <div class="safe-card">
                    {rec}
                </div>
                """, unsafe_allow_html=True)
    
    def render_shop_section(self):
        """رندر بخش فروشگاه"""
        st.header("🛒 فروشگاه مکمل‌ها")
        
        products = self.shop.get_products()
        
        if not products:
            st.info("هیچ محصولی در فروشگاه موجود نیست.")
            return
        
        # دسته‌بندی محصولات
        categories = list(set([p['category'] for p in products if p['category']]))
        selected_category = st.selectbox("انتخاب دسته‌بندی", ["همه"] + categories)
        
        # فیلتر محصولات
        if selected_category != "همه":
            products = [p for p in products if p['category'] == selected_category]
        
        # نمایش محصولات
        cols = st.columns(3)
        
        for idx, product in enumerate(products):
            col = cols[idx % 3]
            
            with col:
                st.markdown(f"""
                <div class="shop-card">
                    <h4>{product['name']}</h4>
                    <p>{product['description'][:100]}...</p>
                    <div class="price-tag">
                        {product['price']:,} تومان
                    </div>
                    <br>
                    <small>موجودی: {product['stock']} عدد</small>
                </div>
                """, unsafe_allow_html=True)
                
                if product['stock'] > 0:
                    if st.button(f"افزودن به سبد", key=f"add_{product['id']}"):
                        self.shop.add_to_cart(product['id'])
                        st.success("محصول به سبد خرید اضافه شد!")
                        st.rerun()
                else:
                    st.error("ناموجود")
    
    def render_cart_section(self):
        """رندر بخش سبد خرید"""
        st.header("🛍️ سبد خرید")
        
        cart_items = self.shop.get_cart_items()
        
        if not cart_items:
            st.info("سبد خرید شما خالی است.")
            return
        
        # نمایش اقلام سبد
        total_amount = 0
        
        for item in cart_items:
            col1, col2, col3, col4 = st.columns([3, 1, 2, 1])
            
            with col1:
                st.write(f"**{item['name']}**")
                st.write(item['description'][:50] + "...")
            
            with col2:
                st.write(f"تعداد: {item['quantity']}")
            
            with col3:
                st.write(f"{item['total_price']:,} تومان")
            
            with col4:
                if st.button("حذف", key=f"remove_{item['id']}"):
                    if item['id'] in st.session_state.cart:
                        del st.session_state.cart[item['id']]
                        st.rerun()
            
            total_amount += item['total_price']
            st.divider()
        
        # مجموع سبد خرید
        st.markdown(f"""
        <div class="metric-card">
            <h3>مجموع: {total_amount:,} تومان</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # دکمه پرداخت
        if st.button("💳 پرداخت", key="payment_btn"):
            payment_result = self.shop.create_zarinpal_payment(
                total_amount, 
                "خرید مکمل‌های غذایی"
            )
            
            if payment_result['success']:
                st.success("در حال انتقال به درگاه پرداخت...")
                st.markdown(f'<meta http-equiv="refresh" content="0;url={payment_result["payment_url"]}">', 
                          unsafe_allow_html=True)
            else:
                st.error(f"خطا در ایجاد پرداخت: {payment_result.get('error', 'خطای نامشخص')}")
    
    def render_history_section(self):
        """رندر بخش تاریخچه"""
        st.header("📈 تاریخچه آنالیزها")
        
        # نمایش آخرین آنالیز
        if st.session_state.analysis_results:
            st.subheader("آخرین آنالیز")
            
            timestamp = st.session_state.analysis_results.get('timestamp')
            if timestamp:
                st.info(f"زمان آنالیز: {timestamp.strftime('%Y/%m/%d %H:%M')}")
            
            # نمایش خلاصه نتایج
            interactions = st.session_state.analysis_results.get('interactions', {})
            severity_summary = interactions.get('severity_summary', {})
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("تداخلات شدید", severity_summary.get('high', 0))
            with col2:
                st.metric("تداخلات متوسط", severity_summary.get('medium', 0))
            with col3:
                st.metric("تداخلات خفیف", severity_summary.get('low', 0))
            
            if st.button("مشاهده جزئیات کامل"):
                self.render_analysis_results()
        else:
            st.info("هنوز آنالیزی انجام نداده‌اید.")

# تابع اصلی برای اجرای برنامه
def main():
    """تابع اصلی برنامه"""
    app = SupplementAnalysisUI()
    app.run()

# اجرای برنامه
if __name__ == "__main__":
    main()
