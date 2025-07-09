import easyocr
path = 'runs/detect/predict15/crops/container_number/14.jpg'
reader = easyocr.Reader(['en'])  # Language
result = reader.readtext(path)
print(result[0][1])  # Extracted text


