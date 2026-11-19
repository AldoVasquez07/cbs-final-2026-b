# PROYECTO FINAL: CriptoClásico

**Laboratorio de Cifrado Clásico y Criptoanálisis**

| | |
|---|---|
| **Curso** | Ciberseguridad |
| **Profesor** | Marco Antonio Camacho Alatrista |
| **Alumno** | Aldo Ray Vasquez Lopez |

---

## Descripción

CriptoClásico es una herramienta educativa que implementa cifrados clásicos, permite
cifrar y descifrar mensajes, y realiza criptoanálisis mediante análisis de frecuencia.
Su objetivo es afianzar la terminología y los métodos de ataque básicos de la Semana 14.

Está desarrollada en **Python** con **Flask**, **NumPy** y **Matplotlib**, y una interfaz
web en **HTML y CSS**.

> **Aviso:** es una herramienta para aprender. Los cifrados clásicos **no** protegen
> información real; para eso se usan algoritmos modernos como AES.

## Características

- **Cifrados:** César, sustitución monoalfabética, Vigenère y transposición de columnas
  (los cuatro con cifrado y descifrado).
- **Alfabeto español de 27 letras** (A-Z con Ñ entre la N y la O).
- **Normalización automática:** mayúsculas, sin tildes (se conserva la Ñ), sin espacios,
  números ni signos.
- **Análisis de frecuencia:** histograma, comparación con el español, índice de
  coincidencia y chi-cuadrado.
- **Criptoanálisis:** ataque a César, estimación de la longitud de clave de Vigenère (con
  recuperación de la clave), sugerencia de clave para sustitución y edición manual del
  mapeo.
- **Métrica de acierto** contra un texto de referencia.
- **Carga y descarga** de textos en archivos `.txt`.
- **Modo didáctico:** el cifrado de un carácter paso a paso.
- **Teoría:** por qué los cifrados clásicos son vulnerables y en qué se diferencian del
  cifrado moderno.

## Estructura del repositorio

```
cbs-final-2026-b/
├── documentacion/
│   ├── Manual_Usuario.pdf
│   └── Memoria_Tecnica.pdf
├── proy-cifra-cripto/
│   ├── static/
│   │   ├── campos.js
│   │   └── style.css
│   ├── templates/
│   │   ├── _campos_clave.html
│   │   ├── analisis.html
│   │   ├── base.html
│   │   ├── cifrar.html
│   │   ├── criptoanalisis.html
│   │   ├── didactico.html
│   │   └── teoria.html
│   ├── analysis.py
│   ├── app.py
│   ├── ciphers.py
│   ├── cryptanalysis.py
│   ├── demo_frecuencias.png
│   ├── demo_frecuencias_cifrado.png
│   ├── didactic.py
│   └── utils.py
├── .gitignore
├── README.md
└── requirements.txt
```

Los archivos `demo_frecuencias*.png` los genera `analysis.py` al ejecutarlo como
ejemplo de histograma.

### Qué hace cada módulo

| Archivo | Responsabilidad |
|---|---|
| `app.py` | Aplicación Flask: rutas de las cinco pestañas |
| `ciphers.py` | Cifrados clásicos y normalización del texto |
| `analysis.py` | Frecuencias, índice de coincidencia, chi² e histograma |
| `cryptanalysis.py` | Ataques automáticos y mapeo asistido |
| `utils.py` | Porcentaje de acierto y carga/guardado de archivos |
| `didactic.py` | Pasos didácticos y textos de teoría |

Los módulos `ciphers`, `analysis`, `cryptanalysis`, `utils` y `didactic` no dependen de
Flask: se pueden importar y usar desde cualquier script de Python.

## Documentación

La carpeta `documentacion/` contiene dos documentos en PDF:

| Documento | Contenido |
|---|---|
| `Manual_Usuario.pdf` | Manual de usuario: cómo instalar y usar la herramienta |
| `Memoria_Tecnica.pdf` | Memoria técnica: diseño, algoritmos y decisiones de implementación |

## Requisitos

- Python 3.10 o superior (probado con 3.12)
- Flask, NumPy y Matplotlib (listados en `requirements.txt`)

## Instalación y ejecución

Desde la raíz del repositorio (`cbs-final-2026-b/`):

```bash
# (opcional) entorno virtual
python -m venv venv
source venv/bin/activate        # en Windows: venv\Scripts\activate

pip install -r requirements.txt

cd proy-cifra-cripto
python app.py
```

Abre <http://127.0.0.1:5000> en el navegador. Para detener el servidor, `Ctrl + C`.

Cada módulo trae además una verificación rápida al final del archivo, por ejemplo
`python ciphers.py`, que imprime un mensaje de éxito si todo funciona.

## Guía de uso por pestaña

### Cifrar / Descifrar
1. Escribe un texto o carga un archivo `.txt` (el archivo tiene prioridad).
2. Elige el método y la operación; aparecen solo los campos de clave que necesita.
   - **César:** desplazamiento entero (puede ser negativo).
   - **Sustitución:** alfabeto de 27 letras distintas, o usa **Generar aleatorio**.
   - **Vigenère y transposición:** una palabra como clave.
3. **Ejecutar** muestra el texto normalizado y la salida. **Ejecutar y descargar .txt**
   guarda el resultado con un encabezado que indica el método y la clave.

### Análisis de frecuencia
Pega cualquier texto (plano o cifrado). Obtienes el histograma con la frecuencia esperada
del español superpuesta, la tabla letra por letra y el índice de coincidencia, con una
interpretación de qué tipo de cifrado es compatible.

### Criptoanálisis
Pega un texto cifrado sin conocer la clave y elige el ataque:
- **César:** prueba los 27 desplazamientos y los ordena por chi² (menor = más parecido al
  español).
- **Vigenère:** muestra el índice de coincidencia promedio por longitud de clave, sugiere
  la longitud y recupera la clave. Puedes forzar otra longitud.
- **Sustitución:** parte de una sugerencia por frecuencias y deja corregir letras
  (*cifrada → plana*). Al fijar un par, la letra plana que ya estaba usada se intercambia
  con la otra y los pares fijados quedan bloqueados. El alfabeto resultante se puede pegar
  en la pestaña Cifrar / Descifrar.

En los tres casos puedes pegar el **texto original de referencia** para ver el porcentaje
de acierto y una comparación alineada (`|` letra correcta, `.` letra incorrecta).

### Modo didáctico
Elige método, clave y la posición de una letra del texto. Verás los pasos numéricos de su
cifrado y puedes avanzar letra por letra con los botones anterior y siguiente.

### Teoría
Explicación de la vulnerabilidad al análisis de frecuencia y tabla comparativa entre
cifrado clásico y moderno.

## Cobertura de los requisitos

| Req. | Descripción | Dónde |
|---|---|---|
| 1 | César con clave configurable | `ciphers.cesar_cifrar / cesar_descifrar` |
| 2 | Sustitución con alfabeto personalizado | `ciphers.sustitucion_cifrar / sustitucion_descifrar` |
| 3 | Vigenère con clave de palabra | `ciphers.vigenere_cifrar / vigenere_descifrar` |
| 4 | Transposición de columnas | `ciphers.transposicion_cifrar / transposicion_descifrar` |
| 5 | Validar y normalizar la entrada | `ciphers.normalizar_texto` |
| 6 | Histograma de frecuencias | `analysis.grafico_frecuencias` · pestaña Análisis |
| 7 | Comparar con el español | `analysis.comparar_con_espanol` · pestaña Análisis |
| 8 | Ataque automático a César | `cryptanalysis.ataque_cesar` · pestaña Criptoanálisis |
| 9 | Longitud de clave de Vigenère (IC) | `cryptanalysis.estimar_longitud_vigenere` |
| 10 | Clave probable para sustitución | `cryptanalysis.sugerir_mapeo_sustitucion` |
| 11 | Mapeo manual asistido | `cryptanalysis.MapeoAsistido` |
| 12 | Porcentaje de acierto | `utils.porcentaje_acierto` |
| 13 | Cargar y guardar textos | `utils.cargar_texto / guardar_texto` · pestaña Cifrar |
| 14 | Cifrado de un carácter paso a paso | `didactic.explicar_caracter` · pestaña Modo didáctico |
| 15 | Vulnerabilidad vs. cifrado moderno | `didactic.explicacion_vulnerabilidad` · pestaña Teoría |

## Decisiones de diseño

- **Solo letras:** todos los cifrados trabajan sobre el texto normalizado (sin espacios ni
  signos). Es lo habitual en criptoanálisis y simplifica el análisis de frecuencia.
- **Transposición sin relleno:** no se añaden letras de relleno, así el descifrado
  recupera el texto exacto.
- **Chi-cuadrado** para puntuar candidatos en el ataque a César y en cada columna de
  Vigenère.
- **Porcentaje de acierto posicional:** compara letra por letra; si el descifrado pierde o
  añade una letra, las siguientes se desfasan y bajan el porcentaje.
- **Sin sesiones:** en el criptoanálisis de sustitución, las correcciones viajan en un
  campo oculto del formulario y el servidor reconstruye el mapeo en cada envío.
- **Límites de archivos:** solo `.txt`, hasta 1 MB, en UTF-8 o Latin-1.

## Limitaciones

- La tabla de frecuencias del español es una referencia aproximada.
- El análisis de frecuencia, el índice de coincidencia y el ataque a Vigenère necesitan
  textos de al menos unos cientos de letras para ser fiables; con textos cortos los
  resultados pueden ser engañosos.
- La sugerencia automática para sustitución suele acertar solo parte de las letras: está
  pensada como punto de partida para el ajuste manual.
- El servidor integrado de Flask es para desarrollo y uso local, no para producción.

## Autor

**Aldo Ray Vasquez Lopez**
Curso de Ciberseguridad · Profesor Marco Antonio Camacho Alatrista