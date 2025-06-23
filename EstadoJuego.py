import json
import copy
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from UtilidadesGeometria import UtilidadesGeometria
from UtilidadesTexto import UtilidadesTexto
from Config import LABEL_NAMES, SUIT_MAP, POSICIONES_POR_JUGADORES, CARD_VALUE_MAP

MAPA_ETIQUETAS = {i: name for i, name in enumerate(LABEL_NAMES)}

class Jugador:
    def __init__(self, nombre: str):
        self.nombre = nombre
        self.stack = 0.0
        self.stack_normalizado = 0.0
        self.stack_anterior = 0.0
        self.stack_anterior_normalizado = 0.0
        self.apuesta_actual = 0.0
        self.apuesta_normalizada = 0.0
        self.apuesta_anterior = 0.0
        self.apuesta_anterior_normalizada = 0.0
        self.posicion_relativa = ""
        self.posicion_indice = -1
        self.es_heroe = False
        self.es_turno_actual = False
        self.estado = "no_activo"
        self.estado_anterior = "no_activo"
        self.cartas = []
        self.cartas_persistentes = []
        self.center = (0, 0)
        self.box = (0, 0, 0, 0)
        self.ultima_accion = "Ninguna"
        self.ultima_accion_detectada_frame = 0
        self.es_all_in = False

    def actualizarEstado(self, tipo_jugador: str):
        mapeo_estados = {
            'JugadorPrincipal': 'activo',
            'JugadorActivo': 'activo', 
            'JugadorNoActivo': 'no_activo',
            'JugadorAusente': 'ausente'
        }
        self.estado = mapeo_estados.get(tipo_jugador, 'no_activo')

    def persistirCartas(self, nuevas_cartas: List[str]):
        if len(nuevas_cartas) > len(self.cartas_persistentes):
            self.cartas_persistentes = nuevas_cartas.copy()
        self.cartas = self.cartas_persistentes.copy()

    def toDiccionario(self) -> Dict:
        return {
            "nombre": self.nombre,
            "stack": self.stack,
            "stack_normalizado": self.stack_normalizado,
            "apuesta_actual": self.apuesta_actual,
            "apuesta_normalizada": self.apuesta_normalizada,
            "posicion_relativa": self.posicion_relativa,
            "posicion_indice": self.posicion_indice,
            "es_heroe": self.es_heroe,
            "es_turno_actual": self.es_turno_actual,
            "estado": self.estado,
            "cartas": self.cartas,
            "ultima_accion": self.ultima_accion,
            "es_all_in": self.es_all_in
        }

class Fase:
    def __init__(self, nombre_fase: str):
        self.nombre_fase = nombre_fase
        self.jugadores = {}
        self.bote_total = 0.0
        self.bote_total_normalizado = 0.0
        self.bote_apuesta = 0.0
        self.bote_apuesta_normalizado = 0.0
        self.cartas_comunitarias = []
        self.cartas_comunitarias_persistentes = []
        self.acciones_realizadas = []
        self.dealer_position = -1
        self.sb_actual = 0.05
        self.bb_actual = 0.10
        self.tiene_ante = False
        self.posiciones_determinadas = False
        self.numero_jugadores_mesa = 0
        self.numero_apuestas_detectadas = 0
        self.coordenadas_apuestas = {}
        self.apuesta_mas_alta = 0.0
        self.apuesta_mas_alta_normalizada = 0.0
        self.ultimo_frame_procesado = 0
        
        # NUEVO: Historial de raises para contexto
        self.historial_raises = []  # Lista de (jugador, monto_normalizado, tipo_raise)
        self.bote_antes_ultima_apuesta = 0.0
        self.bote_antes_ultima_apuesta_norm = 0.0

    def agregarAccion(self, nombre_jugador: str, accion: str, monto: float = 0.0):
        self.acciones_realizadas.append((nombre_jugador, accion, monto))
        
        # Guardar contexto de raises
        if "Raise" in accion and nombre_jugador in self.jugadores:
            jugador = self.jugadores[nombre_jugador]
            self.historial_raises.append({
                "jugador": nombre_jugador,
                "monto_norm": jugador.apuesta_normalizada,
                "tipo": accion,
                "bote_previo_norm": self.bote_antes_ultima_apuesta_norm
            })

    def obtenerUltimaAccion(self, excluir_heroe: str = "") -> str:
        """Obtiene la última acción realizada antes del turno del héroe EN ESTA FASE"""
        if not self.acciones_realizadas:
            return "Ninguna"
        
        # En PreFlop, verificar si ha habido acciones reales o solo ciegas
        if self.nombre_fase == "PreFlop":
            # Si no hay acciones registradas, es porque solo hay ciegas
            acciones_reales = [a for _, a, _ in self.acciones_realizadas if a not in ["Ninguna"]]
            if not acciones_reales:
                return "Ninguna"
        
        # Filtrar acciones del héroe y acciones "Ninguna"
        acciones_validas = [
            (nombre, accion, monto) for nombre, accion, monto in self.acciones_realizadas
            if nombre != excluir_heroe and accion != "Ninguna"
        ]
        
        if not acciones_validas:
            return "Ninguna"
        
        # Si hay jugadores ordenados por posición, usar ese orden
        jugadores_activos = [j for j in self.jugadores.values() if j.estado == 'activo']
        if len(jugadores_activos) >= 2 and self.posiciones_determinadas:
            # Ordenar jugadores por posición
            jugadores_ordenados = sorted(jugadores_activos, key=lambda j: j.posicion_indice)
            
            # Encontrar la posición del héroe
            heroe = next((j for j in jugadores_ordenados if j.es_heroe), None)
            if heroe:
                pos_heroe = jugadores_ordenados.index(heroe)
                
                # Buscar la última acción del jugador inmediatamente anterior
                for i in range(pos_heroe - 1, -1, -1):
                    jugador_anterior = jugadores_ordenados[i]
                    # Buscar su última acción en el historial
                    for nombre, accion, monto in reversed(acciones_validas):
                        if nombre == jugador_anterior.nombre:
                            return accion
        
        # Si no encontramos una acción específica del jugador anterior,
        # devolver la última acción general
        return acciones_validas[-1][1]

    def obtenerMaximaApuesta(self) -> float:
        if not self.jugadores:
            return 0.0
        return max(j.apuesta_actual for j in self.jugadores.values())

    def obtenerMaximaApuestaNormalizada(self) -> float:
        if not self.jugadores:
            return 0.0
        return max(j.apuesta_normalizada for j in self.jugadores.values())

    def persistirCartasComunitarias(self, nuevas_cartas: List[str]):
        if len(nuevas_cartas) > len(self.cartas_comunitarias_persistentes):
            self.cartas_comunitarias_persistentes = nuevas_cartas.copy()
        self.cartas_comunitarias = self.cartas_comunitarias_persistentes.copy()

    def obtenerHistorialAccionesFormateado(self) -> str:
        """Obtiene un historial formateado de las acciones para debug"""
        if not self.acciones_realizadas:
            return "Sin acciones"
        
        acciones_str = []
        for nombre, accion, monto in self.acciones_realizadas:
            if monto > 0:
                acciones_str.append(f"{nombre}:{accion}(${monto:.2f})")
            else:
                acciones_str.append(f"{nombre}:{accion}")
        
        return " -> ".join(acciones_str)

class EstadoJuego:
    def __init__(self, ocr_processor):
        self.procesador_ocr = ocr_processor
        self.fase_actual = None
        self.fase_anterior = None
        self.id_mano_actual = 1
        self.historial_fases = []
        self.nombre_heroe = ""
        self.secuencia_fases = ['PreFlop', 'Flop', 'Turn', 'River', 'Showdown']
        self.cartas_comunitarias_cache = []
        self.cambio_detectado = False
        self.apuestas_totales_anteriores = 0

    def obtenerIndiceFase(self, nombre_fase: str) -> int:
        try:
            return self.secuencia_fases.index(nombre_fase)
        except ValueError:
            return -1

    def extraerDetecciones(self, resultados_yolo: List[Any], frame: Any) -> Dict[str, List[Dict]]:
        detecciones = {name: [] for name in LABEL_NAMES}
        if not resultados_yolo: 
            return detecciones
        
        result = resultados_yolo[0]
        boxes = result.boxes.xyxy.cpu().numpy()
        classes = result.boxes.cls.cpu().numpy()
        
        for box, cls_id in zip(boxes, classes):
            etiqueta = MAPA_ETIQUETAS.get(int(cls_id))
            if etiqueta:
                caja_segura = tuple(map(int, box))
                detecciones[etiqueta].append({
                    "box": caja_segura, 
                    "center": UtilidadesGeometria.get_center(caja_segura), 
                    "crop": frame[caja_segura[1]:caja_segura[3], caja_segura[0]:caja_segura[2]]
                })
        return detecciones

    def parsearCartaDeComponentes(self, deteccion_valor: Dict, deteccion_palo: Dict) -> Optional[str]:
        texto_valor = self.procesador_ocr.get_text_from_image(deteccion_valor['crop'], es_valor_carta=True)
        etiqueta_palo = deteccion_palo['label']
        valor = UtilidadesTexto.clean_card_value(texto_valor)
        palo = SUIT_MAP.get(etiqueta_palo)
        if valor and palo:
            return f"{valor}{palo}"
        return None

    def identificarCartasEnCajas(self, cajas_cartas: List[Dict], todas_detecciones: Dict) -> List[str]:
        cartas = []
        for caja_carta in cajas_cartas:
            valores_dentro = [
                v for v in todas_detecciones.get('ValorCarta', []) 
                if UtilidadesGeometria.is_contained(v['box'], caja_carta['box'])
            ]
            palos_dentro = []
            for nombre_palo in SUIT_MAP.keys():
                for p in todas_detecciones.get(nombre_palo, []):
                    if UtilidadesGeometria.is_contained(p['box'], caja_carta['box']):
                        palos_dentro.append({'label': nombre_palo, 'det': p})
            
            if valores_dentro and palos_dentro:
                carta_str = self.parsearCartaDeComponentes(valores_dentro[0], palos_dentro[0])
                if carta_str:
                    cartas.append(carta_str)
        return sorted(list(set(cartas)))

    def determinarCiegasYNormalizacion(self, detecciones: Dict, nombre_fase: str):
        if not self.fase_actual or nombre_fase != 'PreFlop':
            return
        
        apuestas_detectadas = []
        for deteccion_apuesta in detecciones.get('Apuesta', []):
            texto_apuesta = self.procesador_ocr.get_text_from_image(deteccion_apuesta['crop'])
            valor_apuesta = UtilidadesTexto.clean_monetary_value(texto_apuesta)
            if valor_apuesta is not None and valor_apuesta > 0:
                apuestas_detectadas.append(valor_apuesta)
        
        self.fase_actual.tiene_ante = bool(detecciones.get('BoteApuesta') and nombre_fase == 'PreFlop')
        
        if len(apuestas_detectadas) >= 2:
            apuestas_ordenadas = sorted(apuestas_detectadas)
            self.fase_actual.sb_actual = apuestas_ordenadas[0]
            self.fase_actual.bb_actual = apuestas_ordenadas[1]
        elif len(apuestas_detectadas) == 1:
            apuesta_unica = apuestas_detectadas[0]
            if self.fase_actual.bb_actual > 0:
                if abs(apuesta_unica - self.fase_actual.sb_actual) > abs(apuesta_unica - self.fase_actual.bb_actual):
                    self.fase_actual.bb_actual = apuesta_unica
            else:
                self.fase_actual.bb_actual = apuesta_unica
        
        if self.fase_actual.bb_actual < 0.01:
            self.fase_actual.bb_actual = 0.10

    def normalizarEnBB(self, valor: float) -> float:
        if not self.fase_actual or self.fase_actual.bb_actual <= 0:
            return valor
        return round(valor / self.fase_actual.bb_actual, 2)

    def obtenerCartasComunitariasPorFase(self, detecciones: Dict, nombre_fase: str) -> List[str]:
        cartas_detectadas = self.identificarCartasEnCajas(
            detecciones.get('CartaComunitaria', []), detecciones
        )
        
        if not self.fase_actual:
            return []
        
        self.fase_actual.persistirCartasComunitarias(cartas_detectadas)
        
        if nombre_fase == 'PreFlop':
            return []
        
        cartas_esperadas_map = {'Flop': 3, 'Turn': 4, 'River': 5}
        if nombre_fase in cartas_esperadas_map:
            num_esperadas = cartas_esperadas_map[nombre_fase]
            cartas_disponibles = self.fase_actual.cartas_comunitarias_persistentes
            if len(cartas_disponibles) >= num_esperadas:
                return cartas_disponibles[:num_esperadas]
        
        return self.fase_actual.cartas_comunitarias_persistentes

    def clasificarTipoRaise(self, jugador_que_actua: str, apuesta_nueva: float, detecciones: Dict) -> str:
        if not self.fase_actual:
            return "Raise Min"
        
        bb = 1.0  # En valores normalizados
        jugador_actual = self.fase_actual.jugadores.get(jugador_que_actua)
        if not jugador_actual:
            return "Raise Min"
            
        apuesta_nueva_normalizada = jugador_actual.apuesta_normalizada
        
        # Obtener apuestas normalizadas de otros jugadores
        otras_apuestas_norm = [
            j.apuesta_normalizada for nombre, j in self.fase_actual.jugadores.items() 
            if nombre != jugador_que_actua and j.apuesta_normalizada > 0
        ]
        max_apuesta_previa_norm = max(otras_apuestas_norm) if otras_apuestas_norm else 0.0
        
        monto_a_igualar_norm = max_apuesta_previa_norm
        monto_subida_norm = apuesta_nueva_normalizada - monto_a_igualar_norm
        
        # Verificar si es All-In primero
        if jugador_actual.stack_normalizado < 0.1 or jugador_actual.es_all_in:
            return "All-In"
        
        # Si detectamos texto All-In en AccionPoker
        texto_accion = self.extraerTextoAccionPoker(jugador_actual, detecciones)
        if texto_accion and 'all' in texto_accion.lower():
            return "All-In"
        
        # Verificar si es solo un Call
        if monto_subida_norm < 0.1:
            return "Call"
        
        print(f"\n[CLASIFICAR_RAISE] {jugador_que_actua}:")
        print(f"  - Apuesta nueva: {apuesta_nueva_normalizada:.2f} BB")
        print(f"  - Max apuesta previa: {max_apuesta_previa_norm:.2f} BB")
        print(f"  - Monto subida: {monto_subida_norm:.2f} BB")
        
        # IMPORTANTE: En PreFlop, si es el primer raise (sobre BB), tiene reglas especiales
        if self.fase_actual.nombre_fase == "PreFlop":
            # Verificar si es el primer raise real (no ciegas)
            raises_reales = [a for _, a, _ in self.fase_actual.acciones_realizadas if "Raise" in a]
            
            if not raises_reales:  # Es el primer raise
                # Un open raise estándar en PreFlop
                if max_apuesta_previa_norm <= 1.0:  # Solo hay BB o menos
                    # Open raise típicos
                    if 1.8 <= apuesta_nueva_normalizada <= 2.5:
                        return "Raise Min"  # 2-2.5x BB es estándar
                    elif 2.5 < apuesta_nueva_normalizada <= 3.5:
                        return "Raise x3"  # 3x BB
                    # Si es más grande, continuar con la lógica de porcentajes
        
        # NUEVO: Verificar si es x2 o x3 de algún raise anterior
        if self.fase_actual.historial_raises:
            print(f"  - Historial raises: {len(self.fase_actual.historial_raises)}")
            
            # Buscar el último raise significativo
            for raise_previo in reversed(self.fase_actual.historial_raises):
                monto_previo_norm = raise_previo["monto_norm"]
                if monto_previo_norm > 0:
                    ratio = apuesta_nueva_normalizada / monto_previo_norm
                    print(f"  - Comparando con raise previo: {monto_previo_norm:.2f} BB, ratio: {ratio:.2f}")
                    
                    # Verificar x2 con tolerancia
                    if 1.8 <= ratio <= 2.2:
                        return "Raise x2"
                    # Verificar x3 con tolerancia
                    elif 2.7 <= ratio <= 3.3:
                        return "Raise x3"
        
        # Si no es x2 o x3, verificar Raise Min
        if self.fase_actual.nombre_fase == "PreFlop":
            # En PreFlop sin raises previos, min es 2BB
            if not any("Raise" in a for _, a, _ in self.fase_actual.acciones_realizadas):
                if abs(apuesta_nueva_normalizada - 2.0) < 0.3:
                    return "Raise Min"
        
        # Para re-raises, calcular el min raise
        if self.fase_actual.historial_raises:
            # El min raise es la apuesta anterior + la última subida
            if len(self.fase_actual.historial_raises) >= 2:
                ultima_subida = self.fase_actual.historial_raises[-1]["monto_norm"] - self.fase_actual.historial_raises[-2]["monto_norm"]
                raise_min_norm = max_apuesta_previa_norm + max(ultima_subida, 1.0)
            else:
                raise_min_norm = max_apuesta_previa_norm + 1.0
            
            if abs(apuesta_nueva_normalizada - raise_min_norm) < 0.3:
                return "Raise Min"
        
        # Calcular porcentajes del bote ANTES de la apuesta actual
        bote_previo_norm = self.fase_actual.bote_antes_ultima_apuesta_norm
        if bote_previo_norm <= 0:
            # Si no tenemos el bote previo guardado, estimarlo
            bote_previo_norm = self.fase_actual.bote_total_normalizado + self.fase_actual.bote_apuesta_normalizado
            # Restar las apuestas actuales
            for j in self.fase_actual.jugadores.values():
                if j.nombre != jugador_que_actua:
                    bote_previo_norm += j.apuesta_normalizada
        
        print(f"  - Bote antes de la apuesta: {bote_previo_norm:.2f} BB")
        
        if bote_previo_norm > 0:
            ratio_bote = monto_subida_norm / bote_previo_norm
            print(f"  - Ratio sobre bote previo: {ratio_bote:.2%}")
            
            if ratio_bote < 0.4:
                return "Raise 33%"
            elif ratio_bote < 0.6:
                return "Raise 50%"
            elif ratio_bote < 0.85:
                return "Raise 75%"
            elif ratio_bote < 1.2:
                return "Raise 100%"
            elif ratio_bote < 1.7:
                return "Raise 150%"
            elif ratio_bote < 2.2:
                return "Raise 200%"
            elif ratio_bote < 2.7:
                return "Raise 250%"
            else:
                return "Raise 300%"
        
        return "Raise Min"

    def actualizarJugador(self, jugador: Jugador, deteccion_jugador: Dict, detecciones: Dict, tipo_jugador: str):
        # Guardar estado anterior
        jugador.estado_anterior = jugador.estado
        jugador.stack_anterior = jugador.stack
        jugador.stack_anterior_normalizado = jugador.stack_normalizado
        jugador.apuesta_anterior = jugador.apuesta_actual
        jugador.apuesta_anterior_normalizada = jugador.apuesta_normalizada
        
        # Actualizar estado actual
        jugador.actualizarEstado(tipo_jugador)
        jugador.center = deteccion_jugador['center']
        jugador.box = deteccion_jugador['box']
        
        # Actualizar stack
        texto_stack = next(
            (self.procesador_ocr.get_text_from_image(s['crop']) 
             for s in detecciones.get('Stack', []) 
             if UtilidadesGeometria.is_contained(s['box'], deteccion_jugador['box'])), 
            None
        )
        if texto_stack:
            valor_stack = UtilidadesTexto.clean_monetary_value(texto_stack)
            if valor_stack is not None:
                jugador.stack = valor_stack
                jugador.stack_normalizado = self.normalizarEnBB(valor_stack)
                # Detectar All-In por stack muy bajo
                if jugador.stack_normalizado < 0.1 and jugador.apuesta_actual > 0:
                    jugador.es_all_in = True
            
            # Detectar All-In por texto en el stack
            if UtilidadesTexto.detectarStackAllIn(texto_stack):
                jugador.es_all_in = True
        
        # Actualizar apuesta
        texto_apuesta = next(
            (self.procesador_ocr.get_text_from_image(a['crop']) 
             for a in detecciones.get('Apuesta', []) 
             if UtilidadesGeometria.euclidean_distance(a['center'], deteccion_jugador['center']) < 150), 
            None
        )
        valor_apuesta = UtilidadesTexto.clean_monetary_value(texto_apuesta) if texto_apuesta else 0.0
        jugador.apuesta_actual = valor_apuesta or 0.0
        jugador.apuesta_normalizada = self.normalizarEnBB(jugador.apuesta_actual)
        
        # Detectar turno actual
        jugador.es_turno_actual = any(
            UtilidadesGeometria.get_iou(t['box'], deteccion_jugador['box']) > 0.1 
            for t in detecciones.get('TurnoActual', [])
        )
        
        # Actualizar cartas del héroe
        if tipo_jugador == 'JugadorPrincipal':
            jugador.es_heroe = True
            self.nombre_heroe = jugador.nombre
            cajas_cartas_jugador = [
                c for c in detecciones.get('CartaJugador', []) 
                if UtilidadesGeometria.is_contained(c['box'], deteccion_jugador['box'], 0.7)
            ]
            cartas_detectadas = self.identificarCartasEnCajas(cajas_cartas_jugador, detecciones)
            jugador.persistirCartas(cartas_detectadas)
        else:
            jugador.es_heroe = False

    def determinarPosiciones(self, jugadores_activos: List[Jugador], centro_dealer: Optional[Tuple[int, int]]):
        num_jugadores = len(jugadores_activos)
        if num_jugadores < 2:
            return
            
        jugadores_ordenados = UtilidadesGeometria.ordenar_jugadores_sentido_horario([
            {"jugador": j, "center": j.center} for j in jugadores_activos
        ])
        
        posiciones_disponibles = POSICIONES_POR_JUGADORES.get(num_jugadores)
        if not posiciones_disponibles:
            return
        
        dealer_idx = 0
        if centro_dealer:
            distancias_dealer = [
                UtilidadesGeometria.euclidean_distance(item["center"], centro_dealer) 
                for item in jugadores_ordenados
            ]
            dealer_idx = np.argmin(distancias_dealer)
        
        self.fase_actual.dealer_position = dealer_idx
        
        for i, item in enumerate(jugadores_ordenados):
            jugador = item["jugador"]
            if num_jugadores == 2:
                if i == dealer_idx:
                    posicion_relativa = "SB"
                    posicion_indice = 0
                else:
                    posicion_relativa = "BB"
                    posicion_indice = 1
            else:
                pos_index = (i - dealer_idx + num_jugadores) % num_jugadores
                posicion_relativa = posiciones_disponibles[pos_index]
                posicion_indice = pos_index
                
            jugador.posicion_relativa = posicion_relativa
            jugador.posicion_indice = posicion_indice
        
        self.fase_actual.posiciones_determinadas = True

    def detectarAcciones(self, detecciones: Dict):
        if not self.fase_actual:
            return
        
        # En PreFlop, verificar si solo hay ciegas
        es_solo_ciegas = False
        if self.fase_actual.nombre_fase == "PreFlop":
            apuestas_activas = sum(1 for j in self.fase_actual.jugadores.values() 
                                 if j.apuesta_actual > 0)
            es_solo_ciegas = apuestas_activas <= 2
            
            # Si no hay acciones registradas y solo hay ciegas, no procesar
            if es_solo_ciegas and not self.fase_actual.acciones_realizadas and not detecciones.get('AccionPoker'):
                print("[PREFLOP] Solo ciegas detectadas, esperando primera acción real")
                return
        
        # Guardar el estado del bote antes de procesar nuevas acciones
        self.fase_actual.bote_antes_ultima_apuesta = self.fase_actual.bote_total
        self.fase_actual.bote_antes_ultima_apuesta_norm = self.fase_actual.bote_total_normalizado
        
        # 1. Detectar acciones desde las etiquetas AccionPoker de YOLO
        for deteccion_accion in detecciones.get('AccionPoker', []):
            # Encontrar el jugador más cercano a esta acción
            jugador_cercano = None
            distancia_minima = float('inf')
            
            for nombre, jugador in self.fase_actual.jugadores.items():
                # Verificar si la acción está dentro del box del jugador
                if UtilidadesGeometria.is_contained(deteccion_accion['box'], jugador.box, 0.5):
                    jugador_cercano = nombre
                    break
                # O si está muy cerca del jugador
                distancia = UtilidadesGeometria.euclidean_distance(
                    deteccion_accion['center'], jugador.center
                )
                if distancia < distancia_minima and distancia < 200:
                    distancia_minima = distancia
                    jugador_cercano = nombre
            
            if jugador_cercano:
                # Extraer el texto de la acción
                texto_accion = self.procesador_ocr.procesar_accion_poker(deteccion_accion['crop'])
                if texto_accion:
                    print(f"[ACCION_DETECTADA] {jugador_cercano}: {texto_accion}")
                    # Verificar si esta acción ya fue registrada
                    if not self._accionYaRegistrada(jugador_cercano, texto_accion):
                        self._procesarNuevaAccion(jugador_cercano, texto_accion, detecciones)
        
        # 2. Detectar cambios en apuestas (para Raises)
        self._detectarCambiosApuestas(detecciones)
        
        # 3. Detectar Folds por ausencia de jugadores activos
        self._detectarFoldsPorEstado(detecciones)
        
        # 4. Detectar All-Ins por stack 0
        self._detectarAllIns()

    def _detectarAllIns(self):
        """Detecta All-Ins por jugadores con stack muy bajo o apuesta igual al stack"""
        # En PreFlop, verificar si solo hay ciegas
        if self.fase_actual.nombre_fase == "PreFlop":
            apuestas_activas = sum(1 for j in self.fase_actual.jugadores.values() 
                                 if j.apuesta_actual > 0)
            if apuestas_activas <= 2 and not self.fase_actual.acciones_realizadas:
                return  # No procesar All-Ins cuando solo hay ciegas
        
        for nombre, jugador in self.fase_actual.jugadores.items():
            if jugador.estado != 'activo':
                continue
            
            # Si el jugador tiene stack 0 o muy bajo y tiene apuesta
            if (jugador.stack_normalizado < 0.1 or jugador.es_all_in) and jugador.apuesta_normalizada > 0:
                if not self._accionYaRegistrada(nombre, "All-In"):
                    jugador.es_all_in = True
                    self.fase_actual.agregarAccion(nombre, "All-In", jugador.apuesta_actual)
                    jugador.ultima_accion = "All-In"
                    self.cambio_detectado = True
                    print(f"[ALL-IN_DETECTADO] {nombre} está All-In (stack: {jugador.stack_normalizado:.2f} BB)")

    def _accionYaRegistrada(self, jugador: str, accion: str) -> bool:
        """Verifica si la acción ya fue registrada para evitar duplicados"""
        if not self.fase_actual.acciones_realizadas:
            return False
        
        # Para All-In, verificar en todo el historial de la fase
        if accion == "All-In":
            for nombre_j, accion_j, _ in self.fase_actual.acciones_realizadas:
                if nombre_j == jugador and accion_j == "All-In":
                    return True
            return False
        
        # Para otras acciones, verificar las últimas 3
        ultimas_acciones = self.fase_actual.acciones_realizadas[-3:] if len(self.fase_actual.acciones_realizadas) >= 3 else self.fase_actual.acciones_realizadas
        
        for nombre_j, accion_j, _ in ultimas_acciones:
            if nombre_j == jugador and accion_j == accion:
                return True
        return False

    def _procesarNuevaAccion(self, jugador: str, accion: str, detecciones: Dict):
        """Procesa y registra una nueva acción detectada"""
        jugador_obj = self.fase_actual.jugadores.get(jugador)
        if not jugador_obj:
            return
        
        # IMPORTANTE: Detectar All-In específicamente
        if accion == "All-In" or (accion and "all" in accion.lower() and "in" in accion.lower()):
            jugador_obj.es_all_in = True
            self.fase_actual.agregarAccion(jugador, "All-In", jugador_obj.apuesta_actual)
            jugador_obj.ultima_accion = "All-In"
            self.cambio_detectado = True
            print(f"[ACCION_REGISTRADA] {jugador} -> All-In (detectado por texto)")
            return
        
        # Para acciones de Raise, necesitamos determinar el monto y tipo
        if accion == "Raise" or "Raise" in accion:
            # Buscar la apuesta actual del jugador
            apuesta_actual = jugador_obj.apuesta_actual
            if apuesta_actual > 0:
                tipo_raise = self.clasificarTipoRaise(jugador, apuesta_actual, detecciones)
                self.fase_actual.agregarAccion(jugador, tipo_raise, apuesta_actual)
                jugador_obj.ultima_accion = tipo_raise
            else:
                # Si no hay apuesta visible, registrar como Raise genérico
                self.fase_actual.agregarAccion(jugador, "Raise Min", 0)
                jugador_obj.ultima_accion = "Raise Min"
        else:
            # Para otras acciones (Fold, Check, Call)
            self.fase_actual.agregarAccion(jugador, accion, jugador_obj.apuesta_actual)
            jugador_obj.ultima_accion = accion
        
        self.cambio_detectado = True
        print(f"[ACCION_REGISTRADA] {jugador} -> {jugador_obj.ultima_accion}")

    def _detectarCambiosApuestas(self, detecciones: Dict):
        """Detecta cambios en las apuestas para identificar Raises y Calls"""
        # IMPORTANTE: En PreFlop, no detectar las ciegas como acciones
        if self.fase_actual.nombre_fase == "PreFlop":
            # Contar apuestas actuales
            apuestas_activas = sum(1 for j in self.fase_actual.jugadores.values() 
                                 if j.apuesta_actual > 0)
            
            # Si hay 2 o menos apuestas en PreFlop, son solo las ciegas
            if apuestas_activas <= 2:
                print("[PREFLOP] Detectadas solo ciegas, no registrando acciones")
                return
        
        for nombre, jugador in self.fase_actual.jugadores.items():
            if jugador.es_heroe:
                continue
                
            # Si la apuesta cambió significativamente (en valores normalizados)
            cambio_apuesta_norm = abs(jugador.apuesta_normalizada - jugador.apuesta_anterior_normalizada)
            if cambio_apuesta_norm > 0.1:  # Más de 0.1 BB de cambio
                # Verificar si es un Call o Raise
                max_apuesta_otros_norm = max(
                    (j.apuesta_normalizada for n, j in self.fase_actual.jugadores.items() 
                     if n != nombre and j.apuesta_normalizada > 0),
                    default=0
                )
                
                # Verificar si el jugador está All-In
                if jugador.stack_normalizado < 0.1 or jugador.es_all_in:
                    if not self._accionYaRegistrada(nombre, "All-In"):
                        self.fase_actual.agregarAccion(nombre, "All-In", jugador.apuesta_actual)
                        jugador.ultima_accion = "All-In"
                        jugador.es_all_in = True
                        self.cambio_detectado = True
                        print(f"[ALL-IN_DETECTADO] {nombre} -> All-In por apuesta")
                        continue
                
                # En PreFlop, verificar si es una acción real o solo ciegas
                if self.fase_actual.nombre_fase == "PreFlop" and not self.fase_actual.acciones_realizadas:
                    # Es la primera acción real después de las ciegas
                    print(f"[PREFLOP] Primera acción real detectada de {nombre}")
                
                if not self._accionYaRegistrada(nombre, "Call") and not self._accionYaRegistrada(nombre, "Raise"):
                    if abs(jugador.apuesta_normalizada - max_apuesta_otros_norm) < 0.2:  # 0.2 BB de tolerancia
                        # Es un Call
                        self.fase_actual.agregarAccion(nombre, "Call", jugador.apuesta_actual)
                        jugador.ultima_accion = "Call"
                        self.cambio_detectado = True
                        print(f"[CALL_DETECTADO] {nombre} igualó a ${jugador.apuesta_actual} ({jugador.apuesta_normalizada:.2f} BB)")
                    elif jugador.apuesta_normalizada > max_apuesta_otros_norm:
                        # Es un Raise
                        tipo_raise = self.clasificarTipoRaise(nombre, jugador.apuesta_actual, detecciones)
                        self.fase_actual.agregarAccion(nombre, tipo_raise, jugador.apuesta_actual)
                        jugador.ultima_accion = tipo_raise
                        self.cambio_detectado = True
                        print(f"[RAISE_DETECTADO] {nombre} -> {tipo_raise} a ${jugador.apuesta_actual} ({jugador.apuesta_normalizada:.2f} BB)")

    def _detectarFoldsPorEstado(self, detecciones: Dict):
        """Detecta Folds cuando un jugador cambia de activo a no activo"""
        # En PreFlop, ser más cuidadoso con la detección de Folds
        if self.fase_actual.nombre_fase == "PreFlop":
            # Si no ha habido acciones reales, no detectar Folds
            if not self.fase_actual.acciones_realizadas:
                return
        
        for nombre, jugador in self.fase_actual.jugadores.items():
            if jugador.es_heroe:
                continue
                
            # Si el jugador estaba activo en la fase anterior pero ahora no
            if jugador.estado_anterior == 'activo' and jugador.estado == 'no_activo':
                if not self._accionYaRegistrada(nombre, "Fold"):
                    self.fase_actual.agregarAccion(nombre, "Fold", 0)
                    jugador.ultima_accion = "Fold"
                    self.cambio_detectado = True
                    print(f"[FOLD_DETECTADO] {nombre} se retiró")

    def extraerTextoAccionPoker(self, jugador: Jugador, detecciones: Dict) -> Optional[str]:
        for deteccion_accion in detecciones.get('AccionPoker', []):
            if UtilidadesGeometria.is_contained(deteccion_accion['box'], jugador.box):
                return self.procesador_ocr.get_text_from_image(deteccion_accion['crop'])
        return None

    def detectarCambioSignificativo(self, detecciones: Dict) -> bool:
        apuestas_actuales = len(detecciones.get('Apuesta', []))
        cambio_apuestas = apuestas_actuales != self.apuestas_totales_anteriores
        
        if self.fase_anterior and self.fase_actual:
            if self.fase_anterior.nombre_fase != self.fase_actual.nombre_fase:
                self.cambio_detectado = True
                return True
        
        return cambio_apuestas

    def debeLimpiarRecomendacion(self) -> bool:
        if not self.fase_actual:
            return True
            
        heroe = next((j for j in self.fase_actual.jugadores.values() if j.es_heroe), None)
        if not heroe:
            return True
            
        for _, accion, _ in self.fase_actual.acciones_realizadas:
            if accion == "All-In":
                return True
        
        return False

    def actualizarDesdeDetecciones(self, resultados_yolo: List[Any], frame: Any):
        self.fase_anterior = copy.deepcopy(self.fase_actual)
        detecciones = self.extraerDetecciones(resultados_yolo, frame)
        
        if not detecciones.get('Principal'):
            self.fase_actual = None
            return

        todas_etiquetas_fase = self.secuencia_fases + ['Espera']
        etiqueta_fase_detectada = next(
            (p for p in todas_etiquetas_fase if detecciones.get(p)), None
        )
        
        nombre_fase = "Espera"
        cambio_de_fase = False
        
        if etiqueta_fase_detectada:
            if etiqueta_fase_detectada == 'Espera':
                if self.fase_actual and self.fase_actual.nombre_fase != 'Espera':
                    self.iniciarNuevaMano()
                nombre_fase = 'Espera'
            elif etiqueta_fase_detectada != 'Espera':
                indice_fase_actual = -1
                if self.fase_actual:
                    indice_fase_actual = self.obtenerIndiceFase(self.fase_actual.nombre_fase)
                indice_fase_detectada = self.obtenerIndiceFase(etiqueta_fase_detectada)
                
                if indice_fase_detectada > indice_fase_actual:
                    nombre_fase = etiqueta_fase_detectada
                    self.cambio_detectado = True
                    cambio_de_fase = True
                elif self.fase_actual:
                    nombre_fase = self.fase_actual.nombre_fase
                else:
                    nombre_fase = etiqueta_fase_detectada

        if len(detecciones.get('TurnoActual', [])) > 1:
            nombre_fase = 'Espera'

        if not self.fase_actual or self.fase_actual.nombre_fase != nombre_fase:
            nueva_fase = Fase(nombre_fase)
            if self.fase_actual:
                nueva_fase.jugadores = copy.deepcopy(self.fase_actual.jugadores)
                nueva_fase.bb_actual = self.fase_actual.bb_actual
                nueva_fase.sb_actual = self.fase_actual.sb_actual
                nueva_fase.dealer_position = self.fase_actual.dealer_position
                nueva_fase.posiciones_determinadas = self.fase_actual.posiciones_determinadas
                nueva_fase.numero_jugadores_mesa = self.fase_actual.numero_jugadores_mesa
                
                # Limpiar acciones de jugadores al cambiar de fase
                if cambio_de_fase:
                    for jugador in nueva_fase.jugadores.values():
                        jugador.ultima_accion = "Ninguna"
                        jugador.apuesta_anterior = 0.0
                        jugador.apuesta_anterior_normalizada = 0.0
                        jugador.es_all_in = False
                    print(f"\n[CAMBIO_FASE] {self.fase_actual.nombre_fase} -> {nombre_fase}")
                    print("[CAMBIO_FASE] Reiniciando historial de acciones")
                    
            self.fase_actual = nueva_fase

        self.detectarCambioSignificativo(detecciones)
        self.determinarCiegasYNormalizacion(detecciones, nombre_fase)
        
        tipos_jugador = ['JugadorPrincipal', 'JugadorActivo', 'JugadorNoActivo', 'JugadorAusente']
        jugadores_activos_detectados = []
        
        for tipo in tipos_jugador:
            for deteccion_jugador in detecciones.get(tipo, []):
                nombre = self.obtenerNombreJugador(deteccion_jugador, detecciones)
                
                if nombre not in self.fase_actual.jugadores:
                    self.fase_actual.jugadores[nombre] = Jugador(nombre)
                
                jugador = self.fase_actual.jugadores[nombre]
                self.actualizarJugador(jugador, deteccion_jugador, detecciones, tipo)
                
                if jugador.estado == 'activo':
                    jugadores_activos_detectados.append(jugador)

        if nombre_fase == 'PreFlop' or not self.fase_actual.posiciones_determinadas:
            self.fase_actual.numero_jugadores_mesa = len(jugadores_activos_detectados)
            if self.fase_actual.numero_jugadores_mesa >= 2:
                centro_dealer = detecciones['BotonDealer'][0]['center'] if detecciones.get('BotonDealer') else None
                self.determinarPosiciones(jugadores_activos_detectados, centro_dealer)
        
        # Construir estado actual al final, que incluye detectar acciones
        self.construirEstadoActual(detecciones, nombre_fase)
        self.validarYLimpiarAcciones()

    def iniciarNuevaMano(self):
        self.id_mano_actual += 1
        if self.fase_actual:
            self.historial_fases.append(self.fase_actual)
        self.fase_actual = None
        self.cartas_comunitarias_cache = []
        self.cambio_detectado = True
        self.apuestas_totales_anteriores = 0

    def obtenerNombreJugador(self, deteccion_jugador: Dict, detecciones: Dict) -> str:
        if self.fase_actual:
            for jugador_existente in self.fase_actual.jugadores.values():
                distancia = UtilidadesGeometria.euclidean_distance(
                    jugador_existente.center, deteccion_jugador['center']
                )
                if distancia < 100:
                    return jugador_existente.nombre
        
        texto_nombre = next(
            (self.procesador_ocr.get_text_from_image(n['crop']) 
             for n in detecciones.get('NombreJugador', []) 
             if UtilidadesGeometria.is_contained(n['box'], deteccion_jugador['box'])), 
            None
        )
        nombre = UtilidadesTexto.clean_player_name(texto_nombre) if texto_nombre else ""
        return nombre if nombre else f"Jugador_{deteccion_jugador['center'][0]}"

    def construirEstadoActual(self, detecciones: Dict, nombre_fase: str):
        if not self.fase_actual:
            return
            
        # Procesar bote
        texto_bote = self.procesador_ocr.get_text_from_image(
            detecciones['Bote'][0]['crop']
        ) if detecciones.get('Bote') else ""
        bote_raw = UtilidadesTexto.limpiarTextoBote(texto_bote) or 0.0
        self.fase_actual.bote_total = bote_raw
        self.fase_actual.bote_total_normalizado = self.normalizarEnBB(bote_raw)
        
        # Procesar bote apuesta
        texto_bote_apuesta = self.procesador_ocr.get_text_from_image(
            detecciones['BoteApuesta'][0]['crop']
        ) if detecciones.get('BoteApuesta') else ""
        bote_apuesta_raw = UtilidadesTexto.clean_monetary_value(texto_bote_apuesta) or 0.0
        self.fase_actual.bote_apuesta = bote_apuesta_raw
        self.fase_actual.bote_apuesta_normalizado = self.normalizarEnBB(bote_apuesta_raw)
        
        # Procesar cartas comunitarias
        cartas_comunitarias = self.obtenerCartasComunitariasPorFase(detecciones, nombre_fase)
        self.fase_actual.cartas_comunitarias = cartas_comunitarias
        
        # IMPORTANTE: Llamar a detectarAcciones aquí
        self.detectarAcciones(detecciones)
        
        # Obtener la última acción excluyendo al héroe
        ultima_accion = self.fase_actual.obtenerUltimaAccion(self.nombre_heroe)
        
        # NUEVO: En PreFlop, verificar si realmente ha habido acciones o solo ciegas
        if nombre_fase == "PreFlop" and not self.fase_actual.acciones_realizadas:
            ultima_accion = "Ninguna"
            print("[PREFLOP] No hay acciones registradas, última acción = 'Ninguna'")
        
        # Actualizar la apuesta más alta
        self.fase_actual.apuesta_mas_alta = max(
            (j.apuesta_actual for j in self.fase_actual.jugadores.values()),
            default=0.0
        )
        self.fase_actual.apuesta_mas_alta_normalizada = self.normalizarEnBB(self.fase_actual.apuesta_mas_alta)
        
        print(f"[ESTADO] Fase: {nombre_fase}")
        print(f"[ESTADO] Bote: ${bote_raw} ({self.fase_actual.bote_total_normalizado:.2f} BB)")
        print(f"[ESTADO] BoteApuesta: ${bote_apuesta_raw} ({self.fase_actual.bote_apuesta_normalizado:.2f} BB)")
        print(f"[ESTADO] Acciones registradas: {len(self.fase_actual.acciones_realizadas)}")
        print(f"[ESTADO] Última acción para infoset: '{ultima_accion}'")
        
        # Debug: mostrar historial de acciones
        if self.fase_actual.acciones_realizadas:
            print("[HISTORIAL] Últimas 5 acciones:")
            for nombre, accion, monto in self.fase_actual.acciones_realizadas[-5:]:
                if nombre in self.fase_actual.jugadores:
                    jugador = self.fase_actual.jugadores[nombre]
                    print(f"  - {nombre}: {accion} (${monto:.2f} = {jugador.apuesta_normalizada:.2f} BB)")
                else:
                    print(f"  - {nombre}: {accion} (${monto:.2f})")

    def validarYLimpiarAcciones(self):
        """Valida y limpia el historial de acciones para evitar inconsistencias"""
        if not self.fase_actual or not self.fase_actual.acciones_realizadas:
            return
        
        # Eliminar acciones duplicadas consecutivas del mismo jugador
        acciones_limpias = []
        ultima_accion_por_jugador = {}
        
        for nombre, accion, monto in self.fase_actual.acciones_realizadas:
            clave = f"{nombre}_{accion}"
            if clave not in ultima_accion_por_jugador or ultima_accion_por_jugador[clave] != monto:
                acciones_limpias.append((nombre, accion, monto))
                ultima_accion_por_jugador[clave] = monto
        
        self.fase_actual.acciones_realizadas = acciones_limpias

    def hayJugadorPrincipal(self) -> bool:
        if not self.fase_actual:
            return False
        return any(j.es_heroe for j in self.fase_actual.jugadores.values())
    
    def esTurnoHeroe(self) -> bool:
        if not self.fase_actual:
            return False
        heroe = next((j for j in self.fase_actual.jugadores.values() if j.es_heroe), None)
        return heroe.es_turno_actual if heroe else False

    def necesitaAccion(self) -> bool:
        return self.esTurnoHeroe()

    def hubocambioSignificativo(self) -> bool:
        if self.cambio_detectado:
            self.cambio_detectado = False
            return True
        return False

    def obtenerEstadoParaJson(self) -> Optional[Dict]:
        if not self.fase_actual:
            return None
            
        jugadores_activos = [j for j in self.fase_actual.jugadores.values() if j.estado == 'activo']
        
        # Obtener la última acción correctamente
        ultima_accion = self.fase_actual.obtenerUltimaAccion(self.nombre_heroe)
        
        # Debug adicional
        print(f"\n[DEBUG ACCIONES]")
        print(f"Total acciones registradas: {len(self.fase_actual.acciones_realizadas)}")
        if self.fase_actual.acciones_realizadas:
            print("Últimas 3 acciones:")
            for nombre, accion, monto in self.fase_actual.acciones_realizadas[-3:]:
                print(f"  {nombre}: {accion} (${monto:.2f})")
        print(f"Última acción para infoset: '{ultima_accion}'")
        
        return {
            "fase_actual": self.fase_actual.nombre_fase,
            "bote_total": self.fase_actual.bote_total,
            "bote_total_normalizado": self.fase_actual.bote_total_normalizado,
            "bote_fase_anterior_o_ante": self.fase_actual.bote_apuesta,
            "bote_fase_anterior_normalizado": self.fase_actual.bote_apuesta_normalizado,
            "tiene_ante": self.fase_actual.tiene_ante,
            "posicion_dealer": self.fase_actual.dealer_position,
            "cartas_comunitarias": self.fase_actual.cartas_comunitarias,
            "cantidad_jugadores_activos": len(jugadores_activos),
            "cantidad_jugadores_mesa": self.fase_actual.numero_jugadores_mesa,
            "jugadores": [j.toDiccionario() for j in self.fase_actual.jugadores.values()],
            "bb_actual": self.fase_actual.bb_actual,
            "sb_actual": self.fase_actual.sb_actual,
            "historial_acciones_fase": ultima_accion,
            "historial_completo": self.fase_actual.obtenerHistorialAccionesFormateado(),
            "id_mano": self.id_mano_actual
        }

    def obtenerEstadoFormateado(self) -> str:
        estado = self.obtenerEstadoParaJson()
        if estado:
            return json.dumps(estado, indent=2, ensure_ascii=False, cls=CodificadorNumpy)
        return "{}"

class CodificadorNumpy(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(CodificadorNumpy, self).default(obj)