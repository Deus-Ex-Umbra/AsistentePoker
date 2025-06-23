import easyocr
import numpy as np
import cv2
from typing import List, Optional, Tuple, Dict
from collections import Counter

class ProcesadorOCR:
    def __init__(self, languages: List[str] = ['en']):
        self.reader = None
        self.fallback_activo = False
        self._inicializar_ocr(languages)
    
    def _inicializar_ocr(self, languages: List[str]):
        try:
            self.reader = easyocr.Reader(languages, gpu=True)
        except Exception:
            try:
                self.reader = easyocr.Reader(languages, gpu=False)
            except Exception as e2:
                print(f"Error crítico en EasyOCR: {e2}")
                self.reader = None
                self.fallback_activo = True

    def get_text_from_image(self, image: np.ndarray, es_valor_carta: bool = False) -> str:
        if image is None or image.size == 0:
            return ""
        
        if es_valor_carta:
            return self._extraer_valor_carta_con_preprocesamiento(image)
        else:
            return self._extraer_texto_normal(image)

    def _extraer_texto_normal(self, image: np.ndarray) -> str:
        if self.reader is not None:
            try:
                results = self.reader.readtext(
                    cv2.cvtColor(image, cv2.COLOR_BGR2GRAY),
                    detail=0,
                    paragraph=True
                )
                if results:
                    return " ".join(results)
            except Exception as e:
                print(f"Error en EasyOCR: {e}")
        return ""

    def _extraer_valor_carta_con_preprocesamiento(self, image: np.ndarray) -> str:
        if self.reader is None:
            return ""
        
        resultados_candidatos = []
        try:
            gray_original = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            resultado_original = self._ocr_con_confianza(gray_original)
            if resultado_original:
                resultados_candidatos.append(resultado_original)
            
            gray_negativo = cv2.bitwise_not(gray_original)
            resultado_negativo = self._ocr_con_confianza(gray_negativo)
            if resultado_negativo:
                resultados_candidatos.append(resultado_negativo)
            
            gray_contraste = cv2.equalizeHist(gray_original)
            resultado_contraste = self._ocr_con_confianza(gray_contraste)
            if resultado_contraste:
                resultados_candidatos.append(resultado_contraste)
            
            _, gray_binario = cv2.threshold(gray_original, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            resultado_binario = self._ocr_con_confianza(gray_binario)
            if resultado_binario:
                resultados_candidatos.append(resultado_binario)

            return self._seleccionar_mejor_resultado(resultados_candidatos)
            
        except Exception as e:
            print(f"Error en procesamiento múltiple OCR: {e}")
            return ""

    def _ocr_con_confianza(self, imagen_procesada: np.ndarray) -> Optional[Tuple[str, float]]:
        try:
            results = self.reader.readtext(imagen_procesada, detail=1)
            if results:
                mejor_resultado = max(results, key=lambda x: x[2])
                texto = mejor_resultado[1].strip().upper()
                confianza = mejor_resultado[2]
                return (texto, confianza)
        except Exception:
            pass
        return None

    def _seleccionar_mejor_resultado(self, candidatos: List[Tuple[str, float]]) -> str:
        if not candidatos:
            return ""
        
        textos = [c[0] for c in candidatos]
        contador_frecuencia = Counter(textos)
        
        puntuaciones = {}
        for texto, confianza in candidatos:
            frecuencia = contador_frecuencia[texto]
            puntuacion = confianza * frecuencia + (frecuencia - 1) * 0.2
            
            if texto not in puntuaciones or puntuacion > puntuaciones[texto]:
                puntuaciones[texto] = puntuacion
        
        if puntuaciones:
            return max(puntuaciones, key=puntuaciones.get)
        
        return ""

    def procesar_accion_poker(self, image: np.ndarray) -> Optional[str]:
        """Procesa una imagen de acción de poker y devuelve la acción detectada"""
        texto_raw = self.get_text_from_image(image)
        if not texto_raw:
            return None
        
        texto = texto_raw.lower().strip()
        
        # IMPORTANTE: Detectar All-In con múltiples variantes
        # Verificar primero All-In ya que es más específico
        all_in_patterns = [
            'all-in', 'all in', 'allin', 'all_in',
            'all - in', 'a l l i n', 'a l l - i n',
            'todo', 'todo adentro', 'completo'
        ]
        
        for pattern in all_in_patterns:
            if pattern in texto:
                print(f"[OCR] Detectado All-In: '{texto_raw}'")
                return "All-In"
        if 'all' in texto and 'in' in texto:
            print(f"[OCR] Detectado All-In (palabras separadas): '{texto_raw}'")
            return "All-In"
        mapeo_acciones_fijas = {
            'fold': 'Fold', 'no ir': 'Fold', 'retire': 'Fold', 'retirarse': 'Fold',
            'check': 'Check', 'pasar': 'Check', 'paso': 'Check', 'ver': 'Check',
            'call': 'Call', 'igualar': 'Call', 'pagar': 'Call', 'ver apuesta': 'Call'
        }
        for termino, accion in mapeo_acciones_fijas.items():
            if termino in texto:
                return accion
        terminos_raise = ['raise', 'subir', 'apostar', 'bet', 'aumentar']
        if any(termino in texto for termino in terminos_raise):
            return "Raise"
        if 'ALL' in texto_raw.upper() and 'IN' in texto_raw.upper():
            print(f"[OCR] Detectado All-In (mayúsculas): '{texto_raw}'")
            return "All-In"
        return texto_raw.strip() if len(texto_raw.strip()) < 20 else None