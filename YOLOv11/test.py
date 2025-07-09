import os
import re
import glob
import requests
import cv2
import numpy as np
from ultralytics import YOLO
import easyocr
from dotenv import load_dotenv

# --- Load environment variables ---
load_dotenv()

API_URL = os.getenv('API_URL', 'http://127.0.0.1:5000/api/containers')
MODEL_PATH = os.getenv('MODEL_PATH', 'yolov11_custom.pt')
IMAGE_PATH = os.getenv('IMAGE_PATH', 'test/images/1.jpg')
LANGUAGES = os.getenv('OCR_LANGUAGES', 'en').split(',')
YOLO_CLASSES = [int(x) for x in os.getenv('YOLO_CLASSES', '1,9').split(',')]
YOLO_BASE_DIR = os.getenv('YOLO_BASE_DIR', 'runs/detect')

def preprocess_image_for_ocr(image_path):
    """
    Optimized preprocessing based on EasyOCR best practices:
    - Upscaling for better character recognition
    - Gaussian blur to reduce noise
    - Simple and fast processing
    """
    img = cv2.imread(image_path)
    if img is None:
        print(f"⚠️  Could not open {image_path}")
        return None

    # 1. Upscale for better character recognition (key factor for accuracy)
    scale_factor = 2
    upscaled = cv2.resize(img, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)
    
    # 2. Apply Gaussian blur to reduce noise (proven effective for EasyOCR)
    blurred = cv2.blur(upscaled, (3, 3))
    
    return blurred

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
    print(f"Loading YOLO model: {model_path}")
    model = YOLO(model_path)
    print(f"Running detection on: {image_path}")
    results = model.predict(
        source=image_path,
        save=False,
        save_crop=True,
        classes=classes,
        conf=0.5  # Confidence threshold
    )
    run_dir = get_latest_predict_folder()
    if not run_dir:
        raise RuntimeError("Could not find any runs/detect/predict* folder")
    return os.path.join(run_dir, 'crops')

def process_ocr(reader, img_path):
    """Process single image with optimized preprocessing"""
    print(f"Processing OCR for: {os.path.basename(img_path)}")
    
    # Apply preprocessing
    processed_img = preprocess_image_for_ocr(img_path)
    if processed_img is None:
        return ""
    
    try:
        # EasyOCR with optimized settings
        ocr_results = reader.readtext(
            processed_img, 
            allowlist='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ',  # Container numbers/ISO codes only
            text_threshold=0.3,  # Lower threshold for better detection
            paragraph=False
        )
    except Exception as e:
        print(f"⚠️  OCR error on {img_path}: {e}")
        return ""
    
    if not ocr_results:
        print(f"⚠️  No text detected in {os.path.basename(img_path)}")
        return ""
    
    # Extract and clean text
    text = " ".join([res[1] for res in ocr_results])
    cleaned_text = re.sub(r'[^a-zA-Z0-9\s]', '', text).strip()
    print(f"✅ Detected text: '{cleaned_text}'")
    return cleaned_text

def process_and_post(crop_base_dir, api_url):
    print("Initializing EasyOCR reader...")
    reader = easyocr.Reader(LANGUAGES, gpu=True)  # Use GPU if available
    
    # Process container numbers
    container_dir = os.path.join(crop_base_dir, 'container_number')
    iso_dir = os.path.join(crop_base_dir, 'iso_code')
    
    print(f"Looking for container crops in: {container_dir}")
    print(f"Looking for ISO crops in: {iso_dir}")
    
    container_texts = []
    if os.path.exists(container_dir):
        for img_file in sorted(glob.glob(os.path.join(container_dir, '*.jpg'))):
            text = process_ocr(reader, img_file)
            if text:
                container_texts.append(text)
    
    # Process ISO codes
    iso_texts = []
    if os.path.exists(iso_dir):
        for img_file in sorted(glob.glob(os.path.join(iso_dir, '*.jpg'))):
            text = process_ocr(reader, img_file)
            if text:
                iso_texts.append(text)
    
    print(f"Found {len(container_texts)} container numbers and {len(iso_texts)} ISO codes")
    
    # Send to API
    if not container_texts:
        print("⚠️  No container numbers detected!")
        return
        
    for i, container_num in enumerate(container_texts):
        iso_code = iso_texts[i] if i < len(iso_texts) else (iso_texts[0] if iso_texts else "")
        
        payload = {
            'container_number': container_num,
            'iso_code': iso_code
        }
        
        print(f"→ Posting container: {container_num} (ISO: {iso_code})...", end=' ')
        try:
            resp = requests.post(api_url, json=payload, timeout=10)
            if resp.status_code == 201:
                print(f"✅ Success (201)")
            elif resp.status_code == 409:
                print(f"⚠️  Already exists (409)")
            else:
                print(f"❌ Error ({resp.status_code})")
        except Exception as e:
            print(f"❌ ERROR: {e}")

if __name__ == '__main__':
    print("🚢 Container Detection OCR Pipeline")
    print("=" * 50)
    print("🔧 Configuration:")
    print(f"  - API URL: {API_URL}")
    print(f"  - Model: {MODEL_PATH}")
    print(f"  - Image: {IMAGE_PATH}")
    print(f"  - Classes: {YOLO_CLASSES}")
    print(f"  - Languages: {LANGUAGES}")
    print()
    
    try:
        print("1️⃣  Running YOLO detection & cropping...")
        base_crop_dir = detect_and_crop(MODEL_PATH, IMAGE_PATH, YOLO_CLASSES)
        print(f"   ✅ Crops saved in: {base_crop_dir}")
        print()
        
        print("2️⃣  Running OCR & sending to API...")
        process_and_post(base_crop_dir, API_URL)
        print()
        print("🎉 Pipeline completed successfully!")
        
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
