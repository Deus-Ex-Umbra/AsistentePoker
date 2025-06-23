import tkinter as tk
from tkinter import font, ttk
import queue
import time
from typing import Dict, Any, Optional
from Config import (
    UI_BACKGROUND_COLOR, UI_TEXT_COLOR_NORMAL, UI_TEXT_COLOR_SUCCESS, 
    UI_TEXT_COLOR_ERROR, UI_TEXT_COLOR_ACTION, UI_UPDATE_INTERVAL_MS,
    UI_WINDOW_POSITION_X, UI_WINDOW_POSITION_Y, UI_WINDOW_WIDTH, UI_WINDOW_HEIGHT
)

class InterfazUsuario(tk.Tk):
    def __init__(self, update_queue: queue.Queue):
        super().__init__()
        self.update_queue = update_queue
        
        self.ultima_actualizacion = 0
        self.recomendacion_mostrada = None
        
        self.configurarVentana()
        self.crearFuentes()
        self.crearWidgets()
        self.verificarCola()

    def configurarVentana(self):
        self.title("🎰 MCCFR Poker Assistant")
        self.geometry(f"{UI_WINDOW_WIDTH}x{UI_WINDOW_HEIGHT}+{UI_WINDOW_POSITION_X}+{UI_WINDOW_POSITION_Y}")
        self.configure(bg=UI_BACKGROUND_COLOR)
        self.attributes('-topmost', True)
        self.resizable(False, False)

    def crearFuentes(self):
        self.font_titulo = font.Font(family="Helvetica", size=13, weight="bold")
        self.font_fase = font.Font(family="Helvetica", size=12, weight="bold")
        self.font_infoset = font.Font(family="Courier", size=9)
        self.font_accion_categoria = font.Font(family="Helvetica", size=11, weight="bold")
        self.font_accion_exacta = font.Font(family="Helvetica", size=16, weight="bold")
        self.font_monto = font.Font(family="Helvetica", size=10)
        self.font_debug = font.Font(family="Courier", size=8)

    def crearWidgets(self):
        self.frame_principal = tk.Frame(self, bg=UI_BACKGROUND_COLOR)
        self.frame_principal.pack(expand=True, fill="both", padx=15, pady=15)
        
        self.label_titulo = tk.Label(
            self.frame_principal, 
            text="🎰 MCCFR POKER ASSISTANT", 
            font=self.font_titulo, 
            bg=UI_BACKGROUND_COLOR, 
            fg="#FFD700"
        )
        self.label_titulo.pack(pady=(0, 15))
        
        self.crearSeccionFase()
        self.crearSeccionInfoset()
        self.crearSeccionAccionRecomendada()
        self.crearSeccionAccionExacta()
        self.crearSeccionDebug()

    def crearSeccionFase(self):
        frame_fase = tk.Frame(self.frame_principal, bg=UI_BACKGROUND_COLOR)
        frame_fase.pack(fill="x", pady=(0, 10))
        
        tk.Label(
            frame_fase, 
            text="Fase Actual:", 
            font=self.font_accion_categoria, 
            bg=UI_BACKGROUND_COLOR, 
            fg="#CCCCCC"
        ).pack(anchor='w')
        
        self.label_fase_actual = tk.Label(
            frame_fase, 
            text="---", 
            font=self.font_fase, 
            bg=UI_BACKGROUND_COLOR, 
            fg=UI_TEXT_COLOR_ACTION
        )
        self.label_fase_actual.pack(anchor='w', padx=(20, 0))

    def crearSeccionInfoset(self):
        frame_infoset = tk.Frame(self.frame_principal, bg=UI_BACKGROUND_COLOR)
        frame_infoset.pack(fill="x", pady=(0, 10))
        
        tk.Label(
            frame_infoset, 
            text="Infoset Consultado:", 
            font=self.font_accion_categoria, 
            bg=UI_BACKGROUND_COLOR, 
            fg="#CCCCCC"
        ).pack(anchor='w')
        
        self.label_infoset = tk.Label(
            frame_infoset, 
            text="N/A", 
            wraplength=300, 
            font=self.font_infoset, 
            bg="#1E1E1E", 
            fg="#FFD700", 
            justify=tk.LEFT, 
            height=3, 
            relief=tk.SUNKEN, 
            bd=1, 
            anchor='nw', 
            padx=5, 
            pady=5
        )
        self.label_infoset.pack(fill="x", padx=(20, 0))

    def crearSeccionAccionRecomendada(self):
        frame_accion_rec = tk.Frame(self.frame_principal, bg=UI_BACKGROUND_COLOR)
        frame_accion_rec.pack(fill="x", pady=(0, 10))
        
        tk.Label(
            frame_accion_rec, 
            text="Acción Recomendada:", 
            font=self.font_accion_categoria, 
            bg=UI_BACKGROUND_COLOR, 
            fg="#CCCCCC"
        ).pack(anchor='w')
        
        self.label_accion_recomendada = tk.Label(
            frame_accion_rec, 
            text="---", 
            font=self.font_accion_categoria, 
            bg=UI_BACKGROUND_COLOR, 
            fg=UI_TEXT_COLOR_NORMAL
        )
        self.label_accion_recomendada.pack(anchor='w', padx=(20, 0))

    def crearSeccionAccionExacta(self):
        frame_accion_exacta = tk.Frame(self.frame_principal, bg=UI_BACKGROUND_COLOR)
        frame_accion_exacta.pack(fill="x", pady=(0, 15))
        
        tk.Label(
            frame_accion_exacta, 
            text="Acción Exacta:", 
            font=self.font_accion_categoria, 
            bg=UI_BACKGROUND_COLOR, 
            fg="#CCCCCC"
        ).pack(anchor='w')
        
        self.label_accion_exacta = tk.Label(
            frame_accion_exacta, 
            text="---", 
            font=self.font_accion_exacta, 
            bg=UI_BACKGROUND_COLOR, 
            fg=UI_TEXT_COLOR_SUCCESS,
            wraplength=300
        )
        self.label_accion_exacta.pack(anchor='w', padx=(20, 0), pady=(5, 0))
        
        self.label_montos = tk.Label(
            frame_accion_exacta, 
            text="", 
            font=self.font_monto, 
            bg=UI_BACKGROUND_COLOR, 
            fg="#FFD700"
        )
        self.label_montos.pack(anchor='w', padx=(20, 0))

    def crearSeccionDebug(self):
        separador = ttk.Separator(self.frame_principal, orient='horizontal')
        separador.pack(fill="x", pady=(10, 5))
        
        self.label_debug = tk.Label(
            self.frame_principal, 
            text="", 
            font=self.font_debug, 
            bg=UI_BACKGROUND_COLOR, 
            fg="#888888",
            wraplength=300,
            justify=tk.LEFT
        )
        self.label_debug.pack(fill="x")
        
        self.label_status = tk.Label(
            self.frame_principal, 
            text="Iniciando...", 
            font=self.font_debug, 
            bg=UI_BACKGROUND_COLOR, 
            fg="#666666"
        )
        self.label_status.pack(anchor='w', pady=(5, 0))

    def verificarCola(self):
        try:
            while True:
                datos = self.update_queue.get_nowait()
                self.procesarActualizacion(datos)
        except queue.Empty:
            pass
        finally:
            self.after(UI_UPDATE_INTERVAL_MS, self.verificarCola)

    def procesarActualizacion(self, datos: Dict[str, Any]):
        self.ultima_actualizacion = time.time()
        estado = datos.get("estado", "desconocido")
        
        if estado == "no_juego":
            self.mostrarNoJuego()
            self.recomendacion_mostrada = None
        elif estado == "no_principal":
            self.mostrarNoPrincipal(datos)
            self.recomendacion_mostrada = None
        elif estado == "esperando_turno":
            if not self.recomendacion_mostrada:
                self.mostrarEsperandoTurno(datos)
        elif estado == "accion_recomendada":
            self.mostrarAccionRecomendada(datos)
            self.recomendacion_mostrada = datos
        elif estado == "error_infoset":
            self.mostrarErrorInfoset(datos)
            self.recomendacion_mostrada = datos
        elif estado == "error_mccfr":
            self.mostrarErrorMCCFR(datos)
            self.recomendacion_mostrada = None
        else:
            if not self.recomendacion_mostrada:
                self.mostrarEstadoDesconocido(datos)
        
        self.actualizarDebugYStatus(datos)

    def mostrarNoJuego(self):
        self.label_fase_actual.config(text="No detectada", fg="#888888")
        self.label_infoset.config(text="Esperando partida de poker...", fg="#888888")
        self.label_accion_recomendada.config(text="---", fg="#888888")
        self.label_accion_exacta.config(text="---", fg="#888888")
        self.label_montos.config(text="")

    def mostrarNoPrincipal(self, datos: Dict[str, Any]):
        fase = datos.get('fase_actual', 'N/A')
        infoset = datos.get('infoset', 'N/A')
        
        self.label_fase_actual.config(text=fase, fg=UI_TEXT_COLOR_ACTION)
        self.label_infoset.config(text=infoset, fg="#FF6666")  # Rojo para error crítico
        self.label_accion_recomendada.config(text="Sin JugadorPrincipal", fg=UI_TEXT_COLOR_ERROR)
        self.label_accion_exacta.config(text="NO DETECTADO", fg=UI_TEXT_COLOR_ERROR)
        self.label_montos.config(text="")

    def mostrarEsperandoTurno(self, datos: Dict[str, Any]):
        fase = datos.get('fase_actual', 'N/A')
        infoset = datos.get('infoset', 'N/A')
        
        self.label_fase_actual.config(text=fase, fg=UI_TEXT_COLOR_ACTION)
        self.label_infoset.config(text=infoset, fg="#CCCCCC")
        self.label_accion_recomendada.config(text="Esperando turno", fg=UI_TEXT_COLOR_NORMAL)
        self.label_accion_exacta.config(text="ESPERANDO...", fg=UI_TEXT_COLOR_ACTION)
        self.label_montos.config(text="(Turno del oponente)")

    def mostrarAccionRecomendada(self, datos: Dict[str, Any]):
        fase = datos.get("fase_actual", "N/A")
        infoset = datos.get("infoset", "N/A")
        infoset_encontrado = datos.get("infoset_encontrado", False)
        accion_mccfr = datos.get("accion_mccfr", "Check")
        accion_espanol = datos.get("accion_espanol", "Pasar")
        monto_desnormalizado = datos.get("monto")
        monto_normalizado = datos.get("monto_normalizado")
        probabilidad = datos.get("probabilidad")
        
        self.label_fase_actual.config(text=fase, fg=UI_TEXT_COLOR_SUCCESS)
        
        # Verde si encontrado, AMARILLO si no encontrado (cambio principal)
        color_infoset = "#00FF00" if infoset_encontrado else "#FFD700"
        self.label_infoset.config(text=infoset, fg=color_infoset)
        
        texto_categoria = f"{accion_mccfr}"
        if probabilidad is not None:
            texto_categoria += f" (Confianza: {probabilidad:.1%})"
        self.label_accion_recomendada.config(text=texto_categoria, fg=UI_TEXT_COLOR_SUCCESS)
        
        self.label_accion_exacta.config(text=accion_espanol, fg=UI_TEXT_COLOR_SUCCESS)
        
        if monto_desnormalizado is not None and monto_normalizado is not None:
            texto_montos = f"${monto_desnormalizado:.2f} / {monto_normalizado:.0f}BB"
            self.label_montos.config(text=texto_montos)
        else:
            self.label_montos.config(text="")

    def mostrarErrorInfoset(self, datos: Dict[str, Any]):
        fase = datos.get("fase_actual", "N/A")
        infoset = datos.get("infoset", "ERROR")
        
        self.label_fase_actual.config(text=fase, fg="#FFD700")  # Amarillo
        self.label_infoset.config(text=infoset, fg="#FFD700")  # Amarillo (cambio principal)
        self.label_accion_recomendada.config(text="Infoset no encontrado", fg="#FFD700")
        self.label_accion_exacta.config(text="PASAR / NO IR", fg="#FFD700")  # Texto actualizado
        self.label_montos.config(text="(Acción segura)")

    def mostrarErrorMCCFR(self, datos: Dict[str, Any]):
        fase = datos.get("fase_actual", "N/A")
        mensaje = datos.get("mensaje", "Error MCCFR")
        
        self.label_fase_actual.config(text=fase, fg=UI_TEXT_COLOR_ERROR)
        self.label_infoset.config(text="ERROR EN CONSULTA", fg="#FF0000")  # Rojo para error crítico
        self.label_accion_recomendada.config(text="Error del sistema", fg=UI_TEXT_COLOR_ERROR)
        self.label_accion_exacta.config(text="ERROR", fg=UI_TEXT_COLOR_ERROR)
        self.label_montos.config(text="")

    def mostrarEstadoDesconocido(self, datos: Dict[str, Any]):
        self.label_fase_actual.config(text="ERROR", fg=UI_TEXT_COLOR_ERROR)
        self.label_infoset.config(text="Estado desconocido", fg="#FF6666")
        self.label_accion_recomendada.config(text="Error del software", fg=UI_TEXT_COLOR_ERROR)
        self.label_accion_exacta.config(text="ERROR", fg=UI_TEXT_COLOR_ERROR)
        self.label_montos.config(text="")

    def actualizarDebugYStatus(self, datos: Dict[str, Any]):
        debug_info = datos.get('debug_info', '')
        self.label_debug.config(text=debug_info)
        
        tiempo_actual = time.time()
        tiempo_desde_actualizacion = tiempo_actual - self.ultima_actualizacion
        
        if tiempo_desde_actualizacion < 1:
            status_color = "#00FF00"
            status_text = "🟢 Software activo"
        elif tiempo_desde_actualizacion < 5:
            status_color = "#FFD700"
            status_text = "🟡 Funcionando"
        else:
            status_color = "#FF6666"
            status_text = "🔴 Sin actualizaciones"
        
        self.label_status.config(text=status_text, fg=status_color)

    def cerrarAplicacion(self):
        try:
            self.quit()
            self.destroy()
        except:
            pass