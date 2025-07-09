from ultralytics import YOLO

model = YOLO('yolov11_custom.pt')

model.predict(source='test/images/20.jpg',save=True,
              save_crop=True, classes=[1,9])
