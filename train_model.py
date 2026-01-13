import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier # Gradient Boosting algortiması eklenmesi 
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# --- AYARLAR ---
print("\n" + "="*50)
print("   YAPAY ZEKA 2.0 (GRADIENT BOOSTING) EĞİTİLİYOR...   ")
print("="*50)

base_path = os.getcwd()
dataset_path = os.path.join(base_path, "dataset", "final_dataset.csv")
model_path = os.path.join(base_path, "models", "antivirus_model.pkl")

if not os.path.exists(dataset_path):
    print("[HATA] Veri seti yok!")
    exit()

df = pd.read_csv(dataset_path)
print(f"[BİLGİ] Toplam Veri Sayısı: {len(df)}")

# --- VERİ HAZIRLIĞI ---
X = df.drop(["FileName", "Label"], axis=1)
X = X.fillna(0)
y = df["Label"]

# Eğitim ve Test (%75 Eğitim, %25 Test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)

# --- MODEL EĞİTİMİ (Gradient Boosting) ---
# Bu algoritma hatalarından ders çıkararak ilerler (Boosting)
print("\n[BİLGİ] Gradient Boosting Modeli eğitiliyor...")
clf = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42)
clf.fit(X_train, y_train)

# --- TEST VE RAPOR ---
y_pred = clf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred) * 100

print("-" * 40)
print(f"✅ GELİŞMİŞ MODEL BAŞARISI: %{accuracy:.2f}")
print("-" * 40)

# Confusion Matrix (Hata Tablosu)
cm = confusion_matrix(y_test, y_pred)
print("\n🔍 DETAYLI ANALİZ (CONFUSION MATRIX):")
print(f"   Gerçek Temiz, Tahmin Temiz (Doğru): {cm[0][0]}")
print(f"   Gerçek Virüs, Tahmin Virüs (Doğru): {cm[1][1]}")
print(f"   Gerçek Temiz, Tahmin VİRÜS (Yanlış Alarm): {cm[0][1]}  <-- Önemli!")
print(f"   Gerçek Virüs, Tahmin TEMİZ (KAÇAN VİRÜS): {cm[1][0]}  <-- Kritik!")

# Kaydet
joblib.dump(clf, model_path)
print(f"\n[KAYDEDİLDİ] Yeni Süper Beyin hazır: {model_path}")
print("="*50)