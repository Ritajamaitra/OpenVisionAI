from ultralytics import YOLO

model = YOLO(
    r".\local_deployment\model\openvisionai-yolo\best.pt"
)

results = model(
    r".\local_deployment\test_image.png"
)

for result in results:
    print("\nClasses:", result.names)

    for box in result.boxes:
        print({
            "class": result.names[int(box.cls[0])],
            "confidence": float(box.conf[0]),
            "bbox": box.xyxy[0].tolist()
        })
