import streamlit as st
import pdfkit
import tempfile
import base64
import os
from datetime import datetime

st.set_page_config(page_title="Dashboard Inmobiliario", layout="centered")

path_wkhtmltopdf = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

def generar_pdf_base64(html):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmpfile:
        pdfkit.from_string(html, tmpfile.name, configuration=config)
    with open(tmpfile.name, "rb") as f:
        pdf_base64 = base64.b64encode(f.read()).decode("utf-8")
    os.unlink(tmpfile.name)
    return pdf_base64

st.sidebar.header("Información del usuario")
nombre_usuario = st.sidebar.text_input("Tu nombre:", value="Inversionista")

st.title("🏘️ Calculadora de Rentabilidad Inmobiliaria")

st.header("1. Datos del inmueble")
valor_inmueble = st.number_input("💰 Valor de compra del inmueble (COP)", min_value=0.0, step=1000000.0, format="%.0f")
ingreso_mensual = st.number_input("🏠 Ingreso mensual por arriendo (COP)", min_value=0.0, step=100000.0, format="%.0f")

st.header("2. Inversión inicial y gastos")
cuota_inicial = st.number_input("💵 Cuota inicial (COP)", min_value=0.0, step=1000000.0, format="%.0f")
gastos_mensuales = st.number_input("🧾 Gastos mensuales (administración, seguros, etc.)", min_value=0.0, step=10000.0, format="%.0f")
gastos_anuales = st.number_input("📆 Costos fijos anuales (impuestos, mantenimiento)", min_value=0.0, step=100000.0, format="%.0f")

st.header("3. Crédito hipotecario")
usar_credito = st.checkbox("¿Usar crédito hipotecario?")

if usar_credito:
    monto_credito = st.number_input("🏦 Monto del crédito (COP)", min_value=0.0, step=1000000.0, format="%.0f")
    tasa_interes = st.number_input("📈 Tasa de interés anual (%)", min_value=0.0, max_value=100.0, step=0.1)
    plazo_credito = st.number_input("📅 Plazo del crédito (años)", min_value=1, max_value=30, step=1)
else:
    monto_credito = 0.0
    tasa_interes = 0.0
    plazo_credito = 0

if st.button("✅ Calcular rentabilidad"):
    st.subheader("📊 Resultados de la inversión")

    if usar_credito and monto_credito > 0:
        tasa_mensual = tasa_interes / 100 / 12
        n_cuotas = plazo_credito * 12
        cuota_mensual_credito = (monto_credito * tasa_mensual) / (1 - (1 + tasa_mensual)**-n_cuotas)
    else:
        cuota_mensual_credito = 0.0

    ingreso_anual = ingreso_mensual * 12
    gastos_totales_anuales = (gastos_mensuales * 12) + gastos_anuales + (cuota_mensual_credito * 12)
    cashflow_anual = ingreso_anual - gastos_totales_anuales

    cap_rate = (ingreso_anual / valor_inmueble) * 100 if valor_inmueble > 0 else 0
    roi = (cashflow_anual / cuota_inicial) * 100 if cuota_inicial > 0 else 0

    st.metric("💸 Cash Flow Anual", f"${cashflow_anual:,.0f}")
    st.metric("📊 CAP Rate", f"{cap_rate:.2f} %")
    st.metric("📈 ROI Anual Estimado", f"{roi:.2f} %")
    if usar_credito:
        st.metric("🏦 Cuota mensual del crédito", f"${cuota_mensual_credito:,.0f}")

    st.header("🧠 Recomendación de inversión")
    if roi >= 10 and cap_rate >= 8 and cashflow_anual > 0:
        recomendacion = "🟢 Recomendación: COMPRAR. Alta rentabilidad y flujo positivo."
    elif 5 <= roi < 10 or 5 <= cap_rate < 8:
        recomendacion = "🟡 Recomendación: MANTENER / ESTUDIAR. Rentabilidad moderada, analizar más."
    else:
        recomendacion = "🔴 Recomendación: NO INVERTIR. Baja rentabilidad o flujo negativo."

    st.markdown(f"<h3 style='color:#0a75ad'>{recomendacion}</h3>", unsafe_allow_html=True)

    if st.button("📄 Exportar resultados a PDF"):
        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        resumen_html = f"""
        <h2>📊 Resumen de Rentabilidad Inmobiliaria</h2>
        <p><b>Nombre:</b> {nombre_usuario}<br>
        <b>Fecha:</b> {fecha_actual}</p>
        <ul>
            <li><b>Valor inmueble:</b> ${valor_inmueble:,.0f}</li>
            <li><b>Ingreso mensual:</b> ${ingreso_mensual:,.0f}</li>
            <li><b>Cash Flow anual:</b> ${cashflow_anual:,.0f}</li>
            <li><b>CAP Rate:</b> {cap_rate:.2f}%</li>
            <li><b>ROI:</b> {roi:.2f}%</li>
            <li><b>Cuota crédito:</b> ${cuota_mensual_credito:,.0f}</li>
            <li><b>Recomendación:</b> {recomendacion}</li>
        </ul>
        """
        pdf_base64 = generar_pdf_base64(resumen_html)
        st.markdown(
            f'<p style="text-align:center"><a href="data:application/pdf;base64,{pdf_base64}" '
            f'download="reporte_inmobiliario.pdf" '
            f'style="font-size:18px; color:#0a75ad; text-decoration:underline;">📥 Descargar PDF</a></p>',
            unsafe_allow_html=True
        )
