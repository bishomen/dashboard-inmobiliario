
import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import tempfile
import base64
from datetime import datetime
import os

st.set_page_config(page_title="Dashboard Inmobiliario", layout="centered")

def crear_pdf(nombre_usuario, fecha, valor_inmueble, ingreso_mensual, cashflow_anual, cap_rate, roi, cuota_credito, recomendacion):
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    c = canvas.Canvas(temp_file.name, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(colors.darkblue)
    c.drawString(50, 750, "Resumen de Rentabilidad Inmobiliaria")
    c.setFont("Helvetica", 12)
    c.setFillColor(colors.black)

    y = 720
    line_height = 20
    data = [
        f"Nombre: {nombre_usuario}",
        f"Fecha: {fecha}",
        f"Valor inmueble: ${valor_inmueble:,.0f}",
        f"Ingreso mensual: ${ingreso_mensual:,.0f}",
        f"Cash Flow anual: ${cashflow_anual:,.0f}",
        f"CAP Rate: {cap_rate:.2f}%",
        f"ROI: {roi:.2f}%",
        f"Cuota crédito: ${cuota_credito:,.0f}",
        f"Recomendación: {recomendacion}"
    ]

    for item in data:
        c.drawString(50, y, item)
        y -= line_height

    c.save()
    with open(temp_file.name, "rb") as f:
        pdf_base64 = base64.b64encode(f.read()).decode("utf-8")
    os.unlink(temp_file.name)
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

    st.metric("💸 Cash Flow Anual", f"${cashflow_anual:,.0f}")
    st.metric("📊 CAP Rate", f"{cap_rate:.2f}%")
    st.metric("📈 ROI", f"{roi:.2f}%")
    st.metric("🏦 Cuota mensual del crédito", f"${cuota_credito:,.0f}")

    if roi >= 10 and cap_rate >= 8 and cashflow_anual > 0:
        recomendacion = "COMPRAR"
    elif 5 <= roi < 10 or 5 <= cap_rate < 8:
        recomendacion = "MANTENER / ESTUDIAR"
    else:
        recomendacion = "NO INVERTIR"
    st.success(f"🧠 Recomendación: {recomendacion}")

    if st.button("📄 Exportar a PDF"):
        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        pdf_base64 = crear_pdf(nombre_usuario, fecha_actual, valor_inmueble, ingreso_mensual, cashflow_anual, cap_rate, roi, cuota_credito, recomendacion)
        st.markdown(
            f'<p style="text-align:center"><a href="data:application/pdf;base64,{pdf_base64}" '
            f'download="reporte_inmobiliario.pdf" '
            f'style="font-size:18px; color:#0a75ad; text-decoration:underline;">📥 Descargar PDF</a></p>',
            unsafe_allow_html=True
        )
