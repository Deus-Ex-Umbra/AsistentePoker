import torch
from ultralytics import YOLO
import numpy as np
from typing import List, Any, Optional
from Config import YOLO_MODEL_PATH, YOLO_DEVICE, CONFIDENCE_THRESHOLD

class DetectorObjetos:
    def __init__(self):
        self.model = None
        self.device = None
        self._inicializar_modelo()
    
    def _inicializar_modelo(self):
        """Inicializa el modelo YOLO con manejo robusto de errores"""
        try:
            # Verificar si CUDA está disponible
            if YOLO_DEVICE == 'cuda' and torch.cuda.is_available():
                self.device = 'cuda'
                print(f"🎮 Usando GPU: {torch.cuda.get_device_name(0)}")
            else:
                self.device = 'cpu'
                print("🖥️ Usando CPU (GPU no disponible)")
            
            # Cargar modelo
            print(f"📁 Cargando modelo YOLO desde: {YOLO_MODEL_PATH}")
            self.model = YOLO(YOLO_MODEL_PATH)
            self.model.to(self.device)
            
            # Verificar que el modelo se cargó correctamente
            if self.model is None:
                raise Exception("El modelo YOLO no se pudo cargar")
                
            print(f"✅ Modelo YOLO cargado exitosamente en {self.device}")
            
        except FileNotFoundError:
            print(f"❌ Archivo del modelo no encontrado: {YOLO_MODEL_PATH}")
            self.model = None
        except Exception as e:
            print(f"❌ Error al cargar el modelo YOLO: {e}")
            self.model = None

    def detectar(self, frame: np.ndarray) -> List[Any]:
        """Detecta objetos en un frame con manejo robusto de errores"""
        if self.model is None:
            return []
        
        if frame is None or frame.size == 0:
            return []
        
        try:
            # Realizar detección con parámetros optimizados
            results = self.model(
                frame, 
                conf=CONFIDENCE_THRESHOLD,
                verbose=False,
                device=self.device
            )
            return results
            
        except torch.cuda.OutOfMemoryError:
            print("⚠️ Sin memoria GPU, intentando con CPU...")
            try:
                self.model.to('cpu')
                self.device = 'cpu'
                results = self.model(frame, conf=CONFIDENCE_THRESHOLD, verbose=False)
                return results
            except Exception as e2:
                print(f"❌ Error en detección con CPU: {e2}")
                return []
                
        except Exception as e:
            print(f"❌ Error en detección: {e}")
            return []
    
    def esta_disponible(self) -> bool:
        """Verifica si el detector está disponible"""
        return self.model is not None
    
    def obtener_info_dispositivo(self) -> str:
        """Retorna información del dispositivo en uso"""
        if self.device == 'cuda':
            return f"GPU: {torch.cuda.get_device_name(0)}"
        else:
            return "CPU"