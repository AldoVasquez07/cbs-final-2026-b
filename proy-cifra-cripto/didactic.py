"""
CriptoClásico - Etapa 5: modo didáctico.

Requisitos cubiertos:
  14 - Mostrar paso a paso el cifrado de un carácter.
  15 - Explicación de por qué los cifrados clásicos son vulnerables al análisis
       de frecuencia y qué los diferencia del cifrado moderno.
"""

import math

from ciphers import (ALFABETO, INDICE, N, normalizar_texto, validar_alfabeto_sustitucion,
                     validar_clave_palabra, _orden_columnas)


def _una_letra(letra: str) -> str:
    letra = normalizar_texto(letra)
    if len(letra) != 1:
        raise ValueError("Indica exactamente una letra del alfabeto.")
    return letra


# ---------------------------------------------------------------------------
# Req. 14: paso a paso de un carácter
# Cada función devuelve {"metodo", "entrada", "pasos": [str], "resultado"}
# ---------------------------------------------------------------------------
def pasos_cesar(letra: str, desplazamiento: int) -> dict:
    letra = _una_letra(letra)
    i = INDICE[letra]
    suma = i + desplazamiento
    j = suma % N
    resultado = ALFABETO[j]
    return {
        "metodo": "César",
        "entrada": letra,
        "pasos": [
            f"El alfabeto tiene {N} letras numeradas de 0 a {N - 1} (A=0, B=1, ..., Ñ=14, ..., Z=26).",
            f"La letra '{letra}' ocupa la posición {i}.",
            f"Se le suma el desplazamiento: {i} + {desplazamiento} = {suma}.",
            f"Se aplica módulo {N} para volver a empezar al pasar de la Z: {suma} mod {N} = {j}.",
            f"La posición {j} corresponde a la letra '{resultado}'.",
        ],
        "resultado": resultado,
    }


def pasos_sustitucion(letra: str, alfabeto_clave: str) -> dict:
    letra = _una_letra(letra)
    alfabeto_clave = validar_alfabeto_sustitucion(alfabeto_clave)
    i = INDICE[letra]
    resultado = alfabeto_clave[i]
    return {
        "metodo": "Sustitución monoalfabética",
        "entrada": letra,
        "pasos": [
            "Se alinean el alfabeto normal y el alfabeto de sustitución:",
            f"   Normal:      {ALFABETO}",
            f"   Sustitución: {alfabeto_clave}",
            f"La letra '{letra}' está en la posición {i} del alfabeto normal.",
            f"En la posición {i} del alfabeto de sustitución está '{resultado}'.",
            "Cada letra se reemplaza siempre por la misma: por eso se conservan las frecuencias.",
        ],
        "resultado": resultado,
    }


def pasos_vigenere(letra: str, clave: str, posicion: int = 0) -> dict:
    letra = _una_letra(letra)
    clave = validar_clave_palabra(clave)
    k = posicion % len(clave)
    letra_clave = clave[k]
    a, b = INDICE[letra], INDICE[letra_clave]
    suma = a + b
    j = suma % N
    resultado = ALFABETO[j]
    return {
        "metodo": "Vigenère",
        "entrada": letra,
        "pasos": [
            f"La clave es '{clave}' y se repite a lo largo del mensaje.",
            f"La letra está en la posición {posicion} del texto; le toca la letra {k + 1} "
            f"de la clave ({posicion} mod {len(clave)} = {k}): '{letra_clave}'.",
            f"'{letra}' vale {a} y '{letra_clave}' vale {b}.",
            f"Se suman los valores: {a} + {b} = {suma}.",
            f"Se aplica módulo {N}: {suma} mod {N} = {j}.",
            f"La posición {j} corresponde a '{resultado}'.",
            "Como la letra de la clave cambia, la misma letra del mensaje puede cifrarse distinto.",
        ],
        "resultado": resultado,
    }


def pasos_transposicion(texto: str, clave: str, posicion: int = 0) -> dict:
    """Sigue el viaje de UN carácter (el de la posición dada) en la transposición."""
    texto = normalizar_texto(texto)
    clave = validar_clave_palabra(clave)
    if not 0 <= posicion < len(texto):
        raise ValueError(f"La posición debe estar entre 0 y {len(texto) - 1}.")
    n_cols = len(clave)
    letra = texto[posicion]
    fila, col = divmod(posicion, n_cols)
    orden = _orden_columnas(clave)
    largo, resto = divmod(len(texto), n_cols)
    tam = lambda c: largo + (1 if c < resto else 0)
    turno = orden.index(col)
    antes = sum(tam(c) for c in orden[:turno])
    nueva_pos = antes + fila
    return {
        "metodo": "Transposición de columnas",
        "entrada": letra,
        "pasos": [
            f"El texto se escribe por filas en {n_cols} columnas, una por letra de la clave '{clave}'.",
            f"La letra '{letra}' (posición {posicion}) cae en la fila {fila + 1}, columna {col + 1} "
            f"(bajo la letra '{clave[col]}').",
            "Las columnas se leen siguiendo el orden alfabético de las letras de la clave: "
            + ", ".join(f"{c + 1}('{clave[c]}')" for c in orden) + ".",
            f"Su columna se lee en el turno {turno + 1}; antes se leyeron {antes} letras.",
            f"Dentro de su columna es la letra número {fila + 1}, así que queda en la posición "
            f"{antes} + {fila} = {nueva_pos} del texto cifrado.",
            "La letra no cambia, solo se mueve de lugar: por eso las frecuencias no se alteran.",
        ],
        "resultado": str(nueva_pos),  # posición final (la letra sigue siendo la misma)
    }


def explicar_caracter(metodo: str, texto: str, posicion: int = 0, clave=None) -> dict:
    """Punto de entrada para la interfaz: explica el cifrado del carácter
    en `posicion` del texto con el método indicado
    ('cesar', 'sustitucion', 'vigenere', 'transposicion')."""
    texto = normalizar_texto(texto)
    if not texto:
        raise ValueError("El texto no contiene letras válidas.")
    if not 0 <= posicion < len(texto):
        raise ValueError(f"La posición debe estar entre 0 y {len(texto) - 1}.")
    letra = texto[posicion]
    if metodo == "cesar":
        return pasos_cesar(letra, int(clave))
    if metodo == "sustitucion":
        return pasos_sustitucion(letra, clave)
    if metodo == "vigenere":
        return pasos_vigenere(letra, clave, posicion)
    if metodo == "transposicion":
        return pasos_transposicion(texto, clave, posicion)
    raise ValueError(f"Método desconocido: {metodo}")


# ---------------------------------------------------------------------------
# Req. 15: explicaciones teóricas
# ---------------------------------------------------------------------------
def _fmt_cientifico(n: int) -> str:
    s = f"{n:.2e}"  # 1.09e+28
    base, exp = s.split("e")
    return f"{base} × 10^{int(exp)}"


def explicacion_vulnerabilidad() -> list:
    """Secciones [{"titulo", "parrafos": [str]}] para mostrar en la interfaz."""
    claves_sust = math.factorial(N)
    return [
        {
            "titulo": "1. El idioma deja huellas",
            "parrafos": [
                "Las letras de un idioma no aparecen con la misma frecuencia. En español, la E y la A "
                "superan el 12 % cada una, mientras que la K, la W o la Ñ casi no aparecen. Esa "
                "distribución es como una huella dactilar del idioma.",
                "Un buen cifrado debería borrar esa huella. Los cifrados clásicos no lo logran del todo.",
            ],
        },
        {
            "titulo": "2. Por qué cada cifrado clásico se rompe",
            "parrafos": [
                f"César: solo existen {N} claves posibles. Un atacante las prueba todas en segundos y "
                "se queda con el resultado que más se parece al español (ataque por fuerza bruta).",
                f"Sustitución monoalfabética: hay {_fmt_cientifico(claves_sust)} claves posibles (27!), "
                "demasiadas para probarlas una por una. Sin embargo, cada letra se cambia siempre por "
                "la misma, así que el histograma del cifrado es el del español con las barras "
                "cambiadas de nombre. Emparejar las letras más frecuentes con E, A, O... da un "
                "primer borrador que se afina a mano. El tamaño del espacio de claves no basta si "
                "el cifrado filtra información estadística.",
                "Vigenère: usar varias letras de clave aplana el histograma, pero la clave se repite. "
                "Si se conoce su longitud, cada columna es un César y se ataca por separado. La "
                "longitud se estima con el índice de coincidencia (≈0.0775 en español y ≈0.037 "
                "en texto aleatorio) o con el método de Kasiski, que busca fragmentos repetidos.",
                "Transposición: no cambia las letras, solo su orden. Por eso el histograma y el "
                "índice de coincidencia son idénticos a los del texto original, lo cual delata que "
                "es una transposición. Se ataca reordenando columnas hasta que aparezcan palabras.",
            ],
        },
        {
            "titulo": "3. Qué hace distinto al cifrado moderno",
            "parrafos": [
                "Difusión y confusión (Shannon): un cifrado moderno como AES mezcla cada bit del "
                "mensaje con muchos otros y oculta la relación entre clave y texto cifrado. Cambiar "
                "un solo bit de la entrada altera cerca de la mitad de los bits de salida (efecto "
                "avalancha). Los clásicos operan letra por letra y no tienen esta mezcla.",
                "Salida indistinguible del azar: el texto cifrado con AES no tiene letras más "
                "frecuentes que otras ni patrones repetidos, así que no hay estadística que explotar.",
                "Espacio de claves enorme y bien aprovechado: AES usa claves de 128 a 256 bits "
                f"(2^128 ≈ {_fmt_cientifico(2 ** 128)} claves como mínimo) y no existe un atajo "
                "conocido que sea mucho mejor que probarlas todas.",
                "Modos de operación y vectores de inicialización: cifrar el mismo mensaje dos veces "
                "produce resultados distintos, algo que un cifrado clásico no hace.",
                "Principio de Kerckhoffs y escrutinio público: la seguridad reside solo en la clave, "
                "no en ocultar el algoritmo. Los algoritmos modernos se publican y los analiza la "
                "comunidad durante años antes de adoptarse.",
                "Integridad y autenticación: los esquemas modernos (por ejemplo AES-GCM) detectan "
                "si alguien modificó el mensaje. Los clásicos no ofrecen nada parecido.",
            ],
        },
        {
            "titulo": "4. Conclusión",
            "parrafos": [
                "Los cifrados clásicos son excelentes para aprender: muestran con claridad qué es una "
                "clave, qué es un ataque y por qué la estadística importa. Pero no deben usarse para "
                "proteger información real. Para eso se usan algoritmos modernos estandarizados y "
                "bibliotecas criptográficas probadas, nunca implementaciones propias.",
            ],
        },
    ]


def tabla_comparativa() -> list:
    """Filas [característica, clásico, moderno] para mostrar como tabla HTML."""
    return [
        ["Unidad que cifra", "Letras individuales", "Bloques o flujos de bits"],
        ["Efecto de cambiar 1 elemento del mensaje", "Cambia solo esa letra", "Cambia cerca de la mitad de la salida (avalancha)"],
        ["Frecuencias en el texto cifrado", "Se conservan o se filtran", "Indistinguibles del azar"],
        ["Mismo mensaje cifrado dos veces", "Mismo resultado", "Distinto (IV o nonce)"],
        ["Tamaño de la clave", f"Muy pequeño (César: {N} claves)", "128 a 256 bits o más"],
        ["Seguridad depende de", "Ocultar el método y la clave", "Solo de la clave (Kerckhoffs)"],
        ["Verifica que el mensaje no fue alterado", "No", "Sí (modos autenticados)"],
        ["Resistencia al criptoanálisis", "Se rompe con lápiz y papel", "Sin ataque práctico conocido"],
    ]


# ---------------------------------------------------------------------------
# Pruebas rápidas: python didactic.py
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    from ciphers import (cesar_cifrar, generar_alfabeto_aleatorio, sustitucion_cifrar,
                         transposicion_cifrar, vigenere_cifrar)

    texto = "Mañana atacamos al amanecer"
    base = normalizar_texto(texto)

    # Los pasos deben coincidir con los cifrados reales de la Etapa 1
    c = cesar_cifrar(base, 7)
    alfa = generar_alfabeto_aleatorio(3)
    s = sustitucion_cifrar(base, alfa)
    v = vigenere_cifrar(base, "SOL")
    t = transposicion_cifrar(base, "CLAVE")
    for pos in range(len(base)):
        assert explicar_caracter("cesar", base, pos, 7)["resultado"] == c[pos]
        assert explicar_caracter("sustitucion", base, pos, alfa)["resultado"] == s[pos]
        assert explicar_caracter("vigenere", base, pos, "SOL")["resultado"] == v[pos]
        nueva = int(explicar_caracter("transposicion", base, pos, "CLAVE")["resultado"])
        assert t[nueva] == base[pos]
    print("Los pasos coinciden con los cifrados reales en todas las posiciones.\n")

    e = explicar_caracter("vigenere", base, 4, "SOL")
    print(f"--- {e['metodo']}: '{e['entrada']}' -> '{e['resultado']}'")
    for p in e["pasos"]:
        print("  •", p)

    e = explicar_caracter("transposicion", base, 4, "CLAVE")
    print(f"\n--- {e['metodo']}: '{e['entrada']}' -> posición {e['resultado']}")
    for p in e["pasos"]:
        print("  •", p)

    secciones = explicacion_vulnerabilidad()
    assert len(secciones) == 4 and len(tabla_comparativa()) >= 6
    print("\n", secciones[1]["parrafos"][1][:140], "...")

    for malo in (lambda: explicar_caracter("cesar", "", 0, 3),
                 lambda: explicar_caracter("xyz", base, 0, 1),
                 lambda: explicar_caracter("cesar", base, 999, 1)):
        try:
            malo()
            raise AssertionError("debió fallar")
        except ValueError:
            pass
    print("\nTodas las pruebas pasaron correctamente.")
