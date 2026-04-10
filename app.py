import streamlit as st
import pandas as pd
import io

# ── Configuración ─────────────────────────────────────────
st.set_page_config(page_title="Cargador de Datos", page_icon="📊", layout="wide")

st.title("📊 Cargador de Datos")
st.caption("Sube archivos CSV o Excel y explora rápidamente")

# ── Función de carga ─────────────────────────────────────
@st.cache_data
def cargar_archivo(file, sheet_name=0):
    nombre = file.name.lower()
    bytes_data = file.read()

    if nombre.endswith(".csv"):
        contenido = bytes_data.decode("utf-8", errors="replace")
        sep = ";" if contenido.count(";") > contenido.count(",") else ","
        return pd.read_csv(io.StringIO(contenido), sep=sep)

    elif nombre.endswith((".xlsx", ".xls")):
        return pd.read_excel(io.BytesIO(bytes_data), sheet_name=sheet_name)

    return None


# ── Sidebar ──────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Opciones")
    filas = st.slider("Filas a mostrar", 5, 100, 20)
    mostrar_nulos = st.checkbox("Resaltar nulos", True)
    mostrar_stats = st.checkbox("Estadísticas", False)


# ── Upload ───────────────────────────────────────────────
archivo = st.file_uploader("Sube tu archivo", type=["csv", "xlsx", "xls"])

if not archivo:
    st.info("👆 Sube un archivo para comenzar")
    st.stop()


# ── Excel: selección de hoja ─────────────────────────────
sheet = 0
if archivo.name.endswith((".xlsx", ".xls")):
    excel = pd.ExcelFile(archivo)
    hojas = excel.sheet_names

    if len(hojas) > 1:
        sheet = st.selectbox("Selecciona hoja", hojas)
    else:
        sheet = hojas[0]


# ── Carga ───────────────────────────────────────────────
df = cargar_archivo(archivo, sheet)

if df is None:
    st.error("No se pudo leer el archivo")
    st.stop()


# ── Métricas ────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
col1.metric("Filas", df.shape[0])
col2.metric("Columnas", df.shape[1])
col3.metric("Nulos", int(df.isnull().sum().sum()))


# ── Filtro columnas ─────────────────────────────────────
cols = st.multiselect("Columnas", df.columns, default=df.columns)
df_view = df[cols] if cols else df


# ── DataFrame ───────────────────────────────────────────
st.subheader("Vista de datos")

if mostrar_nulos:
    st.dataframe(df_view.head(filas).style.highlight_null(color="red"))
else:
    st.dataframe(df_view.head(filas))


# ── Estadísticas ────────────────────────────────────────
if mostrar_stats:
    st.subheader("Estadísticas")
    st.dataframe(df_view.describe(include="all"))


# ── Descarga ────────────────────────────────────────────
st.divider()

c1, c2 = st.columns(2)

with c1:
    st.download_button(
        "Descargar CSV",
        df.to_csv(index=False).encode("utf-8"),
        "datos.csv",
        "text/csv"
    )

with c2:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)

    st.download_button(
        "Descargar Excel",
        buffer.getvalue(),
        "datos.xlsx"
    )
