import undetected_chromedriver as uc
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver import ActionChains
from selenium.common.exceptions import StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
import string
import json
import requests
import uuid
import os 
import threading
import multiprocessing
import tempfile
from fake_useragent import UserAgent

# Türkçe profiller için
existing_emails = set()


def extract_password(proxy_line):
    try:
        # URL şu formatta: http://host:port:username:password...
        parts = proxy_line.strip().split(':')
        if len(parts) >= 4:
            return parts[4]  # 4. kısım şifre
        else:
            return None
    except Exception as e:
        print(f"Hata: {e}")
        return None

def get_random_password_from_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        if not lines:
            return None
        random_line = random.choice(lines)
        return extract_password(random_line)

def validate_proxy_with_api(proxy):
    try:
        proxies = {
            "http": proxy,
            "https": proxy
        }

        headers = {
            "Authorization": "Bearer 6d190351-b933-4dd5-96f8-16170269f3ea"
        }

        response = requests.get("https://proxy.evomi.com/api/v1/ip", proxies=proxies, headers=headers, timeout=10)
        data = response.json()

        print("Gelen yanıt:", data)  # <--- BURAYI EKLEDİK

        if response.status_code == 200 and data.get("status") == "success":
            return True
        else:
            print("Proxy doğrulama başarısız:", data)
            return False

    except Exception as e:
        print("Proxy doğrulama hatası:", e)
        return False

def replace_turkish_chars(text):
    translation_table = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")
    return text.translate(translation_table)

def generate_realistic_email(first_name, last_name):
    first_name_clean = replace_turkish_chars(first_name).lower()
    last_name_clean = replace_turkish_chars(last_name).lower()

    unique_parts = [
        str(random.randint(10, 9999)),                   # 2-4 haneli sayı
        uuid.uuid4().hex[:3],                            # 3 karakterli hash (çok sahici görünür)
        random.choice([
            "x", "v", "z", "pro", "mail", "tr", "online", "real", "user", "official", 
            "admin", "member", "premium", "guest", "vip", "free", "basic", "support", 
            "client", "staff", "mod", "owner", "manager", "superuser", "dev", "developer", 
            "beta", "test", "alpha", "viewer", "subscriber", "streamer", "creator", "artist", 
            "game", "forum", "contact", "news", "guide", "help", "feedback", "service", 
            "product", "chat", "social", "network", "group", "community", "partner", 
            "affiliate", "sales", "marketing", "branding", "business", "startup", 
            "enterprise", "corporate", "agency", "consult", "collaborator", "team", 
            "founder", "innovator", "designer", "programmer", "coder", "engineer", 
            "analyst", "strategist", "influencer", "spammer", "bot", "virtual", "system"
        ]), 
    ]

    email_styles = [
        f"{first_name_clean}.{last_name_clean}",
        f"{first_name_clean}{last_name_clean}",
        f"{first_name_clean}_{last_name_clean}",
        f"{first_name_clean}{random.choice(unique_parts)}",
        f"{last_name_clean}{random.choice(unique_parts)}",
        f"{first_name_clean}.{last_name_clean}{random.choice(unique_parts)}",
        f"{first_name_clean[:3]}{last_name_clean[:3]}{random.choice(unique_parts)}",
        f"{first_name_clean}{random.randint(1, 99)}_{random.choice(unique_parts)}",
        f"{first_name_clean}{random.choice(['_', '.', '-', ''])}{last_name_clean}",
        f"{first_name_clean[:2]}{last_name_clean}{random.randint(100, 999)}",
        f"{last_name_clean}{random.choice(['_', '.', '-', ''])}{first_name_clean}",
        f"{first_name_clean}{random.choice(['.', '-', '_'])}{random.randint(100, 999)}",
        f"{first_name_clean}{random.choice(['_', '.', '-'])}{last_name_clean}{random.randint(10, 99)}",
        f"{first_name_clean[0]}_{last_name_clean}{random.randint(1, 999)}",
        f"{first_name_clean[0].lower()}{last_name_clean.lower()}{random.choice(unique_parts)}",
        f"{first_name_clean[0]}{random.choice(['_', '.', '-', ''])}{last_name_clean[0]}{random.randint(1, 999)}",
        f"{first_name_clean}_{random.choice(['dev', 'user', 'admin'])}{random.randint(1000, 9999)}",
        f"{first_name_clean[:3]}{random.choice(['_', '.', '-'])}{last_name_clean[:3]}{random.randint(1, 99)}",
        f"{first_name_clean}{random.choice(['.', '-', '_', ''])}{random.choice(unique_parts)}",
        f"{first_name_clean}{random.choice(['_', '-', '.'])}{random.randint(10, 99)}{random.choice(['dev', 'admin', 'user'])}",
        f"{first_name_clean}{last_name_clean.lower()}{random.randint(100, 999)}",
        f"{random.choice(['the', 'real', 'official'])}{first_name_clean.lower()}{last_name_clean.lower()}",
        f"{first_name_clean[0]}_{random.choice(unique_parts)}{last_name_clean.lower()}",
        f"{first_name_clean.lower()}{random.choice(['_', '.', '-', ''])}{last_name_clean.lower()}",
        f"{first_name_clean}{random.choice(['_', '-', '.', ''])}{random.randint(100, 999)}",
        f"{first_name_clean}_{last_name_clean}_{random.randint(1, 999)}"
    ]


    domain = random.choice(["gmail.com", "outlook.com", "hotmail.com", "icloud.com"])
    email = f"{random.choice(email_styles)}@{domain}"

    # Benzersiz olana kadar döngü
    while email in existing_emails:
        new_suffix = uuid.uuid4().hex[:3]
        email = f"{first_name_clean}{last_name_clean}{new_suffix}@{domain}"

    existing_emails.add(email)
    return email

def generate_password():
    letters = string.ascii_letters
    digits = string.digits
    special_chars = "#?!&$@%"
    password_length = random.randint(11, 16)
    password = [
        random.choice(letters),                # Harf
        random.choice(digits),                 # Rakam
        random.choice(special_chars)           # Özel karakter
    ]
    all_chars = letters + digits + special_chars
    password += random.choices(all_chars, k=password_length - 3) 
    random.shuffle(password)
    return ''.join(password)

def select_random_names(file_path, count=1):
    with open(file_path, 'r', encoding='utf-8') as file:
        names = [line.strip() for line in file if line.strip()]
    
    if count > len(names):
        raise ValueError("Requested count exceeds the number of names in the file.")
    
    return random.sample(names, count)

def generate_realistic_birthdate():
    start_year = 1992
    end_year = 2008
    while True:
        year = random.randint(start_year, end_year)
        month = random.randint(1, 12)
        try:
            day = random.randint(1, 28 if month == 2 else 30)
            return year, month, day
        except ValueError:
            continue

def generate_display_name(first_name, last_name):
    first_name_clean = replace_turkish_chars(first_name)
    last_name_clean = replace_turkish_chars(last_name)
    styles = [
        f"{first_name} {last_name}",
        f"{first_name_clean}{random.randint(10, 99)}",
        f"{first_name_clean}_{last_name_clean}",
        f"{first_name}",
        f"{first_name_clean.lower()}{last_name_clean[0].lower()}_{random.randint(1, 99)}",
        f"{first_name_clean}.{last_name_clean}",
        f"{first_name_clean.lower()}.{random.randint(1000,9999)}",
        f"{first_name_clean.lower()}{random.choice(['_', '.', '-', ''])}{last_name_clean.lower()}",
        f"{first_name_clean[:3].lower()}{last_name_clean[:3].lower()}{random.randint(1, 999)}",
        f"{last_name_clean}{random.randint(1, 999)}",
        f"{first_name_clean.lower()}_{random.choice(['x', 'xx', 'x_'])}{last_name_clean.lower()}",
        f"{first_name_clean.lower()}{random.choice(['_', '-', '.'])}{random.randint(100, 999)}",
        f"{first_name_clean.lower()}{last_name_clean.lower()}{random.randint(1,99)}",
        f"{first_name_clean.lower()}{last_name_clean.lower()}{random.choice(['_', '-', '.', ''])}{random.randint(1,999)}",
        f"{last_name_clean.lower()}{first_name_clean[0].lower()}{random.randint(1, 999)}",
        f"{first_name_clean.lower()}_{random.randint(1000, 9999)}",
        f"{random.choice(['the', 'real', 'official'])}_{first_name_clean.lower()}",
        f"{first_name_clean.lower()}{random.choice(['_', '-', ''])}dev",
        f"{first_name_clean.lower()}{random.randint(1990, 2025)}",
        f"{first_name_clean.lower()}_user{random.randint(1, 999)}"
    ]


    return random.choice(styles)


def save_account(email, password, first_name, last_name, username, birth_year, birth_month, birth_day, gender, ip_address, location):
    account_data = {
        "email": email,
        "password": password,
        "first_name": first_name,
        "last_name": last_name,
        "username": username,
        "birth_year": birth_year,
        "birth_month": birth_month,
        "birth_day": birth_day,
        "gender": gender,
        "ip_address": ip_address,
        "location": location
    }

    file_path = "data/test_accounts.json"

    # Önceki verileri oku (varsa)
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            try:
                accounts = json.load(file)
            except json.JSONDecodeError:
                accounts = []
    else:
        accounts = []

    # Yeni hesabı ekle
    accounts.append(account_data)

    # Yazım: dizi içinde her obje tek satırda, alt alta
    with open(file_path, "w", encoding="utf-8") as file:
        file.write("[\n")
        for i, acc in enumerate(accounts):
            json_line = json.dumps(acc, ensure_ascii=False)
            file.write(f"  {json_line}")
            if i != len(accounts) - 1:
                file.write(",\n")
            else:
                file.write("\n")
        file.write("]")


def get_proxy_location(proxy):
    try:
        # Eğer proxy bir dict ise IP adresini al
        if isinstance(proxy, dict):
            ip = proxy["server"].split("//")[-1].split(":")[0]
        else:
            ip = proxy.split("//")[-1].split(":")[0]

        response = requests.get(f"http://ip-api.com/json/{ip}")
        data = response.json()
        country = data.get("country", "Bilinmeyen Ülke")
        city = data.get("city", "Bilinmeyen Şehir")
        region = data.get("regionName", "Bilinmeyen")
        zipCode = data.get("zip", "Bilinmeyen"),
        timezone = data.get("timezone", "Bilinmeyen"),
        isp = data.get("isp", "Bilinmeyen"),
        org = data.get("org", "Bilinmeyen"),
        ags = data.get("as", "Bilinmeyen"),
        cords = f"{data.get('lat', 'Bilinmeyen')}, {data.get('lon', 'Bilinmeyen')}"
        return f"{city}, {country}, {region}"
    except Exception as e:
        print(f"Konum belirleme hatası: {e}")
        return "Bilinmeyen Konum"

def human_sleep(min_sec=0.7, max_sec=2.0):
    time.sleep(random.uniform(min_sec, max_sec))

def type_like_human(element, text):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.1))

def human_click(driver, element):
    # Ekrana kaydır
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    time.sleep(random.uniform(0.5, 1.5))

    # Hover gibi davran
    actions = ActionChains(driver)
    actions.move_to_element(element).pause(random.uniform(0.2, 0.6)).click().perform()

    # Ekstra rastgele bekleme
    time.sleep(random.uniform(0.3, 1.2))

def safe_human_click(driver, locator_fn, max_retries=3):
    for attempt in range(max_retries):
        try:
            element = locator_fn()
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(random.uniform(0.4, 1.0))

            actions = ActionChains(driver)
            actions.move_to_element(element).pause(random.uniform(0.2, 0.6)).click().perform()

            return True  # Başarılı
        except StaleElementReferenceException:
            print(f"[{attempt+1}/{max_retries}] Element yeniden bulunuyor...")
            time.sleep(0.5)
    return False

def create_spotify_accounts(screen_position):
    global active_threads
    driver = None
    with position_locks[position]:
        print(f"🖥️ Pozisyon {position} kullanılıyor.")
        try:
            file_path = 'name.txt'  
            random_names = select_random_names(file_path, count=2)

            first_name = random_names[0]
            last_name = random_names[1]
            email = generate_realistic_email(first_name, last_name)
            password = generate_password()
            birth_year, birth_month, birth_day = generate_realistic_birthdate()
            username = generate_display_name(first_name, last_name)
            gender = random.choice(["gender_option_male", "gender_option_female"])
            
            # === Proxy ve User-Agent Ayarları ===
            file_path = 'data/proxy.txt'
            proxy_host = 'core-residential.evomi.com'
            proxy_port = 1000
            proxy_user = 'demoloski3'
            proxy_pass = get_random_password_from_file(file_path)
            
            turkish_user_agents = [
                "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.86 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 11; Redmi Note 10 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 10; HUAWEI P30 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 9; OnePlus 6T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.86 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0"
                "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/123.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Opera/95.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Brave/123.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_7) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/122.0"
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Edge/123.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Opera/95.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0"
                "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Arch Linux; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Opera/95.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0"
                "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Arch Linux; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Opera/95.0.0.0 Safari/537.36",
                "Mozilla/5.0 (iPad; CPU iPad OS 17_0 like Mac OS X) AppleWebKit/600.1.9 (KHTML, like Gecko) Version/15.0 Mobile/11E285 Safari/600.1.9",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 12_4 like Mac OS X) AppleWebKit/602.1.18 (KHTML, like Gecko) Version/16.0 Mobile/11E196 Safari/602.1.18",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 13_2 like Mac OS X) AppleWebKit/603.1.20 (KHTML, like Gecko) Version/13.0 Mobile/17E399 Safari/603.1.20",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 17_0 like Mac OS X) AppleWebKit/604.1.6 (KHTML, like Gecko) Version/12.0 Mobile/18E347 Safari/604.1.6",
                "Mozilla/5.0 (iPad; CPU iPad OS 17_4 like Mac OS X) AppleWebKit/602.1.17 (KHTML, like Gecko) Version/16.0 Mobile/19E152 Safari/602.1.17",
                "Mozilla/5.0 (iPad; CPU iPad OS 15_0 like Mac OS X) AppleWebKit/603.1.3 (KHTML, like Gecko) Version/13.0 Mobile/19E152 Safari/603.1.3",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 17_4 like Mac OS X) AppleWebKit/605.1.5 (KHTML, like Gecko) Version/13.0 Mobile/19E261 Safari/605.1.5",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 16_0 like Mac OS X) AppleWebKit/602.1.2 (KHTML, like Gecko) Version/15.0 Mobile/10E244 Safari/602.1.2",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 16_3 like Mac OS X) AppleWebKit/600.1.6 (KHTML, like Gecko) Version/16.0 Mobile/19E950 Safari/600.1.6",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 14_1 like Mac OS X) AppleWebKit/602.1.3 (KHTML, like Gecko) Version/14.0 Mobile/18E925 Safari/602.1.3",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 13_4 like Mac OS X) AppleWebKit/605.1.7 (KHTML, like Gecko) Version/14.0 Mobile/18E991 Safari/605.1.7",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 14_1 like Mac OS X) AppleWebKit/604.1.8 (KHTML, like Gecko) Version/13.0 Mobile/11E672 Safari/604.1.8",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 15_4 like Mac OS X) AppleWebKit/601.1.6 (KHTML, like Gecko) Version/14.0 Mobile/19E232 Safari/601.1.6",
                "Mozilla/5.0 (iPad; CPU iPad OS 13_2 like Mac OS X) AppleWebKit/605.1.11 (KHTML, like Gecko) Version/17.0 Mobile/20E687 Safari/605.1.11",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 13_0 like Mac OS X) AppleWebKit/604.1.6 (KHTML, like Gecko) Version/13.0 Mobile/15E859 Safari/604.1.6",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 12_4 like Mac OS X) AppleWebKit/605.1.5 (KHTML, like Gecko) Version/13.0 Mobile/19E485 Safari/605.1.5",
                "Mozilla/5.0 (iPad; CPU iPad OS 16_0 like Mac OS X) AppleWebKit/605.1.11 (KHTML, like Gecko) Version/14.0 Mobile/12E800 Safari/605.1.11",
                "Mozilla/5.0 (iPad; CPU iPad OS 15_0 like Mac OS X) AppleWebKit/604.1.20 (KHTML, like Gecko) Version/12.0 Mobile/10E536 Safari/604.1.20",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 17_2 like Mac OS X) AppleWebKit/604.1.3 (KHTML, like Gecko) Version/12.0 Mobile/16E985 Safari/604.1.3",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/602.1.3 (KHTML, like Gecko) Version/14.0 Mobile/14E910 Safari/602.1.3",
                "Mozilla/5.0 (iPad; CPU iPad OS 16_2 like Mac OS X) AppleWebKit/602.1.4 (KHTML, like Gecko) Version/16.0 Mobile/10E382 Safari/602.1.4",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/601.1.16 (KHTML, like Gecko) Version/14.0 Mobile/17E214 Safari/601.1.16",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 15_1 like Mac OS X) AppleWebKit/605.1.8 (KHTML, like Gecko) Version/15.0 Mobile/13E145 Safari/605.1.8",
                "Mozilla/5.0 (iPad; CPU iPad OS 16_2 like Mac OS X) AppleWebKit/601.1.16 (KHTML, like Gecko) Version/13.0 Mobile/18E784 Safari/601.1.16",
                "Mozilla/5.0 (iPad; CPU iPad OS 15_4 like Mac OS X) AppleWebKit/604.1.10 (KHTML, like Gecko) Version/13.0 Mobile/13E706 Safari/604.1.10",
                "Mozilla/5.0 (iPad; CPU iPad OS 15_1 like Mac OS X) AppleWebKit/602.1.12 (KHTML, like Gecko) Version/14.0 Mobile/11E232 Safari/602.1.12",
                "Mozilla/5.0 (iPad; CPU iPad OS 12_3 like Mac OS X) AppleWebKit/604.1.3 (KHTML, like Gecko) Version/12.0 Mobile/12E521 Safari/604.1.3",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 17_3 like Mac OS X) AppleWebKit/603.1.19 (KHTML, like Gecko) Version/17.0 Mobile/19E860 Safari/603.1.19",
                "Mozilla/5.0 (iPad; CPU iPad OS 13_3 like Mac OS X) AppleWebKit/603.1.1 (KHTML, like Gecko) Version/14.0 Mobile/20E585 Safari/603.1.1",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/602.1.2 (KHTML, like Gecko) Version/12.0 Mobile/10E244 Safari/602.1.2",
                "Mozilla/5.0 (iPad; CPU iPad OS 16_0 like Mac OS X) AppleWebKit/600.1.17 (KHTML, like Gecko) Version/12.0 Mobile/20E933 Safari/600.1.17",
                "Mozilla/5.0 (iPad; CPU iPad OS 12_1 like Mac OS X) AppleWebKit/600.1.9 (KHTML, like Gecko) Version/13.0 Mobile/18E925 Safari/600.1.9",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 16_1 like Mac OS X) AppleWebKit/604.1.11 (KHTML, like Gecko) Version/15.0 Mobile/10E536 Safari/604.1.11",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 12_3 like Mac OS X) AppleWebKit/604.1.5 (KHTML, like Gecko) Version/12.0 Mobile/15E903 Safari/604.1.5",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 15_1 like Mac OS X) AppleWebKit/602.1.3 (KHTML, like Gecko) Version/12.0 Mobile/16E616 Safari/602.1.3",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/604.1.15 (KHTML, like Gecko) Version/16.0 Mobile/20E974 Safari/604.1.15",
                "Mozilla/5.0 (iPad; CPU iPad OS 15_4 like Mac OS X) AppleWebKit/605.1.1 (KHTML, like Gecko) Version/16.0 Mobile/13E706 Safari/605.1.1",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 12_1 like Mac OS X) AppleWebKit/604.1.6 (KHTML, like Gecko) Version/14.0 Mobile/17E664 Safari/604.1.6",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 12_4 like Mac OS X) AppleWebKit/604.1.6 (KHTML, like Gecko) Version/13.0 Mobile/13E202 Safari/604.1.6",
                "Mozilla/5.0 (iPad; CPU iPad OS 12_0 like Mac OS X) AppleWebKit/601.1.16 (KHTML, like Gecko) Version/12.0 Mobile/16E985 Safari/601.1.16",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 16_4 like Mac OS X) AppleWebKit/600.1.6 (KHTML, like Gecko) Version/14.0 Mobile/11E232 Safari/600.1.6",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 14_1 like Mac OS X) AppleWebKit/604.1.14 (KHTML, like Gecko) Version/15.0 Mobile/20E585 Safari/604.1.14",
                "Mozilla/5.0 (iPad; CPU iPad OS 16_1 like Mac OS X) AppleWebKit/602.1.8 (KHTML, like Gecko) Version/12.0 Mobile/14E836 Safari/602.1.8",
                "Mozilla/5.0 (iPad; CPU iPad OS 14_3 like Mac OS X) AppleWebKit/603.1.16 (KHTML, like Gecko) Version/12.0 Mobile/13E891 Safari/603.1.16",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 12_0 like Mac OS X) AppleWebKit/602.1.3 (KHTML, like Gecko) Version/12.0 Mobile/18E163 Safari/602.1.3",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 13_1 like Mac OS X) AppleWebKit/604.1.6 (KHTML, like Gecko) Version/13.0 Mobile/17E990 Safari/604.1.6",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 12_2 like Mac OS X) AppleWebKit/603.1.1 (KHTML, like Gecko) Version/14.0 Mobile/18E715 Safari/603.1.1",
                "Mozilla/5.0 (iPad; CPU iPad OS 12_0 like Mac OS X) AppleWebKit/604.1.10 (KHTML, like Gecko) Version/12.0 Mobile/14E147 Safari/604.1.10",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 14_3 like Mac OS X) AppleWebKit/603.1.18 (KHTML, like Gecko) Version/17.0 Mobile/20E620 Safari/603.1.18",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 13_1 like Mac OS X) AppleWebKit/600.1.2 (KHTML, like Gecko) Version/14.0 Mobile/12E800 Safari/600.1.2",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 16_4 like Mac OS X) AppleWebKit/604.1.15 (KHTML, like Gecko) Version/15.0 Mobile/10E536 Safari/604.1.15",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 12_3 like Mac OS X) AppleWebKit/603.1.7 (KHTML, like Gecko) Version/15.0 Mobile/20E344 Safari/603.1.7",
                "Mozilla/5.0 (iPad; CPU iPad OS 12_3 like Mac OS X) AppleWebKit/602.1.12 (KHTML, like Gecko) Version/17.0 Mobile/19E955 Safari/602.1.12",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.14 (KHTML, like Gecko) Version/14.0 Mobile/13E573 Safari/604.1.14",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 13_3 like Mac OS X) AppleWebKit/602.1.17 (KHTML, like Gecko) Version/12.0 Mobile/15E903 Safari/602.1.17",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 15_3 like Mac OS X) AppleWebKit/604.1.11 (KHTML, like Gecko) Version/13.0 Mobile/15E255 Safari/604.1.11",
                "Mozilla/5.0 (iPad; CPU iPad OS 15_2 like Mac OS X) AppleWebKit/604.1.11 (KHTML, like Gecko) Version/14.0 Mobile/16E401 Safari/604.1.11",
                "Mozilla/5.0 (iPad; CPU iPad OS 16_1 like Mac OS X) AppleWebKit/604.1.11 (KHTML, like Gecko) Version/12.0 Mobile/17E258 Safari/604.1.11",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/603.1.20 (KHTML, like Gecko) Version/14.0 Mobile/12E800 Safari/603.1.20",
                "Mozilla/5.0 (iPad; CPU iPad OS 12_3 like Mac OS X) AppleWebKit/602.1.7 (KHTML, like Gecko) Version/13.0 Mobile/15E903 Safari/602.1.7",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/604.1.20 (KHTML, like Gecko) Version/13.0 Mobile/16E616 Safari/604.1.20",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 12_1 like Mac OS X) AppleWebKit/600.1.14 (KHTML, like Gecko) Version/14.0 Mobile/11E664 Safari/600.1.14",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.3 (KHTML, like Gecko) Version/14.0 Mobile/10E720 Safari/605.1.3",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 14_3 like Mac OS X) AppleWebKit/604.1.20 (KHTML, like Gecko) Version/12.0 Mobile/17E214 Safari/604.1.20",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 13_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Mobile/17E289 Safari/605.1.15",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.3 (KHTML, like Gecko) Version/15.0 Mobile/18E925 Safari/604.1.3",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 15_2 like Mac OS X) AppleWebKit/600.1.17 (KHTML, like Gecko) Version/17.0 Mobile/18E991 Safari/600.1.17",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 14_2 like Mac OS X) AppleWebKit/600.1.14 (KHTML, like Gecko) Version/13.0 Mobile/20E942 Safari/600.1.14",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 15_2 like Mac OS X) AppleWebKit/601.1.9 (KHTML, like Gecko) Version/16.0 Mobile/19E647 Safari/601.1.9",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 13_3 like Mac OS X) AppleWebKit/604.1.12 (KHTML, like Gecko) Version/13.0 Mobile/11E573 Safari/604.1.12",
                "Mozilla/5.0 (iPad; CPU iPad OS 12_4 like Mac OS X) AppleWebKit/605.1.3 (KHTML, like Gecko) Version/13.0 Mobile/13E743 Safari/605.1.3",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 14_2 like Mac OS X) AppleWebKit/604.1.14 (KHTML, like Gecko) Version/15.0 Mobile/15E859 Safari/604.1.14",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/604.1.7 (KHTML, like Gecko) Version/17.0 Mobile/10E244 Safari/604.1.7",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 16_1 like Mac OS X) AppleWebKit/604.1.12 (KHTML, like Gecko) Version/17.0 Mobile/16E401 Safari/604.1.12",
                "Mozilla/5.0 (iPad; CPU iPad OS 14_2 like Mac OS X) AppleWebKit/600.1.7 (KHTML, like Gecko) Version/14.0 Mobile/19E647 Safari/600.1.7",
                "Mozilla/5.0 (iPad; CPU iPad OS 13_3 like Mac OS X) AppleWebKit/602.1.3 (KHTML, like Gecko) Version/13.0 Mobile/15E859 Safari/602.1.3",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 14_1 like Mac OS X) AppleWebKit/602.1.7 (KHTML, like Gecko) Version/16.0 Mobile/14E811 Safari/602.1.7",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 16_2 like Mac OS X) AppleWebKit/605.1.4 (KHTML, like Gecko) Version/16.0 Mobile/18E347 Safari/605.1.4",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 16_2 like Mac OS X) AppleWebKit/602.1.17 (KHTML, like Gecko) Version/13.0 Mobile/10E536 Safari/602.1.17",
                "Mozilla/5.0 (iPad; CPU iPad OS 14_1 like Mac OS X) AppleWebKit/604.1.18 (KHTML, like Gecko) Version/17.0 Mobile/16E759 Safari/604.1.18",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/603.1.16 (KHTML, like Gecko) Version/16.0 Mobile/19E485 Safari/603.1.16",
                "Mozilla/5.0 (iPad; CPU iPad OS 17_2 like Mac OS X) AppleWebKit/603.1.18 (KHTML, like Gecko) Version/16.0 Mobile/13E743 Safari/603.1.18",
                "Mozilla/5.0 (iPad; CPU iPad OS 17_3 like Mac OS X) AppleWebKit/604.1.5 (KHTML, like Gecko) Version/13.0 Mobile/16E985 Safari/604.1.5",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 17_2 like Mac OS X) AppleWebKit/604.1.6 (KHTML, like Gecko) Version/16.0 Mobile/16E985 Safari/604.1.6",
                "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.86 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 11; Redmi Note 10 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 10; HUAWEI P30 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 9; OnePlus 6T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.6312.86 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0"
                "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/123.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Opera/95.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Brave/123.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_7) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/122.0"
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Edge/123.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Opera/95.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0"
                "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Arch Linux; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Opera/95.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0"
                "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Arch Linux; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Opera/95.0.0.0 Safari/537.36",
                "Mozilla/5.0 (iPad; CPU iPad OS 17_0 like Mac OS X) AppleWebKit/600.1.9 (KHTML, like Gecko) Version/15.0 Mobile/11E285 Safari/600.1.9",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 12_4 like Mac OS X) AppleWebKit/602.1.18 (KHTML, like Gecko) Version/16.0 Mobile/11E196 Safari/602.1.18",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 13_2 like Mac OS X) AppleWebKit/603.1.20 (KHTML, like Gecko) Version/13.0 Mobile/17E399 Safari/603.1.20",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 17_0 like Mac OS X) AppleWebKit/604.1.6 (KHTML, like Gecko) Version/12.0 Mobile/18E347 Safari/604.1.6",
                "Mozilla/5.0 (iPad; CPU iPad OS 17_4 like Mac OS X) AppleWebKit/602.1.17 (KHTML, like Gecko) Version/16.0 Mobile/19E152 Safari/602.1.17",
                "Mozilla/5.0 (iPad; CPU iPad OS 15_0 like Mac OS X) AppleWebKit/603.1.3 (KHTML, like Gecko) Version/13.0 Mobile/19E152 Safari/603.1.3",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 17_4 like Mac OS X) AppleWebKit/605.1.5 (KHTML, like Gecko) Version/13.0 Mobile/19E261 Safari/605.1.5",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 16_0 like Mac OS X) AppleWebKit/602.1.2 (KHTML, like Gecko) Version/15.0 Mobile/10E244 Safari/602.1.2",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 16_3 like Mac OS X) AppleWebKit/600.1.6 (KHTML, like Gecko) Version/16.0 Mobile/19E950 Safari/600.1.6",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 14_1 like Mac OS X) AppleWebKit/602.1.3 (KHTML, like Gecko) Version/14.0 Mobile/18E925 Safari/602.1.3",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 13_4 like Mac OS X) AppleWebKit/605.1.7 (KHTML, like Gecko) Version/14.0 Mobile/18E991 Safari/605.1.7",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 14_1 like Mac OS X) AppleWebKit/604.1.8 (KHTML, like Gecko) Version/13.0 Mobile/11E672 Safari/604.1.8",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 15_4 like Mac OS X) AppleWebKit/601.1.6 (KHTML, like Gecko) Version/14.0 Mobile/19E232 Safari/601.1.6",
                "Mozilla/5.0 (iPad; CPU iPad OS 13_2 like Mac OS X) AppleWebKit/605.1.11 (KHTML, like Gecko) Version/17.0 Mobile/20E687 Safari/605.1.11",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 13_0 like Mac OS X) AppleWebKit/604.1.6 (KHTML, like Gecko) Version/13.0 Mobile/15E859 Safari/604.1.6",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 12_4 like Mac OS X) AppleWebKit/605.1.5 (KHTML, like Gecko) Version/13.0 Mobile/19E485 Safari/605.1.5",
                "Mozilla/5.0 (iPad; CPU iPad OS 16_0 like Mac OS X) AppleWebKit/605.1.11 (KHTML, like Gecko) Version/14.0 Mobile/12E800 Safari/605.1.11",
                "Mozilla/5.0 (iPad; CPU iPad OS 15_0 like Mac OS X) AppleWebKit/604.1.20 (KHTML, like Gecko) Version/12.0 Mobile/10E536 Safari/604.1.20",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 17_2 like Mac OS X) AppleWebKit/604.1.3 (KHTML, like Gecko) Version/12.0 Mobile/16E985 Safari/604.1.3",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/602.1.3 (KHTML, like Gecko) Version/14.0 Mobile/14E910 Safari/602.1.3",
                "Mozilla/5.0 (iPad; CPU iPad OS 16_2 like Mac OS X) AppleWebKit/602.1.4 (KHTML, like Gecko) Version/16.0 Mobile/10E382 Safari/602.1.4",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/601.1.16 (KHTML, like Gecko) Version/14.0 Mobile/17E214 Safari/601.1.16",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 15_1 like Mac OS X) AppleWebKit/605.1.8 (KHTML, like Gecko) Version/15.0 Mobile/13E145 Safari/605.1.8",
                "Mozilla/5.0 (iPad; CPU iPad OS 16_2 like Mac OS X) AppleWebKit/601.1.16 (KHTML, like Gecko) Version/13.0 Mobile/18E784 Safari/601.1.16",
                "Mozilla/5.0 (iPad; CPU iPad OS 15_4 like Mac OS X) AppleWebKit/604.1.10 (KHTML, like Gecko) Version/13.0 Mobile/13E706 Safari/604.1.10",
                "Mozilla/5.0 (iPad; CPU iPad OS 15_1 like Mac OS X) AppleWebKit/602.1.12 (KHTML, like Gecko) Version/14.0 Mobile/11E232 Safari/602.1.12",
                "Mozilla/5.0 (iPad; CPU iPad OS 12_3 like Mac OS X) AppleWebKit/604.1.3 (KHTML, like Gecko) Version/12.0 Mobile/12E521 Safari/604.1.3",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 17_3 like Mac OS X) AppleWebKit/603.1.19 (KHTML, like Gecko) Version/17.0 Mobile/19E860 Safari/603.1.19",
                "Mozilla/5.0 (iPad; CPU iPad OS 13_3 like Mac OS X) AppleWebKit/603.1.1 (KHTML, like Gecko) Version/14.0 Mobile/20E585 Safari/603.1.1",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/602.1.2 (KHTML, like Gecko) Version/12.0 Mobile/10E244 Safari/602.1.2",
                "Mozilla/5.0 (iPad; CPU iPad OS 16_0 like Mac OS X) AppleWebKit/600.1.17 (KHTML, like Gecko) Version/12.0 Mobile/20E933 Safari/600.1.17",
                "Mozilla/5.0 (iPad; CPU iPad OS 12_1 like Mac OS X) AppleWebKit/600.1.9 (KHTML, like Gecko) Version/13.0 Mobile/18E925 Safari/600.1.9",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 16_1 like Mac OS X) AppleWebKit/604.1.11 (KHTML, like Gecko) Version/15.0 Mobile/10E536 Safari/604.1.11",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 12_3 like Mac OS X) AppleWebKit/604.1.5 (KHTML, like Gecko) Version/12.0 Mobile/15E903 Safari/604.1.5",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 15_1 like Mac OS X) AppleWebKit/602.1.3 (KHTML, like Gecko) Version/12.0 Mobile/16E616 Safari/602.1.3",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/604.1.15 (KHTML, like Gecko) Version/16.0 Mobile/20E974 Safari/604.1.15",
                "Mozilla/5.0 (iPad; CPU iPad OS 15_4 like Mac OS X) AppleWebKit/605.1.1 (KHTML, like Gecko) Version/16.0 Mobile/13E706 Safari/605.1.1",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 12_1 like Mac OS X) AppleWebKit/604.1.6 (KHTML, like Gecko) Version/14.0 Mobile/17E664 Safari/604.1.6",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 12_4 like Mac OS X) AppleWebKit/604.1.6 (KHTML, like Gecko) Version/13.0 Mobile/13E202 Safari/604.1.6",
                "Mozilla/5.0 (iPad; CPU iPad OS 12_0 like Mac OS X) AppleWebKit/601.1.16 (KHTML, like Gecko) Version/12.0 Mobile/16E985 Safari/601.1.16",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 16_4 like Mac OS X) AppleWebKit/600.1.6 (KHTML, like Gecko) Version/14.0 Mobile/11E232 Safari/600.1.6",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 14_1 like Mac OS X) AppleWebKit/604.1.14 (KHTML, like Gecko) Version/15.0 Mobile/20E585 Safari/604.1.14",
                "Mozilla/5.0 (iPad; CPU iPad OS 16_1 like Mac OS X) AppleWebKit/602.1.8 (KHTML, like Gecko) Version/12.0 Mobile/14E836 Safari/602.1.8",
                "Mozilla/5.0 (iPad; CPU iPad OS 14_3 like Mac OS X) AppleWebKit/603.1.16 (KHTML, like Gecko) Version/12.0 Mobile/13E891 Safari/603.1.16",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 12_0 like Mac OS X) AppleWebKit/602.1.3 (KHTML, like Gecko) Version/12.0 Mobile/18E163 Safari/602.1.3",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 13_1 like Mac OS X) AppleWebKit/604.1.6 (KHTML, like Gecko) Version/13.0 Mobile/17E990 Safari/604.1.6",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 12_2 like Mac OS X) AppleWebKit/603.1.1 (KHTML, like Gecko) Version/14.0 Mobile/18E715 Safari/603.1.1",
                "Mozilla/5.0 (iPad; CPU iPad OS 12_0 like Mac OS X) AppleWebKit/604.1.10 (KHTML, like Gecko) Version/12.0 Mobile/14E147 Safari/604.1.10",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 14_3 like Mac OS X) AppleWebKit/603.1.18 (KHTML, like Gecko) Version/17.0 Mobile/20E620 Safari/603.1.18",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 13_1 like Mac OS X) AppleWebKit/600.1.2 (KHTML, like Gecko) Version/14.0 Mobile/12E800 Safari/600.1.2",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 16_4 like Mac OS X) AppleWebKit/604.1.15 (KHTML, like Gecko) Version/15.0 Mobile/10E536 Safari/604.1.15",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 12_3 like Mac OS X) AppleWebKit/603.1.7 (KHTML, like Gecko) Version/15.0 Mobile/20E344 Safari/603.1.7",
                "Mozilla/5.0 (iPad; CPU iPad OS 12_3 like Mac OS X) AppleWebKit/602.1.12 (KHTML, like Gecko) Version/17.0 Mobile/19E955 Safari/602.1.12",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.14 (KHTML, like Gecko) Version/14.0 Mobile/13E573 Safari/604.1.14",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 13_3 like Mac OS X) AppleWebKit/602.1.17 (KHTML, like Gecko) Version/12.0 Mobile/15E903 Safari/602.1.17",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 15_3 like Mac OS X) AppleWebKit/604.1.11 (KHTML, like Gecko) Version/13.0 Mobile/15E255 Safari/604.1.11",
                "Mozilla/5.0 (iPad; CPU iPad OS 15_2 like Mac OS X) AppleWebKit/604.1.11 (KHTML, like Gecko) Version/14.0 Mobile/16E401 Safari/604.1.11",
                "Mozilla/5.0 (iPad; CPU iPad OS 16_1 like Mac OS X) AppleWebKit/604.1.11 (KHTML, like Gecko) Version/12.0 Mobile/17E258 Safari/604.1.11",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/603.1.20 (KHTML, like Gecko) Version/14.0 Mobile/12E800 Safari/603.1.20",
                "Mozilla/5.0 (iPad; CPU iPad OS 12_3 like Mac OS X) AppleWebKit/602.1.7 (KHTML, like Gecko) Version/13.0 Mobile/15E903 Safari/602.1.7",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/604.1.20 (KHTML, like Gecko) Version/13.0 Mobile/16E616 Safari/604.1.20",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 12_1 like Mac OS X) AppleWebKit/600.1.14 (KHTML, like Gecko) Version/14.0 Mobile/11E664 Safari/600.1.14",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.3 (KHTML, like Gecko) Version/14.0 Mobile/10E720 Safari/605.1.3",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 14_3 like Mac OS X) AppleWebKit/604.1.20 (KHTML, like Gecko) Version/12.0 Mobile/17E214 Safari/604.1.20",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 13_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Mobile/17E289 Safari/605.1.15",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/604.1.3 (KHTML, like Gecko) Version/15.0 Mobile/18E925 Safari/604.1.3",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 15_2 like Mac OS X) AppleWebKit/600.1.17 (KHTML, like Gecko) Version/17.0 Mobile/18E991 Safari/600.1.17",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 14_2 like Mac OS X) AppleWebKit/600.1.14 (KHTML, like Gecko) Version/13.0 Mobile/20E942 Safari/600.1.14",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 15_2 like Mac OS X) AppleWebKit/601.1.9 (KHTML, like Gecko) Version/16.0 Mobile/19E647 Safari/601.1.9",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 13_3 like Mac OS X) AppleWebKit/604.1.12 (KHTML, like Gecko) Version/13.0 Mobile/11E573 Safari/604.1.12",
                "Mozilla/5.0 (iPad; CPU iPad OS 12_4 like Mac OS X) AppleWebKit/605.1.3 (KHTML, like Gecko) Version/13.0 Mobile/13E743 Safari/605.1.3",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 14_2 like Mac OS X) AppleWebKit/604.1.14 (KHTML, like Gecko) Version/15.0 Mobile/15E859 Safari/604.1.14",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/604.1.7 (KHTML, like Gecko) Version/17.0 Mobile/10E244 Safari/604.1.7",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 16_1 like Mac OS X) AppleWebKit/604.1.12 (KHTML, like Gecko) Version/17.0 Mobile/16E401 Safari/604.1.12",
                "Mozilla/5.0 (iPad; CPU iPad OS 14_2 like Mac OS X) AppleWebKit/600.1.7 (KHTML, like Gecko) Version/14.0 Mobile/19E647 Safari/600.1.7",
                "Mozilla/5.0 (iPad; CPU iPad OS 13_3 like Mac OS X) AppleWebKit/602.1.3 (KHTML, like Gecko) Version/13.0 Mobile/15E859 Safari/602.1.3",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 14_1 like Mac OS X) AppleWebKit/602.1.7 (KHTML, like Gecko) Version/16.0 Mobile/14E811 Safari/602.1.7",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 16_2 like Mac OS X) AppleWebKit/605.1.4 (KHTML, like Gecko) Version/16.0 Mobile/18E347 Safari/605.1.4",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 16_2 like Mac OS X) AppleWebKit/602.1.17 (KHTML, like Gecko) Version/13.0 Mobile/10E536 Safari/602.1.17",
                "Mozilla/5.0 (iPad; CPU iPad OS 14_1 like Mac OS X) AppleWebKit/604.1.18 (KHTML, like Gecko) Version/17.0 Mobile/16E759 Safari/604.1.18",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/603.1.16 (KHTML, like Gecko) Version/16.0 Mobile/19E485 Safari/603.1.16",
                "Mozilla/5.0 (iPad; CPU iPad OS 17_2 like Mac OS X) AppleWebKit/603.1.18 (KHTML, like Gecko) Version/16.0 Mobile/13E743 Safari/603.1.18",
                "Mozilla/5.0 (iPad; CPU iPad OS 17_3 like Mac OS X) AppleWebKit/604.1.5 (KHTML, like Gecko) Version/13.0 Mobile/16E985 Safari/604.1.5",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 17_2 like Mac OS X) AppleWebKit/604.1.6 (KHTML, like Gecko) Version/16.0 Mobile/16E985 Safari/604.1.6",
                "Mozilla/5.0 (iPad; CPU iPad OS 17_4 like Mac OS X) AppleWebKit/602.1.12 (KHTML, like Gecko) Version/15.0 Mobile/11E664 Safari/602.1.12",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 12_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/20E933 Safari/605.1.15",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 13_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Mobile/18E347 Safari/605.1.15",
                "Mozilla/5.0 (iPad; CPU iPad OS 13_1 like Mac OS X) AppleWebKit/602.1.12 (KHTML, like Gecko) Version/12.0 Mobile/17E864 Safari/602.1.12",
                "Mozilla/5.0 (iPad; CPU iPad OS 17_1 like Mac OS X) AppleWebKit/603.1.16 (KHTML, like Gecko) Version/16.0 Mobile/17E865 Safari/603.1.16",
                "Mozilla/5.0 (iPad; CPU iPad OS 15_1 like Mac OS X) AppleWebKit/601.1.2 (KHTML, like Gecko) Version/14.0 Mobile/19E232 Safari/601.1.2",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 16_3 like Mac OS X) AppleWebKit/602.1.3 (KHTML, like Gecko) Version/13.0 Mobile/16E616 Safari/602.1.3",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.8 (KHTML, like Gecko) Version/15.0 Mobile/14E910 Safari/605.1.8",
                "Mozilla/5.0 (iPad; CPU iPad OS 12_1 like Mac OS X) AppleWebKit/600.1.7 (KHTML, like Gecko) Version/13.0 Mobile/17E664 Safari/600.1.7",
                "Mozilla/5.0 (iPad; CPU iPad OS 15_2 like Mac OS X) AppleWebKit/604.1.18 (KHTML, like Gecko) Version/16.0 Mobile/13E891 Safari/604.1.18",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 14_0 like Mac OS X) AppleWebKit/605.1.4 (KHTML, like Gecko) Version/17.0 Mobile/10E244 Safari/605.1.4",
                "Mozilla/5.0 (iPad; CPU iPad OS 17_2 like Mac OS X) AppleWebKit/600.1.6 (KHTML, like Gecko) Version/12.0 Mobile/11E573 Safari/600.1.6",
                "Mozilla/5.0 (iPad; CPU iPad OS 12_0 like Mac OS X) AppleWebKit/603.1.7 (KHTML, like Gecko) Version/16.0 Mobile/11E927 Safari/603.1.7",
                "Mozilla/5.0 (iPad; CPU iPad OS 15_2 like Mac OS X) AppleWebKit/605.1.14 (KHTML, like Gecko) Version/12.0 Mobile/10E423 Safari/605.1.14",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/604.1.5 (KHTML, like Gecko) Version/17.0 Mobile/16E759 Safari/604.1.5",
                "Mozilla/5.0 (iPad; CPU iPad OS 12_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/17E399 Safari/605.1.15",
                "Mozilla/5.0 (Linux; Android 10; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.1473.93 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 11; SM-A525F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5445.134 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 11; OnePlus KB2003) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.2769.67 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.1518.57 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 10; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.9907.99 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 10; Redmi Note 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.6776.77 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.7572.103 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 10; XQ-BC52) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.7074.125 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 14; CPH2197) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6038.1 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 13; V2145A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.6140.100 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.7074.125 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 10; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.6776.77 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 11; XQ-AT52) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.1473.93 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 13; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.1518.57 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; M2012K11AC) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.4138.146 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 14; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5445.134 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 10; IN2023) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.9400.77 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; OnePlus KB2003) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.2686.129 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 14; CPH2197) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.4001.147 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 10; V2145A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5054.9 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 11; M2012K11AC) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.8155.78 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.6140.100 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.1473.93 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; Redmi Note 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.5220.135 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 13; V2145A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.7572.103 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 14; XQ-BC52) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5445.134 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 13; Redmi Note 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.1518.57 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 10; M2012K11AC) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.6715.70 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; OnePlus KB2003) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.6173.145 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.4309.80 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 13; XQ-AT52) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.2769.67 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.4001.147 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 10; M2012K11AC) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.7074.125 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 14; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.2769.67 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; IN2023) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.5239.66 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; 2201117TY) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.2769.67 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 14; IN2023) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5445.134 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 13; Redmi Note 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.1098.131 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 10; Redmi Note 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5111.143 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 14; OnePlus GM1913) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.1518.57 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; M2012K11AC) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.4309.80 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 11; IN2023) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.6776.77 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 14; V2145A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.9734.33 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 11; IN2023) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5445.134 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; XQ-AT52) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.9882.124 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 10; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.7572.103 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 14; V2145A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.1473.93 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 10; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.1473.93 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.4309.80 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; OnePlus GM1913) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.7074.125 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 10; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.1098.131 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.7572.103 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; XQ-AT52) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.9734.33 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 13; SM-A525F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.6776.77 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; XQ-AT52) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.7074.125 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 14; V2145A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.9734.33 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.2686.129 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 11; M2012K11AC) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5445.134 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; Redmi Note 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.8155.78 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; CPH2197) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.5239.66 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 14; V2145A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.2769.67 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 11; V2145A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.4309.80 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 13; SM-A525F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.7074.125 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.4001.147 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 13; M2012K11AC) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.2769.67 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 11; SM-A525F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.6715.70 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.5220.135 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 10; OnePlus KB2003) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.4001.147 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 11; SM-A525F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5054.9 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 14; XQ-AT52) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.4309.80 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 11; SM-A525F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.1473.93 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 10; XQ-BC52) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.5220.135 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 11; OnePlus GM1913) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.4138.146 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 14; XQ-BC52) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.2686.129 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 13; XQ-AT52) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.2686.129 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 14; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5111.143 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 13; 2201117TY) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5054.9 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 11; CPH2197) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6038.1 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.5220.135 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.5220.135 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 14; OnePlus KB2003) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.1098.131 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 10; V2145A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.1098.131 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 13; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.5220.135 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 10; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6038.1 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 10; M2012K11AC) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.9734.33 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; Redmi Note 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.4309.80 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; V2145A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.6173.145 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.6776.77 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 14; V2145A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.7074.125 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 14; 2201117TY) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.4001.147 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5054.9 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 11; OnePlus KB2003) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.1518.57 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5445.134 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 11; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.7074.125 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 14; IN2023) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.6715.70 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 11; OnePlus KB2003) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.5220.135 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.4138.146 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 13; OnePlus KB2003) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.2686.129 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 10; XQ-BC52) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.6140.100 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 10; V2145A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5054.9 Mobile Safari/537.36",
                "Mozilla/5.0 (iPad; CPU iPad OS 17_4 like Mac OS X) AppleWebKit/602.1.12 (KHTML, like Gecko) Version/15.0 Mobile/11E664 Safari/602.1.12",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 12_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/20E933 Safari/605.1.15",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 13_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Mobile/18E347 Safari/605.1.15",
                "Mozilla/5.0 (iPad; CPU iPad OS 13_1 like Mac OS X) AppleWebKit/602.1.12 (KHTML, like Gecko) Version/12.0 Mobile/17E864 Safari/602.1.12",
                "Mozilla/5.0 (iPad; CPU iPad OS 17_1 like Mac OS X) AppleWebKit/603.1.16 (KHTML, like Gecko) Version/16.0 Mobile/17E865 Safari/603.1.16",
                "Mozilla/5.0 (iPad; CPU iPad OS 15_1 like Mac OS X) AppleWebKit/601.1.2 (KHTML, like Gecko) Version/14.0 Mobile/19E232 Safari/601.1.2",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 16_3 like Mac OS X) AppleWebKit/602.1.3 (KHTML, like Gecko) Version/13.0 Mobile/16E616 Safari/602.1.3",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.8 (KHTML, like Gecko) Version/15.0 Mobile/14E910 Safari/605.1.8",
                "Mozilla/5.0 (iPad; CPU iPad OS 12_1 like Mac OS X) AppleWebKit/600.1.7 (KHTML, like Gecko) Version/13.0 Mobile/17E664 Safari/600.1.7",
                "Mozilla/5.0 (iPad; CPU iPad OS 15_2 like Mac OS X) AppleWebKit/604.1.18 (KHTML, like Gecko) Version/16.0 Mobile/13E891 Safari/604.1.18",
                "Mozilla/5.0 (iPod touch; CPU iPod touch OS 14_0 like Mac OS X) AppleWebKit/605.1.4 (KHTML, like Gecko) Version/17.0 Mobile/10E244 Safari/605.1.4",
                "Mozilla/5.0 (iPad; CPU iPad OS 17_2 like Mac OS X) AppleWebKit/600.1.6 (KHTML, like Gecko) Version/12.0 Mobile/11E573 Safari/600.1.6",
                "Mozilla/5.0 (iPad; CPU iPad OS 12_0 like Mac OS X) AppleWebKit/603.1.7 (KHTML, like Gecko) Version/16.0 Mobile/11E927 Safari/603.1.7",
                "Mozilla/5.0 (iPad; CPU iPad OS 15_2 like Mac OS X) AppleWebKit/605.1.14 (KHTML, like Gecko) Version/12.0 Mobile/10E423 Safari/605.1.14",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/604.1.5 (KHTML, like Gecko) Version/17.0 Mobile/16E759 Safari/604.1.5",
                "Mozilla/5.0 (iPad; CPU iPad OS 12_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/17E399 Safari/605.1.15",
                "Mozilla/5.0 (Linux; Android 10; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.1473.93 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 11; SM-A525F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5445.134 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 11; OnePlus KB2003) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.2769.67 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.1518.57 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 10; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.9907.99 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 10; Redmi Note 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.6776.77 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.7572.103 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 10; XQ-BC52) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.7074.125 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 14; CPH2197) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6038.1 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 13; V2145A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.6140.100 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.7074.125 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 10; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.6776.77 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 11; XQ-AT52) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.1473.93 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 13; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.1518.57 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; M2012K11AC) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.4138.146 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 14; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5445.134 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 10; IN2023) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.9400.77 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; OnePlus KB2003) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.2686.129 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 14; CPH2197) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.4001.147 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 10; V2145A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5054.9 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 11; M2012K11AC) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.8155.78 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.6140.100 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.1473.93 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; Redmi Note 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.5220.135 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 13; V2145A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.7572.103 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 14; XQ-BC52) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5445.134 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 13; Redmi Note 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.1518.57 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 10; M2012K11AC) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.6715.70 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; OnePlus KB2003) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.6173.145 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.4309.80 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 13; XQ-AT52) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.2769.67 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.4001.147 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 10; M2012K11AC) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.7074.125 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 14; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.2769.67 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; IN2023) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.5239.66 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; 2201117TY) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.2769.67 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 14; IN2023) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5445.134 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 13; Redmi Note 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.1098.131 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 10; Redmi Note 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5111.143 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 14; OnePlus GM1913) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.1518.57 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; M2012K11AC) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.4309.80 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 11; IN2023) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.6776.77 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 14; V2145A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.9734.33 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 11; IN2023) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5445.134 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; XQ-AT52) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.9882.124 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 10; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.7572.103 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 14; V2145A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.1473.93 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 10; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.1473.93 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.4309.80 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; OnePlus GM1913) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.7074.125 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 10; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.1098.131 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.7572.103 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; XQ-AT52) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.9734.33 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 13; SM-A525F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.6776.77 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; XQ-AT52) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.7074.125 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 14; V2145A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.9734.33 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.2686.129 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 11; M2012K11AC) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5445.134 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; Redmi Note 11) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.8155.78 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; CPH2197) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.5239.66 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 14; V2145A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.2769.67 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 11; V2145A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.4309.80 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 13; SM-A525F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.7074.125 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.4001.147 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 13; M2012K11AC) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.2769.67 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 11; SM-A525F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.6715.70 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.5220.135 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 10; OnePlus KB2003) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.4001.147 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 11; SM-A525F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5054.9 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 14; XQ-AT52) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.4309.80 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 11; SM-A525F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.1473.93 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 10; XQ-BC52) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.5220.135 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 11; OnePlus GM1913) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.4138.146 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 14; XQ-BC52) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.2686.129 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 13; XQ-AT52) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.2686.129 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 14; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5111.143 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 13; 2201117TY) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5054.9 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 11; CPH2197) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6038.1 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.5220.135 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.5220.135 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 14; OnePlus KB2003) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.1098.131 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 10; V2145A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.1098.131 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 13; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.5220.135 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 10; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.6038.1 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 10; M2012K11AC) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.9734.33 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; Redmi Note 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.4309.80 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; V2145A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.6173.145 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.6776.77 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 14; V2145A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.7074.125 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 14; 2201117TY) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.4001.147 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5054.9 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 11; OnePlus KB2003) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.1518.57 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5445.134 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 11; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.7074.125 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 14; IN2023) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.6715.70 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 11; OnePlus KB2003) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.5220.135 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 12; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.4138.146 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 13; OnePlus KB2003) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.2686.129 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 10; XQ-BC52) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.6140.100 Mobile Safari/537.36",
                "Mozilla/5.0 (Linux; Android 10; V2145A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5054.9 Mobile Safari/537.36",
            ]
            #user_agent = random.choice(turkish_user_agents)
            user_agent = UserAgent().random
            # === Chrome Ayarları ===
            options = uc.ChromeOptions()
            os.makedirs("extension/proxy_folder", exist_ok=True)
            PROXY_FOLDER = os.path.abspath(os.path.join('extension', 'proxy_folder'))
            os.makedirs(PROXY_FOLDER, exist_ok=True)
            
            manifest_json = """
                {
                    "version": "1.0.0",
                    "manifest_version": 3,
                    "name": "Chrome Proxy",
                    "permissions": [
                        "proxy",
                        "tabs",
                        "storage",
                        "webRequest",
                        "webRequestAuthProvider"
                    ],
                    "host_permissions": [
                        "<all_urls>"
                    ],
                    "background": {
                        "service_worker": "background.js"
                    },
                    "minimum_chrome_version": "22.0.0"
                }
                """
            background_js = """
                var config = {
                        mode: "fixed_servers",
                        rules: {
                        singleProxy: {
                            scheme: "http",
                            host: "%s",
                            port: parseInt(%s)
                        },
                        bypassList: ["localhost"]
                        }
                    };
                chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
                function callbackFn(details) {
                    return {
                        authCredentials: {
                            username: "%s",
                            password: "%s"
                        }
                    };
                }
                chrome.webRequest.onAuthRequired.addListener(
                            callbackFn,
                            {urls: ["<all_urls>"]},
                            ['blocking']
                );
                """% (proxy_host, proxy_port, proxy_user, proxy_pass)
            with open(f"{PROXY_FOLDER}/manifest.json","w") as f:
                f.write(manifest_json)
            with open(f"{PROXY_FOLDER}/background.js","w") as f:
                f.write(background_js)

            device_resolutions = {
                "phone": [
                    (360, 640),  # iPhone 6/7/8
                    (375, 667),  # iPhone X
                    (412, 732),  # Galaxy S8
                    (360, 800),  # Nexus 5
                    (375, 812),  # iPhone XS Max
                ],
                "tablet": [
                    (768, 1024),  # iPad Mini
                    (800, 1280),  # Galaxy Tab
                    (800, 1280),  # Nexus 7
                    (1200, 1920), # iPad Pro
                ],
                "desktop": [
                    (1024, 768),  # Standard Desktop
                    (1366, 768),  # HD Laptop
                    (1440, 900),  # MacBook Air
                    (1920, 1080), # Full HD
                    (2560, 1440), # Quad HD
                    (3840, 2160), # 4K
                ]
            }

            device_type = random.choice(["phone", "tablet", "desktop"]) 
            resolution = random.choice(device_resolutions[device_type])
            
            options.add_argument(f"--user-agent={user_agent}")
            options.add_argument(f"--load-extension={PROXY_FOLDER}")
            options.add_argument("--window-size={resolution[0]},{resolution[1]}")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--lang=tr-TR")


            # === Driver Başlat ===

            driver = uc.Chrome(options=options)

            driver.set_window_size(1000, 500)
            width, height = driver.execute_script("return [window.innerWidth, window.innerHeight];")
            if screen_position == 'top_left':
                driver.set_window_position(0, 0)
            elif screen_position == 'top_right':
                driver.set_window_position(1000, 0)
            elif screen_position == 'bottom_left':
                driver.set_window_position(0, 500)
            elif screen_position == 'bottom_right':
                driver.set_window_position(1000, 500)
            
            actions = ActionChains(driver)

            # === Fingerprint Gizle ===
            """
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": 

                    Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                    Object.defineProperty(navigator, 'languages', {get: () => ['tr-TR', 'tr']});
                    Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});
                    Object.defineProperty(navigator, 'deviceMemory', {get: () => 8});
                    Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 8});
                
            })
            """
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": user_agent})


            driver.execute_cdp_cmd('Network.enable', {})  # Ağ özelliklerini etkinleştir
            driver.execute_cdp_cmd('Network.setExtraHTTPHeaders', {
                "headers": {
                    "Accept-Language": "tr-TR"
                }
            })
            
            driver.get("https://api.ipify.org?format=text")
            human_sleep(1.5, 2)
            
            used_ips = set()
            with open("data/test_accounts.json", "r", encoding="utf-8") as f:
                accounts = json.load(f)

            for account in accounts:
                expected_ip = account["ip_address"]
                used_ips.add(expected_ip)

            ip_address = driver.find_element(By.TAG_NAME, "body").text
            print(f"Proxy IP adresi: {ip_address}")
            location = get_proxy_location(ip_address)
            print(f"Proxy konumu: {location}")

            if ip_address in used_ips:
                print("Bu IP daha önce kullanıldı, çıkış yapılıyor...")
                driver.quit()
            
            
            # === Spotify Hesap Oluşturma Sayfası ===
            driver.get("https://www.spotify.com/tr/signup/")
            print("Sayfa yükleniyor lütfen bekleyiniz...")
            wait = WebDriverWait(driver, 9)
            print("Sayfa yüklendi. İşlem başlıyor...")
            
            
            # === Çerezler ===
            try:
                onetrust_btn = wait.until(EC.presence_of_element_located((By.ID, "onetrust-accept-btn-handler")))
                if onetrust_btn.is_displayed() and onetrust_btn.is_enabled():
                    driver.execute_script("arguments[0].click();", onetrust_btn)
                    print("Çerez bildirimi tıklandı.")
                else:
                    print("Çerez bildirimi bulunamadı veya tıklanamaz durumda.")
            except Exception as e:
                print(f"Çerez bildirimi tıklanamadı: {e}")
            human_sleep(1, 2)
            
            
            # === Email ===
            input_email = wait.until(EC.presence_of_element_located((By.ID, "username")))
            type_like_human(input_email, email)
            human_sleep(1, 2)
            try:
                e_submit_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='submit']")))
                if e_submit_btn.is_displayed() and e_submit_btn.is_enabled():
                    #driver.execute_script("arguments[0].scrollIntoView(true);", e_submit_btn)
                    #driver.execute_script("arguments[0].click();", e_submit_btn)
                    human_click(driver, e_submit_btn)
                    human_sleep()
                    print("(Email) Submit butona tıklandı.")
                else:
                    print("(Email) Submit butona bulunamadı veya tıklanamaz durumda.")
            except Exception as e:
                print(f"(Email) Submit butona tıklanamadı: {e}")
                driver.quit()
            
            
            # === Password ===
            input_password = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[id='new-password']")))
            type_like_human(input_password, password)
            human_sleep(1, 2)
            try:
                p_submit_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='submit']")))
                if p_submit_btn.is_displayed() and p_submit_btn.is_enabled():
                    #driver.execute_script("arguments[0].click();", p_submit_btn)
                    human_click(driver, p_submit_btn)
                    human_sleep()
                    print("(Password) Submit butona tıklandı.")
                else:
                    print("(Password) Submit butona bulunamadı veya tıklanamaz durumda.")
            except Exception as e:
                print(f"(Password) Submit butona tıklanamadı: {e}")
                driver.quit()
            human_sleep(1, 2)
            
            
            # === Username ===
            input_username = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[id='displayName']")))
            type_like_human(input_username, username)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[id='day']"))).send_keys(birth_day)
            month_dropdown_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "select[id='month']")))
            month_dropdown = Select(month_dropdown_element)
            month_dropdown.select_by_index(birth_month)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[id='year']"))).send_keys(birth_year)
            gender_label = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f"label[for='{gender}']")))
            driver.execute_script("arguments[0].click();", gender_label)
            human_sleep(1, 2)
            try:
                u_submit_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='submit']")))
                if u_submit_btn.is_displayed() and u_submit_btn.is_enabled():
                    driver.execute_script("arguments[0].click();", u_submit_btn)
                    print("(Username) Submit butona tıklandı.")
                else:
                    print("(Username) Submit butona bulunamadı veya tıklanamaz durumda.")
            except Exception as e:
                print(f"(Username) Submit butona tıklanamadı: {e}")
                driver.quit()
            human_sleep(1, 2)
            
            
            # === Terms and Conditions ===
            # terms_label = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "label[for='terms-conditions-checkbox']")))
            # driver.execute_script("arguments[0].click();", terms_label)
            try:
                t_submit_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='submit']")))
                if t_submit_btn.is_displayed() and t_submit_btn.is_enabled():
                    #driver.execute_script("arguments[0].click();", t_submit_btn)
                    human_click(driver, t_submit_btn)
                    human_sleep()
                    print("(Terms) Submit butona tıklandı.")
                else:
                    print("(Terms) Submit butona bulunamadı veya tıklanamaz durumda.")
            except Exception as e:
                print(f"(Terms) Submit butona tıklanamadı: {e}")
                driver.quit()
            time.sleep(15)
            
            if any(keyword in driver.current_url.lower() for keyword in ["windows", "android", "ios", "linux", "download"]):
                print(f"✅ Hesap başarıyla oluşturuldu: {email} | {password} | {username}")
                save_account(email, password, first_name, last_name, username, birth_year, birth_month, birth_day, gender, ip_address,location)
            elif any(keyword in driver.current_url.lower() for keyword in ["recaptcha"]):
                print(f" Recaptcha attı çözüm işlemi gerçekleşiyor.")
                driver.quit()
                print(driver.current_url)
                url = driver.current_url
                time.sleep(10)

                # reCAPTCHA checkbox'ını tıklamak (görünürse)
                iframe = driver.find_element(By.XPATH, "//iframe[contains(@src, 'recaptcha')]")
                driver.switch_to.frame(iframe)
                checkbox = driver.find_element(By.CLASS_NAME, "recaptcha-checkbox-border")
                checkbox.click()
                driver.switch_to.default_content()
                time.sleep(3)

                sitekey = driver.find_element(By.XPATH, '//*[@id="encore-web-main-content"]/div/div/div/div/div/div/div[1]/div').get_attribute('outerHTML')
                sitekey_clean = sitekey.split('" data-action')[0].split('data-sitekey="')[1]
                print("Sitekey: ", sitekey_clean)

                solver = recaptchaV2Proxyless()
                solver.set_verbose(1)
                solver.set_key("dd51673d9ded73e7f747225d4ba4fddf")
                solver.set_website_url(url)
                solver.set_website_key(sitekey_clean)

                g_response = solver.solve_and_return_solution()
                if g_response != 0:
                    print("g_response: " + g_response)
                else:
                    print("Task finished with error: " + solver.error_code)

                human_sleep(2, 4)

                # Token'ı 'g-recaptcha-response' input'a yerleştiriyoruz ve input event'i tetikliyoruz.
                driver.execute_script("""
                    var response = arguments[0];
                    var element = document.getElementById("g-recaptcha-response");
                    element.style.display = "";  // Token'ı görünür yap
                    element.value = response;  // Token'ı textarea'ya yaz

                    // change ve input event'lerini tetikle
                    var event = new Event('change', { 'bubbles': true });
                    element.dispatchEvent(event);  // change event'ini tetikledik

                    var inputEvent = new Event('input', { 'bubbles': true });
                    element.dispatchEvent(inputEvent);  // input event'ini tetikledik

                    // onChange callback fonksiyonunu tetikle
                    var callback = window[document.querySelector('.g-recaptcha').getAttribute('data-callback')];
                    if (callback) {
                        callback(response);  // onChange callback fonksiyonunu çağırıyoruz
                    }

                    element.style.display = 'none';  // Input'u tekrar gizle
                """, g_response)



                WebDriverWait(driver, 20).until(
                    EC.invisibility_of_element_located((By.XPATH, "//iframe[contains(@src, 'bframe')]"))
                )

                # Devam et butonuna bas
                driver.find_element(By.XPATH, '//*[@id="encore-web-main-content"]/div/div/div/div/div/div/button').click()

                time.sleep(20)

                            
            else:
                print("❌ Hesap oluşturulurken bir hata oluştu.")
            driver.quit()
        except Exception as e:
            print("Hata:", e)
        finally:
            print(f"✅ Pozisyon {position} boşaltıldı.")
            active_threads -= 1
            if driver:
                driver.quit()
        

def thread_worker():
    try:
        create_spotify_accounts()
    except Exception as e:
        print(f"[HATA] Thread içinde istisna oluştu: {e}")

def process_worker():
    try:
        create_spotify_accounts()  # Her bir işlemde hesap oluşturma fonksiyonunu çalıştırıyoruz
    except Exception as e:
        print(f"[HATA] Process içinde istisna oluştu: {e}")

NUM_ACCOUNTS = 5000
MAX_THREADS = 4
MAX_PROCESSES = 1

positions = ['top_left', 'top_right', 'bottom_left', 'bottom_right']
position_locks = {pos: threading.Lock() for pos in positions}
threads = []
active_threads = 0 

if __name__ == "__main__":
    for i in range(NUM_ACCOUNTS):
        position = positions[i % len(positions)]

        while active_threads >= MAX_THREADS:
            time.sleep(0.5)

        active_threads += 1
        t = threading.Thread(target=create_spotify_accounts, args=(position,))
        threads.append(t)
        t.start()
        print(f"🚀 Thread {i+1} ({position}) başlatıldı.")

    for t in threads:
        t.join()

    print("🎉 Tüm hesaplar başarıyla oluşturuldu.")