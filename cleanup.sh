import re
import os
import shutil

def clean_file(file_path, backup=True):
    if not os.path.exists(file_path):
        print(f"فایل {file_path} یافت نشد!")
        return

    if backup:
        backup_path = file_path + '.bak'
        shutil.copy2(file_path, backup_path)
        print(f"نسخه پشتیبان در {backup_path} ایجاد شد.")

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    cleaned_content = re.sub(r'[^\x20-\x7E\u0600-\u06FF\n\t,.!?]', '', content)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(cleaned_content)
    print(f"فایل {file_path} تمیز شد.")

def clean_all_csv(folder_path="data"):  # تغییر به پوشه data
    if not os.path.isdir(folder_path):
        print(f"پوشه {folder_path} یافت نشد!")
        return

    csv_files = [f for f in os.listdir(folder_path) if f.lower().endswith(".csv")]
    if not csv_files:
        print(f"هیچ فایل CSV قابل خواندن در پوشه {folder_path} یافت نشد!")
        return

    for file in csv_files:
        file_path = os.path.join(folder_path, file)
        print(f"در حال تمیز کردن: {file}")
        clean_file(file_path)

if __name__ == "__main__":
    clean_all_csv()
