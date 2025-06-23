import struct
import os
import glob
import re
from typing import Dict, Any, List
from Config import MCCFR_MODELS_DIR, FORMATO_FLOTANTE, ENDIANNESS_POR_DEFECTO, MAX_ACCIONES_POR_NODO, MAX_LONGITUD_STRING, NUMERO_MAGICO_CPP
class MccfrParsingError(Exception): pass
class MccfrEndOfFileError(MccfrParsingError): pass
class MccfrFormatError(MccfrParsingError): pass
class MCCFRLoader:
    def __init__(self): self.mccfr_data: Dict[int, Dict[str, Any]] = {}
    def _leer_bytes_exactos(self, f, n):
        buf = f.read(n)
        if len(buf) < n: raise MccfrEndOfFileError(f"Expected {n} bytes, got {len(buf)}.")
        return buf
    def _leer_struct(self, f, fmt, end):
        full_fmt = end + fmt
        try: return struct.unpack(full_fmt, self._leer_bytes_exactos(f, struct.calcsize(full_fmt)))
        except struct.error as e: raise MccfrFormatError(f"Error unpacking struct with format '{full_fmt}': {e}")
    def _leer_string(self, f, end, ctx="?"):
        length = self._leer_struct(f, 'I', end)[0]
        if length == 0: return ""
        if length > MAX_LONGITUD_STRING: raise MccfrFormatError(f"Error in '{ctx}': String length ({length}) exceeds limit.")
        try: return self._leer_bytes_exactos(f, length).decode('latin-1', errors='replace')
        except UnicodeDecodeError as e: raise MccfrFormatError(f"Error in '{ctx}': Could not decode string. Error: {e}")
    def _parsear_archivo_mccfr(self, file_path: str, endianness: str = ENDIANNESS_POR_DEFECTO) -> Dict[str, Any]:
        with open(file_path, 'rb') as f:
            h_vals = self._leer_struct(f, 'IIQIIB3B4x', endianness)
            header = {"numero_magico": h_vals[0], "version": h_vals[1], "timestamp": h_vals[2], "total_nodos": h_vals[3], "checksum": h_vals[4], "num_jugadores": h_vals[5]}
            if header["numero_magico"] != NUMERO_MAGICO_CPP: raise MccfrFormatError(f"Invalid magic number in {os.path.basename(file_path)}.")
            if not (2 <= header["num_jugadores"] <= 10): raise MccfrFormatError(f"Invalid player count: {header['num_jugadores']}.")
            nodos = {}
            for i in range(header["total_nodos"]):
                key = self._leer_string(f, endianness, ctx=f"key_{i+1}")
                num_actions = self._leer_struct(f, 'I', endianness)[0]
                if not (0 < num_actions <= MAX_ACCIONES_POR_NODO): raise MccfrFormatError(f"Invalid action count ({num_actions}) for node '{key}'.")
                actions = []
                for _ in range(num_actions):
                    actions.append({"accion": self._leer_string(f, endianness, ctx="action_text"), "arrepentimiento": self._leer_struct(f, FORMATO_FLOTANTE, endianness)[0], "suma_estrategia": self._leer_struct(f, FORMATO_FLOTANTE, endianness)[0]})
                nodos[key] = actions
            return {"cabecera": header, "nodos": nodos}
    def cargar_modelos_en_memoria(self) -> Dict[int, Dict[str, Any]]:
        bin_files = glob.glob(os.path.join(MCCFR_MODELS_DIR, 'mccfr_*_poker.bin'))
        if not bin_files:
            print(f"Error: No se encontraron archivos .bin en: {MCCFR_MODELS_DIR}")
            return {}
        for file_path in sorted(bin_files):
            try:
                match = re.search(r'mccfr_(\d+)_poker\.bin', os.path.basename(file_path))
                if match:
                    num_jugadores = int(match.group(1))
                    print(f"  -> Cargando modelo para {num_jugadores} jugadores desde '{os.path.basename(file_path)}'...")
                    datos_modelo = self._parsear_archivo_mccfr(file_path)
                    self.mccfr_data[num_jugadores] = datos_modelo
                    print(f"     ...Cargado. {datos_modelo['cabecera']['total_nodos']} nodos.")
            except (MccfrParsingError, Exception) as e: print(f"Error processing {file_path}: {e}")
        return self.mccfr_data