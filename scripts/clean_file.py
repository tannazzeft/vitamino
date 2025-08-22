import re
import os

def clean_file(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    cleaned_content = re.sub(r'[^\x20-\x7E\u0600-\u06FF\n\t]', '', content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(cleaned_content)


def clean_all_csv(folder_path):
    for file in os.listdir(folder_path):
        if file.endswith(".csv"):
            file_path = os.path.join(folder_path, file)
            print(f"در حال تمیز کردن: {file}")
            clean_file(file_path)


clean_all_csv("./")
