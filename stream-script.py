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
from multiprocessing import Process
from datetime import datetime
from fake_useragent import UserAgent
from selenium_stealth import stealth
from fake_headers import Headers



# Main Functions
def get_public_ip():
    ip = requests.get("https://api.ipify.org").text
    return ip

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
    
def proxy_ip_control(driver, threadid):
    driver.get("https://api.ipify.org?format=text")
    time.sleep(1.5)
    ip_address = driver.find_element(By.TAG_NAME, "body").text
    print(f"Thread {threadid}: Proxy IP adresi: {ip_address}")
    location = get_proxy_location(ip_address)
    print(f"Thread {threadid}: Proxy konumu: {location}")
    return ip_address


def human_sleep(min_sec=0.7, max_sec=2.0):
    time.sleep(random.uniform(min_sec, max_sec))

def type_like_human(element, text):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.1))

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

def human_click(driver, element):
    # Ekrana kaydır
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    time.sleep(random.uniform(0.5, 1.5))

    # Hover gibi davran
    actions = ActionChains(driver)
    actions.move_to_element(element).pause(random.uniform(0.2, 0.6)).click().perform()

    # Ekstra rastgele bekleme
    time.sleep(random.uniform(0.3, 1.2))

# Kullanıcı bilgilerini JSON dosyasından çekme
def load_user_accounts():
    with open("data/lastfile.json", "r", encoding='utf-8') as file:
        accounts = json.load(file)  
    return accounts

def get_random_account():
    accounts = load_user_accounts()
    return random.choice(accounts)

def get_account_by_index(index):
    accounts = load_user_accounts()
    if 0 <= index < len(accounts):
        return accounts[index]
    else:
        raise IndexError("Geçersiz index")

# Dinleme işlemi için Spotify'a giriş yapma
def login_to_spotify(driver, email, password, threadid):
    driver.get("https://www.spotify.com/tr/login/")
    print(f"Thread {threadid}: Sayfa yükleniyor lütfen bekleyiniz...")
    wait = WebDriverWait(driver, 10)
    print(f"Thread {threadid}: Sayfa yüklendi. İşlem başlıyor...")


    # E-posta
    input_email = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input#login-username")))
    type_like_human(input_email, email)

    try:
        input_password = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input#login-password")))
        print(f"Thread {threadid}: Şifre inputu zaten açık, email submit atlandı.")
    except TimeoutException:
        try:
            e_submit_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button#login-button")))
            if e_submit_btn.is_displayed() and e_submit_btn.is_enabled():
                human_click(driver, e_submit_btn)
                human_sleep()
                print(f"Thread {threadid}: (Email) Submit butona tıklandı.")
            else:
                print(f"Thread {threadid}: (Email) Submit butona bulunamadı veya tıklanamaz durumda.")
        except Exception as e:
            print(f"Thread {threadid}: (Email) Submit butona tıklanamadı: {e}")
            driver.quit()
    
    # Şifre
    input_password = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input#login-password")))
    type_like_human(input_password, password)
    human_sleep(1, 2)
    try:
        p_submit_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button#login-button")))
        if p_submit_btn.is_displayed() and p_submit_btn.is_enabled():
            #driver.execute_script("arguments[0].click();", p_submit_btn)
            human_click(driver, p_submit_btn)
            human_sleep()
            print(f"Thread {threadid}: (Password) Submit butona tıklandı.")
        else:
            print(f"Thread {threadid}: (Password) Submit butona bulunamadı veya tıklanamaz durumda.")
    except Exception as e:
        print(f"Thread {threadid}: (Password) Submit butona tıklanamadı: {e}")
        driver.quit()
    human_sleep(1, 2)
    print(f"Thread {threadid}: Giriş yapılıyor: {email}")
    onetrust = False

    human_sleep(5, 7)
    # Çerezler
    try:
        onetrust_btn = wait.until(EC.presence_of_element_located((By.ID, "onetrust-accept-btn-handler")))
        if onetrust_btn.is_displayed() and onetrust_btn.is_enabled():
            driver.execute_script("arguments[0].click();", onetrust_btn)
            print(f"Thread {threadid}: Çerez bildirimi tıklandı. (1)")
            onetrust = True
        else:
            print(f"Thread {threadid}: Çerez bildirimi bulunamadı veya tıklanamaz durumda. (1)")
    except Exception as e:
        print(f"Thread {threadid}: Çerez bildirimi tıklanamadı. (1)")
    human_sleep(1, 2)
    return onetrust

# Dinleme işlemi için rastgele bir şarkı çalma
def play_random_song(driver, search_name, singer, url, onetrust, threadid):
    driver.get("https://open.spotify.com")
    wait = WebDriverWait(driver, 10)
    if (onetrust == False):
        # Çerezler
        try:
            onetrust_btn = wait.until(EC.presence_of_element_located((By.ID, "onetrust-accept-btn-handler")))
            if onetrust_btn.is_displayed() and onetrust_btn.is_enabled():
                driver.execute_script("arguments[0].click();", onetrust_btn)
                print(f"Thread {threadid}: Çerez bildirimi tıklandı. (2)")
                onetrust = True
            else:
                print(f"Thread {threadid}: Çerez bildirimi bulunamadı veya tıklanamaz durumda. (2)")
        except Exception as e:
            print(f"Thread {threadid}: Çerez bildirimi tıklanamadı: (2)")
        human_sleep(1, 2)

    """
    try:
        search_link = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"a[href='/search']")))
        human_click(driver, search_link)
        print(f"Thread {threadid}: Search link tıklandı. (1)")
        human_sleep(1.5, 4)
    except:
        print(f"Thread {threadid}: Search link bulunamadı, geçildi. (1)")

    try:
        search_link2 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"button[data-testid='search']")))
        human_click(driver, search_link2)
        print(f"Thread {threadid}: Search link tıklandı. (2)")
        human_sleep(1.5, 4)
    except:
        print(f"Thread {threadid}: Search link bulunamadı, geçildi. (2)")
    search = False
    try:
        search_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,"input[data-testid='search-input']")))        
        human_sleep(1.5, 4)
        search_main = singer + " " + search_name
        type_like_human(search_input, search_main)
        print(f"Thread {threadid}: Search input girildi.")
        human_sleep(1.5, 4)
        search = True
    except:
        print(f"Thread {threadid}: Search input girilemedi, geçildi.")
    
    if (onetrust == False):
        # Çerezler
        try:
            onetrust_btn = wait.until(EC.presence_of_element_located((By.ID, "onetrust-accept-btn-handler")))
            if onetrust_btn.is_displayed() and onetrust_btn.is_enabled():
                driver.execute_script("arguments[0].click();", onetrust_btn)
                print(f"Thread {threadid}: Çerez bildirimi tıklandı. (3)")
                onetrust = True
            else:
                print(f"Thread {threadid}: Çerez bildirimi bulunamadı veya tıklanamaz durumda. (3)")
        except Exception as e:
            print(f"Thread {threadid}: Çerez bildirimi tıklanamadı. (3)")
        human_sleep(1, 2)
    
    try:
        add_button = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR,"button[aria-label='tertiaryCtaDismiss']")))
        human_sleep(1.5, 4)
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", add_button)
        human_sleep(0.5, 2)
        driver.execute_script("arguments[0].click();", add_button)
        human_sleep(0.5, 2)
        print(f"Thread {threadid}: Reklam geçildi.")
    except Exception as e:
        print(f"Thread {threadid}: Reklam sayfası çıkmadı devam.")

    if (search == False):
        try:
            search_input = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR,"input[data-testid='search-input']")))        
            human_sleep(1.5, 4)
            search_main = singer + " " + search_name
            type_like_human(search_input, search_main)
            print(f"Thread {threadid}: Search input girildi.")
            human_sleep(1.5, 4)
            search = True
        except:
            print(f"Thread {threadid}: Search input girilemedi, geçildi.")
    else :
        print(f"Thread {threadid}: Input girilmiş devam")
    """

    try:
        driver.get(url)
        print(f"Thread {threadid}: (url) Sayfa yükleniyor lütfen bekleyiniz...")
        wait = WebDriverWait(driver, 10)
        print(f"Thread {threadid}: (url)Sayfa yüklendi. İşlem başlıyor...")
        play_button = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-testid='play-button']")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", play_button)
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-testid='play-button']")))
        driver.execute_script("arguments[0].click();", play_button)
        print(f"Thread {threadid}: (url) Play butonuna JS ile tıklandı.")
        if any(keyword in driver.current_url.lower() for keyword in ["login"]):
            print(f"Thread {threadid}: Giriş yapılamamış çıkış yapılıyor.")
            driver.quit()
        else:
            print(f"Thread {threadid}: Dinlenme gerçekleşiyor.")
            if (onetrust == False):
                # Çerezler
                try:
                    onetrust_btn = wait.until(EC.presence_of_element_located((By.ID, "onetrust-accept-btn-handler")))
                    if onetrust_btn.is_displayed() and onetrust_btn.is_enabled():
                        driver.execute_script("arguments[0].click();", onetrust_btn)
                        print(f"Thread {threadid}: Çerez bildirimi tıklandı. (2)")
                        onetrust = True
                    else:
                        print(f"Thread {threadid}: Çerez bildirimi bulunamadı veya tıklanamaz durumda. (2)")
                except Exception as e:
                    print(f"Thread {threadid}: Çerez bildirimi tıklanamadı: (2)")
            human_sleep(1.5, 4)
            human_sleep(60, 120)
    except Exception as e:
        print(f"Thread {threadid}: (url) !!!!!!Play butonuna JS ile tıklanamadı.")

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

def create_driver(screen_position, threadid, headless = False):
    file_path = 'data/proxy.txt'
    proxy_host = 'core-residential.evomi.com'
    proxy_port = 1000
    proxy_user = 'demoloski3'
    proxy_pass = get_random_password_from_file(file_path)
    print(f"Thread {threadid}  password : {proxy_pass}")

    user_agent = UserAgent().random

    
    # === Chrome Ayarları ===
    proxy_dir = f"proxies/proxy_{threadid}"
    os.makedirs(proxy_dir, exist_ok=True)
    PROXY_FOLDER = os.path.abspath(os.path.join('proxies', f'proxy_{threadid}'))
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
    
    prefs = {
        "webrtc.ip_handling_policy": "disable_non_proxied_udp",
        "webrtc.multiple_routes_enabled": False,
        "webrtc.nonproxied_udp_enabled": False
    }

    headers = Headers(browser="chrome", os="win", headers=True)
    user_agent = headers.generate()["User-Agent"]

    options = uc.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_experimental_option("prefs", prefs)  # Chrome tercihlerini (örneğin otomatik indirme, varsayılan ses/video aygıtları vb.) ayarlamak için kullanılır.
    options.add_argument("--disable-blink-features=AutomationControlled")  # `navigator.webdriver = true` olmasını engeller, bot olduğunu gizler.
    options.add_argument("--disable-infobars")  # “Chrome is being controlled by automated software” uyarısını gizler.
    options.add_argument("--disable-dev-shm-usage")  # Bellek sınırlı sistemlerde çökmeyi önlemek için /dev/shm yerine disk kullanır.
    options.add_argument("--no-sandbox")  # Chrome'un sandbox (izolasyon) güvenliğini kapatır, bazı sistemlerde otomasyonu kolaylaştırır.
    #options.add_argument("--disable-extensions")  # Tüm Chrome uzantılarını devre dışı bırakır.
    options.add_argument("--disable-gpu")  # GPU hızlandırmasını devre dışı bırakır, özellikle headless modda yararlıdır.
    options.add_argument("--mute-audio")  # Sesleri tamamen susturur, arka planda çalışan otomasyonlar için iyidir.
    options.add_argument("--use-fake-ui-for-media-stream")  # Kamera ve mikrofon izin penceresini göstermeden otomatik izin verir.
    options.add_argument("--disable-popup-blocking")  # Açılır pencerelerin otomatik olarak engellenmesini devre dışı bırakır.
    options.add_argument("--start-maximized")  # Tarayıcıyı maksimum boyutta başlatır.
    options.add_argument("--disable-background-networking")  # Arka planda çalışan ağ etkinliklerini devre dışı bırakır.
    options.add_argument("--metrics-recording-only")  # Telemetri verilerini kaydetmeyi kısıtlar.
    options.add_argument("--disable-client-side-phishing-detection")  # Phishing (oltalama) tespit sistemini kapatır.
    options.add_argument("--disable-default-apps")  # Chrome'un varsayılan uygulamalarını yüklemesini engeller.
    options.add_argument("--disable-hang-monitor")  # Sayfa yanıt vermediğinde hata vermesini engeller.
    options.add_argument("--window-size=1920,1080")  # Pencere boyutunu sabitler; bot olarak algılanmayı azaltır.
    options.add_argument("--no-default-browser-check")  # Chrome’un varsayılan tarayıcı kontrolünü devre dışı bırakır.

    options.add_argument("--lang=tr-TR")  # Tarayıcı dilini Türkçe yapar.
    options.add_argument("--disable-webrtc")  # WebRTC’yi tamamen devre dışı bırakır (gerçek bir bayrak değildir, uyumlu değilse etkisiz olur).
    options.add_argument("--disable-ipv6")  # IPv6 bağlantılarını kapatır.
    options.add_argument("--disable-features=WebRtcHideLocalIpsWithMdns")  # Gerçek IP adreslerinin sızdırılmasını engeller (WebRTC içindir).
    
    
    #options.add_argument(f"user-agent={user_agent}")  # Tarayıcı için özel bir User-Agent tanımlar.
    options.add_argument(f"--load-extension={PROXY_FOLDER}")  # Belirtilen dizindeki uzantıyı yükler (örneğin proxy eklentisi).

    
    driver = uc.Chrome(
        options=options,
        driver_executable_path=ChromeDriverManager().install()  # doğru sürümle yükler
    )

    driver.set_window_size(960, 500)
    if screen_position == 'top_left':
        driver.set_window_position(0, 0)
    elif screen_position == 'top_right':
        driver.set_window_position(960, 0)
    elif screen_position == 'bottom_left':
        driver.set_window_position(0, 540)
    elif screen_position == 'bottom_right':
        driver.set_window_position(960, 540)

    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3],
            });
            Object.defineProperty(navigator, 'languages', {
                get: () => ['tr-TR', 'tr'],
            });
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            window.chrome = { runtime: {} }; // Avoid missing chrome.runtime
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) =>
                parameters.name === 'notifications'
                    ? Promise.resolve({ state: Notification.permission })
                    : originalQuery(parameters);
        """
    })

    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
        // AudioContext spoofing
        const getFloatFrequencyData = AnalyserNode.prototype.getFloatFrequencyData;
        AnalyserNode.prototype.getFloatFrequencyData = function() {
            const original = new Float32Array(this.frequencyBinCount);
            getFloatFrequencyData.call(this, original);
            for (let i = 0; i < original.length; i++) {
                original[i] = original[i] + Math.random() * 0.1; // slight random noise
            }
            return original;
        };
        """
    })

    stealth(driver,
        languages=["tr-TR", "tr"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )

    
    return driver

def select_random_song_from_json(json_path, genre_key):
    with open(json_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    artist = random.choice(list(data[genre_key].keys()))
    song = random.choice(data[genre_key][artist])
    return genre_key, artist, song


def save_ip_to_json(json_path, ip_address, threadid):
    try:
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as file:
                data = json.load(file)
        else:
            data = {}
        # Add new entry with timestamp
        data[timestamp] = {"ip_address": ip_address}
        # Save updated data back to the file
        with open(json_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
        print(f"Thread {threadid}: IP address {ip_address} saved at {timestamp}.")
    except Exception as e:
        print(f"Thread {threadid}: An error occurred: {e}")


def main(position, threadid):
    global active_threads
    driver = None
    with position_locks[position]:
        try:
            accounts = get_random_account()
            print(accounts)
            email = accounts["email"]
            password = accounts["password"]

            driver = create_driver(position,threadid)
            ip_address = proxy_ip_control(driver,threadid)
            own_ip = get_public_ip()
            if (ip_address == own_ip):
                print(f"Thread {threadid}: {own_ip} == {ip_address} => ip'ler aynı çıkış yapılıyor.")
                driver.quit()
            
            onetrust = login_to_spotify(driver, email, password, threadid)
            songs = [
                ["Andale", "Ongun170", "https://open.spotify.com/track/2ZlGbvn8k1sJP7beqRGbMX?si=371dd5e925c84001"],
                #["Her Yerimde Varsın", "Zparga", "https://open.spotify.com/intl-tr/track/2xc9YZ604fHQCOH3LsDYp3"]
            ]
            selected_song = random.choice(songs)
            play_random_song(driver, selected_song[0], selected_song[1], selected_song[2], onetrust, threadid)
            save_ip_to_json("data/play_used_ip.json", ip_address, threadid)
        except Exception as e:
            print(f"Thread {threadid}: Hata:", e)
        finally:
            print(f"Thread {threadid}: ✅ Pozisyon {position} boşaltıldı.")
            active_threads -= 1
            if driver:
                driver.quit()


NUM_PLAYS = 500
MAX_THREADS = 4
MAX_PROCESSES = 1

positions = ['top_left', 'top_right', 'bottom_left', 'bottom_right']
position_locks = {pos: threading.Lock() for pos in positions}
threads = []
active_threads = 0 

if __name__ == "__main__":
    #genre, artist, song = select_random_song_from_json("JSON/songs.json", "Pop")
    #print(f"Genre: {genre}, Artist: {artist}, Song: {song}")

    for i in range(NUM_PLAYS):
        position = positions[i % len(positions)]

        while active_threads >= MAX_THREADS:
            time.sleep(0.5)

        active_threads += 1
        t = threading.Thread(target=main, args=(position,i+1))
        threads.append(t)
        t.start()
        print(f"🚀 Thread {i+1} ({position}) başlatıldı.")

    for t in threads:
        t.join()

    print("🎉 Tüm dinletmeler başarıyla verildi.")

    input("Çıkmak için enter'a basın...")
