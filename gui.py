import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import pefile
import joblib
import pandas as pd
import threading
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- MODEL İLE BİREBİR AYNI OLMASI GEREKEN SÜTUN SIRALAMASI (feature extractor py için bu)---
FEATURE_COLUMNS = [
    "Machine", "SizeOfOptionalHeader", "Characteristics", "MajorLinkerVersion",
    "SizeOfCode", "SizeOfInitializedData", "AddressOfEntryPoint", "ImageBase",
    "SectionAlignment", "FileAlignment", "MajorOperatingSystemVersion", "NumberOfSections"
]

# --- AYARLAR ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")
WATCH_DIR = os.path.expanduser("~/Downloads")

# --- İZLEME MOTORU ---
class MonitorHandler(FileSystemEventHandler):
    def __init__(self, callback_function):
        self.callback = callback_function

    def on_created(self, event):
        self.process(event)

    def on_moved(self, event):
        if not event.is_directory and event.dest_path.endswith(".exe"):
            self.callback(event.dest_path)

    def process(self, event):
        if event.is_directory: return
        if event.src_path.endswith(".exe"):
            self.callback(event.src_path)

# --- ANA UYGULAMA ARAYÜZÜ ---
class AntivirusApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("🛡️ AI SENTINEL - CANLI KORUMA")
        self.geometry("750x550")
        
        self.base_path = os.getcwd()
        self.model_path = os.path.join(self.base_path, "models", "antivirus_model.pkl")
        self.model = None
        self.observer = None

        self.create_widgets()
        self.load_model()

    def create_widgets(self):
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        
        ctk.CTkLabel(self.sidebar, text="AI SENTINEL", font=("Montserrat", 22, "bold")).pack(pady=30)
        
        self.switch_var = ctk.StringVar(value="off")
        self.switch = ctk.CTkSwitch(self.sidebar, text="Canlı Koruma", command=self.toggle_protection,
                                    variable=self.switch_var, onvalue="on", offvalue="off", font=("Arial", 13, "bold"))
        self.switch.pack(pady=20, padx=20)
        
        ctk.CTkLabel(self.sidebar, text=f"İzlenen:\nDownloads", text_color="gray", font=("Arial", 11)).pack(side="bottom", pady=20)

        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)

        self.status_label = ctk.CTkLabel(self.main_frame, text="SİSTEM GÜVENLİ", font=("Roboto", 30, "bold"), text_color="#00C851")
        self.status_label.pack(pady=(50, 10))

        self.file_info = ctk.CTkLabel(self.main_frame, text="Lütfen dosyayı indirilenler klasörüne atın.", font=("Roboto", 13))
        self.file_info.pack(pady=5)

        self.btn_manual = ctk.CTkButton(self.main_frame, text="MANUEL DOSYA SEÇ", command=self.manual_scan, height=45)
        self.btn_manual.pack(pady=30)

        self.log_box = ctk.CTkTextbox(self.main_frame, height=200, font=("Courier New", 12))
        self.log_box.pack(pady=10, padx=20, fill="x")
        self.log_box.insert("0.0", ">>> Antivirüs Başlatıldı.\n")

    def load_model(self):
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                self.log(">>> Model başarıyla yüklendi.")
            else:
                self.log(">>> HATA: Model dosyası bulunamadı!")
        except Exception as e:
            self.log(f">>> Model yüklenemedi: {e}")

    def log(self, msg):
        self.log_box.insert("end", msg + "\n")
        self.log_box.see("end")

    def toggle_protection(self):
        if self.switch_var.get() == "on":
            self.event_handler = MonitorHandler(self.trigger_scan)
            self.observer = Observer()
            self.observer.schedule(self.event_handler, path=WATCH_DIR, recursive=False)
            self.observer.start()
            self.log("🟢 Koruma Aktif.")
            self.status_label.configure(text="KORUMA AKTİF", text_color="#00C851")
        else:
            if self.observer:
                self.observer.stop()
                self.observer.join()
            self.log("🔴 Koruma Kapatıldı.")
            self.status_label.configure(text="KORUMA KAPALI", text_color="gray")

    def manual_scan(self):
        path = filedialog.askopenfilename(filetypes=[("Executable Files", "*.exe")])
        if path:
            self.trigger_scan(path)

    def trigger_scan(self, file_path):
        threading.Thread(target=self.scan_logic, args=(file_path,), daemon=True).start()

    def scan_logic(self, file_path):
        filename = os.path.basename(file_path)
        self.file_info.configure(text=f"Taranıyor: {filename}")
        time.sleep(3)
        
        try:
            pe = pefile.PE(file_path)
            feat_dict = {
                "Machine": pe.FILE_HEADER.Machine,
                "SizeOfOptionalHeader": pe.FILE_HEADER.SizeOfOptionalHeader,
                "Characteristics": pe.FILE_HEADER.Characteristics,
                "MajorLinkerVersion": pe.OPTIONAL_HEADER.MajorLinkerVersion,
                "SizeOfCode": pe.OPTIONAL_HEADER.SizeOfCode,
                "SizeOfInitializedData": pe.OPTIONAL_HEADER.SizeOfInitializedData,
                "AddressOfEntryPoint": pe.OPTIONAL_HEADER.AddressOfEntryPoint,
                "ImageBase": pe.OPTIONAL_HEADER.ImageBase,
                "SectionAlignment": pe.OPTIONAL_HEADER.SectionAlignment,
                "FileAlignment": pe.OPTIONAL_HEADER.FileAlignment,
                "MajorOperatingSystemVersion": pe.OPTIONAL_HEADER.MajorOperatingSystemVersion,
                "NumberOfSections": pe.FILE_HEADER.NumberOfSections,
            }
            
            df = pd.DataFrame([feat_dict])
            df = df[FEATURE_COLUMNS] 
            
            prediction = self.model.predict(df)[0]
            prob = self.model.predict_proba(df)[0]

            if prediction == 1:
                self.status_label.configure(text="🚨 TEHDİT BULUNDU!", text_color="#ff4444")
                self.log(f"⚠️ ZARARLI: {filename} (%{prob[1]*100:.1f})")
                messagebox.showwarning("GÜVENLİK", f"Zararlı Yazılım Tespit Edildi:\n{filename}")
            else:
                self.status_label.configure(text="✅ SİSTEM GÜVENLİ", text_color="#00C851")
                self.log(f"✅ GÜVENLİ: {filename} (%{prob[0]*100:.1f})")

        except Exception as e:
            self.log(f"❌ Hata ({filename}): {str(e)}")
            self.status_label.configure(text="ANALİZ HATASI", text_color="orange")

if __name__ == "__main__":
    app = AntivirusApp()
    app.mainloop()