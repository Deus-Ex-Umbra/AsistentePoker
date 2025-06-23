import time
import threading
import queue
import json
import copy
import traceback
import numpy as np
from Config import LOOP_DELAY_SECONDS, LABEL_NAMES, MCCFR_QUERY_COOLDOWN_SECONDS
from MCCFRLoader import MCCFRLoader
from CapturadorPantalla import CapturadorPantalla
from DetectorObjetos import DetectorObjetos
from ProcesadorOCR import ProcesadorOCR
from EstadoJuego import EstadoJuego
from TomadorDeDecisiones import TomadorDeDecisiones
from InterfazUsuario import InterfazUsuario
from ListenerTeclado import ListenerTeclado
from UtilidadesDebug import guardar_frame_con_cajas

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NumpyEncoder, self).default(obj)

def main():
    print("Iniciando MCCFR Poker Assistant...")
    
    estado_compartido = {}
    
    cargador_mccfr = MCCFRLoader()
    datos_mccfr = cargador_mccfr.cargar_modelos_en_memoria()
    if not datos_mccfr:
        print("Error: No se pudieron cargar los modelos MCCFR")
        return
    
    capturador = CapturadorPantalla()
    detector = DetectorObjetos()
    ocr = ProcesadorOCR()
    manejador_estado = EstadoJuego(ocr)
    tomador_decisiones = TomadorDeDecisiones(datos_mccfr)
    
    cola_ui = queue.Queue()
    label_map = {i: name for i, name in enumerate(LABEL_NAMES)}
    
    listener_teclado = ListenerTeclado(estado_compartido)
    threading.Thread(target=lambda: InterfazUsuario(cola_ui).mainloop(), daemon=True).start()
    listener_teclado.start()
    
    ultima_data_ui = None
    contador_ciclos = 0
    tiempo_ultima_consulta_mccfr = 0
    
    print("Iniciando bucle principal...")
    print(f"   - Frecuencia de estado: {LOOP_DELAY_SECONDS}s")
    print(f"   - Cooldown de decisión: {MCCFR_QUERY_COOLDOWN_SECONDS}s")
    print("Controles: Q=Salir | P=Pausar | F=Forzar acción\n")
    
    try:
        while estado_compartido.get('running', True):
            if estado_compartido.get('paused', False):
                time.sleep(LOOP_DELAY_SECONDS)
                continue
            
            tiempo_inicio_ciclo = time.time()
            contador_ciclos += 1
            
            frame = capturador.capturar_frame()
            if frame is None:
                time.sleep(LOOP_DELAY_SECONDS)
                continue
            
            resultados_yolo = detector.detectar(frame)
            
            accion_forzada = estado_compartido.get('force_action', False)
            if accion_forzada:
                guardar_frame_con_cajas(frame, resultados_yolo, label_map)
            
            manejador_estado.actualizarDesdeDetecciones(resultados_yolo, frame)
            estado_actual = manejador_estado.obtenerEstadoParaJson()
            
            if contador_ciclos % 20 == 0 and estado_actual:
                print(f"\n--- ESTADO JUEGO (Ciclo {contador_ciclos}) ---")
                print(json.dumps(estado_actual, indent=2, ensure_ascii=False, cls=NumpyEncoder))
                print("-" * 50)
            
            data_ui = None
            es_turno_heroe = manejador_estado.necesitaAccion()

            if estado_actual and (es_turno_heroe or accion_forzada):
                tiempo_actual = time.time()
                if (tiempo_actual - tiempo_ultima_consulta_mccfr > MCCFR_QUERY_COOLDOWN_SECONDS) or accion_forzada:
                    recomendacion = tomador_decisiones.obtenerRecomendacionCompleta(estado_actual)
                    if recomendacion.get('infoset_encontrado', False):
                        data_ui = {"estado": "accion_recomendada", **recomendacion}
                    else:
                        data_ui = {
                            "estado": "accion_recomendada", 
                            **recomendacion
                        }
                        print(f"[MCCFR] Infoset no encontrado: {recomendacion.get('infoset')}. Usando acción segura.")
                    
                    tiempo_ultima_consulta_mccfr = tiempo_actual
                    if accion_forzada:
                        estado_compartido['force_action'] = False

            if not data_ui:
                if not estado_actual:
                    data_ui = {"estado": "no_juego"}
                elif not manejador_estado.hayJugadorPrincipal():
                    data_ui = {
                        "estado": "no_principal",
                        "fase_actual": estado_actual.get('fase_actual', 'N/A'),
                        "infoset": "Sin jugador principal detectado"
                    }
                else:
                    data_ui = {
                        "estado": "esperando_turno", 
                        "fase_actual": estado_actual.get('fase_actual', 'N/A'),
                        "infoset": estado_actual.get("infoset_key", "N/A") if estado_actual else "N/A"
                    }

            if data_ui and data_ui != ultima_data_ui:
                ultima_data_ui = data_ui
                cola_ui.put(copy.deepcopy(data_ui))
            
            tiempo_transcurrido = time.time() - tiempo_inicio_ciclo
            tiempo_espera = max(0, LOOP_DELAY_SECONDS - tiempo_transcurrido)
            time.sleep(tiempo_espera)
            
    except Exception:
        traceback.print_exc()
    finally:
        print("Cerrando software...")
        estado_compartido['running'] = False
        if listener_teclado.is_alive():
            listener_teclado.join(timeout=1)

if __name__ == '__main__':
    main()