from ultralytics import YOLO

model = YOLO(
    r".\local_deployment\model\openvisionai-yolo\best.pt"
)

results = model(
    r".\local_deployment\test_image.png",
    conf=0.01
)

for result in results:
    print("Classes:", result.names)
    print("Detections:", len(result.boxes))

    for box in result.boxes:
        print({
            "class": result.names[int(box.cls[0])],
            "confidence": float(box.conf[0]),
            "bbox": box.xyxy[0].tolist()
        })
