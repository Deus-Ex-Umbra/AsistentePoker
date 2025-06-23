import numpy as np
import mss
import cv2
from typing import Optional
class CapturadorPantalla:
    def __init__(self):
        self.sct, self.monitor = None, None
        try:
            self.sct = mss.mss()
            self.monitor = self.sct.monitors[1]
        except mss.exception.ScreenShotError: pass
    def capturar_frame(self) -> Optional[np.ndarray]:
        if not self.sct: return None
        try: return cv2.cvtColor(np.array(self.sct.grab(self.monitor)), cv2.COLOR_BGRA2BGR)
        except mss.exception.ScreenShotError: return None