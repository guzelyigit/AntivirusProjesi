import os
import pefile
import pandas as pd

# --- AYARLAR VE SÜTUN SIRALAMASI ---
# Bu sıralama hem eğitimde hem de GUI'de milimetrik olarak aynı kalmalıdır.
FEATURE_COLUMNS = [
    "Machine", "SizeOfOptionalHeader", "Characteristics", "MajorLinkerVersion",
    "SizeOfCode", "SizeOfInitializedData", "AddressOfEntryPoint", "ImageBase",
    "SectionAlignment", "FileAlignment", "MajorOperatingSystemVersion", "NumberOfSections"
]

base_path = os.getcwd()
output_csv = os.path.join(base_path, "dataset", "final_dataset.csv")

# Klasör yolları
folders = {
    0: os.path.join(base_path, "dataset", "benign"),
    1: os.path.join(base_path, "dataset", "malware")
}

data_list = []

print("\n" + "="*50)
print("   🔍 GERÇEK VERİ ANALİZİ VE ÖZELLİK ÇIKARMA   ")
print("="*50)

for label, folder_path in folders.items():
    status_text = "TEMİZ" if label == 0 else "VİRÜS"
    if not os.path.exists(folder_path):
        print(f"[UYARI] {status_text} klasörü bulunamadı: {folder_path}")
        continue
    
    files = [f for f in os.listdir(folder_path) if f.endswith(".exe")]
    print(f"\n[{status_text}] Klasörü Taranıyor: {folder_path}")
    print(f"i Bulunan dosya sayısı: {len(files)}")

    for filename in files:
        file_path = os.path.join(folder_path, filename)
        
        # --- HATA YAKALAYICI  ---
        try:
            pe = pefile.PE(file_path)
            
            # Özellikleri çıkar
            features = {
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
                "Label": label,      # 0 veya 1
                "FileName": filename # Takip için
            }
            data_list.append(features)
            print(f"  [OK] {filename}")

        except pefile.PEFormatError:
            # Dosya bir EXE değilse veya PE başlığı bozuksa buraya düşer
            print(f"  [HATA] {filename}: Geçersiz PE Formatı (Atlanıyor)")
        except Exception as e:
            # Diğer tüm hatalar (Dosya boş, erişim engellendi vb.)
            print(f"  [HATA] {filename}: {str(e)}")
            continue

# --- VERİYİ KAYDET ---
if data_list:
    df = pd.DataFrame(data_list)
    
    # Sütunları garantiye aldım (Önce FileName, sonra özellikler, en son Label)
    final_columns = ["FileName"] + FEATURE_COLUMNS + ["Label"]
    df = df[final_columns]
    
    df.to_csv(output_csv, index=False)
    print("\n" + "="*50)
    print(f"✅ İŞLEM BAŞARILI! Veri seti hazır.")
    print(f"📍 Kayıt Yeri: {output_csv}")
    print(f"📊 Toplam Başarılı Veri: {len(df)} adet")
    print("="*50)
else:
    print("\n[!] HATA: Hiçbir dosya analiz edilemedi. Klasörleri kontrol et.")