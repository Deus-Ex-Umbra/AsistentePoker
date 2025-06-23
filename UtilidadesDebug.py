import cv2
import numpy as np
import os
import datetime
from typing import List, Any, Dict
from Config import LOGS_DIR, LABEL_NAMES
np.random.seed(42)
COLORS = np.random.randint(100, 255, size=(len(LABEL_NAMES), 3), dtype="uint8")
LABEL_COLOR_MAP = {name: tuple(int(c) for c in COLORS[i]) for i, name in enumerate(LABEL_NAMES)}
def guardar_frame_con_cajas(frame: np.ndarray, yolo_results: List[Any], label_map: Dict[int, str]):
    if not os.path.exists(LOGS_DIR): os.makedirs(LOGS_DIR)
    frame_con_cajas = frame.copy()
    if not yolo_results: return
    result = yolo_results[0]
    boxes, classes, confs = result.boxes.xyxy.cpu().numpy(), result.boxes.cls.cpu().numpy(), result.boxes.conf.cpu().numpy()
    for box, cls_id, conf in zip(boxes, classes, confs):
        x1, y1, x2, y2 = map(int, box)
        label = label_map.get(int(cls_id), "Desconocido")
        color = LABEL_COLOR_MAP.get(label, (0, 255, 0))
        cv2.rectangle(frame_con_cajas, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame_con_cajas, f"{label}: {conf:.2f}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    ruta_guardado = os.path.join(LOGS_DIR, f"debug_frame_{timestamp}.png")
    try:
        cv2.imwrite(ruta_guardado, frame_con_cajas)
        print(f"📸 Imagen de depuración guardada en: {ruta_guardado}")
    except Exception as e:
        print(f"❌ Error al guardar la imagen de depuración: {e}")