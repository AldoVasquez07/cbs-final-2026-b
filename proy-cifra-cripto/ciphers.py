import random
import unicodedata

ALFABETO = "ABCDEFGHIJKLMNÑOPQRSTUVWXYZ"
N = len(ALFABETO)
INDICE = {letra: i for i, letra in enumerate(ALFABETO)}


# ---------------------------------------------------------------------------
# Req. 5: validacion y normalizacion
# ---------------------------------------------------------------------------
def normalizar_texto(texto: str) -> str:
    """Convierte a mayusculas, quita tildes/dieresis (conserva la Ñ),
    y elimina espacios y cualquier caracter que no sea del alfabeto."""
    texto = texto.upper().replace("Ñ", "\0")  # proteger la Ñ
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    texto = texto.replace("\0", "Ñ")
    return "".join(c for c in texto if c in INDICE)


def validar_clave_palabra(clave: str) -> str:
    """Normaliza una clave de palabra; lanza ValueError si queda vacia."""
    clave = normalizar_texto(clave)
    if not clave:
        raise ValueError("La clave debe contener al menos una letra.")
    return clave


# ---------------------------------------------------------------------------
# Req. 1: Cesar
# ---------------------------------------------------------------------------
def cesar_cifrar(texto: str, desplazamiento: int) -> str:
    texto = normalizar_texto(texto)
    return "".join(ALFABETO[(INDICE[c] + desplazamiento) % N] for c in texto)


def cesar_descifrar(texto: str, desplazamiento: int) -> str:
    return cesar_cifrar(texto, -desplazamiento)


# ---------------------------------------------------------------------------
# Req. 2: sustitucion monoalfabetica con alfabeto personalizado
# ---------------------------------------------------------------------------
def generar_alfabeto_aleatorio(semilla=None) -> str:
    letras = list(ALFABETO)
    random.Random(semilla).shuffle(letras)
    return "".join(letras)


def validar_alfabeto_sustitucion(alfabeto: str) -> str:
    """El alfabeto de sustitucion debe ser una permutacion de las 27 letras."""
    alfabeto = normalizar_texto(alfabeto)
    if len(alfabeto) != N or set(alfabeto) != set(ALFABETO):
        raise ValueError(
            f"El alfabeto debe tener exactamente {N} letras distintas "
            "(una permutacion de A-Z con Ñ)."
        )
    return alfabeto


def sustitucion_cifrar(texto: str, alfabeto_clave: str) -> str:
    alfabeto_clave = validar_alfabeto_sustitucion(alfabeto_clave)
    tabla = {ALFABETO[i]: alfabeto_clave[i] for i in range(N)}
    return "".join(tabla[c] for c in normalizar_texto(texto))


def sustitucion_descifrar(texto: str, alfabeto_clave: str) -> str:
    alfabeto_clave = validar_alfabeto_sustitucion(alfabeto_clave)
    tabla = {alfabeto_clave[i]: ALFABETO[i] for i in range(N)}
    return "".join(tabla[c] for c in normalizar_texto(texto))


# ---------------------------------------------------------------------------
# Req. 3: Vigenère
# ---------------------------------------------------------------------------
def vigenere_cifrar(texto: str, clave: str) -> str:
    texto = normalizar_texto(texto)
    clave = validar_clave_palabra(clave)
    return "".join(
        ALFABETO[(INDICE[c] + INDICE[clave[i % len(clave)]]) % N]
        for i, c in enumerate(texto)
    )


def vigenere_descifrar(texto: str, clave: str) -> str:
    texto = normalizar_texto(texto)
    clave = validar_clave_palabra(clave)
    return "".join(
        ALFABETO[(INDICE[c] - INDICE[clave[i % len(clave)]]) % N]
        for i, c in enumerate(texto)
    )


# ---------------------------------------------------------------------------
# Req. 4: transposicion de columnas
# ---------------------------------------------------------------------------
def _orden_columnas(clave: str) -> list:
    """indices de columna en el orden en que se leen (alfabetico por letra
    de la clave; si hay letras repetidas, de izquierda a derecha)."""
    return sorted(range(len(clave)), key=lambda j: (INDICE[clave[j]], j))


def transposicion_cifrar(texto: str, clave: str) -> str:
    """Escribe el texto por filas bajo la clave y lee por columnas
    siguiendo el orden alfabetico de las letras de la clave.
    No usa relleno, asi el descifrado recupera el texto exacto."""
    texto = normalizar_texto(texto)
    clave = validar_clave_palabra(clave)
    n_cols = len(clave)
    columnas = [texto[j::n_cols] for j in range(n_cols)]
    return "".join(columnas[j] for j in _orden_columnas(clave))


def transposicion_descifrar(texto: str, clave: str) -> str:
    texto = normalizar_texto(texto)
    clave = validar_clave_palabra(clave)
    n_cols = len(clave)
    largo, resto = divmod(len(texto), n_cols)
    columnas = [None] * n_cols
    pos = 0
    for j in _orden_columnas(clave):
        tam = largo + (1 if j < resto else 0)
        columnas[j] = texto[pos:pos + tam]
        pos += tam
    resultado = []
    for fila in range(largo + 1):
        for j in range(n_cols):
            if fila < len(columnas[j]):
                resultado.append(columnas[j][fila])
    return "".join(resultado)


# ---------------------------------------------------------------------------
# Pruebas rapidas: python ciphers.py
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    original = "Mañana, ¡atacamos al amanecer! Cañon y pingüino."
    base = normalizar_texto(original)
    print("Normalizado:", base)

    c = cesar_cifrar(original, 3)
    assert cesar_descifrar(c, 3) == base
    print("Cesar (3):        ", c)

    alfa = generar_alfabeto_aleatorio(semilla=42)
    s = sustitucion_cifrar(original, alfa)
    assert sustitucion_descifrar(s, alfa) == base
    print("Sustitucion:      ", s, "| alfabeto:", alfa)

    v = vigenere_cifrar(original, "LIMON")
    assert vigenere_descifrar(v, "LIMON") == base
    print("Vigenère (LIMON): ", v)

    t = transposicion_cifrar(original, "CLAVE")
    assert transposicion_descifrar(t, "CLAVE") == base
    print("Transposicion:    ", t)

    # Prueba con longitudes variadas y claves con letras repetidas
    for n in range(1, 40):
        txt = ALFABETO * 2
        txt = txt[:n]
        for k in ("A", "ZETA", "MAMA", "ÑANDU"):
            assert transposicion_descifrar(transposicion_cifrar(txt, k), k) == txt
    print("\nTodas las pruebas pasaron correctamente.")