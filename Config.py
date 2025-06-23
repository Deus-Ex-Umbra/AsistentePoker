import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
YOLO_MODEL_PATH = os.path.join(BASE_DIR, './Yolo12n', 'best.pt') 
MCCFR_MODELS_DIR = os.path.join(BASE_DIR, '../PokerNGPlusPlus/')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

if not os.path.exists(LOGS_DIR): 
    os.makedirs(LOGS_DIR)

LOOP_DELAY_SECONDS = 0.3
MCCFR_QUERY_COOLDOWN_SECONDS = 1.0
YOLO_DEVICE = 'cuda'
CONFIDENCE_THRESHOLD = 0.45

UI_BACKGROUND_COLOR = "#2E2E2E"
UI_TEXT_COLOR_NORMAL = "#E0E0E0"
UI_TEXT_COLOR_SUCCESS = "#4CAF50"
UI_TEXT_COLOR_ERROR = "#F44336"
UI_TEXT_COLOR_ACTION = "#2196F3"

KEY_QUIT = 'q'
KEY_PAUSE_RESUME = 'p'
KEY_FORCE_ACTION = 'f'

LABEL_NAMES = [
    'AccionPoker', 'Apuesta', 'Bote', 'BoteApuesta', 'BotonDealer',
    'CartaComunitaria', 'CartaJugador', 'CartaShowdown', 'Corazon', 'Diamante',
    'Espada', 'Espera', 'Flop', 'Ganador', 'JugadorActivo',
    'JugadorAusente', 'JugadorNoActivo', 'JugadorPrincipal', 'NombreJugador', 'PreFlop',
    'Principal', 'River', 'Showdown', 'Stack', 'Trebol',
    'Turn', 'TurnoActual', 'ValorCarta'
]

CARD_VALUE_MAP = {
    'A': 'A', 'K': 'K', 'Q': 'Q', 'J': 'J', 'T': 'T', 
    '10': 'T', 'O': 'T',
    '9': '9', '8': '8', '7': '7', '6': '6', '5': '5', '4': '4', '3': '3', '2': '2'
}

SUIT_MAP = {
    'Corazon': 'h',
    'Diamante': 'd',
    'Trebol': 'c',
    'Espada': 's'
}

TREYS_CATEGORY_MAP = {
    "High Card": "Carta Alta",
    "Pair": "Par",
    "Two Pair": "Doble Par", 
    "Three of a Kind": "Trío",
    "Straight": "Escalera",
    "Flush": "Color",
    "Full House": "Full House",
    "Four of a Kind": "Poker",
    "Straight Flush": "Escalera de Color"
}

POSICIONES_POR_JUGADORES = {
    2: ["SB", "BB"],
    3: ["BTN", "SB", "BB"],
    4: ["BTN", "SB", "BB", "CO"],
    5: ["BTN", "SB", "BB", "UTG", "CO"],
    6: ["BTN", "SB", "BB", "UTG", "HJ", "CO"],
    7: ["BTN", "SB", "BB", "UTG", "UTG+1", "HJ", "CO"],
    8: ["BTN", "SB", "BB", "UTG", "UTG+1", "LJ", "HJ", "CO"],
    9: ["BTN", "SB", "BB", "UTG", "UTG+1", "UTG+2", "LJ", "HJ", "CO"],
    10: ["BTN", "SB", "BB", "UTG", "UTG+1", "UTG+2", "UTG+3", "LJ", "HJ", "CO"]
}

ACCIONES_POKER = [
    "Fold", "Check", "Call", "All-In", "Raise Min", "Raise x2", "Raise x3", 
    "Raise 33%", "Raise 50%", "Raise 75%", "Raise 100%", "Raise 150%", 
    "Raise 200%", "Raise 250%", "Raise 300%"
]

ACCIONES_ESPAÑOL = {
    "Fold": "No Ir", "Check": "Pasar", "Call": "Pagar", "All-In": "All In",
    "Raise Min": "Subir Mínimo", "Raise x2": "Subir x2", "Raise x3": "Subir x3", 
    "Raise 33%": "Subir 33%", "Raise 50%": "Subir 50%", "Raise 75%": "Subir 75%",
    "Raise 100%": "Subir 100%", "Raise 150%": "Subir 150%", "Raise 200%": "Subir 200%",
    "Raise 250%": "Subir 250%", "Raise 300%": "Subir 300%"
}

NUMERO_MAGICO_CPP = 0x4D434346
FORMATO_FLOTANTE = 'd'
ENDIANNESS_POR_DEFECTO = '<'
MAX_ACCIONES_POR_NODO = 10000
MAX_LONGITUD_STRING = 100000

DEFAULT_SMALL_BLIND = 0.05
DEFAULT_BIG_BLIND = 0.10

DURACION_MINIMA_RECOMENDACION = 2.0
COOLDOWN_ENTRE_RECOMENDACIONES = 0.5

DEBUG_SAVE_FRAMES = False
DEBUG_PRINT_DETECTIONS = False
DEBUG_PRINT_OCR = False

DISTANCIA_MAXIMA_APUESTA_JUGADOR = 150
THRESHOLD_CONTENCION_CARTAS = 0.7
THRESHOLD_IOU_TURNO_ACTUAL = 0.1

BB_MINIMO_PARA_NORMALIZACION = 0.01
PRECISION_NORMALIZACION = 2

STACK_MAXIMO_VALIDO = 1e9
APUESTA_MAXIMA_VALIDA = 1e6
PORCENTAJE_RAISE_MAXIMO = 500

UI_UPDATE_INTERVAL_MS = 100
UI_WINDOW_POSITION_X = 1520
UI_WINDOW_POSITION_Y = 650
UI_WINDOW_WIDTH = 350
UI_WINDOW_HEIGHT = 400

MENSAJE_INICIANDO = "🎰 Inicializando MCCFR Poker Assistant..."
MENSAJE_SISTEMA_LISTO = "✅ Sistema inicializado correctamente"
MENSAJE_ERROR_YOLO = "❌ Error al cargar el modelo YOLO"
MENSAJE_ERROR_MCCFR = "❌ Error al cargar los modelos MCCFR"
MENSAJE_NO_JUEGO = "🔍 No se detecta juego activo"
MENSAJE_NO_HEROE = "⚠️ Sin Jugador Principal detectado"
MENSAJE_ESPERANDO_TURNO = "🎮 Esperando turno del héroe..."
MENSAJE_RECOMENDACION = "🎯 RECOMENDACIÓN"

PREFLOP_MAX_CIEGAS = 2
PREFLOP_IGNORAR_CIEGAS = True 
PREFLOP_OPEN_RAISE_MIN = 2.0
PREFLOP_OPEN_RAISE_STANDARD = 2.5 
PREFLOP_OPEN_RAISE_3X = 3.0