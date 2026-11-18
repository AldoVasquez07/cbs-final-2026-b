import os

from ciphers import normalizar_texto

TAMANO_MAX_BYTES = 1_000_000  # 1 MB: suficiente para textos de práctica
EXTENSIONES_PERMITIDAS = {".txt"}


# ---------------------------------------------------------------------------
# Req. 12: porcentaje de acierto
# ---------------------------------------------------------------------------
def porcentaje_acierto(descifrado: str, referencia: str) -> dict:
    """Compara letra por letra (posición a posición) el texto descifrado con
    el de referencia, ambos normalizados. Si las longitudes difieren, las
    letras sobrantes o faltantes cuentan como errores (el denominador es la
    longitud mayor). Devuelve porcentaje, letras correctas y total."""
    d = normalizar_texto(descifrado)
    r = normalizar_texto(referencia)
    total = max(len(d), len(r))
    if total == 0:
        return {"porcentaje": 0.0, "correctas": 0, "total": 0}
    correctas = sum(a == b for a, b in zip(d, r))
    return {
        "porcentaje": round(correctas / total * 100, 2),
        "correctas": correctas,
        "total": total,
    }


def marcar_diferencias(descifrado: str, referencia: str) -> str:
    """Línea de marcas para mostrar bajo el texto: '|' donde coincide y
    '.' donde falla (útil para depurar el criptoanálisis asistido)."""
    d = normalizar_texto(descifrado)
    r = normalizar_texto(referencia)
    marcas = ["|" if a == b else "." for a, b in zip(d, r)]
    marcas += ["."] * (abs(len(d) - len(r)))
    return "".join(marcas)


# ---------------------------------------------------------------------------
# Presentación
# ---------------------------------------------------------------------------
def formatear_bloques(texto: str, tamano: int = 5) -> str:
    """Agrupa el texto en bloques (por defecto de 5 letras) para leer mejor
    un criptograma: 'HOLAMUNDO' -> 'HOLAM UNDO'."""
    return " ".join(texto[i:i + tamano] for i in range(0, len(texto), tamano))


# ---------------------------------------------------------------------------
# Req. 13: carga y guardado
# ---------------------------------------------------------------------------
def decodificar_bytes(datos: bytes) -> str:
    """Decodifica bytes de un archivo de texto: UTF-8 y, si falla, Latin-1
    (típico de archivos .txt creados en Windows)."""
    if len(datos) > TAMANO_MAX_BYTES:
        raise ValueError(
            f"El archivo supera el límite de {TAMANO_MAX_BYTES // 1000} KB."
        )
    for codificacion in ("utf-8-sig", "latin-1"):
        try:
            return datos.decode(codificacion)
        except UnicodeDecodeError:
            continue
    raise ValueError("No se pudo leer el archivo como texto.")


def validar_nombre_archivo(nombre: str) -> None:
    ext = os.path.splitext(nombre)[1].lower()
    if ext not in EXTENSIONES_PERMITIDAS:
        raise ValueError("Solo se permiten archivos .txt")


def cargar_texto(ruta: str) -> str:
    """Lee un archivo .txt desde disco."""
    validar_nombre_archivo(ruta)
    if not os.path.isfile(ruta):
        raise FileNotFoundError(f"No existe el archivo: {ruta}")
    with open(ruta, "rb") as f:
        return decodificar_bytes(f.read())


def guardar_texto(ruta: str, contenido: str, encabezado: str = "") -> str:
    """Guarda un resultado (cifrado o descifrado) en un .txt en UTF-8.
    Si se da encabezado (por ejemplo 'Cifrado: César, clave 3'), se escribe
    como primera línea con prefijo '# '. Devuelve la ruta guardada."""
    validar_nombre_archivo(ruta)
    carpeta = os.path.dirname(ruta)
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        if encabezado:
            f.write(f"# {encabezado}\n")
        f.write(contenido)
        if not contenido.endswith("\n"):
            f.write("\n")
    return ruta


# ---------------------------------------------------------------------------
# Pruebas rápidas: python utils.py
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import tempfile

    ref = "Mañana atacamos al amanecer"
    base = normalizar_texto(ref)

    # Req. 12
    assert porcentaje_acierto(base, ref)["porcentaje"] == 100.0
    parcial = base[:-4] + "XXXX"
    p = porcentaje_acierto(parcial, ref)
    print("Acierto parcial:", p)
    assert p["correctas"] == len(base) - 4
    corto = porcentaje_acierto(base[:10], ref)
    print("Texto incompleto:", corto)
    assert corto["total"] == len(base) and corto["correctas"] == 10
    assert porcentaje_acierto("", "")["total"] == 0
    print("Marcas:", base)
    print("       ", marcar_diferencias(parcial, ref))

    print("Bloques:", formatear_bloques(base))

    # Req. 13
    with tempfile.TemporaryDirectory() as tmp:
        ruta = os.path.join(tmp, "salida", "resultado.txt")
        guardar_texto(ruta, "ODQDPD", encabezado="Cifrado: César, clave 3")
        with open(ruta, encoding="utf-8") as f:
            print("Archivo guardado:", repr(f.read()))
        assert cargar_texto(ruta).startswith("# Cifrado")

        # archivo en Latin-1 (como los de Windows) con Ñ y tildes
        ruta2 = os.path.join(tmp, "windows.txt")
        with open(ruta2, "wb") as f:
            f.write("Niño y camión".encode("latin-1"))
        assert cargar_texto(ruta2) == "Niño y camión"

        for malo in ("script.py", "datos.docx"):
            try:
                validar_nombre_archivo(malo)
                raise AssertionError("debió rechazar " + malo)
            except ValueError:
                pass
        try:
            decodificar_bytes(b"a" * (TAMANO_MAX_BYTES + 1))
            raise AssertionError("debió rechazar archivo grande")
        except ValueError:
            pass

    print("\nTodas las pruebas pasaron correctamente.")
