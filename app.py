
import streamlit as st
from datetime import datetime
import base64
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import simpleSplit
import tempfile
import os

st.set_page_config(page_title="Dashboard Inversión Inmobiliaria", layout="centered")

st.title(" Dashboard de Inversión Inmobiliaria")

st.sidebar.header("Parámetros de la inversión")

valor_inmueble = st.sidebar.number_input(" Valor del inmueble (COP)", min_value=0.0, step=1000000.0, format="%.0f")
ingreso_mensual = st.sidebar.number_input(" Ingreso mensual por renta (COP)", min_value=0.0, step=100000.0, format="%.0f")
gastos_mensuales = st.sidebar.number_input(" Gastos mensuales (COP)", min_value=0.0, step=10000.0, format="%.0f")
gastos_anuales = st.sidebar.number_input(" Gastos anuales fijos (COP)", min_value=0.0, step=100000.0, format="%.0f")
cuota_inicial = st.sidebar.number_input(" Inversión inicial (cuota inicial + remodelación) (COP)", min_value=0.0, step=1000000.0, format="%.0f")

usar_credito = st.sidebar.checkbox("¿Usar crédito hipotecario?")
if usar_credito:
    monto_credito = st.sidebar.number_input(" Monto del crédito (COP)", min_value=0.0, step=1000000.0, format="%.0f")
    tasa_interes_anual = st.sidebar.number_input(" Tasa de interés anual (%)", min_value=0.0, max_value=100.0, step=0.1)
    plazo_anios = st.sidebar.slider(" Plazo del crédito (años)", 1, 30, 15)
else:
    monto_credito = 0
    tasa_interes_anual = 0
    plazo_anios = 0

ingreso_anual = ingreso_mensual * 12
tasa_mensual = (tasa_interes_anual / 100) / 12
n_cuotas = plazo_anios * 12 if usar_credito else 0
cuota_mensual = (monto_credito * tasa_mensual) / (1 - (1 + tasa_mensual) ** -n_cuotas) if usar_credito and tasa_mensual > 0 else 0
gastos_totales = gastos_mensuales * 12 + gastos_anuales + cuota_mensual * 12
cashflow_anual = ingreso_anual - gastos_totales

cap_rate = (ingreso_anual / valor_inmueble) * 100 if valor_inmueble else 0
roi = (cashflow_anual / cuota_inicial) * 100 if cuota_inicial else 0
payback = cuota_inicial / cashflow_anual if cashflow_anual > 0 else None
rentabilidad_bruta = (ingreso_anual / valor_inmueble) * 100 if valor_inmueble else 0
rentabilidad_neta = (cashflow_anual / valor_inmueble) * 100 if valor_inmueble else 0
price_to_rent = valor_inmueble / ingreso_anual if ingreso_anual else None

if roi >= 10 and cap_rate >= 8 and cashflow_anual > 0:
    recomendacion = " COMPRAR"
elif roi >= 5 and cashflow_anual > 0:
    recomendacion = " MANTENER / REVISAR"
else:
    recomendacion = " NO INVERTIR"

# Resultados
st.subheader(" Indicadores financieros")
col1, col2 = st.columns(2)

with col1:
    st.metric(" CAP Rate (%)", f"{cap_rate:.2f}%", help="CAP Rate = (Ingreso anual / Valor del inmueble) × 100.   \nMide la rentabilidad bruta del inmueble sin crédito. Representa la tasa de retorno de una propiedad asumiendo que se compra en su totalidad con efectivo, es decir, " \
    "sin utilizar ningún tipo de financiamiento (como un crédito hipotecario). Su principal utilidad es permitir una comparación rápida de la rentabilidad de diferentes propiedades, ya que elimina el factor de la deuda. Un CAP Rate alto (por ejemplo, por encima del 8%) " \
    "generalmente indica una propiedad con mayor potencial de retorno, pero a menudo implica un mayor riesgo o que la propiedad se encuentra en una zona menos consolidada. Un CAP Rate bajo (por debajo del 5%) puede señalar una inversión más segura y estable, en una ubicación " \
    "de alta demanda con menor riesgo, pero con un retorno de alquiler más modesto. ")
    
    st.metric(" Rentabilidad Bruta (%)", f"{rentabilidad_bruta:.2f}%", help="Rentabilidad Bruta = (Ingreso anual / Valor del inmueble) × 100.  La Rentabilidad Bruta es una métrica simple que se utiliza para tener una idea rápida de la rentabilidad de una inversión inmobiliaria " \
    "a través del alquiler, sin tomar en cuenta los gastos asociados. Utilidad: Sirve como un primer filtro para comparar rápidamente diferentes propiedades, ya que te da un porcentaje del retorno que podrías obtener anualmente solo con los ingresos del alquiler. Sin embargo, no es un " \
    "indicador preciso del beneficio real, ya que ignora los gastos como impuestos, seguros, mantenimiento, etc.." )
    
    
    
    st.metric(" ROI (%)", f"{roi:.2f}%", help="ROI = (Flujo de caja anual / Inversión real) × 100. El Retorno de la Inversión (ROI), o Return on Investment, es una métrica fundamental que mide la eficiencia o la rentabilidad de una inversión. Indica la cantidad de dinero que se gana " \
    "o se pierde en relación con la cantidad de dinero invertido. Un ROI anual considerado bueno para una propiedad de alquiler suele estar entre el 8% y el 12%. Menos del 5%: Generalmente se considera un ROI bajo, lo que podría indicar que los gastos son muy altos en comparación con los ingresos o que el precio de compra fue elevado."
    "Entre 5% y 8%: Es un rango aceptable, especialmente en mercados estables y con poca volatilidad. Más del 12%: Se considera un ROI excelente, que a menudo se encuentra en propiedades que requieren reformas, o en mercados con una alta demanda y precios de alquiler competitivos. ")
    
    
    
    
    st.metric(" Payback. (Período de Recuperación)", f"{payback:.2f}" if payback else "No aplica", help="Payback = Inversión real / Flujo de Caja Neto Anual. Es una métrica financiera que se utiliza para determinar el tiempo que tardará un inversionista en recuperar el capital total que invirtió en un proyecto. ")

with col2:
   
    st.metric(" Rentabilidad Neta (%)", f"{rentabilidad_neta:.2f}%", help="Rentabilidad Neta = (Cash Flow anual / Valor del inmueble) × 100. es una métrica más precisa que la Rentabilidad Bruta, ya que mide la rentabilidad real de una inversión inmobiliaria por alquiler, después de descontar todos los gastos asociados.")
   
   
    st.metric(" Price-to-Rent (Relación Precio-Alquiler) ", f"{price_to_rent:.2f}" if price_to_rent else "No aplica", help="Price-to-Rent = Valor del inmueble / Ingreso anual\nIdeal: Menor a 15 años. es un indicador que se utiliza para comparar el costo de comprar una propiedad con el costo de alquilarla en un mercado específico." \
    "Su objetivo principal es ayudar a determinar si es más ventajoso financieramente comprar una vivienda o seguir alquilando en un área determinada. Ratio alto (mayor a 21): El mercado es más favorable para alquilar. Esto sugiere que los precios de las viviendas son muy altos en comparación con los alquileres, lo que hace que comprar sea una opción más costosa." \
    "Ratio moderado (entre 15 y 20): Es un mercado equilibrado. Comprar y alquilar son opciones financieramente similares." \
    "Ratio bajo (menor a 15): El mercado es más favorable para comprar. Los precios de las viviendas son relativamente bajos en comparación con los alquileres, lo que hace que la compra sea una opción más atractiva desde el punto de vista de la inversión.  ")
   
   
    st.metric(" Cash Flow anual (Flujo de Caja Anual)", f"${cashflow_anual:,.0f}", help="Ingreso anual - Gastos anuales (incluye crédito). es la ganancia o pérdida neta que genera una propiedad durante un año, después de que se han pagado todos los gastos. Es una de las métricas más " \
    "importantes para los inversionistas, ya que muestra si el inmueble está generando ganancias constantes o si, por el contrario, requiere de dinero adicional para mantenerse. Cash Flow Positivo: La propiedad genera más ingresos de los que gasta. Esta es la situación ideal para un inversionista, ya que el inmueble se paga solo y genera una ganancia adicional." \
    "Cash Flow Negativo: La propiedad genera más gastos de los que ingresa. En este caso, el dueño debe poner dinero de su bolsillo cada mes para mantener la inversión. Esto podría ser aceptable si el inversionista espera una plusvalía muy alta en el futuro. ")
   
   
    st.metric(" Cuota mensual crédito", f"${cuota_mensual:,.0f}" if usar_credito else "No aplica", help="Cuota estimada del crédito según tasa y plazo")


st.subheader(" Recomendación de inversión")
st.success(recomendacion)

# Justificación detallada
st.markdown("### 📌 Análisis y justificación de indicadores")
if cap_rate >= 8:
    st.success("✔️ CAP Rate alto: buena rentabilidad.")
elif cap_rate >= 5:
    st.info("➖ CAP Rate moderado.")
else:
    st.warning("⚠️ CAP Rate bajo.")

if rentabilidad_bruta >= 10:
    st.success("✔️ Rentabilidad bruta excelente.")
elif rentabilidad_bruta >= 6:
    st.info("➖ Rentabilidad bruta aceptable.")
else:
    st.warning("⚠️ Rentabilidad bruta baja.")

if rentabilidad_neta >= 8:
    st.success("✔️ Rentabilidad neta sólida.")
elif rentabilidad_neta >= 4:
    st.info("➖ Rentabilidad neta aceptable.")
else:
    st.warning("⚠️ Rentabilidad neta insuficiente.")

if payback and payback <= 10:
    st.success(f"✔️ Payback corto ({payback:.2f} años).")
elif payback and payback <= 15:
    st.info(f"➖ Payback moderado ({payback:.2f} años).")
elif payback:
    st.warning(f"⚠️ Payback largo ({payback:.2f} años).")

if price_to_rent and price_to_rent <= 15:
    st.success(f"✔️ Price-to-Rent bajo ({price_to_rent:.2f}).")
elif price_to_rent and price_to_rent <= 20:
    st.info(f"➖ Price-to-Rent moderado ({price_to_rent:.2f}).")
elif price_to_rent:
    st.warning(f"⚠️ Price-to-Rent alto ({price_to_rent:.2f}).")

# Exportar PDF con análisis
def generar_pdf():
    ruta_pdf = os.path.join(tempfile.gettempdir(), f"reporte_completo_{datetime.now().timestamp()}.pdf")
    c = canvas.Canvas(ruta_pdf, pagesize=letter)
    w, h = letter

    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(colors.darkblue)
    c.drawString(50, h - 50, " Informe de Inversión Inmobiliaria")

    y = h - 80
    c.setFont("Helvetica", 12)
    campos = [
        ("Valor inmueble", f"${valor_inmueble:,.0f}"),
        ("Ingreso mensual", f"${ingreso_mensual:,.0f}"),
        ("Cash Flow anual", f"${cashflow_anual:,.0f}"),
        ("CAP Rate", f"{cap_rate:.2f}%"),
        ("Rentabilidad Bruta", f"{rentabilidad_bruta:.2f}%"),
        ("Rentabilidad Neta", f"{rentabilidad_neta:.2f}%"),
        ("ROI", f"{roi:.2f}%"),
        ("Payback", f"{payback:.2f}" if payback else "No aplica"),
        ("Price-to-Rent", f"{price_to_rent:.2f}" if price_to_rent else "No aplica"),
        ("Recomendación", recomendacion)
    ]
    for campo, valor in campos:
        c.setFont("Helvetica-Bold", 11)
        c.drawString(50, y, f"{campo}:")
        c.setFont("Helvetica", 11)
        c.drawString(250, y, valor)
        y -= 20

    y -= 10
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Justificación:")
    y -= 20
    comentarios = [
        ("CAP Rate", cap_rate, [(8, "✔️ Alto"), (5, "➖ Moderado"), (0, "⚠️ Bajo")]),
        ("Rentabilidad Bruta", rentabilidad_bruta, [(10, "✔️ Excelente"), (6, "➖ Aceptable"), (0, "⚠️ Baja")]),
        ("Rentabilidad Neta", rentabilidad_neta, [(8, "✔️ Sólida"), (4, "➖ Aceptable"), (0, "⚠️ Insuficiente")]),
        ("Payback", payback or 0, [(0, "❌ Sin Cash Flow")] if not payback else [(10, "✔️ Corto"), (15, "➖ Moderado"), (999, "⚠️ Largo")]),
        ("Price-to-Rent", price_to_rent or 0, [(15, "✔️ Bajo"), (20, "➖ Moderado"), (999, "⚠️ Alto")])
    ]
    for nombre, valor, rangos in comentarios:
        for umbral, mensaje in rangos:
            if valor <= umbral:
                txt = f"{mensaje} {nombre}: {valor:.2f}" if valor else f"{mensaje} {nombre}: No aplica"
                for l in simpleSplit(txt, "Helvetica", 10, w - 100):
                    c.drawString(50, y, l)
                    y -= 14
                break

    c.save()
    with open(ruta_pdf, "rb") as f:
        return base64.b64encode(f.read()).decode()

if st.button(" Descargar informe PDF"):
    pdf64 = generar_pdf()
    st.markdown(
        f'<a href="data:application/pdf;base64,{pdf64}" download="reporte_inversion.pdf">📥 Descargar PDF</a>',
        unsafe_allow_html=True
    )
