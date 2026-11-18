import numpy as np

from analysis import FREC_ESPANOL, IC_ESPANOL, chi_cuadrado, contar_letras, indice_coincidencia
from ciphers import ALFABETO, INDICE, N, cesar_descifrar, normalizar_texto


# ---------------------------------------------------------------------------
# Req. 8: ataque automático a César
# ---------------------------------------------------------------------------
def ataque_cesar(texto: str) -> list:
    """Prueba los 27 desplazamientos y puntúa cada resultado con chi-cuadrado
    contra el español (menor = más probable). Devuelve la lista ordenada del
    mejor al peor; cada elemento: desplazamiento, clave_letra, texto, chi2."""
    texto = normalizar_texto(texto)
    resultados = []
    for d in range(N):
        candidato = cesar_descifrar(texto, d)
        resultados.append({
            "desplazamiento": d,
            "clave_letra": ALFABETO[d],
            "texto": candidato,
            "chi2": round(chi_cuadrado(candidato), 2),
        })
    return sorted(resultados, key=lambda r: r["chi2"])


# ---------------------------------------------------------------------------
# Req. 9: longitud de clave de Vigenère
# ---------------------------------------------------------------------------
def ic_por_longitud(texto: str, max_longitud: int = 20) -> list:
    """Para cada longitud k, divide el texto en k columnas (letras i, i+k, ...)
    y promedia el índice de coincidencia de las columnas."""
    texto = normalizar_texto(texto)
    resultados = []
    for k in range(1, max_longitud + 1):
        if len(texto) < 2 * k:
            break
        columnas = [texto[i::k] for i in range(k)]
        ic = float(np.mean([indice_coincidencia(c) for c in columnas]))
        resultados.append({"longitud": k, "ic_promedio": round(ic, 4)})
    return resultados


def estimar_longitud_vigenere(texto: str, max_longitud: int = 20) -> dict:
    """Devuelve la tabla de IC por longitud y la longitud sugerida.
    Los múltiplos de la longitud real también dan IC alto, por eso se elige
    la longitud MÁS CORTA cuyo IC está cerca del máximo (>= 90 % del máximo)."""
    tabla = ic_por_longitud(texto, max_longitud)
    if not tabla:
        raise ValueError("Texto demasiado corto para estimar la longitud de clave.")
    ic_max = max(r["ic_promedio"] for r in tabla)
    sugerida = next(r["longitud"] for r in tabla if r["ic_promedio"] >= 0.9 * ic_max)
    return {"tabla": tabla, "sugerida": sugerida, "ic_referencia_espanol": IC_ESPANOL}


def sugerir_clave_vigenere(texto: str, longitud: int) -> str:
    """Dada la longitud, cada columna es un César: se ataca cada una por
    separado y la letra de clave es el desplazamiento ganador."""
    texto = normalizar_texto(texto)
    clave = ""
    for i in range(longitud):
        mejor = ataque_cesar(texto[i::longitud])[0]
        clave += ALFABETO[mejor["desplazamiento"]]
    return clave


# ---------------------------------------------------------------------------
# Req. 10: clave más probable para sustitución monoalfabética
# ---------------------------------------------------------------------------
def sugerir_mapeo_sustitucion(texto: str) -> dict:
    """Empareja las letras del cifrado, ordenadas de más a menos frecuentes,
    con las letras del español en el mismo orden de frecuencia.
    Devuelve {letra_cifrada: letra_plana} (una permutación de las 27)."""
    conteo = contar_letras(texto)
    # orden estable: a igual conteo, se respeta el orden del alfabeto
    orden_cifrado = sorted(range(N), key=lambda i: (-conteo[i], i))
    orden_espanol = sorted(range(N), key=lambda i: (-FREC_ESPANOL[i], i))
    return {ALFABETO[c]: ALFABETO[p] for c, p in zip(orden_cifrado, orden_espanol)}


def mapeo_a_alfabeto_clave(mapeo: dict) -> str:
    """Convierte {cifrada: plana} al formato de ciphers.py, donde
    alfabeto_clave[i] es la letra cifrada que corresponde a ALFABETO[i]."""
    inverso = {plana: cifrada for cifrada, plana in mapeo.items()}
    return "".join(inverso[letra] for letra in ALFABETO)


def aplicar_mapeo(texto: str, mapeo: dict) -> str:
    return "".join(mapeo[c] for c in normalizar_texto(texto))


# ---------------------------------------------------------------------------
# Req. 11: criptoanálisis asistido (corrección manual del mapeo)
# ---------------------------------------------------------------------------
class MapeoAsistido:
    """Mapeo editable para criptoanálisis asistido.

    Parte de la sugerencia automática. El usuario fija pares con `fijar`;
    como el mapeo debe seguir siendo una permutación, si la letra plana ya
    la usaba otra letra cifrada, ambas intercambian sus asignaciones.
    Los pares fijados quedan bloqueados y no se alteran en intercambios.
    """

    def __init__(self, texto_cifrado: str):
        self.texto = normalizar_texto(texto_cifrado)
        self.mapeo = sugerir_mapeo_sustitucion(self.texto)
        self.bloqueadas = set()  # letras cifradas fijadas por el usuario

    def fijar(self, cifrada: str, plana: str) -> None:
        cifrada, plana = normalizar_texto(cifrada), normalizar_texto(plana)
        if len(cifrada) != 1 or len(plana) != 1:
            raise ValueError("Indica exactamente una letra cifrada y una letra plana.")
        if cifrada in self.bloqueadas and self.mapeo[cifrada] != plana:
            self.bloqueadas.discard(cifrada)  # el usuario se corrige a sí mismo
        otra = next(c for c, p in self.mapeo.items() if p == plana)
        if otra != cifrada:
            if otra in self.bloqueadas:
                raise ValueError(
                    f"'{plana}' ya está fijada para la letra cifrada '{otra}'. "
                    "Libérala primero."
                )
            self.mapeo[otra] = self.mapeo[cifrada]  # intercambio
        self.mapeo[cifrada] = plana
        self.bloqueadas.add(cifrada)

    def liberar(self, cifrada: str) -> None:
        self.bloqueadas.discard(normalizar_texto(cifrada))

    def reiniciar(self) -> None:
        self.mapeo = sugerir_mapeo_sustitucion(self.texto)
        self.bloqueadas = set()

    def descifrar(self) -> str:
        return aplicar_mapeo(self.texto, self.mapeo)

    def alfabeto_clave(self) -> str:
        return mapeo_a_alfabeto_clave(self.mapeo)

    def tabla(self) -> list:
        conteo = contar_letras(self.texto)
        return [
            {"cifrada": c, "plana": self.mapeo[c], "conteo": int(conteo[INDICE[c]]),
             "fijada": c in self.bloqueadas}
            for c in ALFABETO
        ]


# ---------------------------------------------------------------------------
# Pruebas rápidas: python cryptanalysis.py
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    from ciphers import (cesar_cifrar, sustitucion_cifrar, sustitucion_descifrar,
                         generar_alfabeto_aleatorio, vigenere_cifrar)

    texto = (
        "La criptografia es el arte de escribir mensajes de forma que solo el "
        "destinatario pueda entenderlos. Desde la antiguedad los romanos usaban "
        "un cifrado sencillo que desplazaba cada letra un numero fijo de "
        "posiciones en el alfabeto. Con el tiempo aparecieron metodos mas "
        "elaborados, como el que usa una palabra clave para variar el "
        "desplazamiento en cada letra del mensaje. Sin embargo, el lenguaje "
        "humano tiene patrones muy marcados: algunas letras aparecen mucho mas "
        "que otras, y esas huellas permiten a un analista paciente recuperar "
        "el texto original sin conocer la clave. Por eso los cifrados "
        "clasicos hoy se estudian como ejemplo de lo que no se debe usar, y "
        "sirven para entender por que la criptografia moderna se apoya en "
        "matematicas mucho mas profundas y en claves de gran tamano que "
        "ningun analista podria probar una por una aunque dispusiera de "
        "todo el tiempo del mundo."
    )
    base = normalizar_texto(texto)

    # --- Req. 8
    cifrado = cesar_cifrar(texto, 11)
    r = ataque_cesar(cifrado)
    print(f"César: mejor desplazamiento = {r[0]['desplazamiento']} "
          f"(chi² {r[0]['chi2']}) vs. segundo {r[1]['chi2']}")
    assert r[0]["desplazamiento"] == 11 and r[0]["texto"] == base

    # --- Req. 9
    cifrado_v = vigenere_cifrar(texto, "LIMON")
    est = estimar_longitud_vigenere(cifrado_v)
    print("Vigenère: longitud sugerida =", est["sugerida"])
    print("   IC por longitud:",
          {t["longitud"]: t["ic_promedio"] for t in est["tabla"][:10]})
    assert est["sugerida"] == 5
    clave = sugerir_clave_vigenere(cifrado_v, est["sugerida"])
    print("   Clave recuperada:", clave)
    assert clave == "LIMON"

    # --- Req. 10
    alfa = generar_alfabeto_aleatorio(semilla=7)
    cifrado_s = sustitucion_cifrar(texto, alfa)
    mapeo = sugerir_mapeo_sustitucion(cifrado_s)
    assert sorted(mapeo.values()) == sorted(ALFABETO)  # es permutación
    auto = aplicar_mapeo(cifrado_s, mapeo)
    acierto = sum(a == b for a, b in zip(auto, base)) / len(base) * 100
    print(f"Sustitución: acierto automático = {acierto:.1f} % de las letras")

    # --- Req. 11
    m = MapeoAsistido(cifrado_s)
    verdadero = {alfa[i]: ALFABETO[i] for i in range(N)}  # mapeo correcto
    for c, p in sorted(verdadero.items(), key=lambda kv: -m.tabla()[INDICE[kv[0]]]["conteo"])[:12]:
        m.fijar(c, p)
    mejora = sum(a == b for a, b in zip(m.descifrar(), base)) / len(base) * 100
    print(f"Asistido: tras corregir 12 letras = {mejora:.1f} %")
    assert mejora > acierto
    assert sorted(m.mapeo.values()) == sorted(ALFABETO)

    # corregir todo debe dar el texto exacto, y el alfabeto debe servir en ciphers.py
    for c, p in verdadero.items():
        m.liberar(c)
    for c, p in verdadero.items():
        m.fijar(c, p)
    assert m.descifrar() == base
    assert sustitucion_descifrar(cifrado_s, m.alfabeto_clave()) == base
    print("\nTodas las pruebas pasaron correctamente.")