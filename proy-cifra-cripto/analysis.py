import matplotlib

matplotlib.use("Agg")  # backend sin ventana: sirve para Flask y para guardar PNG
import matplotlib.pyplot as plt
import numpy as np

from ciphers import ALFABETO, INDICE, N, normalizar_texto

# Frecuencias aproximadas de las letras en español (%), orden de ALFABETO.
_FREC_ESPANOL_PCT = {
    "A": 12.53, "B": 1.42, "C": 4.68, "D": 5.86, "E": 13.68, "F": 0.69,
    "G": 1.01, "H": 0.70, "I": 6.25, "J": 0.44, "K": 0.01, "L": 4.97,
    "M": 3.15, "N": 6.71, "Ñ": 0.31, "O": 8.68, "P": 2.51, "Q": 0.88,
    "R": 6.87, "S": 7.98, "T": 4.63, "U": 3.93, "V": 0.90, "W": 0.02,
    "X": 0.22, "Y": 0.90, "Z": 0.52,
}

_v = np.array([_FREC_ESPANOL_PCT[c] for c in ALFABETO])
FREC_ESPANOL = _v / _v.sum() * 100  # normalizada para sumar exactamente 100

IC_ESPANOL = 0.0775      # índice de coincidencia típico del español
IC_ALEATORIO = 1 / N     # ≈ 0.0370, texto uniformemente aleatorio


# ---------------------------------------------------------------------------
# Conteo y frecuencias
# ---------------------------------------------------------------------------
def contar_letras(texto: str) -> np.ndarray:
    """Vector de 27 posiciones con el conteo de cada letra (orden ALFABETO)."""
    conteo = np.zeros(N, dtype=int)
    for c in normalizar_texto(texto):
        conteo[INDICE[c]] += 1
    return conteo


def frecuencias_relativas(texto: str) -> np.ndarray:
    """Frecuencia de cada letra en porcentaje (suma 100; ceros si no hay texto)."""
    conteo = contar_letras(texto)
    total = conteo.sum()
    if total == 0:
        return np.zeros(N)
    return conteo / total * 100


# ---------------------------------------------------------------------------
# Req. 7: comparación con el español
# ---------------------------------------------------------------------------
def comparar_con_espanol(texto: str) -> list:
    """Tabla letra por letra: observada vs. esperada (en %) y diferencia."""
    obs = frecuencias_relativas(texto)
    conteo = contar_letras(texto)
    return [
        {
            "letra": ALFABETO[i],
            "conteo": int(conteo[i]),
            "observada": round(float(obs[i]), 2),
            "esperada": round(float(FREC_ESPANOL[i]), 2),
            "diferencia": round(float(obs[i] - FREC_ESPANOL[i]), 2),
        }
        for i in range(N)
    ]


def chi_cuadrado(texto: str) -> float:
    """Estadístico chi-cuadrado contra el español. Menor = más parecido.
    Devuelve infinito si el texto está vacío."""
    conteo = contar_letras(texto)
    total = conteo.sum()
    if total == 0:
        return float("inf")
    esperado = FREC_ESPANOL / 100 * total
    esperado = np.maximum(esperado, 1e-9)
    return float(((conteo - esperado) ** 2 / esperado).sum())


# ---------------------------------------------------------------------------
# Índice de coincidencia
# ---------------------------------------------------------------------------
def indice_coincidencia(texto: str) -> float:
    """IC = sum(n_i * (n_i - 1)) / (L * (L - 1)).
    ≈0.0775 en español; ≈0.037 en texto aleatorio o muy poliafabético."""
    conteo = contar_letras(texto)
    L = int(conteo.sum())
    if L < 2:
        return 0.0
    return float((conteo * (conteo - 1)).sum() / (L * (L - 1)))


# ---------------------------------------------------------------------------
# Req. 6: histograma
# ---------------------------------------------------------------------------
def grafico_frecuencias(texto: str, comparar: bool = True,
                        titulo: str = "Frecuencia de letras", ruta: str = None):
    """Histograma de frecuencias del texto. Si comparar=True, superpone las
    frecuencias esperadas del español. Si se da ruta, guarda un PNG.
    Devuelve la figura de Matplotlib."""
    obs = frecuencias_relativas(texto)
    x = np.arange(N)

    fig, ax = plt.subplots(figsize=(11, 4.5))
    if comparar:
        ancho = 0.4
        ax.bar(x - ancho / 2, obs, ancho, label="Texto analizado", color="#c0392b")
        ax.bar(x + ancho / 2, FREC_ESPANOL, ancho, label="Español esperado",
               color="#2980b9")
        ax.legend()
    else:
        ax.bar(x, obs, 0.7, color="#c0392b")

    ax.set_xticks(x)
    ax.set_xticklabels(list(ALFABETO))
    ax.set_xlabel("Letra")
    ax.set_ylabel("Frecuencia (%)")
    ax.set_title(titulo)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()

    if ruta:
        fig.savefig(ruta, dpi=120)
    return fig


# ---------------------------------------------------------------------------
# Pruebas rápidas: python analysis.py
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    from ciphers import cesar_cifrar, vigenere_cifrar

    texto = (
        "En un lugar de la Mancha de cuyo nombre no quiero acordarme no ha "
        "mucho tiempo que vivia un hidalgo de los de lanza en astillero "
        "adarga antigua rocin flaco y galgo corredor una olla de algo mas "
        "vaca que carnero salpicon las mas noches duelos y quebrantos los "
        "sabados lentejas los viernes algun palomino de anadidura los "
        "domingos consumian las tres partes de su hacienda"
    )

    assert abs(FREC_ESPANOL.sum() - 100) < 1e-9
    assert abs(frecuencias_relativas(texto).sum() - 100) < 1e-9

    ic_plano = indice_coincidencia(texto)
    ic_cesar = indice_coincidencia(cesar_cifrar(texto, 5))
    ic_vig = indice_coincidencia(vigenere_cifrar(texto, "LIMONADA"))
    print(f"IC texto plano : {ic_plano:.4f}  (español ≈ {IC_ESPANOL})")
    print(f"IC César       : {ic_cesar:.4f}  (igual que el plano: no cambia)")
    print(f"IC Vigenère    : {ic_vig:.4f}  (cae hacia {IC_ALEATORIO:.4f})")
    assert abs(ic_plano - ic_cesar) < 1e-12
    assert ic_vig < ic_plano

    chi_plano = chi_cuadrado(texto)
    chi_cesar = chi_cuadrado(cesar_cifrar(texto, 5))
    print(f"Chi² plano: {chi_plano:.1f} | Chi² César: {chi_cesar:.1f}")
    assert chi_plano < chi_cesar

    print("\nTop 5 letras del texto vs. esperado:")
    tabla = sorted(comparar_con_espanol(texto), key=lambda r: -r["conteo"])[:5]
    for r in tabla:
        print(f"  {r['letra']}: obs {r['observada']:5.2f}%  esp {r['esperada']:5.2f}%  "
              f"dif {r['diferencia']:+.2f}")

    grafico_frecuencias(texto, titulo="Texto plano vs. español",
                        ruta="demo_frecuencias.png")
    grafico_frecuencias(cesar_cifrar(texto, 5), titulo="Texto cifrado (César 5)",
                        ruta="demo_frecuencias_cifrado.png")
    print("\nHistogramas guardados. Todas las pruebas pasaron correctamente.")