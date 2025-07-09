import os
import re
import glob
import requests
import cv2
from ultralytics import YOLO
import easyocr
from dotenv import load_dotenv

# Load environment variables from .env in project root
load_dotenv()

# --- CONFIGURATION ---
API_URL = os.getenv('API_URL', 'http://127.0.0.1:5000/api/containers')
MODEL_PATH = 'yolov11_custom.pt'
IMAGE_PATH = os.getenv('IMAGE_PATH', 'test/images/12.jpg')
LANGUAGES = os.getenv('OCR_LANGUAGES', 'en').split(',')
YOLO_CLASSES = [int(x) for x in os.getenv('YOLO_CLASSES', '1,9').split(',')]
YOLO_BASE_DIR = os.getenv('YOLO_BASE_DIR', 'runs/detect')
# ----------------------

def get_latest_predict_folder(base=None):
    if base is None:
        base = YOLO_BASE_DIR
    runs = glob.glob(os.path.join(base, 'predict*'))
    def num(p):
        m = re.search(r'predict(\d+)', p)
        return int(m.group(1)) if m else -1
    runs = sorted(runs, key=num)
    return runs[-1] if runs else None

def detect_and_crop(model_path, image_path, classes):
    model = YOLO(model_path)
    results = model.predict(
        source=image_path,
        save=False,
        save_crop=True,
        classes=classes
    )
    run_dir = get_latest_predict_folder()
    if not run_dir:
        raise RuntimeError("Could not find any runs/detect/predict* folder")
    return os.path.join(run_dir, 'crops')

def process_ocr(reader, img_path):
    img = cv2.imread(img_path)
    if img is None:
        print(f"⚠️  Could not open {img_path}")
        return ""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    try:
        ocr_results = reader.readtext(thresh)
    except Exception as e:
        print(f"⚠️  OCR error on {img_path}: {e}")
        return ""
    if not ocr_results:
        print(f"⚠️  No text detected in {os.path.basename(img_path)}")
        return ""
    text = " ".join([res[1] for res in ocr_results])
    cleaned_text = re.sub(r'[^a-zA-Z0-9\s]', '', text).strip()
    return cleaned_text

def process_and_post(crop_base_dir, api_url):
    reader = easyocr.Reader(LANGUAGES)
    container_dir = os.path.join(crop_base_dir, 'container_number')
    iso_dir = os.path.join(crop_base_dir, 'iso_code')
    container_texts = []
    for img_file in sorted(glob.glob(os.path.join(container_dir, '*.jpg'))):
        text = process_ocr(reader, img_file)
        if text:
            container_texts.append(text)
    iso_texts = []
    for img_file in sorted(glob.glob(os.path.join(iso_dir, '*.jpg'))):
        text = process_ocr(reader, img_file)
        if text:
            iso_texts.append(text)
    for i, container_num in enumerate(container_texts):
        iso_code = iso_texts[i] if i < len(iso_texts) else (iso_texts[0] if iso_texts else "")
        payload = {
            'container_number': container_num,
            'iso_code': iso_code
        }
        print(f"→ Posting container: {container_num} (ISO: {iso_code})...", end=' ')
        try:
            resp = requests.post(api_url, json=payload)
            print(f"Status: {resp.status_code}")
        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == '__main__':
    print("🔧 Configuration loaded from .env:")
    print(f"  - API URL: {API_URL}")
    print(f"  - Model: {MODEL_PATH}")
    print(f"  - Image: {IMAGE_PATH}")
    print(f"  - Classes: {YOLO_CLASSES}")
    print(f"  - Languages: {LANGUAGES}")
    print("\n1) Running detection & cropping…")
    base_crop_dir = detect_and_crop(MODEL_PATH, IMAGE_PATH, YOLO_CLASSES)
    print("→ Crops saved in:", base_crop_dir)
    print("\n2) Running OCR & sending to API…")
    process_and_post(base_crop_dir, API_URL)
