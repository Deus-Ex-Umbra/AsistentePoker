# Asistente Inteligente de Póker Texas No-Limit Hold'em en Tiempo Real basado en MCCFR con Muestreo de Resultados

## Autor
**Gabriel Aparicio Llanquipacha**  
Carrera: Ingeniería en Ciencias de la Computación  
Universidad San Francisco Xavier de Chuquisaca (USFX)  
Sucre, Bolivia

## Descripción del Proyecto

Este proyecto implementa un asistente inteligente de póker en tiempo real que utiliza el algoritmo **Monte Carlo Counterfactual Regret Minimization (MCCFR)** con Muestreo de Resultados para proporcionar recomendaciones estratégicas óptimas durante partidas de Texas No-Limit Hold'em. El sistema emplea técnicas avanzadas de visión por computadora y procesamiento de texto óptico (OCR) para detectar automáticamente el estado del juego y consultar estrategias preentrenadas basadas en teoría de juegos.

### ¿Qué es MCCFR?

**Monte Carlo Counterfactual Regret Minimization (MCCFR)** es una variante optimizada del algoritmo Counterfactual Regret Minimization (CFR) diseñada específicamente para juegos de información imperfecta como el póker. A diferencia del CFR canónico que debe explorar exhaustivamente todo el árbol de decisiones, MCCFR utiliza técnicas de muestreo Monte Carlo para reducir drásticamente la carga computacional.

El algoritmo funciona mediante los siguientes principios fundamentales:

1. **Muestreo de Resultados**: En lugar de calcular valores esperados exactos para cada acción, MCCFR muestrea una única trayectoria del juego hasta un estado terminal.

2. **Corrección de Sesgo**: Para compensar el sesgo introducido por el muestreo, las actualizaciones de arrepentimiento se ponderan por el inverso de la probabilidad de muestreo.

3. **Convergencia a Equilibrio de Nash**: A través de millones de iteraciones de autojuego, la estrategia promedio converge hacia un equilibrio de Nash aproximado, que representa una estrategia inexploitable en el contexto de teoría de juegos.

4. **Regret Matching**: El algoritmo utiliza la técnica de "regret matching" para actualizar las estrategias, minimizando el arrepentimiento contrafactual acumulado.

La fórmula clave del MCCFR con Muestreo de Resultados es:

```
R_t(I, a) ← R_{t-1}(I, a) + [π_{-i}^σ(h_z) / q(z)] · u_i(z, a)
```

Donde:
- `R_t(I, a)` es el arrepentimiento acumulado para la acción `a` en el infoset `I`
- `π_{-i}^σ(h_z)` representa la probabilidad de contribución de los oponentes
- `q(z)` es la probabilidad de muestreo del resultado `z`
- `u_i(z, a)` es la utilidad obtenida al tomar la acción `a`

## Características Principales

- **Detección Automática del Estado de Juego**: Utiliza YOLO v12 para detectar elementos visuales de la interfaz de póker
- **Procesamiento OCR Avanzado**: Extrae información textual de cartas, apuestas y nombres de jugadores
- **Consulta MCCFR en Tiempo Real**: Accede a modelos preentrenados con más de 2.4 millones de infosets únicos
- **Interfaz de Usuario Intuitiva**: Proporciona recomendaciones claras y traducidas al español
- **Soporte Multi-jugador**: Compatible con partidas de 2 a 10 jugadores
- **Estrategia GTO**: Implementa estrategia Game Theory Optimal basada en equilibrio de Nash

## Requisitos del Sistema

### Hardware Mínimo
- RAM: 8 GB (16 GB recomendado)
- GPU: Compatible con CUDA (opcional, mejora el rendimiento)
- CPU: Procesador multi-núcleo moderno
- Almacenamiento: 5 GB de espacio libre

### Software
- Python 3.8 o superior
- Sistema operativo: Windows 10/11, Linux Ubuntu 18.04+, macOS 10.15+

## Instalación

### 1. Clonar el Repositorio
```bash
git clone [URL_DEL_REPOSITORIO]
cd poker-mccfr-assistant
```

### 2. Crear Entorno Virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Descargar Recursos Adicionales

#### Modelos MCCFR Preentrenados
Descargar desde: [Repositorios Completos](https://drive.google.com/drive/folders/1VIMWPVC0bHLpkHRsCgQa2_uiCjrhgV2v?usp=drive_link)

Extraer en el directorio `../PokerNGPlusPlus/`

#### Pesos del Modelo YOLO
Descargar desde: [Pesos YOLO](https://drive.google.com/drive/folders/1h1FXNBSRxMy_KMFNT4moZungN9h7ynzd)

Colocar el archivo `best.pt` en `./Yolo12n/`

#### Video Explicativo
Disponible en: [Video Demostrativo](https://drive.google.com/drive/folders/16HYjuCk00rNIjWUdkB-jD88990FDGacn)

### 5. Configuración
Verificar las rutas en `Config.py`:
```python
YOLO_MODEL_PATH = './Yolo12n/best.pt'
MCCFR_MODELS_DIR = '../PokerNGPlusPlus/'
```

## Uso del Sistema

### Ejecución
```bash
python main.py
```

### Controles de Teclado
- **Q**: Salir del programa
- **P**: Pausar/Reanudar detección
- **F**: Forzar nueva recomendación

### Interfaz de Usuario
El sistema despliega una ventana flotante que muestra:
- Fase actual del juego
- Infoset consultado
- Acción recomendada por MCCFR
- Monto exacto de apuesta
- Estado del sistema

## Arquitectura del Sistema

### Descripción de Archivos

#### Módulos Principales
- **`main.py`**: Punto de entrada principal, coordina todos los módulos y ejecuta el bucle principal del sistema
- **`EstadoJuego.py`**: Gestiona el estado completo de la partida, incluyendo jugadores, fases, apuestas y acciones
- **`TomadorDeDecisiones.py`**: Implementa la lógica de consulta MCCFR y cálculo de recomendaciones
- **`MCCFRLoader.py`**: Carga y parsea los modelos MCCFR preentrenados desde archivos binarios

#### Módulos de Detección
- **`CapturadorPantalla.py`**: Captura frames de la pantalla en tiempo real usando MSS
- **`DetectorObjetos.py`**: Implementa la detección de objetos usando YOLO v12
- **`ProcesadorOCR.py`**: Extrae texto de imágenes usando EasyOCR con preprocesamiento avanzado

#### Módulos de Interfaz
- **`InterfazUsuario.py`**: Interfaz gráfica Tkinter para mostrar recomendaciones
- **`ListenerTeclado.py`**: Maneja los controles de teclado del sistema

#### Módulos Utilitarios
- **`UtilidadesGeometria.py`**: Funciones para cálculos geométricos y ordenamiento de jugadores
- **`UtilidadesTexto.py`**: Procesamiento y limpieza de texto extraído por OCR
- **`UtilidadesDebug.py`**: Herramientas de depuración y logging
- **`Config.py`**: Configuración central del sistema y constantes

#### Documentación
- **`paste.txt`**: Artículo científico completo en formato LaTeX con metodología y resultados

## Metodología Científica

El proyecto se basa en el artículo científico incluido que documenta:

1. **Entrenamiento Masivo**: 1 billón de manos autojugadas
2. **Exploración de Infosets**: 2,403,013 infosets únicos explorados
3. **Validación Estadística**: 100 millones de manos aleatorias para validar el evaluador
4. **Pruebas de Rendimiento**: Evaluación contra Slumbot en 1,000 manos
5. **Abstracción Optimizada**: Sistema de infosets diseñado para eficiencia computacional

## Resultados Obtenidos

- **Tasa de Ganancia Positiva**: Demostrada contra bot de referencia Slumbot
- **Estrategia Emergente**: Desarrollo de estilo agresivo como comportamiento óptimo
- **Rendimiento en Tiempo Real**: Procesamiento a 27+ millones de manos por segundo
- **Modelos Compactos**: 95,990 nodos para modalidad Heads-Up (2 jugadores)

## Limitaciones Conocidas

1. **Abstracción con Pérdida**: El sistema de infosets ignora algunos detalles del historial de apuestas
2. **Estrategia Estática**: No se adapta dinámicamente a patrones específicos de oponentes
3. **Dependencia de Hardware**: Requiere recursos computacionales significativos para modelos completos
4. **Detección Visual**: Dependiente de la calidad y consistencia de la interfaz de póker

## Contribuciones Académicas

Este proyecto contribuye al campo de la inteligencia artificial en juegos mediante:

1. **Implementación Práctica**: Demostración de MCCFR en software de tiempo real
2. **Metodología de Entrenamiento**: Sistema de guardado por lotes para superar limitaciones de hardware
3. **Validación Empírica**: Pruebas contra bots de referencia establecidos
4. **Documentación Científica**: Artículo completo con metodología reproducible

## Licencia y Uso Académico

Este proyecto fue desarrollado con fines académicos y de investigación en el marco de la carrera de Ingeniería en Ciencias de la Computación de la Universidad San Francisco Xavier de Chuquisaca (USFX).

## Contacto

**Gabriel Aparicio Llanquipacha**  
Estudiante de Ingeniería en Ciencias de la Computación  
Universidad San Francisco Xavier de Chuquisaca (USFX)  
Sucre, Bolivia

---

*Este README acompaña el artículo científico "Asistente Inteligente de Póker Texas No-Limit Hold'em en Tiempo Real basado en MCCFR con Muestreo de Resultados" presentado como trabajo de investigación en la USFX.*
