import numpy as np
import math
from typing import Tuple, List, Dict, Any

BoundingBox = Tuple[int, int, int, int]

class UtilidadesGeometria:
    @staticmethod
    def get_center(box: BoundingBox) -> Tuple[int, int]:
        x1, y1, x2, y2 = box
        return (int((x1 + x2) / 2), int((y1 + y2) / 2))

    @staticmethod
    def get_area(box: BoundingBox) -> float:
        x1, y1, x2, y2 = box
        return float((x2 - x1) * (y2 - y1))

    @staticmethod
    def euclidean_distance(point1: Tuple[int, int], point2: Tuple[int, int]) -> float:
        return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

    @staticmethod
    def get_iou(box1: BoundingBox, box2: BoundingBox) -> float:
        x1_inter, y1_inter = max(box1[0], box2[0]), max(box1[1], box2[1])
        x2_inter, y2_inter = min(box1[2], box2[2]), min(box1[3], box2[3])
        inter_width, inter_height = x2_inter - x1_inter, y2_inter - y1_inter
        if inter_width <= 0 or inter_height <= 0: return 0.0
        inter_area = float(inter_width * inter_height)
        union_area = UtilidadesGeometria.get_area(box1) + UtilidadesGeometria.get_area(box2) - inter_area
        return inter_area / union_area if union_area > 0 else 0.0

    @staticmethod
    def get_overlap_percentage(container_box: BoundingBox, content_box: BoundingBox) -> float:
        x1_inter, y1_inter = max(container_box[0], content_box[0]), max(container_box[1], content_box[1])
        x2_inter, y2_inter = min(container_box[2], content_box[2]), min(container_box[3], content_box[3])
        inter_width, inter_height = x2_inter - x1_inter, y2_inter - y1_inter
        if inter_width <= 0 or inter_height <= 0: return 0.0
        inter_area = float(inter_width * inter_height)
        content_area = UtilidadesGeometria.get_area(content_box)
        return inter_area / content_area if content_area > 0 else 0.0

    @staticmethod
    def is_contained(inner_box: BoundingBox, outer_box: BoundingBox, threshold: float = 0.9) -> bool:
        return UtilidadesGeometria.get_overlap_percentage(outer_box, inner_box) >= threshold

    @staticmethod
    def ordenar_jugadores_sentido_horario(jugadores: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if len(jugadores) < 2:
            return jugadores

        centros = [j['center'] for j in jugadores if 'center' in j]
        if not centros:
            return jugadores
            
        centro_mesa_x = sum(c[0] for c in centros) / len(centros)
        centro_mesa_y = sum(c[1] for c in centros) / len(centros)

        try:
            jugadores_ordenados = sorted(
                jugadores,
                key=lambda j: math.atan2(j['center'][1] - centro_mesa_y, j['center'][0] - centro_mesa_x)
            )
            return jugadores_ordenados
        except Exception:
            return jugadores
