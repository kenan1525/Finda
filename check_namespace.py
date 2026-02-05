import os
import sys
import site

# Site-packages yollarını bul
site_packages = site.getsitepackages()
print(f"Site packages: {site_packages}")

for sp in site_packages:
    google_path = os.path.join(sp, 'google')
    if os.path.exists(google_path):
        print(f"Checking {google_path}...")
        init_file = os.path.join(google_path, '__init__.py')
        if os.path.exists(init_file):
            print(f"OZEL_UYARI: {init_file} bulundu! Bu dosya 'google' namespace paketini bozuyor olabilir.")
            # Okuyup içeriğine bakalım
            try:
                with open(init_file, 'r') as f:
                    content = f.read()
                print(f"__init__.py icerigi:\n{content}")
                
                # Eğer dosya boşsa veya namespace ile ilgili değilse sorun olabilir.
                # Genellikle google klasöründe __init__.py olmamalı (implicit namespace)
                # Veya pkg_resources kullanan türde olmalı.
            except Exception as e:
                print(f"Dosya okunamadı: {e}")
        else:
            print(f"{google_path} içinde __init__.py YOK (Beklenen durum).")
            
        genai_path = os.path.join(google_path, 'genai')
        if os.path.exists(genai_path):
            print(f"'genai' klasörü mevcut: {genai_path}")
        else:
            print(f"'genai' klasörü MEVCUT DEGIL!")

try:
    import google
    print(f"google imported from: {google.__path__}")
except Exception as e:
    print(f"google import error: {e}")

try:
    import google.genai
    print("WARNING: 'import google.genai' WORKED in this script!")
except ImportError as e:
    print(f"import google.genai FAILED: {e}")
