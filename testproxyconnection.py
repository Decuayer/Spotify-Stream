import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import requests
import random
from seleniumwire import webdriver 


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
    


def proxy_ip_control(driver):
    driver.get("https://api.ipify.org?format=text")
    time.sleep(1.5)
    ip_address = driver.find_element(By.TAG_NAME, "body").text
    print(f"Proxy IP adresi: {ip_address}")
    location = get_proxy_location(ip_address)
    print(f"Proxy konumu: {location}")
    return ip_address

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

# Proxy bilgileri
file_path = 'data/proxy.txt'
proxy_host = "core-residential.evomi.com"
proxy_port = 1000
proxy_username = "demoloski3"
proxy_password = get_proxy_location(file_path)

proxy = f"{proxy_host}:{proxy_port}"

webdriver_options = {
    'proxy': {
        'http': f'http://{proxy_username}:{proxy_password}@{proxy}',
        'https': f'http://{proxy_username}:{proxy_password}@{proxy}',
    }
}

options = uc.ChromeOptions()
options.add_argument(f'--proxy-server=http://{proxy}')  # Proxy'yi ekle
options.add_argument('--ignore-certificate-errors')
options.add_argument('--no-sandbox')
options.add_argument('--disable-blink-features=AutomationControlled')  
options.add_argument('--disable-webgl')  # Disable WebGL fingerprinting
options.add_argument('--disable-webrtc')  # Disable WebRTC IP leaks
options.add_argument('--disable-extensions')  # Disable extensions to avoid detection
options.add_argument('--start-maximized')

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
]


options.add_argument(f"user-agent={random.choice(user_agents)}")
options.add_argument("enable-features=NetworkServiceInProcess")
options.add_argument("--remote-debugging-port=9222")

driver = webdriver.Chrome(options=options, seleniumwire_options=webdriver_options)
try:
    proxy_ip_control(driver)
    driver.get("https://browserscan.net")  # IP adresini gösteren basit servis
    
    time.sleep(1000)
except Exception as e:
    print("Hata oluştu:", e)
finally:
    driver.quit()
