import streamlit as st
import pandas as pd
import io

# ── Configuración ───────────────────────────────────────
st.set_page_config(page_title="Cargador de Datos", page_icon="📊", layout="wide")

st.title("📊 Cargador de Datos")
st.caption("Carga archivos CSV o Excel y explora fácilmente")

# ── Función de carga segura ─────────────────────────────
@st.cache_data
def cargar_archivo(file, sheet_name=0):
    nombre = file.name.lower()
    bytes_data = file.read()

    try:
        if nombre.endswith(".csv"):
            contenido = bytes_data.decode("utf-8", errors="replace")
            sep = ";" if contenido.count(";") > contenido.count(",") else ","
            return pd.read_csv(io.StringIO(contenido), sep=sep)

        elif nombre.endswith((".xlsx", ".xls")):
            return pd.read_excel(io.BytesIO(bytes_data), sheet_name=sheet_name)

    except Exception as e:
        return None

    return None


# ── Sidebar ────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Opciones")
    filas = st.slider("Filas a mostrar", 5, 100, 20)
    mostrar_nulos = st.checkbox("Resaltar nulos", True)
    mostrar_stats = st.checkbox("Mostrar estadísticas", False)


# ── Upload ─────────────────────────────────────────────
archivo = st.file_uploader("Sube tu archivo", type=["csv", "xlsx", "xls"])

if not archivo:
    st.info("👆 Sube un archivo para comenzar")
    st.stop()


# ── Selección de hoja (Excel) ──────────────────────────
sheet = 0
if archivo.name.endswith((".xlsx", ".xls")):
    try:
        excel = pd.ExcelFile(archivo)
        hojas = excel.sheet_names

        if len(hojas) > 1:
            sheet = st.selectbox("Selecciona hoja", hojas)
        else:
            sheet = hojas[0]

    except Exception:
        st.warning("No se pudieron leer las hojas del Excel")


# ── Cargar datos ───────────────────────────────────────
df = cargar_archivo(archivo, sheet)

if df is None:
    st.error("❌ No se pudo leer el archivo. Verifica el formato.")
    st.stop()


# ── Métricas ───────────────────────────────────────────
c1, c2, c3 = st.columns(3)
c1.metric("Filas", df.shape[0])
c2.metric("Columnas", df.shape[1])
c3.metric("Nulos", int(df.isnull().sum().sum()))


# ── Selección de columnas ──────────────────────────────
cols = st.multiselect("Columnas a mostrar", df.columns, default=df.columns)
df_view = df[cols] if cols else df


# ── Vista de datos ─────────────────────────────────────
st.subheader("📋 Vista de datos")

try:
    if mostrar_nulos:
        st.dataframe(
            df_view.head(filas).style.highlight_null(color="red"),
            use_container_width=True
        )
    else:
        st.dataframe(df_view.head(filas), use_container_width=True)

except Exception:
    st.dataframe(df_view.head(filas), use_container_width=True)


# ── Estadísticas ───────────────────────────────────────
if mostrar_stats:
    st.subheader("📈 Estadísticas")
    try:
        st.dataframe(df_view.describe(include="all"), use_container_width=True)
    except Exception:
        st.warning("No se pudieron generar estadísticas")


st.metric("Promedio precio", round(df["precio_unitario"].mean(), 2))
st.write(df.describe())

# ── Descargas ──────────────────────────────────────────
st.divider()
c1, c2 = st.columns(2)

# CSV siempre disponible
with c1:
    st.download_button(
        "⬇ Descargar CSV",
        df.to_csv(index=False).encode("utf-8"),
        "datos.csv",
        "text/csv"
    )

