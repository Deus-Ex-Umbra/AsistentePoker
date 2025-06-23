import re
from typing import Optional
from Config import CARD_VALUE_MAP

class UtilidadesTexto:
    @staticmethod
    def limpiarValorMonetario(texto: str) -> Optional[float]:
        if not texto:
            return None
        
        texto = texto.strip().lower()
        
        casos_especiales = [
            'all in', 'allin', 'all-in',
            'reconectando', 'reconnecting', 'connecting',
            'post blind', 'post blinds',
            'esperando', 'waiting',
            'ausente', 'away'
        ]
        
        for caso in casos_especiales:
            if caso in texto:
                if 'all' in caso:
                    return 0.0
                else:
                    return None
        
        texto = re.sub(r'[¥$€£₹¢₽₿₫₪₱₩₦₴₡₵₸₼₾₽]', '', texto)
        texto = re.sub(r'\b(usd|eur|btc|eth|cg|chips?|fichas?)\b', '', texto)
        
        limpio = re.sub(r'[^\d.,]', '', texto)
        
        if not limpio:
            return None
        
        if limpio.count('.') > 1:
            partes = limpio.split('.')
            if len(partes) > 1:
                ultimo = partes[-1]
                if len(ultimo) <= 2 and ',' not in ultimo:
                    limpio = ''.join(partes[:-1]) + '.' + ultimo
                else:
                    limpio = ''.join(partes)
        
        if ',' in limpio:
            if '.' in limpio:
                limpio = limpio.replace(',', '')
            else:
                partes = limpio.split(',')
                if len(partes) == 2 and len(partes[1]) <= 2:
                    limpio = partes[0] + '.' + partes[1]
                else:
                    limpio = limpio.replace(',', '')
        
        try:
            val = float(limpio)
            if 0 <= val <= 1e9:
                return round(val, 2)
            else:
                return None
        except (ValueError, TypeError):
            return None

    @staticmethod
    def clean_monetary_value(texto: str) -> Optional[float]:
        return UtilidadesTexto.limpiarValorMonetario(texto)

    @staticmethod
    def limpiarNombreJugador(texto: str) -> str:
        if not texto:
            return ""
        
        texto = texto.strip()
        
        texto = re.sub(r'\s*\d{1,3}(?:\.\d+)?\s*%\s*$', '', texto)
        
        casos_ignorar = [
            'post blind', 'post blinds', 'posting blind', 'posting blinds',
            'small blind', 'big blind', 'sb', 'bb',
            'esperando', 'waiting', 'reconnecting', 'reconectando',
            'thinking', 'pensando', 'decidiendo',
            'all in', 'allin', 'all-in'
        ]
        
        texto_minuscula = texto.lower()
        for caso in casos_ignorar:
            if caso in texto_minuscula:
                return ""
        
        limpio = re.sub(r'[^\w\s\-_]', '', texto)
        limpio = re.sub(r'\s+', ' ', limpio).strip()
        
        if len(limpio) > 20:
            limpio = limpio[:20]
        
        return limpio

    @staticmethod
    def clean_player_name(texto: str) -> str:
        return UtilidadesTexto.limpiarNombreJugador(texto)

    @staticmethod
    def limpiarValorCarta(texto: str) -> Optional[str]:
        if not texto:
            return None
        
        texto = texto.upper().strip()
        
        correcciones = {
            'I': '1',
            'S': '5',
            'G': '6',
            'B': '8',
            'D': '0',
            'Z': '2',
            'L': '1',
            'C': '0',
        }
        
        for k, v in correcciones.items():
            texto = texto.replace(k, v)
        
        if texto in ['0', 'O']:
            return 'Q'
        
        if texto == '10':
            return 'T'
        
        valores_validos = {'2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A'}
        
        if texto in valores_validos:
            return texto
        
        return None

    @staticmethod
    def clean_card_value(texto: str) -> Optional[str]:
        return UtilidadesTexto.limpiarValorCarta(texto)

    @staticmethod
    def limpiarTextoBote(texto: str) -> Optional[float]:
        if not texto:
            return None
        
        texto = texto.strip().lower()
        
        patrones = [
            r'bote:?\s*([\d.,]+)',
            r'pot:?\s*([\d.,]+)',
            r'total:?\s*([\d.,]+)',
            r'([\d.,]+)'
        ]
        
        for patron in patrones:
            match = re.search(patron, texto)
            if match:
                valor_texto = match.group(1)
                return UtilidadesTexto.limpiarValorMonetario(valor_texto)
        
        return None

    @staticmethod
    def extraerAccionPoker(texto: str) -> Optional[str]:
        if not texto:
            return None
        
        texto = texto.strip().lower()
        
        mapeo_acciones = {
            'fold': 'Fold',
            'no ir': 'Fold',
            'retire': 'Fold',
            'pasar': 'Fold',
            
            'check': 'Check',
            'ver': 'Check',
            'paso': 'Check',
            
            'call': 'Call',
            'pagar': 'Call',
            'igualar': 'Call',
            'ver apuesta': 'Call',
            
            'all in': 'All-In',
            'allin': 'All-In',
            'all-in': 'All-In',
            'todo': 'All-In',
            
            'raise': 'Raise',
            'subir': 'Raise',
            'apostar': 'Raise',
            'bet': 'Raise'
        }
        
        for termino, accion in mapeo_acciones.items():
            if termino in texto:
                return accion
        
        if any(term in texto for term in ['raise', 'subir', 'bet']):
            if 'min' in texto:
                return 'Raise Min'
            elif 'x2' in texto or '2x' in texto:
                return 'Raise x2'
            elif 'x3' in texto or '3x' in texto:
                return 'Raise x3'
            elif '%' in texto:
                match = re.search(r'(\d+)%', texto)
                if match:
                    porcentaje = match.group(1)
                    return f'Raise {porcentaje}%'
            
            return 'Raise'
        
        return None

    @staticmethod
    def validarNombreJugador(nombre: str) -> bool:
        if not nombre or len(nombre.strip()) == 0:
            return False
        
        nombre = nombre.strip().lower()
        
        terminos_invalidos = [
            'post blind', 'posting', 'esperando', 'waiting',
            'reconectando', 'connecting', 'thinking', 'decidiendo',
            'all in', 'allin', '%', 'fold', 'call', 'raise',
            'check', 'bet', 'pot', 'bote'
        ]
        
        for termino in terminos_invalidos:
            if termino in nombre:
                return False
        
        if not re.search(r'[a-zA-Z0-9]', nombre):
            return False
        
        return True

    @staticmethod
    def detectarStackAllIn(texto: str) -> bool:
        """Detecta si el texto del stack indica All-In"""
        if not texto:
            return False
        
        texto = texto.strip().lower()
        
        indicadores_all_in = [
            'all in', 'allin', 'all-in',
            'todo', 'completo',
            'sin fichas', 'no chips',
            'all', 'in'
        ]
        
        return any(indicador in texto for indicador in indicadores_all_in)

    @staticmethod
    def normalizarFaseJuego(texto: str) -> str:
        if not texto:
            return "Espera"
        
        texto = texto.strip().lower()
        
        mapeo_fases = {
            'preflop': 'PreFlop',
            'pre-flop': 'PreFlop',
            'pre flop': 'PreFlop',
            'flop': 'Flop',
            'turn': 'Turn',
            'river': 'River',
            'showdown': 'Showdown',
            'espera': 'Espera',
            'waiting': 'Espera'
        }
        
        return mapeo_fases.get(texto, 'Espera')

    @staticmethod
    def extraerNumeroDeTexto(texto: str) -> Optional[float]:
        if not texto:
            return None
        
        match = re.search(r'([\d.,]+)', texto)
        if match:
            return UtilidadesTexto.limpiarValorMonetario(match.group(1))
        
        return None