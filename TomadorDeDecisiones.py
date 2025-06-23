import random
import re
from typing import Dict, Any, Optional, List, Tuple
from treys import Card, Evaluator
from UtilidadesTexto import UtilidadesTexto
from Config import TREYS_CATEGORY_MAP

class TomadorDeDecisiones:
    def __init__(self, datos_mccfr: Dict[int, Dict[str, Any]]):
        self.datos_mccfr = datos_mccfr
        self.evaluador = Evaluator()

    def convertirACartasTreys(self, cartas_str: List[str]) -> List[int]:
        cartas_treys_list = []
        for carta_str in cartas_str:
            if len(carta_str) == 2:
                try:
                    carta_trey_int = Card.new(carta_str)
                    cartas_treys_list.append(carta_trey_int)
                except Exception as e:
                    print(f"Error convirtiendo carta '{carta_str}': {e}")
                    continue
        return cartas_treys_list

    def evaluarCategoriaMano(self, cartas_heroe_str: List[str], cartas_comunitarias_str: List[str]) -> str:
        if len(cartas_heroe_str) != 2:
            return "Carta Alta"

        if not cartas_comunitarias_str or len(cartas_comunitarias_str) == 0:
            return self.evaluarCategoriaPreflop(cartas_heroe_str)

        try:
            cartas_heroe = self.convertirACartasTreys(cartas_heroe_str)
            cartas_comunitarias = self.convertirACartasTreys(cartas_comunitarias_str)
            
            if not cartas_heroe or len(cartas_heroe) != 2:
                return self.evaluarCategoriaPreflop(cartas_heroe_str)

            rank = self.evaluador.evaluate(cartas_heroe, cartas_comunitarias)
            class_int = self.evaluador.get_rank_class(rank)
            class_str = self.evaluador.class_to_string(class_int)
            
            return TREYS_CATEGORY_MAP.get(class_str, "Carta Alta")
            
        except Exception as e:
            print(f"Error evaluando mano con Treys: {e}")
            return "Carta Alta"

    def evaluarCategoriaPreflop(self, cartas_heroe: List[str]) -> str:
        if len(cartas_heroe) != 2:
            return "Carta Alta"
        
        try:
            valor1_str = cartas_heroe[0][:-1].upper()
            valor2_str = cartas_heroe[1][:-1].upper()
            if valor1_str == valor2_str:
                return "Par"
            else:
                return "Carta Alta"
        except:
            return "Carta Alta"

    def obtenerHeroe(self, estado_juego: Dict[str, Any]) -> Optional[Dict]:
        jugadores = estado_juego.get('jugadores', [])
        return next((p for p in jugadores if p.get('es_heroe')), None)

    def determinarManoPreflop(self, cartas_heroe: List[str]) -> str:
        if len(cartas_heroe) != 2:
            return "XX"
        
        try:
            carta1, carta2 = cartas_heroe
            valor1_str, valor2_str = carta1[:-1].upper(), carta2[:-1].upper()
            suit1, suit2 = carta1[-1], carta2[-1]
            
            valor_map = {
                '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 
                'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14
            }
            valor1, valor2 = valor_map.get(valor1_str, 0), valor_map.get(valor2_str, 0)
            
            if valor1 == 0 or valor2 == 0:
                return "XX"
            
            if valor1 < valor2:
                valor1, valor2 = valor2, valor1
                valor1_str, valor2_str = valor2_str, valor1_str

            if valor1 == valor2:
                return f"{valor1_str}{valor2_str}"
            else:
                suited = 's' if suit1 == suit2 else 'o'
                return f"{valor1_str}{valor2_str}{suited}"
                
        except Exception:
            return "XX"

    def limpiarPosicion(self, posicion: str) -> str:
        if not posicion or posicion.strip() == "":
            return "UTG"
            
        posicion = posicion.strip().upper()
        posiciones_validas = {
            'BTN', 'SB', 'BB', 'UTG', 'UTG+1', 'UTG+2', 'UTG+3', 
            'LJ', 'HJ', 'CO', 'MP', 'EP'
        }
        
        if posicion in posiciones_validas:
            return posicion
            
        mapeo_posiciones = {
            'BUTTON': 'BTN',
            'SMALL_BLIND': 'SB', 
            'BIG_BLIND': 'BB',
            'UNDER_THE_GUN': 'UTG',
            'CUTOFF': 'CO',
            'HIJACK': 'HJ',
            'LOJACK': 'LJ',
            'MIDDLE': 'MP',
            'EARLY': 'EP'
        }
        
        return mapeo_posiciones.get(posicion, 'UTG')

    def limpiarFase(self, fase: str) -> str:
        if not fase:
            return "Preflop"
            
        fase = fase.strip()
        mapeo_fases = {
            'PreFlop': 'Preflop',
            'Flop': 'Flop',
            'Turn': 'Turn', 
            'River': 'River'
        }
        
        return mapeo_fases.get(fase, 'Preflop')

    def limpiarAccionPrevia(self, historial_acciones: str) -> str:
        if not historial_acciones or historial_acciones.strip() == "":
            return "Ninguna"
            
        ultima_accion = historial_acciones.strip()
        
        acciones_validas = [
            "Fold", "Check", "Call", "All-In", "Raise Min", "Raise x2", "Raise x3", 
            "Raise 33%", "Raise 50%", "Raise 75%", "Raise 100%", "Raise 150%", 
            "Raise 200%", "Raise 250%", "Raise 300%", "Ninguna"
        ]
        
        return ultima_accion if ultima_accion in acciones_validas else "Ninguna"

    def construirClaveInfoset(self, estado_juego: Dict[str, Any]) -> str:
        heroe = self.obtenerHeroe(estado_juego)
        
        if not heroe or len(heroe.get('cartas', [])) != 2:
            cartas_mano = "XX"
            categoria_mano = "Carta Alta"
        else:
            cartas_mano = self.determinarManoPreflop(heroe['cartas'])
            categoria_mano = self.evaluarCategoriaMano(
                heroe['cartas'], 
                estado_juego.get('cartas_comunitarias', [])
            )
        
        posicion = self.limpiarPosicion(heroe.get('posicion_relativa', '')) if heroe else "UTG"
        fase = self.limpiarFase(estado_juego.get('fase_actual', ''))
        accion_previa = self.limpiarAccionPrevia(estado_juego.get('historial_acciones_fase', ''))
        
        clave = f"{cartas_mano}:{categoria_mano}:{posicion}:{fase}:{accion_previa}"
        estado_juego["infoset_key"] = clave
        
        return clave

    def obtenerAccionRecomendada(self, estado_juego: Dict[str, Any]) -> Tuple[str, float, bool]:
        num_jugadores = estado_juego.get('cantidad_jugadores_mesa', 2)
        if num_jugadores < 2:
            return self._accionSegura(estado_juego)
            
        modelo_jugadores = max(2, min(10, num_jugadores))
        
        if modelo_jugadores not in self.datos_mccfr:
            if not self.datos_mccfr:
                return self._accionSegura(estado_juego)
            modelo_jugadores = min(
                self.datos_mccfr.keys(), 
                key=lambda x: abs(x - modelo_jugadores)
            )
        
        clave_infoset = self.construirClaveInfoset(estado_juego)
        nodos_modelo = self.datos_mccfr[modelo_jugadores].get('nodos', {})
        info_nodo = nodos_modelo.get(clave_infoset)
        
        if not info_nodo:
            return self._accionSegura(estado_juego)
        
        suma_total_estrategia = sum(
            max(0.0, a.get('suma_estrategia', 0.0)) for a in info_nodo
        )
        
        if suma_total_estrategia <= 1e-9:
            accion_segura = min(
                info_nodo, 
                key=lambda x: x.get('arrepentimiento', float('inf'))
            )
            return accion_segura.get('accion', "Fold"), 0.0, True
        
        mejor_accion = max(
            info_nodo, 
            key=lambda x: max(0.0, x.get('suma_estrategia', 0.0))
        )
        
        nombre_accion = mejor_accion.get('accion', 'Check')
        prob_accion = max(0.0, mejor_accion.get('suma_estrategia', 0.0)) / suma_total_estrategia
        
        return nombre_accion, prob_accion, True

    def _accionSegura(self, estado_juego: Dict[str, Any]) -> Tuple[str, float, bool]:
        """Determina la acción más segura cuando no se encuentra el infoset"""
        # Verificar si hay apuestas activas
        jugadores = estado_juego.get('jugadores', [])
        hay_apuesta = any(j.get('apuesta_actual', 0) > 0 for j in jugadores if not j.get('es_heroe'))
        
        if hay_apuesta:
            # Si hay apuesta, Fold es la acción más segura
            return "Fold", 0.0, False
        else:
            # Si no hay apuesta, Check es la acción más segura
            return "Check", 0.0, False

    def calcularMontoSubida(self, accion: str, estado_juego: Dict[str, Any]) -> Optional[float]:
        """Calcula el monto de subida basándose en valores normalizados y contexto de apuestas"""
        if "Raise" not in accion:
            return None
        
        # Trabajar con valores normalizados
        bote_norm = estado_juego.get('bote_total_normalizado', 0.0)
        bote_apuesta_norm = estado_juego.get('bote_fase_anterior_normalizado', 0.0)
        bb = estado_juego.get('bb_actual', 0.10)
        heroe = self.obtenerHeroe(estado_juego)
        
        if not heroe or bb <= 0:
            return None
        
        apuesta_heroe_norm = heroe.get('apuesta_normalizada', 0.0)
        oponentes = [p for p in estado_juego.get('jugadores', []) if not p.get('es_heroe')]
        apuesta_max_oponente_norm = max(
            (p.get('apuesta_normalizada', 0.0) for p in oponentes), 
            default=0.0
        )
        monto_a_igualar_norm = apuesta_max_oponente_norm - apuesta_heroe_norm
        
        print(f"\n[CALCULO_RAISE] {accion}")
        print(f"  - Bote normalizado: {bote_norm:.2f} BB")
        print(f"  - Bote apuesta norm: {bote_apuesta_norm:.2f} BB")
        print(f"  - Apuesta héroe norm: {apuesta_heroe_norm:.2f} BB")
        print(f"  - Max apuesta oponente norm: {apuesta_max_oponente_norm:.2f} BB")
        print(f"  - Monto a igualar norm: {monto_a_igualar_norm:.2f} BB")
        
        # Calcular en valores normalizados primero
        monto_final_norm = 0.0
        
        if "Raise Min" in accion:
            # Para Raise Min, necesitamos saber cuál fue la última subida
            # Buscar en el historial de acciones
            ultima_subida_norm = 1.0  # Por defecto 1 BB
            
            # Si hay raises previos en el historial, calcular la última subida
            jugadores = estado_juego.get('jugadores', [])
            apuestas_norm = []
            for p in jugadores:
                if p.get('apuesta_normalizada', 0.0) > 0:
                    apuestas_norm.append(p.get('apuesta_normalizada', 0.0))
            
            apuestas_norm = sorted(apuestas_norm)
            if len(apuestas_norm) >= 2:
                ultima_subida_norm = apuestas_norm[-1] - apuestas_norm[-2]
                ultima_subida_norm = max(ultima_subida_norm, 1.0)  # Mínimo 1 BB
            
            monto_final_norm = apuesta_max_oponente_norm + ultima_subida_norm
            print(f"  - Última subida norm: {ultima_subida_norm:.2f} BB")
        
        elif any(x in accion for x in ["33%", "50%", "75%", "100%", "150%", "200%", "250%", "300%"]):
            # Raise basado en porcentaje del bote
            porcentaje_match = re.search(r'(\d+)%', accion)
            if porcentaje_match:
                porcentaje = float(porcentaje_match.group(1)) / 100.0
                
                # IMPORTANTE: Calcular el bote SIN incluir la apuesta del héroe actual
                # Bote efectivo = bote + bote_apuesta + apuestas de otros jugadores (no la del héroe)
                apuestas_otros_norm = sum(
                    p.get('apuesta_normalizada', 0.0) 
                    for p in estado_juego.get('jugadores', [])
                    if not p.get('es_heroe')
                )
                
                bote_efectivo_norm = bote_norm + bote_apuesta_norm + apuestas_otros_norm
                
                # El raise es un porcentaje del bote efectivo
                monto_subida_norm = bote_efectivo_norm * porcentaje
                monto_final_norm = monto_a_igualar_norm + monto_subida_norm
                
                print(f"  - Apuestas otros norm: {apuestas_otros_norm:.2f} BB")
                print(f"  - Bote efectivo norm (sin héroe): {bote_efectivo_norm:.2f} BB")
                print(f"  - Porcentaje: {porcentaje:.1%}")
                print(f"  - Monto subida norm: {monto_subida_norm:.2f} BB")
        
        elif "x2" in accion or "x3" in accion:
            # Raise multiplicador sobre la apuesta anterior
            multiplicador_match = re.search(r'x(\d+)', accion)
            if multiplicador_match:
                multiplicador = float(multiplicador_match.group(1))
                if apuesta_max_oponente_norm > 0:
                    monto_final_norm = apuesta_max_oponente_norm * multiplicador
                else:
                    # Si no hay apuesta previa, usar 2BB o 3BB
                    monto_final_norm = multiplicador
                print(f"  - Multiplicador: x{multiplicador}")
        
        # Convertir de vuelta a valor real
        if monto_final_norm > 0:
            monto_final_real = monto_final_norm * bb
            print(f"  - Monto final norm: {monto_final_norm:.2f} BB")
            print(f"  - Monto final real: ${monto_final_real:.2f}")
            
            # Verificar que sea un raise válido
            apuesta_heroe_real = heroe.get('apuesta_actual', 0.0)
            max_apuesta_real = max(
                (p.get('apuesta_actual', 0.0) for p in estado_juego.get('jugadores', [])),
                default=0.0
            )
            
            # El monto debe ser al menos el doble de la BB o la apuesta anterior + BB
            min_raise_real = max(max_apuesta_real + bb, bb * 2)
            
            # Verificar que no exceda el stack del héroe
            stack_heroe_real = heroe.get('stack', 0.0)
            stack_efectivo_real = stack_heroe_real + apuesta_heroe_real
            
            if monto_final_real > stack_efectivo_real:
                print(f"  - Ajustando a stack efectivo: ${stack_efectivo_real:.2f} (All-In)")
                return stack_efectivo_real
            
            if monto_final_real < min_raise_real:
                print(f"  - Ajustando al mínimo legal: ${min_raise_real:.2f}")
                return min_raise_real
                
            return monto_final_real
        
        return None

    def traducirAccionAEspanol(self, accion_mccfr: str, monto: Optional[float] = None) -> str:
        if not accion_mccfr:
            return "Pasar/No Ir"
        
        traducciones = {
            "Fold": "No Ir",
            "Check": "Pasar", 
            "Call": "Pagar",
            "All-In": "All In"
        }
        
        if accion_mccfr in traducciones:
            return traducciones[accion_mccfr]
        
        if "Raise" in accion_mccfr:
            if monto is not None and monto > 0:
                return f"Igualar o Subir a ${monto:.2f}"
            else:
                tipo_raise = accion_mccfr.replace("Raise ", "")
                return f"Subir ({tipo_raise})"
        
        return accion_mccfr.replace("_", " ").title()

    def obtenerRecomendacionCompleta(self, estado_juego: Dict[str, Any]) -> Dict[str, Any]:
        accion_mccfr, probabilidad, encontrado = self.obtenerAccionRecomendada(estado_juego)
        
        monto, monto_normalizado = None, None
        if accion_mccfr and "Raise" in accion_mccfr:
            monto = self.calcularMontoSubida(accion_mccfr, estado_juego)
            if monto is not None:
                bb_actual = estado_juego.get('bb_actual', 0.10)
                if bb_actual > 0:
                    monto_normalizado = round(monto / bb_actual, 2)
        
        accion_espanol = self.traducirAccionAEspanol(accion_mccfr, monto)
        
        # Si no se encontró el infoset y la acción es Check/Fold
        if not encontrado:
            accion_espanol = "Pasar / No Ir"
            
        return {
            "accion_mccfr": accion_mccfr,
            "accion_espanol": accion_espanol,
            "monto": monto,
            "monto_normalizado": monto_normalizado,
            "probabilidad": probabilidad,
            "infoset": estado_juego.get("infoset_key", "[ERROR]"),
            "infoset_encontrado": encontrado,
            "fase_actual": estado_juego.get('fase_actual', 'N/A')
        }