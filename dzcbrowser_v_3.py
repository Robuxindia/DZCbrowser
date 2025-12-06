import os
import json
import time
import base64
import ctypes
import threading
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import pythoncom
import win32com.client

# --- DATA SETUP ---
appdata = os.getenv("APPDATA") or os.getcwd()
data_dir = os.path.join(appdata, "DZCbrowser")
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

key_path = os.path.join(data_dir, "key.bin")
data_path = os.path.join(data_dir, "data.enc")

# --- KEY / DATA FUNCTIONS ---
def create_key_file(password):
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=200_000,
    )
    password_key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    password_fernet = Fernet(password_key)
    master_key = Fernet.generate_key()
    encrypted_master = password_fernet.encrypt(master_key)
    key_data = {
        "salt": base64.urlsafe_b64encode(salt).decode(),
        "encrypted": encrypted_master.decode()
    }
    with open(key_path, "w") as f:
        json.dump(key_data, f)

    init_data = {"history": [], "bookmarks": [], "passwords": []}
    data_fernet = Fernet(master_key)
    with open(data_path, "wb") as f:
        f.write(data_fernet.encrypt(json.dumps(init_data).encode()))

def load_master_key(password):
    try:
        with open(key_path, "r") as f:
            key_data = json.load(f)
        salt = base64.urlsafe_b64decode(key_data["salt"].encode())
        encrypted_master = key_data["encrypted"].encode()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=200_000,
        )
        password_key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        master_key = Fernet(password_key).decrypt(encrypted_master)
        return master_key
    except Exception:
        return None

def load_data(master_key):
    if not os.path.exists(data_path):
        return {"history": [], "bookmarks": [], "passwords": []}
    with open(data_path, "rb") as f:
        enc = f.read()
    try:
        data_fernet = Fernet(master_key)
        return json.loads(data_fernet.decrypt(enc).decode())
    except Exception:
        return {"history": [], "bookmarks": [], "passwords": []}

def save_data(master_key, data):
    data_fernet = Fernet(master_key)
    with open(data_path, "wb") as f:
        f.write(data_fernet.encrypt(json.dumps(data).encode()))

# --- EDGE WEBVIEW2 SETUP ---
class Browser:
    def __init__(self):
        self.master_key = None
        self.data = None
        self.url = "https://www.bing.com"

    def start(self):
        pythoncom.CoInitialize()
        self.webview = win32com.client.Dispatch("Microsoft.Web.WebView2.WinForms.WebView2")
        self.webview.CreateControl()  # Initialize COM control
        self.webview.Source = self.url
        print("WebView2 Başladı. Tarayıcı hazır.")

# --- MAIN ---
if not os.path.exists(key_path):
    pw = input("Ana şifre belirleyin: ")
    create_key_file(pw)
    master_key = load_master_key(pw)
else:
    pw = input("Ana şifreyi girin: ")
    master_key = load_master_key(pw)
    if not master_key:
        print("Yanlış şifre!")
        exit()

data = load_data(master_key)
browser = Browser()
browser.start()
