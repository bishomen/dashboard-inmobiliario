
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import simpleSplit
import tempfile
import base64
from datetime import datetime
import os

st.set_page_config(page_title="Dashboard Inmobiliario", layout="centered")

def generar_justificacion(roi, cap_rate, cashflow_anual, recomendacion):
    razones_buenas = []
    razones_malas = []

    if roi >= 10:
        razones_buenas.append("el ROI es alto (superior al 10%)")
    elif roi >= 5:
        razones_buenas.append("el ROI es moderado (entre 5% y 10%)")
    else:
        razones_malas.append("el ROI es bajo (menor al 5%)")

    if cap_rate >= 8:
        razones_buenas.append("el CAP Rate es alto (superior al 8%)")
    elif cap_rate >= 5:
        razones_buenas.append("el CAP Rate es moderado (entre 5% y 8%)")
    else:
        razones_malas.append("el CAP Rate es bajo")

    if cashflow_anual > 0:
        razones_buenas.append("el flujo de caja anual es positivo")
    else:
        razones_malas.append("el flujo de caja anual es negativo")

    justificacion = f"Se recomienda {recomendacion.upper()} porque "
    if recomendacion == "COMPRAR":
        justificacion += ", ".join(razones_buenas) + "."
    elif recomendacion == "MANTENER / ESTUDIAR":
        justificacion += "se deben considerar factores mixtos como: " + ", ".join(razones_buenas + razones_malas) + "."
    else:
        justificacion += ", ".join(razones_malas)
        if razones_buenas:
            justificacion += ", a pesar de que " + ", ".join(razones_buenas)
        justificacion += "."

    return justificacion

def crear_pdf(nombre_usuario, fecha, valor_inmueble, ingreso_mensual, cashflow_anual, cap_rate, roi, cuota_credito, recomendacion, justificacion):
    tmpdir = tempfile.gettempdir()
    ruta_pdf = os.path.join(tmpdir, f"reporte_{datetime.now().timestamp()}.pdf")

    c = canvas.Canvas(ruta_pdf, pagesize=letter)
    width, height = letter

    c.setFillColor(colors.darkblue)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 50, "📊 Informe de Rentabilidad Inmobiliaria")

    c.setFont("Helvetica", 12)
    c.setFillColor(colors.black)
    c.drawString(50, height - 70, f"Generado por: {nombre_usuario} | Fecha: {fecha}")
    c.line(50, height - 75, width - 50, height - 75)

    y = height - 100
    espaciado = 18
    campos = [
        ("Valor del inmueble", f"${valor_inmueble:,.0f}"),
        ("Ingreso mensual", f"${ingreso_mensual:,.0f}"),
        ("Cash Flow anual", f"${cashflow_anual:,.0f}"),
        ("CAP Rate", f"{cap_rate:.2f}%"),
        ("ROI estimado", f"{roi:.2f}%"),
        ("Cuota mensual crédito", f"${cuota_credito:,.0f}"),
    ]

    for titulo, valor in campos:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, f"{titulo}:")
        c.setFont("Helvetica", 12)
        c.drawString(250, y, valor)
        y -= espaciado

    y -= 15
    c.setFont("Helvetica-Bold", 14)
    color = colors.green if recomendacion == "COMPRAR" else colors.orange if "MANTENER" in recomendacion else colors.red
    c.setFillColor(color)
    c.drawString(50, y, f"📌 Recomendación final: {recomendacion.upper()}")

    y -= 30
    c.setFont("Helvetica", 11)
    c.setFillColor(colors.black)

    lineas = simpleSplit(justificacion, "Helvetica", 11, width - 100)
    for linea in lineas:
        c.drawString(50, y, linea)
        y -= 15

    c.save()

    with open(ruta_pdf, "rb") as f:
        pdf_base64 = base64.b64encode(f.read()).decode("utf-8")

    os.remove(ruta_pdf)
    return pdf_base64

# Interfaz
st.sidebar.header("Información del usuario")
nombre_usuario = st.sidebar.text_input("Tu nombre:", value="Inversionista")

st.title("📊 Calculadora de Rentabilidad Inmobiliaria")

valor_inmueble = st.number_input("💰 Valor de compra (COP)", min_value=0.0, step=1000000.0, format="%.0f")
ingreso_mensual = st.number_input("🏠 Ingreso mensual (COP)", min_value=0.0, step=100000.0, format="%.0f")
cuota_inicial = st.number_input("💵 Cuota inicial (COP)", min_value=0.0, step=1000000.0, format="%.0f")
gastos_mensuales = st.number_input("🧾 Gastos mensuales", min_value=0.0, step=10000.0, format="%.0f")
gastos_anuales = st.number_input("📆 Costos fijos anuales", min_value=0.0, step=100000.0, format="%.0f")

usar_credito = st.checkbox("¿Usar crédito hipotecario?")
if usar_credito:
    monto_credito = st.number_input("🏦 Monto del crédito (COP)", min_value=0.0, step=1000000.0, format="%.0f")
    tasa_interes = st.number_input("📈 Tasa de interés anual (%)", min_value=0.0, max_value=100.0, step=0.1)
    plazo_credito = st.number_input("📅 Plazo (años)", min_value=1, max_value=30, step=1)
else:
    monto_credito = 0.0
    tasa_interes = 0.0
    plazo_credito = 0

if st.button("✅ Calcular rentabilidad"):
    if usar_credito and monto_credito > 0:
        tasa_mensual = tasa_interes / 100 / 12
        n_cuotas = plazo_credito * 12
        cuota_credito = (monto_credito * tasa_mensual) / (1 - (1 + tasa_mensual)**-n_cuotas)
    else:
        cuota_credito = 0.0

    ingreso_anual = ingreso_mensual * 12
    gastos_total = gastos_mensuales * 12 + gastos_anuales + cuota_credito * 12
    cashflow_anual = ingreso_anual - gastos_total
    cap_rate = (ingreso_anual / valor_inmueble) * 100 if valor_inmueble else 0
    roi = (cashflow_anual / cuota_inicial) * 100 if cuota_inicial else 0

    if roi >= 10 and cap_rate >= 8 and cashflow_anual > 0:
        recomendacion = "COMPRAR"
    elif 5 <= roi < 10 or 5 <= cap_rate < 8:
        recomendacion = "MANTENER / ESTUDIAR"
    else:
        recomendacion = "NO INVERTIR"

    justificacion = generar_justificacion(roi, cap_rate, cashflow_anual, recomendacion)

    st.session_state.resultado = {
        "nombre_usuario": nombre_usuario,
        "fecha": datetime.now().strftime("%d/%m/%Y"),
        "valor_inmueble": valor_inmueble,
        "ingreso_mensual": ingreso_mensual,
        "cashflow_anual": cashflow_anual,
        "cap_rate": cap_rate,
        "roi": roi,
        "cuota_credito": cuota_credito,
        "recomendacion": recomendacion,
        "justificacion": justificacion
    }

    st.metric("💸 Cash Flow Anual", f"${cashflow_anual:,.0f}")
    st.metric("📊 CAP Rate", f"{cap_rate:.2f}%")
    st.metric("📈 ROI", f"{roi:.2f}%")
    st.metric("🏦 Cuota mensual del crédito", f"${cuota_credito:,.0f}")
    st.success(f"🧠 Recomendación: {recomendacion}")
    st.info("📌 " + justificacion)

if "resultado" in st.session_state:
    if st.button("📄 Exportar a PDF"):
        r = st.session_state.resultado
        pdf_base64 = crear_pdf(
            r["nombre_usuario"], r["fecha"], r["valor_inmueble"], r["ingreso_mensual"],
            r["cashflow_anual"], r["cap_rate"], r["roi"], r["cuota_credito"],
            r["recomendacion"], r["justificacion"]
        )
        st.markdown(
            f'<a href="data:application/pdf;base64,{pdf_base64}" '
            f'download="reporte_inmobiliario.pdf" '
            f'style="font-size:18px; color:#0a75ad; text-decoration:underline;">📥 Descargar PDF</a>',
            unsafe_allow_html=True
        )
