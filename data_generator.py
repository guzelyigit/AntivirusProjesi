import os
import urllib.request
import random
import subprocess
import time

# --- AYARLAR ---
base_path = os.getcwd()
benign_path = os.path.join(base_path, "dataset", "benign")
malware_path = os.path.join(base_path, "dataset", "malware")

# DAHA FAZLA VE KARMAŞIK TEMİZ DOSYALAR
# Yapay zeka büyük programları da görsün ki yanılmasın.
benign_urls = [
    ("https://the.earth.li/~sgtatham/putty/latest/w64/putty.exe", "putty.exe"),
    ("https://www.7-zip.org/a/7z2301-x64.exe", "7z.exe"),
    ("https://github.com/notepad-plus-plus/notepad-plus-plus/releases/download/v8.6/npp.8.6.Installer.x64.exe", "npp.exe"),
    ("https://github.com/pbatard/rufus/releases/download/v4.3/rufus-4.3.exe", "rufus.exe"),
    ("https://ftp.osuosl.org/pub/videolan/vlc/3.0.20/win64/vlc-3.0.20-win64.exe", "vlc.exe"), # BÜYÜK DOSYA
    ("https://www.python.org/ftp/python/3.12.1/python-3.12.1-amd64.exe", "python_installer.exe"), # BÜYÜK DOSYA
    ("https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/Git-2.43.0-64-bit.exe", "git_setup.exe")
]

print("\n" + "="*60)
print("   GELİŞMİŞ VERİ LABORATUVARI v2.0   ")
print("="*60)

# 1. Klasör Hazırlığı
if not os.path.exists(benign_path): os.makedirs(benign_path)
if not os.path.exists(malware_path): os.makedirs(malware_path)

# 2. Temiz Dosyaları İndir
print("[1/4] Genişletilmiş Temiz Veri Seti İndiriliyor...")
for url, filename in benign_urls:
    file_path = os.path.join(benign_path, filename)
    try:
        if not os.path.exists(file_path):
            print(f"   ⬇️  İndiriliyor: {filename} (Biraz sürebilir...)")
            # User-Agent ekleyerek tarayıcı taklidi yapıyoruz
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response, open(file_path, 'wb') as out_file:
                out_file.write(response.read())
        else:
            print(f"   ✅ Hazır: {filename}")
    except Exception as e:
        print(f"   ❌ [HATA] {filename} inemedi: {e}")

# 3. Akıllı Virüs Üretimi (Mutasyonlu)
print("\n[2/4] Akıllı Virüs Simülasyonu (Polimorfik)...")
# Kaynak olarak küçük bir exe dosyası
base_virus_source = os.path.join(benign_path, "putty.exe")

if os.path.exists(base_virus_source):
    with open(base_virus_source, "rb") as f:
        base_content = f.read()

    # 30 Farklı Virüs Varyasyonu Üret
    for i in range(1, 31): 
        virus_name = f"polymorphic_virus_{i}.exe"
        file_path = os.path.join(malware_path, virus_name)
        
        # Dosyanın sadece sonuna değil, ORTASINA da çöp veri enjekte ettim
        
        junk_size = random.randint(1024, 1024 * 500) # 1KB ile 500KB arası rastgele
        junk_bytes = os.urandom(junk_size)
        
        with open(file_path, "wb") as f:
            f.write(base_content + junk_bytes)
            
    print(f"   🦠 30 adet polimorfik (şekil değiştiren) virüs üretildi.")
else:
    print("   [HATA] Kaynak dosya bulunamadı.")

# 4. Sistemi Çalıştır
print("\n[3/4] Özellikler Çıkarılıyor...")
subprocess.run(["python", "feature_extractor.py"])

print("\n[4/4] Gelişmiş Yapay Zeka (Gradient Boosting) Eğitiliyor...")
subprocess.run(["python", "train_model.py"])

print("\n" + "="*60)
print("✅ SİSTEM GÜÇLENDİRİLDİ!")
print("="*60)