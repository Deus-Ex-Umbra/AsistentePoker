import keyboard
import threading
import time
from typing import Dict, Any
from Config import KEY_QUIT, KEY_PAUSE_RESUME, KEY_FORCE_ACTION
class ListenerTeclado(threading.Thread):
    def __init__(self, shared_state: Dict[str, Any]):
        super().__init__(daemon=True)
        self.shared_state = shared_state
        self.shared_state['running'] = True
        self.shared_state['paused'] = False
        self.shared_state['force_action'] = False
    def run(self):
        keyboard.add_hotkey(KEY_QUIT, self.quit_app)
        keyboard.add_hotkey(KEY_PAUSE_RESUME, self.toggle_pause)
        keyboard.add_hotkey(KEY_FORCE_ACTION, self.force_action)
        while self.shared_state.get('running', True): time.sleep(0.1)
    def quit_app(self): self.shared_state['running'] = False
    def toggle_pause(self):
        self.shared_state['paused'] = not self.shared_state.get('paused', False)
        print(f"\n--- PROGRAMA {'PAUSADO' if self.shared_state['paused'] else 'REANUDADO'} ---")
    def force_action(self):
        print("\n--- Forzando nueva recomendación de acción ---")
        self.shared_state['force_action'] = True
