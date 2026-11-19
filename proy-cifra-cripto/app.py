"""
CriptoClásico - Etapa 6: interfaz Flask completa.

6A: cifrar / descifrar            -> req. 1-5 y 13
6B: análisis, criptoanálisis,
    modo didáctico y teoría       -> req. 6-12, 14 y 15
Ejecutar:  python app.py   y abrir http://127.0.0.1:5000
"""

import base64
import io
import os
import tempfile

import matplotlib.pyplot as plt

from flask import Flask, Response, redirect, render_template, request, url_for

import analysis as an
import ciphers as c
import cryptanalysis as ca
import didactic as dd
from utils import (TAMANO_MAX_BYTES, decodificar_bytes, formatear_bloques,
                   guardar_texto, marcar_diferencias, porcentaje_acierto,
                   validar_nombre_archivo)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = TAMANO_MAX_BYTES + 100_000  # margen del formulario

METODOS = {
    "cesar": "César (desplazamiento)",
    "sustitucion": "Sustitución monoalfabética",
    "vigenere": "Vigenère",
    "transposicion": "Transposición de columnas",
}

# (endpoint, título). Los endpoints que aún no existen se muestran deshabilitados.
PESTANAS = [
    ("cifrar", "Cifrar / Descifrar"),
    ("analisis", "Análisis de frecuencia"),
    ("criptoanalisis", "Criptoanálisis"),
    ("didactico", "Modo didáctico"),
    ("teoria", "Teoría"),
]


@app.context_processor
def inyectar_navegacion():
    pestanas = [
        {"endpoint": ep, "titulo": t,
         "url": url_for(ep) if ep in app.view_functions else None}
        for ep, t in PESTANAS
    ]
    return {"pestanas": pestanas, "pestana_activa": request.endpoint}


# ---------------------------------------------------------------------------
# Lógica de cifrado (separada de las rutas para poder probarla)
# ---------------------------------------------------------------------------
def procesar(metodo: str, operacion: str, texto: str, form: dict):
    """Aplica el método elegido. Devuelve (resultado, encabezado).
    Lanza ValueError con un mensaje claro si algo es inválido."""
    if metodo not in METODOS:
        raise ValueError("Método desconocido.")
    if operacion not in ("cifrar", "descifrar"):
        raise ValueError("Operación desconocida.")
    if not c.normalizar_texto(texto):
        raise ValueError("El texto no contiene ninguna letra válida (A-Z, Ñ).")

    cifrar = operacion == "cifrar"
    verbo = "Cifrado" if cifrar else "Descifrado"

    if metodo == "cesar":
        try:
            d = int(form["desplazamiento"])
        except (ValueError, TypeError):
            raise ValueError("El desplazamiento debe ser un número entero.")
        fn = c.cesar_cifrar if cifrar else c.cesar_descifrar
        return fn(texto, d), f"{verbo}: César, desplazamiento {d}"

    if metodo == "sustitucion":
        alfabeto = c.validar_alfabeto_sustitucion(form["alfabeto"])
        fn = c.sustitucion_cifrar if cifrar else c.sustitucion_descifrar
        return fn(texto, alfabeto), f"{verbo}: sustitución, alfabeto {alfabeto}"

    clave = c.validar_clave_palabra(form["clave"])
    if metodo == "vigenere":
        fn = c.vigenere_cifrar if cifrar else c.vigenere_descifrar
        return fn(texto, clave), f"{verbo}: Vigenère, clave {clave}"

    fn = c.transposicion_cifrar if cifrar else c.transposicion_descifrar
    return fn(texto, clave), f"{verbo}: transposición, clave {clave}"


def leer_texto_entrada():
    """Texto del archivo subido (.txt) si hay uno; si no, el del cuadro de texto."""
    archivo = request.files.get("archivo")
    if archivo and archivo.filename:
        validar_nombre_archivo(archivo.filename)
        return decodificar_bytes(archivo.read())
    return request.form.get("texto", "")


def formulario_por_defecto() -> dict:
    return {
        "texto": "", "metodo": "cesar", "operacion": "cifrar",
        "desplazamiento": "3", "alfabeto": "", "clave": "", "bloques": "",
    }


# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------
@app.route("/")
def inicio():
    return redirect(url_for("cifrar"))


@app.route("/cifrar", methods=["GET", "POST"])
def cifrar():
    form = formulario_por_defecto()
    ctx = {"metodos": METODOS, "error": None, "resultado": None,
           "normalizado": None, "encabezado": None}

    if request.method == "POST":
        for campo in form:
            form[campo] = request.form.get(campo, form[campo])
        accion = request.form.get("accion", "procesar")

        try:
            if accion == "aleatorio":
                form["alfabeto"] = c.generar_alfabeto_aleatorio()
                form["metodo"] = "sustitucion"
            else:
                texto = leer_texto_entrada()
                form["texto"] = texto
                resultado, encabezado = procesar(
                    form["metodo"], form["operacion"], texto, form)
                if form["bloques"]:
                    resultado = formatear_bloques(resultado)

                if accion == "descargar":
                    return descargar(resultado, encabezado, form)

                ctx.update(resultado=resultado, encabezado=encabezado,
                           normalizado=c.normalizar_texto(texto))
        except (ValueError, UnicodeError) as e:
            ctx["error"] = str(e)

    return render_template("cifrar.html", form=form, **ctx)


def descargar(resultado: str, encabezado: str, form: dict) -> Response:
    """Req. 13: entrega el resultado como archivo .txt (usa utils.guardar_texto)."""
    with tempfile.TemporaryDirectory() as tmp:
        ruta = os.path.join(tmp, "resultado.txt")
        guardar_texto(ruta, resultado, encabezado=encabezado)
        with open(ruta, "rb") as f:
            datos = f.read()
    nombre = f"{form['operacion']}_{form['metodo']}.txt"
    return Response(
        datos, mimetype="text/plain; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{nombre}"'},
    )


# ===========================================================================
# 6B - Análisis de frecuencia (req. 6 y 7)
# ===========================================================================
def figura_a_base64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=110)
    plt.close(fig)  # libera memoria: Flask no debe acumular figuras abiertas
    return base64.b64encode(buf.getvalue()).decode()


def interpretar_ic(ic: float, n_letras: int) -> str:
    if n_letras < 100:
        aviso = " Con menos de 100 letras el índice es poco fiable."
    else:
        aviso = ""
    if ic >= 0.065:
        return ("Índice cercano al del español (0.0775): compatible con texto plano o con "
                "un cifrado que conserva las frecuencias (César, sustitución, transposición)." + aviso)
    if ic <= 0.047:
        return ("Índice cercano al de un texto aleatorio (0.037): compatible con un cifrado "
                "polialfabético como Vigenère." + aviso)
    return ("Índice intermedio: puede ser Vigenère con clave corta, o un texto breve "
            "cuyas estadísticas aún no son estables." + aviso)


@app.route("/analisis", methods=["GET", "POST"])
def analisis():
    form = {"texto": "", "comparar": "1"}
    ctx = {"error": None, "datos": None}

    if request.method == "POST":
        form["comparar"] = request.form.get("comparar", "")
        try:
            texto = leer_texto_entrada()
            form["texto"] = texto
            norm = c.normalizar_texto(texto)
            if len(norm) < 2:
                raise ValueError("Se necesitan al menos 2 letras válidas para analizar.")
            ic = an.indice_coincidencia(norm)
            fig = an.grafico_frecuencias(
                norm, comparar=bool(form["comparar"]), titulo="Frecuencia de letras del texto")
            ctx["datos"] = {
                "n_letras": len(norm),
                "distintas": int((an.contar_letras(norm) > 0).sum()),
                "ic": round(ic, 4),
                "chi2": round(an.chi_cuadrado(norm), 1),
                "interpretacion": interpretar_ic(ic, len(norm)),
                "imagen": figura_a_base64(fig),
                "tabla": an.comparar_con_espanol(norm),
            }
        except (ValueError, UnicodeError) as e:
            ctx["error"] = str(e)

    return render_template("analisis.html", form=form, ic_es=an.IC_ESPANOL,
                           ic_azar=round(an.IC_ALEATORIO, 4), **ctx)


# ===========================================================================
# 6B - Criptoanálisis (req. 8 a 12)
# ===========================================================================
def lineas_alineadas(descifrado: str, referencia: str, ancho: int = 60) -> list:
    """Divide en líneas de `ancho` letras: referencia, descifrado y marcas."""
    d = c.normalizar_texto(descifrado)
    r = c.normalizar_texto(referencia)
    marcas = marcar_diferencias(d, r)
    n = max(len(d), len(r))
    d, r, marcas = d.ljust(n), r.ljust(n), marcas.ljust(n)
    return [{"ref": r[i:i + ancho], "des": d[i:i + ancho], "marcas": marcas[i:i + ancho]}
            for i in range(0, n, ancho)]


def agregar_acierto(res: dict, descifrado: str, referencia: str) -> None:
    """Req. 12: si hay texto de referencia, mide el porcentaje de acierto."""
    if c.normalizar_texto(referencia):
        res["acierto"] = porcentaje_acierto(descifrado, referencia)
        res["alineado"] = lineas_alineadas(descifrado, referencia)


def parsear_correcciones(cadena: str) -> dict:
    """'X:E;Q:A' -> {'X': 'E', 'Q': 'A'} (la última corrección de una letra manda)."""
    corr = {}
    for par in cadena.split(";"):
        if ":" not in par:
            continue
        a, b = (c.normalizar_texto(x) for x in par.split(":", 1))
        if len(a) == 1 and len(b) == 1:
            corr.pop(a, None)
            corr[a] = b
    return corr


def serializar_correcciones(corr: dict) -> str:
    return ";".join(f"{a}:{b}" for a, b in corr.items())


def construir_mapeo(cifrado: str, corr: dict) -> "ca.MapeoAsistido":
    """El estado vive en el formulario: se reconstruye el mapeo reaplicando
    las correcciones sobre la sugerencia automática."""
    m = ca.MapeoAsistido(cifrado)
    for a, b in corr.items():
        m.fijar(a, b)
    return m


def analisis_cesar(cifrado: str, referencia: str) -> dict:
    candidatos = ca.ataque_cesar(cifrado)
    for x in candidatos:
        x["vista"] = x["texto"][:40]
    res = {"tipo": "cesar", "candidatos": candidatos, "mejor": candidatos[0]}
    agregar_acierto(res, candidatos[0]["texto"], referencia)
    return res


def analisis_vigenere(cifrado: str, referencia: str, longitud_txt: str) -> dict:
    est = ca.estimar_longitud_vigenere(cifrado, 20)
    if longitud_txt.strip():
        try:
            longitud = int(longitud_txt)
        except ValueError:
            raise ValueError("La longitud de clave debe ser un número entero.")
        if not 1 <= longitud <= min(40, len(cifrado)):
            raise ValueError("La longitud debe estar entre 1 y 40 (y no superar el texto).")
    else:
        longitud = est["sugerida"]
    clave = ca.sugerir_clave_vigenere(cifrado, longitud)
    descifrado = c.vigenere_descifrar(cifrado, clave)
    tope = max(r["ic_promedio"] for r in est["tabla"])
    for r in est["tabla"]:
        r["ancho"] = round(r["ic_promedio"] / max(tope, 0.0001) * 100)
        r["elegida"] = r["longitud"] == longitud
    res = {"tipo": "vigenere", "tabla": est["tabla"], "sugerida": est["sugerida"],
           "usada": longitud, "clave": clave, "descifrado": descifrado,
           "ic_es": an.IC_ESPANOL, "ic_azar": round(an.IC_ALEATORIO, 4)}
    agregar_acierto(res, descifrado, referencia)
    return res


def analisis_sustitucion(cifrado: str, referencia: str, form: dict, accion: str) -> dict:
    corr = parsear_correcciones(form["correcciones"])
    error = None
    if accion == "reiniciar":
        corr = {}
    elif accion.startswith("quitar:"):
        corr.pop(c.normalizar_texto(accion[7:]), None)
    elif accion == "fijar":
        a = c.normalizar_texto(form["corr_cifrada"])
        b = c.normalizar_texto(form["corr_plana"])
        if len(a) != 1 or len(b) != 1:
            error = "Indica una sola letra cifrada y una sola letra plana."
        else:
            candidata = dict(corr)
            candidata.pop(a, None)
            candidata[a] = b
            try:
                construir_mapeo(cifrado, candidata)
                corr = candidata
            except ValueError as e:
                error = str(e)

    m = construir_mapeo(cifrado, corr)
    descifrado = m.descifrar()
    celdas = sorted(m.tabla(), key=lambda t: (-t["conteo"], t["cifrada"]))
    form["correcciones"] = serializar_correcciones(corr)
    res = {"tipo": "sustitucion", "descifrado": descifrado, "celdas": celdas,
           "correcciones": list(corr.items()), "alfabeto": m.alfabeto_clave(),
           "error_local": error}
    agregar_acierto(res, descifrado, referencia)
    return res


@app.route("/criptoanalisis", methods=["GET", "POST"])
def criptoanalisis():
    form = {"texto": "", "metodo": "cesar", "referencia": "", "longitud": "",
            "correcciones": "", "corr_cifrada": "", "corr_plana": ""}
    ctx = {"error": None, "res": None}

    if request.method == "POST":
        for campo in form:
            form[campo] = request.form.get(campo, form[campo])
        accion = request.form.get("accion", "analizar")
        try:
            texto = leer_texto_entrada()
            form["texto"] = texto
            cifrado = c.normalizar_texto(texto)
            if len(cifrado) < 2:
                raise ValueError("Se necesitan al menos 2 letras válidas para analizar.")
            if form["metodo"] == "cesar":
                ctx["res"] = analisis_cesar(cifrado, form["referencia"])
            elif form["metodo"] == "vigenere":
                ctx["res"] = analisis_vigenere(cifrado, form["referencia"], form["longitud"])
            elif form["metodo"] == "sustitucion":
                ctx["res"] = analisis_sustitucion(cifrado, form["referencia"], form, accion)
            else:
                raise ValueError("Método desconocido.")
            form["corr_cifrada"] = form["corr_plana"] = ""
        except (ValueError, UnicodeError) as e:
            ctx["error"] = str(e)

    return render_template("criptoanalisis.html", form=form, **ctx)


# ===========================================================================
# 6B - Modo didáctico (req. 14)
# ===========================================================================
def calcular_didactico(form: dict, accion: str) -> dict:
    # En GET no hay formulario enviado: se usa el texto de ejemplo por defecto.
    texto = leer_texto_entrada() if request.method == "POST" else form["texto"]
    form["texto"] = texto
    norm = c.normalizar_texto(texto)
    if not norm:
        raise ValueError("El texto no contiene ninguna letra válida (A-Z, Ñ).")
    try:
        pos = int(form["posicion"])
    except ValueError:
        raise ValueError("La posición debe ser un número entero.")
    pos += {"sig": 1, "ant": -1}.get(accion, 0)
    pos = max(1, min(len(norm), pos))
    form["posicion"] = str(pos)

    metodo = form["metodo"]
    if metodo == "cesar":
        try:
            clave = int(form["desplazamiento"])
        except ValueError:
            raise ValueError("El desplazamiento debe ser un número entero.")
    elif metodo == "sustitucion":
        clave = form["alfabeto"]
    else:
        clave = form["clave"]
    explicacion = dd.explicar_caracter(metodo, norm, pos - 1, clave)

    ini, fin = max(0, pos - 1 - 30), min(len(norm), pos + 30)  # ventana de 61 letras
    return {
        "explicacion": explicacion,
        "letras": [(ch, ini + i + 1 == pos) for i, ch in enumerate(norm[ini:fin])],
        "recortado_izq": ini > 0, "recortado_der": fin < len(norm),
        "total": len(norm), "pos": pos,
        "es_posicion": metodo == "transposicion",
    }


@app.route("/didactico", methods=["GET", "POST"])
def didactico():
    form = {"texto": "Mañana atacamos al amanecer", "metodo": "cesar",
            "operacion": "cifrar", "desplazamiento": "3", "alfabeto": "",
            "clave": "LIMON", "posicion": "1", "bloques": ""}
    ctx = {"error": None, "didactico": None}
    accion = "mostrar"

    if request.method == "POST":
        for campo in form:
            form[campo] = request.form.get(campo, form[campo])
        accion = request.form.get("accion", "mostrar")

    try:
        if accion == "aleatorio":
            form["alfabeto"] = c.generar_alfabeto_aleatorio()
            form["metodo"] = "sustitucion"
            ctx["didactico"] = calcular_didactico(form, "mostrar")
        elif request.method == "GET" and not form["alfabeto"]:
            form["alfabeto"] = c.generar_alfabeto_aleatorio(semilla=1)  # ejemplo estable
            ctx["didactico"] = calcular_didactico(form, accion)
        else:
            ctx["didactico"] = calcular_didactico(form, accion)
    except (ValueError, UnicodeError) as e:
        ctx["error"] = str(e)

    return render_template("didactico.html", form=form, metodos=METODOS, **ctx)


# ===========================================================================
# 6B - Teoría (req. 15)
# ===========================================================================
@app.route("/teoria")
def teoria():
    return render_template("teoria.html", secciones=dd.explicacion_vulnerabilidad(),
                           tabla=dd.tabla_comparativa())


@app.errorhandler(413)
def archivo_muy_grande(_e):
    return render_template(
        "cifrar.html", form=formulario_por_defecto(), metodos=METODOS,
        error="El archivo supera el límite de 1 MB.", resultado=None,
        normalizado=None, encabezado=None), 413


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)