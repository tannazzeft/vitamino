#!/bin/bash
set -e

FILE="app.py"

# 1. ایجاد بکاپ
cp "$FILE" "$FILE.bak"
echo "📂 پشتیبان ساخته شد: $FILE.bak"

# 2. حذف ایمپورت‌های استفاده‌نشده و خطوط بی‌مصرف
autoflake --in-place --remove-all-unused-imports --remove-unused-variables "$FILE"

# 3. حذف خطوط خالی اضافی
sed -i '/^[[:space:]]*$/N;/^\n$/D' "$FILE"

# 4. تبدیل تب به ۴ فاصله (اگر هنوز جایی مونده)
sed -i 's/\t/    /g' "$FILE"

# 5. فرمت استاندارد با black
black "$FILE"

# 6. بررسی استایل با flake8 (اختیاری، خطاها فقط گزارش می‌شوند)
flake8 "$FILE" || true

echo "✅ فایل $FILE تمیز و فرمت شد."
