import os
from flask import Flask, render_template, request, redirect, url_for
import cv2
from ultralytics import YOLO
import numpy as np
import folium

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
RESULT_FOLDER = 'static/results'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

# Load YOLO model (use pretrained weights or custom trained animal model)
model = YOLO('models/yolov8n.pt')  # lightweight model for demo

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Upload file
        file = request.files['file']
        if file:
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)

            # Detect animals
            result_img_path, herd_count = detect_animals(filepath)

            # Optional: Map alert for herd
            map_path = generate_map_alert(herd_count)

            return render_template('index.html', 
                                   result_image=result_img_path,
                                   herd_count=herd_count,
                                   map_file=map_path)
    return render_template('index.html', result_image=None)

def detect_animals(img_path):
    img = cv2.imread(img_path)
    results = model(img)  # YOLO detection
    boxes = results[0].boxes.xyxy  # bounding boxes
    herd_count = len(boxes)

    # Draw boxes
    for box in boxes:
        x1, y1, x2, y2 = map(int, box)
        cv2.rectangle(img, (x1, y1), (x2, y2), (0,255,0), 2)
        cv2.putText(img, 'Animal', (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)

    result_img_path = os.path.join(RESULT_FOLDER, os.path.basename(img_path))
    cv2.imwrite(result_img_path, img)

    return result_img_path, herd_count

def generate_map_alert(count):
    # For demo: create simple map at fixed location
    m = folium.Map(location=[30.3753, 69.3451], zoom_start=5)
    folium.Marker(
        location=[30.3753, 69.3451],
        popup=f"Herd detected: {count} animals",
        icon=folium.Icon(color='red')
    ).add_to(m)
    map_file = 'static/results/map.html'
    m.save(map_file)
    return map_file

if __name__ == '__main__':
    app.run(debug=True)