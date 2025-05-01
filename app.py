# archivo: app.py
import streamlit as st

st.set_page_config(page_title="Calculadora Inmobiliaria", layout="centered")

st.title("📋 Ingreso de datos del inmueble")

st.subheader("1. Información del inmueble")
valor_inmueble = st.number_input("💰 Valor de compra del inmueble (COP)", min_value=0.0, step=1000000.0, format="%.0f")
ingreso_mensual = st.number_input("🏠 Ingreso mensual por arriendo (COP)", min_value=0.0, step=100000.0, format="%.0f")

st.subheader("2. Inversión inicial y gastos")
cuota_inicial = st.number_input("💵 Cuota inicial (COP)", min_value=0.0, step=1000000.0, format="%.0f")
gastos_mensuales = st.number_input("🧾 Gastos mensuales (administración, seguros, etc.)", min_value=0.0, step=10000.0, format="%.0f")
gastos_anuales = st.number_input("📆 Costos fijos anuales (impuestos, mantenimiento)", min_value=0.0, step=100000.0, format="%.0f")

st.subheader("3. Crédito hipotecario")
usar_credito = st.checkbox("¿Usar crédito hipotecario?")

if usar_credito:
    monto_credito = st.number_input("🏦 Monto del crédito (COP)", min_value=0.0, step=1000000.0, format="%.0f")
    tasa_interes = st.number_input("📈 Tasa de interés anual (%)", min_value=0.0, max_value=100.0, step=0.1)
    plazo_credito = st.number_input("📅 Plazo del crédito (años)", min_value=1, max_value=30, step=1)
else:
    monto_credito = 0.0
    tasa_interes = 0.0
    plazo_credito = 0

# Guardar datos en sesión (para usar en siguientes módulos)
st.session_state["datos_inmueble"] = {
    "valor_inmueble": valor_inmueble,
    "ingreso_mensual": ingreso_mensual,
    "cuota_inicial": cuota_inicial,
    "gastos_mensuales": gastos_mensuales,
    "gastos_anuales": gastos_anuales,
    "usar_credito": usar_credito,
    "monto_credito": monto_credito,
    "tasa_interes": tasa_interes,
    "plazo_credito": plazo_credito,
}

if st.button("✅ Guardar y continuar"):
    st.success("Datos guardados. Puedes avanzar al siguiente módulo.")

# Continúa en app.py debajo del módulo 1

st.title("📊 Cálculo de Rentabilidad Inmobiliaria")

datos = st.session_state.get("datos_inmueble", {})

if not datos:
    st.warning("Primero debes ingresar los datos del inmueble en el Módulo 1.")
else:
    # Extraer datos
    valor_inmueble = datos["valor_inmueble"]
    ingreso_mensual = datos["ingreso_mensual"]
    cuota_inicial = datos["cuota_inicial"]
    gastos_mensuales = datos["gastos_mensuales"]
    gastos_anuales = datos["gastos_anuales"]
    usar_credito = datos["usar_credito"]
    monto_credito = datos["monto_credito"]
    tasa_interes = datos["tasa_interes"] / 100
    plazo_credito = datos["plazo_credito"]

    # Calcular cuota mensual del crédito (si aplica)
    if usar_credito and monto_credito > 0:
        tasa_mensual = tasa_interes / 12
        n_cuotas = plazo_credito * 12
        cuota_mensual_credito = (monto_credito * tasa_mensual) / (1 - (1 + tasa_mensual)**-n_cuotas)
    else:
        cuota_mensual_credito = 0.0

    # Cálculos
    ingreso_anual = ingreso_mensual * 12
    gastos_totales_anuales = (gastos_mensuales * 12) + gastos_anuales + (cuota_mensual_credito * 12)

    cashflow_anual = ingreso_anual - gastos_totales_anuales
    cap_rate = (ingreso_anual / valor_inmueble) * 100 if valor_inmueble > 0 else 0
    roi = (cashflow_anual / cuota_inicial) * 100 if cuota_inicial > 0 else 0

    # Mostrar resultados
    st.subheader("📈 Resultados de la inversión")
    st.metric("💸 Cash Flow Anual", f"${cashflow_anual:,.0f}")
    st.metric("📊 CAP Rate", f"{cap_rate:.2f} %")
    st.metric("📈 ROI Anual Estimado", f"{roi:.2f} %")
    if usar_credito:
        st.metric("🏦 Cuota mensual del crédito", f"${cuota_mensual_credito:,.0f}")

    if roi >= 10:
        st.success("👍 Excelente rentabilidad. Vale la pena estudiar esta inversión.")
    elif 5 <= roi < 10:
        st.warning("⚠️ Rentabilidad moderada. Depende de tus objetivos de inversión.")
    else:
        st.error("🔻 Rentabilidad baja. Revisa costos o ingreso esperado.")
# Continúa en app.py después del Módulo 2

st.title("🧠 Recomendación de Inversión")

# Nos aseguramos de que ya se hayan hecho los cálculos en el módulo 2
if not datos or valor_inmueble == 0 or cuota_inicial == 0:
    st.warning("Por favor completa los módulos anteriores primero.")
else:
    # Lógica de recomendación
    if roi >= 10 and cap_rate >= 8 and cashflow_anual > 0:
        recomendacion = "🟢 Recomendación: COMPRAR. Alta rentabilidad y flujo positivo."
        color = "green"
    elif 5 <= roi < 10 or 5 <= cap_rate < 8:
        recomendacion = "🟡 Recomendación: MANTENER / ESTUDIAR. Rentabilidad moderada, hay que analizar más."
        color = "orange"
    else:
        recomendacion = "🔴 Recomendación: NO INVERTIR. Baja rentabilidad o flujo negativo."
        color = "red"

    # Mostrar recomendación destacada
    st.markdown(f"<h3 style='color:{color}'>{recomendacion}</h3>", unsafe_allow_html=True)
    
    # Justificación detallada
    st.markdown("### 📝 Justificación")
    st.markdown(f"- **ROI estimado:** {roi:.2f}%")
    st.markdown(f"- **Cap Rate:** {cap_rate:.2f}%")
    st.markdown(f"- **Cash Flow anual:** ${cashflow_anual:,.0f}")
    if usar_credito:
        st.markdown(f"- **Incluye crédito con cuota mensual de:** ${cuota_mensual_credito:,.0f}")

