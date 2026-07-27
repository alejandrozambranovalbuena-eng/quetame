"""
Sistema Inteligente de Alerta Temprana — Quetame (Cundinamarca)
Dashboard interactivo construido con Streamlit + Plotly.

Autores: Alejandro Zambrano Valbuena · Camilo Torres Hernández (Concejal de Quetame).
Especialización en Nuevas Tecnologías e Innovación y Gestión de Ciudades — Universidad Externado de Colombia.

Este dashboard es un PROTOTIPO INTERACTIVO de la solución propuesta: parte de datos reales
del proyecto y de fuentes periodísticas verificadas (evento real del 17-18 de julio de 2023 en
Naranjal, Quetame) y simula, con fines demostrativos, la capa de monitoreo en tiempo real que
tendría el sistema una vez instalado.
"""

import time
import json
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ============================================================================
# VERSIÓN Y CHANGELOG (visible solo en un expander discreto, no en cabecera/pie)
# ============================================================================
VERSION = "9.0"

AUTORES = ["Alejandro Zambrano Valbuena", "Camilo Torres Hernández — Concejal de Quetame",
           "Leticia Floralba González", "Javier Alejandro Flórez", "Cristian Sneyder Rodríguez Aguilar"]

# ============================================================================
# CONFIG GENERAL
# ============================================================================
st.set_page_config(
    page_title="Quetame IoT — Alerta Temprana",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

ORANGE, ORANGE_DARK, ORANGE_BG = "#FF441F", "#D8340F", "#FFE4DB"
BLUE, BLUE_DARK, BLUE_BG = "#155EEF", "#0B3FA8", "#DCE8FF"
GREEN, GREEN_DARK, GREEN_BG = "#00B879", "#00875A", "#D4F7E9"
PURPLE, PURPLE_DARK, PURPLE_BG = "#7C3AED", "#5B21B6", "#EDE1FE"
RED, RED_DARK, RED_BG = "#F0323C", "#B0141C", "#FFDEDF"
AMBER, AMBER_DARK, AMBER_BG = "#FFA800", "#B36B00", "#FFEDC2"
PINK, PINK_BG = "#EC4899", "#FCE4F1"
TEXT_DARK, TEXT_GRAY = "#14161A", "#4B5563"
CARD_BORDER = "#ECEDF1"
TRM_COP = 3206.86  # TRM Banco de la República, 23 de julio de 2026

CUSTOM_CSS = f"""
<style>
    .stApp {{ background-color: #ffffff; }}
    .block-container {{ padding-top: 1.4rem; max-width: 1300px; }}
    h1, h2, h3, h4 {{ color: {TEXT_DARK} !important; font-weight: 800; }}

    .hero {{
        background: linear-gradient(120deg, #ffffff 60%, {ORANGE_BG} 100%);
        border-radius: 22px; padding: 26px 34px; margin-bottom: 14px;
        border: 1px solid {CARD_BORDER}; box-shadow: 0 2px 14px rgba(20,20,30,0.05);
    }}
    .eyebrow {{
        display: inline-block; font-size: 12.5px; font-weight: 800; letter-spacing: 1.2px;
        padding: 5px 14px; border-radius: 20px; margin-bottom: 10px;
    }}
    .eyebrow.o {{ background: {ORANGE_BG}; color: {ORANGE_DARK}; }}
    .eyebrow.r {{ background: {RED_BG}; color: {RED_DARK}; }}
    .eyebrow.g {{ background: {GREEN_BG}; color: {GREEN_DARK}; }}
    .eyebrow.b {{ background: {BLUE_BG}; color: {BLUE_DARK}; }}
    .eyebrow.p {{ background: {PURPLE_BG}; color: {PURPLE_DARK}; }}
    .vbadge {{
        display:inline-block; background:{TEXT_DARK}; color:#fff; font-size:11.5px; font-weight:800;
        padding: 3px 10px; border-radius: 8px; margin-left: 8px; vertical-align: middle;
    }}
    .authors {{ display:flex; gap:10px; flex-wrap:wrap; margin-top:10px; }}
    .author-chip {{
        display:flex; align-items:center; gap:8px; background:#fff; border:1px solid {CARD_BORDER};
        border-radius:30px; padding:6px 14px 6px 6px; font-size:13px; font-weight:700; color:{TEXT_DARK};
        box-shadow: 0 1px 6px rgba(20,20,30,0.04);
    }}
    .author-avatar {{
        width:26px; height:26px; border-radius:50%; display:flex; align-items:center; justify-content:center;
        color:#fff; font-size:12px; font-weight:800;
    }}

    div[data-testid="stMetric"] {{
        background-color: #ffffff; border: 1px solid {CARD_BORDER};
        border-radius: 14px; padding: 14px 18px; box-shadow: 0 1px 6px rgba(20,20,30,0.03);
    }}
    div[data-testid="stMetricLabel"] {{ color: {TEXT_GRAY} !important; }}
    div[data-testid="stMetricValue"] {{ color: {ORANGE_DARK} !important; }}

    .card {{
        background: #ffffff; border: 1px solid {CARD_BORDER}; border-radius: 16px;
        padding: 20px 22px; margin-bottom: 14px; box-shadow: 0 1px 8px rgba(20,20,30,0.03);
    }}
    .card h3, .card h4 {{ margin-top: 0; color: {TEXT_DARK} !important; }}
    .card p {{ color: #333844; font-size: 14px; line-height: 1.6; }}
    .card ul {{ color: #333844; font-size: 13.5px; line-height: 1.6; margin: 6px 0 0 0; padding-left: 18px; }}
    .card.orange {{ border-left: 6px solid {ORANGE}; }}
    .card.teal   {{ border-left: 6px solid {GREEN}; }}
    .card.purple {{ border-left: 6px solid {PURPLE}; }}
    .card.blue   {{ border-left: 6px solid {BLUE}; }}
    .card.red    {{ border-left: 6px solid {RED}; }}
    .card.pink   {{ border-left: 6px solid {PINK}; }}
    .card.fill-red    {{ background: {RED_BG}; border: none; }}
    .card.fill-green  {{ background: {GREEN_BG}; border: none; }}
    .card.fill-blue   {{ background: {BLUE_BG}; border: none; }}
    .card.fill-orange {{ background: {ORANGE_BG}; border: none; }}
    .card.fill-purple {{ background: {PURPLE_BG}; border: none; }}
    .card.clickable {{ cursor: pointer; }}

    .actor-head {{ display:flex; align-items:center; gap:10px; margin-bottom:6px; }}
    .actor-icon {{
        width:42px; height:42px; border-radius:12px; display:flex; align-items:center; justify-content:center;
        font-size:20px; color:#fff;
    }}

    .quote {{
        border-left: 4px solid {ORANGE}; background: {ORANGE_BG}; padding: 14px 18px;
        font-style: italic; color: #7a2c15; border-radius: 0 10px 10px 0;
    }}
    .sensor-card {{
        background:#fff; border:1px solid {CARD_BORDER}; border-radius:14px; padding:14px 16px;
        box-shadow: 0 1px 6px rgba(20,20,30,0.03);
    }}
    .step {{
        background:#fff; border:1px solid {CARD_BORDER}; border-radius:14px; padding:16px; text-align:center;
        height: 100%;
    }}
    .step .n {{
        width:34px;height:34px;border-radius:50%;background:{ORANGE};color:#fff;font-weight:800;
        display:flex;align-items:center;justify-content:center;margin:0 auto 8px auto;
    }}
    a {{ color: {BLUE} !important; font-weight: 600; }}

    .phone {{
        width: 270px; margin: 0 auto; border: 10px solid #111318; border-radius: 34px;
        overflow: hidden; background: #f2f3f5; box-shadow: 0 10px 30px rgba(0,0,0,0.18);
    }}
    .phone .bar {{ background:#111318; height:22px; display:flex; align-items:center; justify-content:center; }}
    .phone .notch {{ width:56px; height:12px; background:#000; border-radius:8px; }}
    .phone .screen {{ padding: 14px 12px; min-height: 300px; }}
    .bubble-red {{
        background:{RED}; color:#fff; padding:10px 14px; border-radius:14px 14px 14px 3px;
        font-size:12.5px; line-height:1.5; margin-bottom:8px;
    }}
    .bubble-green {{
        background:#25D366; color:#fff; padding:10px 14px; border-radius:14px 14px 14px 3px;
        font-size:12.5px; line-height:1.5; margin-bottom:8px;
    }}
    .bubble-user {{
        background:#ffffff; color:{TEXT_DARK}; padding:8px 12px; border-radius:14px 14px 14px 3px;
        font-size:12px; line-height:1.45; margin-bottom:7px; border:1px solid {CARD_BORDER};
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }}
    .bubble-user .who {{ font-size:10.5px; font-weight:800; color:{BLUE}; display:block; margin-bottom:2px; }}
    .river-tank {{
        width:56px; height:190px; border:3px solid {TEXT_DARK}; border-radius:10px; position:relative;
        overflow:hidden; background:#eef2fb; margin: 0 auto;
    }}
    .river-fill {{
        position:absolute; bottom:0; left:0; width:100%;
        background: linear-gradient(180deg, #6db4ff, {BLUE});
    }}

    .console {{ border:1px solid {CARD_BORDER}; border-radius:16px; overflow:hidden; }}
    .console .bar2 {{ background:{TEXT_DARK}; color:#fff; padding:12px 18px; font-weight:800; }}

    .section-banner {{
        background: linear-gradient(120deg, {TEXT_DARK}, #232838);
        border-radius: 20px; padding: 22px 30px; margin: 18px 0 10px 0;
    }}
    .section-banner h2 {{ color:#fff !important; margin:0; }}
    .section-banner p {{ color:#c7cbd6; margin:4px 0 0 0; font-size:14px; }}

    .big-title {{ font-size: 24px !important; font-weight: 900 !important; color:{ORANGE_DARK} !important; margin: 4px 0 10px 0; }}

    /* Tabs — más vivas, tipo pill */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px; background:#F7F7F9; padding:10px; border-radius:18px; border:1px solid {CARD_BORDER};
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: #ffffff; border-radius: 999px !important; padding: 10px 20px;
        border: 1px solid {CARD_BORDER}; font-weight: 800; color: {TEXT_GRAY}; font-size: 14.5px;
    }}
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, {ORANGE}, {ORANGE_DARK}) !important; color: #fff !important;
        border: none; box-shadow: 0 4px 12px rgba(255,68,31,0.3);
    }}

    /* Botones — cobran vida al pasar el mouse */
    .stButton > button {{
        border-radius: 14px !important; font-weight: 800 !important; padding: 10px 18px !important;
        border: 1px solid {CARD_BORDER} !important; background: #ffffff !important; color: {TEXT_DARK} !important;
        box-shadow: 0 1px 6px rgba(20,20,30,0.05);
        transition: transform 0.18s cubic-bezier(.34,1.56,.64,1), box-shadow 0.18s ease, border-color 0.18s ease, color 0.18s ease !important;
    }}
    .stButton > button:hover {{
        border-color: {ORANGE} !important; color: {ORANGE_DARK} !important;
        transform: translateY(-3px) scale(1.035);
        box-shadow: 0 10px 22px rgba(255,68,31,0.22) !important;
    }}
    .stButton > button:active {{ transform: translateY(-1px) scale(0.98); box-shadow: 0 3px 10px rgba(20,20,30,0.15) !important; }}
    button[kind="primary"] {{
        background: linear-gradient(135deg, {ORANGE}, {ORANGE_DARK}) !important; color:#fff !important;
        border: none !important; box-shadow: 0 4px 14px rgba(255,68,31,0.3) !important;
        transition: transform 0.18s cubic-bezier(.34,1.56,.64,1), box-shadow 0.18s ease, filter 0.18s ease !important;
    }}
    button[kind="primary"]:hover {{
        transform: translateY(-3px) scale(1.045) !important;
        box-shadow: 0 14px 26px rgba(255,68,31,0.42) !important;
        filter: brightness(1.06);
        color: #fff !important;
    }}
    button[kind="primary"]:active {{ transform: translateY(-1px) scale(0.98) !important; }}

    /* Tarjetas y pasos — leve elevación al pasar el mouse */
    .card, .step, .sensor-card {{ transition: transform 0.2s ease, box-shadow 0.2s ease; }}
    .card:hover, .step:hover, .sensor-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 10px 24px rgba(20,20,30,0.10);
    }}
    .stTabs [data-baseweb="tab"] {{ transition: transform 0.15s ease; }}
    .stTabs [data-baseweb="tab"]:hover {{ transform: translateY(-2px); }}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
PLOTLY_TEMPLATE = "plotly_white"


def cop(usd_low, usd_high=None):
    def fmt(u):
        v = round(u * TRM_COP, -3)
        return f"${v:,.0f}".replace(",", ".")
    if usd_high is None:
        return fmt(usd_low)
    return f"{fmt(usd_low)} – {fmt(usd_high)}"


def section_banner(title, subtitle):
    st.markdown(f"""
    <div class="section-banner">
      <h2>{title}</h2>
      <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


# ============================================================================
# DATOS REALES DEL PROYECTO
# ============================================================================

ACTORES = [
    {"Hélice": "Gobierno", "icon": "🏛", "color": "blue", "fill": BLUE,
     "Actores": "Alcaldía de Quetame, Concejo Municipal, UNGRD, IDEAM, MinTIC",
     "Rol": "Liderar la implementación y articulación institucional",
     "Aporta": "Financiación, normatividad, gestión del riesgo, operación institucional",
     "Funciones": [
         "Financiar la instalación de sensores y la plataforma",
         "Emitir la normativa municipal de gestión del riesgo",
         "Coordinar la cadena de alerta institucional",
         "Autorizar y liderar la evacuación cuando se activa la alerta roja",
     ]},
    {"Hélice": "Academia", "icon": "🎓", "color": "purple", "fill": PURPLE,
     "Actores": "Universidad Externado de Colombia, universidades aliadas, investigadores",
     "Rol": "Desarrollo técnico y análisis científico",
     "Aporta": "Investigación, analítica de datos, IA, validación metodológica, capacitación",
     "Funciones": [
         "Diseñar y entrenar el modelo predictivo de riesgo",
         "Validar metodológicamente los umbrales de alerta",
         "Formar operadores locales en el uso de la plataforma",
         "Evaluar resultados y proponer mejoras cada 6 meses",
     ]},
    {"Hélice": "Sector privado", "icon": "🏢", "color": "orange", "fill": ORANGE,
     "Actores": "Operadores tecnológicos, empresas IoT, telecomunicaciones, desarrolladores de software",
     "Rol": "Proveer infraestructura y soluciones tecnológicas",
     "Aporta": "Sensores, conectividad, plataformas digitales, soporte técnico",
     "Funciones": [
         "Instalar y mantener los sensores IoT en campo",
         "Garantizar conectividad LoRaWAN/4G en zona rural",
         "Operar y escalar la plataforma cloud (Context Broker)",
         "Dar soporte técnico durante alertas activas",
     ]},
    {"Hélice": "Comunidad", "icon": "👥", "color": "teal", "fill": GREEN,
     "Actores": "Juntas de Acción Comunal, líderes comunitarios, habitantes de zonas de riesgo",
     "Rol": "Participación y apropiación social del sistema",
     "Aporta": "Reporte ciudadano, vigilancia comunitaria, cultura de prevención, respuesta temprana",
     "Funciones": [
         "Reportar novedades de campo mediante la app ciudadana",
         "Participar en simulacros de evacuación cada 6 meses",
         "Vigilar y cuidar los sensores cercanos a sus viviendas",
         "Formar líderes que multipliquen la cultura de prevención",
     ]},
]
ACTORES_DF = pd.DataFrame([{k: v for k, v in a.items() if k in ("Hélice", "Actores", "Rol", "Aporta")} for a in ACTORES])

RIESGOS = pd.DataFrame([
    {"Riesgo técnico": "Daño o robo de sensores", "Estrategia de mitigación": "Mantenimiento periódico y protección física de equipos en campo", "Severidad": "Media"},
    {"Riesgo técnico": "Falta de conectividad rural", "Estrategia de mitigación": "Redes redundantes LoRaWAN + 4G/5G en zonas de montaña", "Severidad": "Alta"},
    {"Riesgo técnico": "Falsas alarmas", "Estrategia de mitigación": "Validación automática de eventos mediante IA cruzada con datos del IDEAM", "Severidad": "Media"},
    {"Riesgo técnico": "Baja precisión del modelo predictivo", "Estrategia de mitigación": "Entrenamiento continuo con nuevos datos históricos y de campo", "Severidad": "Alta"},
    {"Riesgo técnico": "Baja apropiación comunitaria", "Estrategia de mitigación": "Talleres, simulacros y formación continua de líderes comunitarios", "Severidad": "Media"},
    {"Riesgo técnico": "Dependencia energética (zonas sin red eléctrica)", "Estrategia de mitigación": "Panel solar + batería de respaldo con autonomía ≥72 h por nodo", "Severidad": "Alta"},
    {"Riesgo técnico": "Punto único de falla en la nube", "Estrategia de mitigación": "Modo degradado: umbral de alerta autónomo en el gateway local sin depender de internet", "Severidad": "Alta"},
    {"Riesgo técnico": "Privacidad de datos ciudadanos", "Estrategia de mitigación": "Cifrado TLS extremo a extremo y cumplimiento de la Ley 1581 de 2012 (Habeas Data)", "Severidad": "Media"},
])

PROTOCOLOS = pd.DataFrame([
    {"Capa": "1&2 · Captura", "Tecnología / Enlace": "Nodos a concentrador", "Protocolo": "LoRaWAN (EU868)", "Tipo": "Sencillo / inalámbrico"},
    {"Capa": "1&2 · Captura", "Tecnología / Enlace": "Energía de los nodos", "Protocolo": "Panel solar + batería (≥72 h autonomía)", "Tipo": "Resiliencia energética"},
    {"Capa": "3 · Plataforma", "Tecnología / Enlace": "Envío a servidor cloud", "Protocolo": "MQTT sobre TLS", "Tipo": "Ligero e integrable"},
    {"Capa": "3 · Plataforma", "Tecnología / Enlace": "Ingesta de datos climáticos", "Protocolo": "API REST (JSON) — IDEAM", "Tipo": "Servicios públicos"},
    {"Capa": "3 · Plataforma", "Tecnología / Enlace": "Continuidad sin internet", "Protocolo": "Modo degradado local (umbral autónomo)", "Tipo": "Resiliencia operativa"},
    {"Capa": "5 · Alertas", "Tecnología / Enlace": "Gateway de mensajería", "Protocolo": "HTTPS Webhook", "Tipo": "SMS / WhatsApp"},
    {"Capa": "5 · Alertas", "Tecnología / Enlace": "Enlace de sirenas físicas", "Protocolo": "Relé RF activo", "Tipo": "Operación directa"},
    {"Capa": "Transversal", "Tecnología / Enlace": "Protección de datos ciudadanos", "Protocolo": "Cifrado TLS + Ley 1581 de 2012 (Habeas Data)", "Tipo": "Cumplimiento normativo"},
])

ESPECIFICACIONES = pd.DataFrame([
    {"Capa": "1&2 · Captura", "Especificación": "Frecuencia de muestreo", "Valor objetivo": "Lluvia: cada 5 min · Movimiento: continuo"},
    {"Capa": "1&2 · Captura", "Especificación": "Autonomía energética", "Valor objetivo": "≥ 72 horas sin sol (batería + panel solar)"},
    {"Capa": "1&2 · Captura", "Especificación": "Redundancia", "Valor objetivo": "Doble sensor en variables críticas (humedad y movimiento)"},
    {"Capa": "3 · Plataforma", "Especificación": "Latencia de ingesta", "Valor objetivo": "< 30 segundos sensor → nube"},
    {"Capa": "3 · Plataforma", "Especificación": "Disponibilidad objetivo (uptime)", "Valor objetivo": "> 99%"},
    {"Capa": "4 · IA", "Especificación": "Frecuencia de recálculo del índice de riesgo", "Valor objetivo": "Cada 5 minutos"},
    {"Capa": "4 · IA", "Especificación": "Reentrenamiento del modelo", "Valor objetivo": "Mensual, con nuevos datos de campo"},
    {"Capa": "5 · Alertas", "Especificación": "Latencia de despliegue de alerta", "Valor objetivo": "< 5 minutos desde la detección"},
    {"Capa": "5 · Alertas", "Especificación": "Canales simultáneos", "Valor objetivo": "SMS + WhatsApp + sirena + app móvil"},
    {"Capa": "6 · Acción", "Especificación": "Tiempo de respuesta institucional", "Valor objetivo": "< 15 minutos (cadena Alcaldía → UNGRD → Bomberos/Defensa Civil)"},
])

KPIS = pd.DataFrame([
    {"Indicador": "Tiempo de alerta (sensor → notificación)", "Meta a 24 meses": "< 5 minutos", "Avance actual": 0},
    {"Indicador": "Cobertura de sensores en zonas críticas", "Meta a 24 meses": "100% (Naranjal + El Algodonal)", "Avance actual": 0},
    {"Indicador": "Tasa de falsas alarmas", "Meta a 24 meses": "< 10%", "Avance actual": 0},
    {"Indicador": "Líderes comunitarios (JAC) capacitados", "Meta a 24 meses": "> 80%", "Avance actual": 0},
    {"Indicador": "Disponibilidad de la plataforma (uptime)", "Meta a 24 meses": "> 99%", "Avance actual": 0},
])

COSTOS = pd.DataFrame([
    {"Concepto": "Sensor IoT por punto (lluvia + humedad + movimiento)", "Estimado (COP)": cop(150, 400) + " / unidad", "Nota": "Sujeto a cotización con proveedor"},
    {"Concepto": "Gateway LoRaWAN", "Estimado (COP)": cop(300, 800) + " / unidad", "Nota": "Cobertura aprox. 5–15 km en zona de montaña"},
    {"Concepto": "Plataforma cloud + Context Broker", "Estimado (COP)": cop(3000, 8000) + " / año", "Nota": "Varía según volumen de datos"},
    {"Concepto": "Mensajería masiva SMS/WhatsApp", "Estimado (COP)": cop(50, 200) + " / mes", "Nota": "Según número de suscriptores"},
    {"Concepto": "Mantenimiento y capacitación anual", "Estimado (COP)": "Variable", "Nota": "Depende del alcance pactado con la Alcaldía"},
])

ANTES_DESPUES = pd.DataFrame([
    {"Dimensión": "Tiempo de reacción", "Sin sistema (hoy)": "Horas, después del evento", "Con el sistema": "Minutos, antes del evento"},
    {"Dimensión": "Información disponible", "Sin sistema (hoy)": "Ninguna en tiempo real", "Con el sistema": "Lluvia, humedad y movimiento cada 5 min"},
    {"Dimensión": "Coordinación institucional", "Sin sistema (hoy)": "Reactiva y dispersa", "Con el sistema": "Protocolo automático Alcaldía → UNGRD → Bomberos"},
    {"Dimensión": "Confianza ciudadana", "Sin sistema (hoy)": "Baja (no hay aviso previo)", "Con el sistema": "Alertas verificadas y multicanal"},
    {"Dimensión": "Pérdidas evitables", "Sin sistema (hoy)": "Vidas y viviendas en riesgo constante", "Con el sistema": "Evacuación preventiva antes del colapso"},
])

ACTIVIDADES = [
    ("Fase 1 · Diagnóstico y diseño", "Identificación de zonas de riesgo", "Alcaldía + Gestión del Riesgo", 1, 2, "Mapa de zonas críticas priorizadas"),
    ("Fase 1 · Diagnóstico y diseño", "Recolección de información histórica y técnica", "IDEAM + Alcaldía", 1, 3, "Base de datos histórica consolidada"),
    ("Fase 1 · Diagnóstico y diseño", "Diseño del sistema IoT", "Empresa tecnológica + Academia", 2, 4, "Documento de arquitectura técnica"),
    ("Fase 1 · Diagnóstico y diseño", "Socialización inicial con la comunidad", "Alcaldía + Líderes comunitarios", 3, 5, "Acta de socialización comunitaria"),
    ("Fase 1 · Diagnóstico y diseño", "Formulación técnica final del proyecto", "Alcaldía + Consultor", 4, 6, "Proyecto técnico aprobado"),
    ("Fase 2 · Implementación", "Compra de sensores y equipos", "Alcaldía", 6, 7, "Equipos adquiridos"),
    ("Fase 2 · Implementación", "Instalación de sensores (lluvia, suelo, sismo)", "Empresa tecnológica", 7, 10, "Red de sensores instalada"),
    ("Fase 2 · Implementación", "Implementación de red IoT", "Empresa TIC", 8, 10, "Red LoRaWAN operativa"),
    ("Fase 2 · Implementación", "Desarrollo de plataforma (dashboard)", "Empresa software", 8, 11, "Plataforma / dashboard funcional"),
    ("Fase 2 · Implementación", "Pruebas del sistema", "Alcaldía + Empresa", 10, 12, "Informe de pruebas y ajustes"),
    ("Fase 3 · Capacitación (paralela)", "Talleres comunitarios", "Alcaldía + Gestión del Riesgo", 6, 24, "Comunidad capacitada (registro de asistencia)"),
    ("Fase 3 · Capacitación (paralela)", "Campañas de sensibilización", "Alcaldía", 6, 24, "Material de sensibilización difundido"),
    ("Fase 3 · Capacitación (paralela)", "Formación de líderes comunitarios", "Alcaldía", 8, 20, "Líderes JAC certificados"),
    ("Fase 3 · Capacitación (paralela)", "Simulacros de evacuación (cada 6 meses)", "Bomberos + Defensa Civil", 6, 24, "Informe de simulacro"),
    ("Fase 4 · Operación y seguimiento", "Monitoreo en tiempo real", "Alcaldía", 12, 24, "Plataforma operando 24/7"),
    ("Fase 4 · Operación y seguimiento", "Activación de alertas (permanente)", "Gestión del Riesgo", 12, 24, "Protocolo de alerta activo"),
    ("Fase 4 · Operación y seguimiento", "Mantenimiento de sensores (cada 6 meses)", "Empresa tecnológica", 12, 24, "Bitácora de mantenimiento"),
    ("Fase 4 · Operación y seguimiento", "Evaluación de resultados", "Alcaldía + Academia", 18, 24, "Informe de evaluación de impacto"),
]
crono = pd.DataFrame(ACTIVIDADES, columns=["Fase", "Actividad", "Responsable", "Mes inicio", "Mes fin", "Entregable"])
BASE_DATE = datetime(2026, 7, 1)
crono["Inicio"] = crono["Mes inicio"].apply(lambda m: BASE_DATE + timedelta(days=30 * (m - 1)))
crono["Fin"] = crono["Mes fin"].apply(lambda m: BASE_DATE + timedelta(days=30 * m))
crono["Duración (meses)"] = crono["Mes fin"] - crono["Mes inicio"]

ZONAS = {
    "El Algodonal": {"lat": 4.3295, "lon": -73.8365, "estado": "🔴 Riesgo alto",
                      "sensores": ["Pluviómetro EA-01", "Sensor de humedad EA-02", "Sensor de movimiento EA-03"]},
    "Naranjal": {"lat": 4.3402, "lon": -73.8288, "estado": "🟡 Riesgo medio",
                  "sensores": ["Pluviómetro NJ-01", "Sensor de humedad NJ-02", "Sensor de nivel de río NJ-03"]},
    "Casco urbano Quetame": {"lat": 4.3333, "lon": -73.8333, "estado": "🟢 Monitoreo normal",
                              "sensores": ["Pluviómetro CU-01", "Sensor de humedad CU-02"]},
}


HIST_CALIBRACION = pd.DataFrame([
    {"Fecha": "2021-03-14", "Zona": "El Algodonal", "Lluvia acumulada (mm)": 38, "Humedad previa (%)": 62, "Resultado": "🟢 Sin evento"},
    {"Fecha": "2022-06-02", "Zona": "Naranjal", "Lluvia acumulada (mm)": 55, "Humedad previa (%)": 71, "Resultado": "🟡 Movimiento menor"},
    {"Fecha": "2023-07-17", "Zona": "Naranjal", "Lluvia acumulada (mm)": 92, "Humedad previa (%)": 85, "Resultado": "🔴 Deslizamiento (evento real)"},
    {"Fecha": "2024-04-09", "Zona": "El Algodonal", "Lluvia acumulada (mm)": 47, "Humedad previa (%)": 68, "Resultado": "🟢 Sin evento"},
    {"Fecha": "2024-11-22", "Zona": "El Algodonal", "Lluvia acumulada (mm)": 61, "Humedad previa (%)": 74, "Resultado": "🟡 Movimiento menor"},
    {"Fecha": "2025-05-30", "Zona": "Naranjal", "Lluvia acumulada (mm)": 44, "Humedad previa (%)": 58, "Resultado": "🟢 Sin evento"},
    {"Fecha": "2025-09-12", "Zona": "El Algodonal", "Lluvia acumulada (mm)": 78, "Humedad previa (%)": 80, "Resultado": "🟡 Movimiento menor"},
])


def analizar_similitud_historica(lluvia_acumulada_sim, humedad_previa_sim):
    """Heurística ilustrativa: compara el escenario simulado contra los registros
    históricos de calibración y devuelve una 'confianza del modelo' (0-100) y el
    evento histórico más parecido. No es un modelo de ML real, es un proxy simple
    de distancia euclidiana pensado para dar contexto de decisión."""
    mejor = None
    mejor_dist = None
    for _, row in HIST_CALIBRACION.iterrows():
        d_lluvia = row["Lluvia acumulada (mm)"] - lluvia_acumulada_sim
        d_hum = row["Humedad previa (%)"] - humedad_previa_sim
        dist = (d_lluvia ** 2 + d_hum ** 2) ** 0.5
        if mejor_dist is None or dist < mejor_dist:
            mejor_dist, mejor = dist, row
    confianza = int(max(35, min(97, round(100 - mejor_dist * 1.05))))
    return confianza, mejor


COMPARATIVA_KPI = pd.DataFrame({
    "Indicador": ["Tiempo de respuesta (min)", "Cobertura de sensores (%)", "Canales de alerta activos", "Actores institucionales coordinados"],
    "Antes (hoy)": [180, 0, 0, 1],
    "Meta a 24 meses": [5, 100, 4, 4],
})


ETAPAS_DESLIZAMIENTO = ["Suelo estable", "Saturación del suelo", "Grietas y micro-movimientos",
                        "Ladera inestable", "Deslizamiento en curso"]


def etapa_idx(r, umbral_ia):
    if r < 30:
        return 0
    elif r < 50:
        return 1
    elif r < 70:
        return 2
    elif r < umbral_ia:
        return 3
    return 4


def render_escalada(idx):
    colores = [GREEN, AMBER, "#FF8A00", RED, "#7A0E14"]
    chips = ""
    for i, nombre in enumerate(ETAPAS_DESLIZAMIENTO):
        activo = i == idx
        bg = colores[i] if activo else "#F0F1F4"
        fg = "#fff" if activo else TEXT_GRAY
        peso = "800" if activo else "600"
        chips += (f'<div style="flex:1;text-align:center;background:{bg};color:{fg};font-weight:{peso};'
                  f'font-size:11px;padding:8px 4px;border-radius:8px;margin:0 3px;">{i+1}. {nombre}</div>')
    return f'<div style="display:flex;">{chips}</div>'


def river_3d_figure(nivel_cm, nivel_critico, key_suffix=""):
    xs = np.linspace(-9, 9, 22)
    ys = np.linspace(0, 70, 46)
    X, Y = np.meshgrid(xs, ys)
    # Cauce serpenteante (meandro) para que se vea como un río real, no un canal recto
    meandro = 3.2 * np.sin(Y / 11) + 1.4 * np.sin(Y / 5 + 1.2)
    Xc = X - meandro
    terrain = 3.0 - 2.6 * np.exp(-(Xc ** 2) / 10) - 0.05 * Y + 0.10 * np.sin(Y / 4.5)
    nivel_escalado = np.clip((nivel_cm - 10) / max(nivel_critico, 1) * 2.9, 0.15, 3.0)
    agua = np.where(terrain < nivel_escalado, nivel_escalado, np.nan)

    fig = go.Figure()
    fig.add_trace(go.Surface(
        z=terrain, x=X, y=Y, showscale=False, opacity=1.0, name="Terreno",
        colorscale=[[0, "#8a6a45"], [0.45, "#7a9b5a"], [1, "#3f7a3a"]],
        lighting=dict(ambient=0.6, diffuse=0.7, roughness=0.9, specular=0.05),
    ))
    fig.add_trace(go.Surface(
        z=agua, x=X, y=Y, showscale=False, opacity=0.9, name="Agua",
        colorscale=[[0, "#8ecfff"], [1, BLUE]],
    ))
    fig.update_layout(
        height=460, margin=dict(l=0, r=0, t=10, b=0), paper_bgcolor="rgba(0,0,0,0)",
        scene=dict(
            xaxis=dict(visible=False), yaxis=dict(visible=False),
            zaxis=dict(visible=False, range=[0, 3.2]),
            camera=dict(eye=dict(x=0.9, y=-2.6, z=1.35)),
            aspectratio=dict(x=0.75, y=2.4, z=0.35),
        ),
    )
    return fig


def filtro_texto(df: pd.DataFrame, query: str) -> pd.DataFrame:
    if not query:
        return df
    q = query.lower()
    mask = df.apply(lambda col: col.astype(str).str.lower().str.contains(q, na=False))
    return df[mask.any(axis=1)]


# ============================================================================
# CUADROS EMERGENTES (st.dialog)
# ============================================================================
@st.dialog("❗ El problema, en detalle")
def dialog_problema():
    st.markdown("""
    ##### Línea de tiempo del evento real que originó este proyecto
    """)
    linea = pd.DataFrame([
        {"Fecha": "17 de julio de 2023, ~11:15 p.m.", "Evento": "Desbordamiento de varias quebradas en la vereda El Naranjal, Quetame"},
        {"Fecha": "18 de julio de 2023", "Evento": "Confirmadas ~20 muertes y 9 personas desaparecidas; más de 20 viviendas y una escuela afectadas"},
        {"Fecha": "2023 – 2025", "Evento": "Registro fotográfico muestra el avance del deslizamiento de El Algodonal hacia el casco urbano"},
    ])
    st.dataframe(linea, use_container_width=True, hide_index=True)
    st.caption("Fuentes: [El Tiempo](https://www.eltiempo.com/bogota/avalancha-en-quetame-y-el-naranjal-en-cundinamarca-hablan-las-victimas-787405) · "
               "[Infobae](https://www.infobae.com/colombia/2023/07/18/asi-fue-la-avalancha-en-quetame-revelan-video-del-momento-exacto-de-la-tragedia-que-deja-hasta-ahora-10-muertos-y-al-menos-20-desaparecidos/)")

    fig = go.Figure(go.Bar(
        x=["Fallecidos", "Desaparecidos", "Viviendas afectadas"], y=[20, 9, 20],
        marker_color=[RED, AMBER, BLUE], text=[20, 9, 20], textposition="outside",
    ))
    fig.update_layout(template=PLOTLY_TEMPLATE, height=280, paper_bgcolor="rgba(0,0,0,0)",
                       title="Evento del 17-18 de julio de 2023 en Naranjal (cifras iniciales reportadas)")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("La cifra de «30+ vidas perdidas» usada en el proyecto agrega fallecidos y desaparecidos de este evento. "
               "«50+ viviendas afectadas» incluye también daños posteriores reportados en El Algodonal.")


@st.dialog("✅ La solución, en detalle")
def dialog_solucion():
    st.markdown("##### ¿Cuánto tiempo se gana al pasar de reactivo a preventivo?")
    fig = go.Figure()
    fig.add_trace(go.Bar(y=["Hoy (reactivo)"], x=[180], orientation="h", marker_color=RED, name="Minutos de reacción",
                          text=["~3 horas después del evento"], textposition="inside"))
    fig.add_trace(go.Bar(y=["Con el sistema (preventivo)"], x=[5], orientation="h", marker_color=GREEN,
                          text=["< 5 minutos, antes del evento"], textposition="outside"))
    fig.update_layout(template=PLOTLY_TEMPLATE, height=220, paper_bgcolor="rgba(0,0,0,0)", showlegend=False,
                       xaxis_title="Minutos", margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("""
    **En 4 pasos:**
    1. 🌧️ El sensor mide lluvia, humedad y movimiento cada pocos minutos.
    2. 📡 El dato viaja por LoRaWAN hasta la plataforma en la nube.
    3. 🧠 La IA cruza el dato con el histórico y el IDEAM y calcula el riesgo.
    4. 🚨 Si supera el umbral, se avisa por SMS, WhatsApp, app y sirena — en minutos, no en horas.
    """)


@st.dialog("Detalle: vidas perdidas")
def dialog_vidas():
    st.write("**Evento:** desbordamiento de quebradas en El Naranjal, Quetame.")
    st.write("**Fecha:** 17–18 de julio de 2023.")
    st.write("**Cifra:** ~20 fallecidos confirmados + 9 desaparecidos en los reportes iniciales (el proyecto agrupa esta cifra como «30+»).")
    st.caption("Fuente: El Tiempo, Infobae (julio de 2023).")


@st.dialog("Detalle: viviendas afectadas")
def dialog_viviendas():
    st.write("**Evento del 17–18 de julio de 2023:** más de 20 viviendas y una escuela afectadas en El Naranjal.")
    st.write("**Cifra del proyecto (50+):** suma afectaciones adicionales reportadas después en El Algodonal.")
    st.caption("Fuente: El Tiempo (julio de 2023) + documento de avance del proyecto.")


@st.dialog("Detalle: avance del deslizamiento")
def dialog_distancia():
    st.write("Esta cifra muestra **qué tan cerca** está el deslizamiento de El Algodonal de las primeras viviendas del casco urbano de Quetame.")
    st.write("**2023:** el punto de referencia fotográfico mostraba una distancia mayor.")
    st.write("**2025:** el mismo punto de referencia muestra que el deslizamiento avanzó hasta quedar a **~5 metros**.")
    st.markdown("👉 En otras palabras: **si no se actúa, en poco tiempo el deslizamiento podría alcanzar zona poblada.** Por eso el proyecto es urgente, no solo preventivo a largo plazo.")


@st.dialog("Detalle: monitoreo actual")
def dialog_monitoreo():
    st.write("Hoy, Quetame **no tiene ningún sensor ni sistema de alerta instalado** en Naranjal ni en El Algodonal.")
    st.write("Esto significa que cualquier lluvia fuerte o movimiento de tierra ocurre **sin que nadie lo detecte a tiempo**.")
    st.markdown("Una vez instalado el sistema (Fase 2 del cronograma, mes 7–10), este contador pasaría a mostrar sensores activos en tiempo real, como en la pestaña **Monitoreo en vivo**.")


@st.dialog("Detalle del actor")
def dialog_actor(a):
    st.markdown(f"### {a['icon']} {a['Hélice']}")
    st.write(f"**Quiénes son:** {a['Actores']}")
    st.write(f"**Rol en el proyecto:** {a['Rol']}")
    st.write(f"**Qué aportan:** {a['Aporta']}")
    st.markdown("**Funciones específicas:**")
    for f in a["Funciones"]:
        st.markdown(f"- {f}")


@st.dialog("Detalle del riesgo técnico")
def dialog_riesgo(row):
    st.markdown(f"### {row['Riesgo técnico']}")
    st.write(f"**Severidad:** {row['Severidad']}")
    st.write(f"**Estrategia de mitigación:** {row['Estrategia de mitigación']}")


@st.dialog("Detalle de la actividad")
def dialog_actividad(row):
    st.markdown(f"### {row['Actividad']}")
    st.write(f"**Fase:** {row['Fase']}")
    st.write(f"**Responsable:** {row['Responsable']}")
    st.write(f"**Duración:** mes {row['Mes inicio']} a mes {row['Mes fin']} ({row['Duración (meses)']} meses)")
    st.write(f"**Entregable:** {row['Entregable']}")


@st.dialog("📱 Así se vería la alerta en un celular")
def dialog_celular():
    st.markdown(f"""
    <div class="phone">
      <div class="bar"><div class="notch"></div></div>
      <div class="screen">
        <div style="font-size:11px;color:#888;text-align:center;margin-bottom:10px;">
          Mensajes · Defensa Civil Quetame
        </div>
        <div class="bubble-red">
          🚨 <b>ALERTA ROJA</b><br>
          Riesgo alto de deslizamiento en <b>El Algodonal</b>. Evacúe ahora hacia el punto de encuentro
          (Escuela Rural). No use vehículo. Manténgase informado.<br>— Defensa Civil Quetame
        </div>
        <div style="font-size:10px;color:#9aa0a8;text-align:right;margin-bottom:14px;">10:42 a. m. · Entregado</div>
        <div style="font-size:11px;color:#888;text-align:center;margin-bottom:10px;">WhatsApp · Alertas Quetame</div>
        <div class="bubble-green">
          🟢 Sistema de Alertas Quetame: nivel de riesgo bajó a <b>PRECAUCIÓN</b> en Naranjal. Continúe atento
          a nuevas notificaciones.
        </div>
        <div style="font-size:10px;color:#9aa0a8;text-align:right;">10:58 a. m. · Leído ✓✓</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.caption("Maqueta ilustrativa del mensaje que recibiría un habitante — mismo contenido se replica en SMS, WhatsApp y la sirena comunitaria.")


@st.dialog("🏛 Panel de control — Alcaldía de Quetame")
def dialog_alcaldia():
    st.markdown(f"""
    <div class="console">
      <div class="bar2">🏛 Centro de Monitoreo — Alcaldía de Quetame</div>
      <div style="padding:18px;">
        <div style="background:{RED_BG};border-left:5px solid {RED};border-radius:8px;padding:12px 16px;margin-bottom:14px;">
          <b>🔴 Alerta activa detectada</b><br>
          Zona: <b>El Algodonal</b><br>
          Índice de riesgo: <b>82 / 100</b><br>
          Detectado hace: <b>2 minutos</b> · Sensor: Pluviómetro EA-01 + Sensor de movimiento EA-03
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    st.markdown("**Resumen de sensores en la zona:**")
    resumen = pd.DataFrame({
        "Sensor": ["Pluviómetro EA-01", "Sensor humedad EA-02", "Sensor movimiento EA-03"],
        "Última lectura": ["46.2 mm/h", "88.4 %", "Movimiento detectado"],
        "Estado": ["🔴 Crítico", "🟡 Elevado", "🔴 Crítico"],
    })
    st.dataframe(resumen, use_container_width=True, hide_index=True)

    st.write("")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✅ Confirmar y notificar a la comunidad", use_container_width=True, type="primary"):
            st.success("Notificación enviada por SMS, WhatsApp y sirena a El Algodonal. Protocolo UNGRD → Bomberos activado.")
    with c2:
        if st.button("🚫 Marcar como falsa alarma", use_container_width=True):
            st.info("Evento marcado como falsa alarma. Se registra para reentrenar el modelo de IA.")


# ============================================================================
# HERO
# ============================================================================
st.markdown(f"""
<div class="hero">
  <span class="eyebrow o">PROYECTO DE IMPACTO SOCIAL · GESTIÓN DEL RIESGO</span><span class="vbadge">v{VERSION}</span>
  <h1 style="margin-bottom:6px;">Sistema Inteligente de Alerta Temprana — <span style="color:{ORANGE}">Quetame</span></h1>
  <p style="color:{TEXT_GRAY}; font-size:16px; max-width:900px;">
    De la reacción a la anticipación: monitoreo en tiempo real, inteligencia artificial y alertas comunitarias
    para proteger a Quetame frente a los deslizamientos de Naranjal y El Algodonal.
  </p>
  <div class="authors">
    {"".join(f'<div class="author-chip"><div class="author-avatar" style="background:{c};">{"".join(w[0] for w in a.split(" —")[0].split()[:2]).upper()}</div>{a}</div>' for a, c in zip(AUTORES, [ORANGE, BLUE, PURPLE, GREEN, PINK]))}
  </div>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# PROBLEMA vs SOLUCIÓN — clicables
# ============================================================================
pc1, pc2 = st.columns(2)
with pc1:
    st.markdown(f"""
    <div class="card fill-red">
    <span class="eyebrow r">❗ EL PROBLEMA</span>
    <h3>Quetame no ve venir los deslizamientos</h3>
    <p>Naranjal y El Algodonal ya sufrieron tragedias evitables: <b>más de 30 vidas perdidas</b> y
    <b>más de 50 viviendas afectadas</b>. Hoy el municipio se entera del riesgo <b>cuando ya está ocurriendo</b>,
    porque no existe ningún sensor ni sistema de alerta en las zonas críticas.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🔎 Ver el problema en detalle", key="btn_problema", use_container_width=True):
        dialog_problema()
with pc2:
    st.markdown(f"""
    <div class="card fill-green">
    <span class="eyebrow g">✅ LA SOLUCIÓN</span>
    <h3>Sensores + IA + alertas antes del evento</h3>
    <p>Instalar sensores de lluvia, humedad y movimiento del terreno en las zonas críticas, analizar esos datos
    con inteligencia artificial, y avisar a la comunidad por SMS, WhatsApp y sirena <b>minutos antes</b> de que
    el riesgo se convierta en tragedia.</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🔎 Ver la solución en detalle", key="btn_solucion", use_container_width=True):
        dialog_solucion()

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric("Vidas perdidas", "30+", help="Toca el botón para ver fechas y fuentes")
    if st.button("Ver detalle", key="k1b", use_container_width=True):
        dialog_vidas()
with k2:
    st.metric("Viviendas afectadas", "50+")
    if st.button("Ver detalle", key="k2b", use_container_width=True):
        dialog_viviendas()
with k3:
    st.metric("Avance del deslizamiento", "~5 m", help="Distancia actual entre el deslizamiento y el casco urbano")
    if st.button("Ver detalle", key="k3b", use_container_width=True):
        dialog_distancia()
with k4:
    st.metric("Monitoreo actual", "Sin datos", help="No hay sensores instalados todavía")
    if st.button("Ver detalle", key="k4b", use_container_width=True):
        dialog_monitoreo()

# ============================================================================
# BANNER DE SECCIÓN + TABS
# ============================================================================
section_banner("🧭 Nuestro Sistema de Alerta Temprana", "Explora cómo funciona: monitoreo, arquitectura, actores, cronograma e impacto.")

tab1, tab2, tab_sim, tab3, tab4, tab5, tab6 = st.tabs([
    "📌 Resumen", "📡 Monitoreo en vivo", "🌧️ Simulacro", "🏗️ Arquitectura",
    "🤝 Actores", "🛡️ Riesgos & cronograma", "🎯 Impacto",
])

# ---------------------------------------------------------------- TAB 1
with tab1:
    st.markdown("""
    <div class="card">
    <h3>¿Por qué ocurre esto?</h3>
    <p>Quetame (Cundinamarca) tiene pendientes muy pronunciadas, suelos inestables y lluvias intensas. Sumado a
    que hay viviendas construidas en zonas de alto riesgo, los deslizamientos dejaron de ser un hecho aislado
    para convertirse en una amenaza recurrente.</p>
    <div class="quote">"En Quetame existe una ocupación del territorio en zonas de alta inestabilidad
    geotécnica, sin sistemas de monitoreo en tiempo real ni alertas tempranas, lo que convierte eventos
    naturales en tragedias humanas."</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class="card red">
        <h4>⚠ Cómo se maneja hoy (reactivo)</h4>
        <p>Se responde <b>después</b> del evento: no hay datos en tiempo real, ni coordinación institucional
        oportuna. Cuando la alcaldía se entera, la emergencia ya empezó.</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="card teal">
        <h4>✓ Cómo se manejaría con este proyecto (preventivo)</h4>
        <p>Monitoreo continuo con sensores IoT + analítica predictiva. Se activan protocolos de evacuación
        <b>antes</b> de que el riesgo se materialice.</p>
        </div>
        """, unsafe_allow_html=True)

    with st.expander("📖 Ver objetivo general y justificación completa del proyecto"):
        st.markdown("""
        **Objetivo general:** diseñar e implementar un sistema inteligente de alertas tempranas en el municipio
        de Quetame (Cundinamarca), basado en el monitoreo en tiempo real de variables hidroclimáticas y
        geotécnicas, que permita anticipar eventos de riesgo como deslizamientos e inundaciones, reducir la
        vulnerabilidad de la población y fortalecer la toma de decisiones institucional mediante el uso de
        tecnologías emergentes y datos.

        **Justificación:** los eventos en Naranjal y El Algodonal han dejado más de 30 vidas humanas perdidas y
        al menos 50 viviendas afectadas. Esta situación no puede seguir entendiéndose solo como consecuencia de
        factores naturales, sino como resultado de una insuficiente capacidad de anticipación institucional.
        """)

    with st.expander("📎 Fuentes, cifras y enlaces de referencia"):
        st.markdown("""
        - Evento real del 17-18 de julio de 2023 en El Naranjal: [El Tiempo](https://www.eltiempo.com/bogota/avalancha-en-quetame-y-el-naranjal-en-cundinamarca-hablan-las-victimas-787405) · [Infobae](https://www.infobae.com/colombia/2023/07/18/asi-fue-la-avalancha-en-quetame-revelan-video-del-momento-exacto-de-la-tragedia-que-deja-hasta-ahora-10-muertos-y-al-menos-20-desaparecidos/)
        - **~700 municipios** de Colombia están en zonas amenazadas por deslizamientos (Banco Mundial).
        - **Cundinamarca** es el segundo departamento con más registros de movimientos en masa del país (1.068), según la UNGRD.
        - **+80% de la población colombiana** vive en zona de amenaza media, alta o muy alta por movimientos en masa (SGC + Censo 2018).
        - Fuente consolidada: [El Espectador](https://www.elespectador.com/colombia/el-80-de-la-poblacion-amenazada-por-deslizamientos-en-colombia/)
        - Enlaces institucionales: [IDEAM](http://www.ideam.gov.co) · [UNGRD](http://www.gestiondelriesgo.gov.co) · [MinTIC](https://www.mintic.gov.co) · [Universidad Externado de Colombia](https://www.uexternado.edu.co)
        - TRM (tasa de cambio COP/USD) usada en costos: $3.206,86 — Banco de la República, 23 de julio de 2026.
        """)

# ---------------------------------------------------------------- TAB 2
with tab2:
    st.markdown(f"""
    <div class="card fill-blue" style="margin-bottom:14px;">
    <b>📊 Modo demostración:</b> esta vista simula lecturas reales de sensores para mostrar cómo operaría el
    sistema una vez instalado en campo. Los valores cambian cada vez que actualizas.
    </div>
    """, unsafe_allow_html=True)

    with st.expander("❓ ¿Cómo funciona el monitoreo? (paso a paso, explicado simple)", expanded=False):
        s1, s2, s3, s4 = st.columns(4)
        pasos = [
            ("1", "Medición", "Cada sensor mide lluvia, humedad del suelo o movimiento del terreno cada pocos minutos."),
            ("2", "Transmisión", "El sensor envía el dato por radio (LoRaWAN) hasta un concentrador, y de ahí a internet."),
            ("3", "Análisis", "La plataforma cruza el dato nuevo con el histórico y con el IDEAM, y calcula un índice de riesgo."),
            ("4", "Alerta", "Si el índice supera el umbral, se envía la alerta por SMS, WhatsApp, app y sirena, en minutos."),
        ]
        for col, (n, t, d) in zip([s1, s2, s3, s4], pasos):
            with col:
                st.markdown(f'<div class="step"><div class="n">{n}</div><b>{t}</b><p style="font-size:12px;color:{TEXT_GRAY};margin-top:6px;">{d}</p></div>', unsafe_allow_html=True)

    st.info("👉 ¿Quieres ver el simulacro completo (lluvia fuerte, flujo de datos y reacción de cada actor)? Ve a la pestaña **🌧️ Simulacro**.")

    st.divider()
    zona_sel = st.radio("📍 Elige una zona para ver sus sensores", list(ZONAS.keys()), horizontal=True)
    zinfo = ZONAS[zona_sel]

    top_l, top_r = st.columns([3, 1])
    with top_l:
        st.subheader(f"{zona_sel}  ·  {zinfo['estado']}")
    with top_r:
        refrescar = st.button("🔄 Actualizar lecturas", use_container_width=True)

    if "seed_quetame" not in st.session_state or refrescar:
        st.session_state.seed_quetame = int(time.time())
    seed = st.session_state.seed_quetame + abs(hash(zona_sel)) % 1000
    rng = np.random.default_rng(seed)

    st.caption(f"🕒 Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    scols = st.columns(len(zinfo["sensores"]))
    lecturas_actuales = {}
    for i, (col, sensor_name) in enumerate(zip(scols, zinfo["sensores"])):
        bateria = int(rng.uniform(35, 100))
        rssi = int(rng.uniform(-110, -55))
        online = bateria > 15 and rng.random() > 0.05
        estado_txt = "🟢 En línea" if online else ("🟡 Batería baja" if bateria <= 15 else "🔴 Sin señal")
        segs = int(rng.uniform(4, 120))
        lecturas_actuales[sensor_name] = {"bateria": bateria, "rssi": rssi, "segs": segs}
        with col:
            st.markdown(f"""
            <div class="sensor-card">
            <b>{sensor_name}</b><br>
            <span style="font-size:12.5px;color:{TEXT_GRAY};">{estado_txt} · hace {segs}s</span><br><br>
            🔋 Batería: <b>{bateria}%</b><br>
            📶 Señal (RSSI): <b>{rssi} dBm</b>
            </div>
            """, unsafe_allow_html=True)

    st.write("")
    horas = pd.date_range(end=datetime.now(), periods=72, freq="h")
    lluvia = np.clip(rng.normal(4, 3, 72), 0, None)
    lluvia[-6:] += np.linspace(5, 42, 6)
    humedad = np.clip(30 + np.cumsum(rng.normal(0.3, 1.5, 72)), 20, 100)
    nivel_rio = np.clip(20 + np.cumsum(rng.normal(0.1, 0.8, 72)), 10, None)
    indice_riesgo = np.clip((lluvia / 45 * 0.5 + (humedad - 30) / 70 * 0.5) * 100, 0, 100)

    df_ts = pd.DataFrame({"Hora": horas, "Precipitación (mm/h)": lluvia, "Humedad del suelo (%)": humedad,
                           "Nivel de río (cm)": nivel_rio, "Índice de riesgo": indice_riesgo})

    m1, m2, m3 = st.columns(3)
    m1.metric("Precipitación actual", f"{lluvia[-1]:.1f} mm/h", delta=f"{(lluvia[-1]-lluvia[-2]):+.1f}")
    m2.metric("Humedad del suelo", f"{humedad[-1]:.1f} %", delta=f"{(humedad[-1]-humedad[-2]):+.1f}")
    m3.metric("Nivel de río / ladera", f"{nivel_rio[-1]:.1f} cm", delta=f"{(nivel_rio[-1]-nivel_rio[-2]):+.1f}")

    riesgo_actual = df_ts["Índice de riesgo"].iloc[-1]
    nivel_txt, nivel_color = ("🔴 ALERTA ROJA", RED) if riesgo_actual > 70 else \
                              ("🟡 ALERTA AMARILLA", AMBER) if riesgo_actual > 40 else ("🟢 NORMAL", GREEN)

    g1, g2 = st.columns([1, 2])
    with g1:
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number", value=riesgo_actual,
            title={"text": f"Índice de riesgo actual<br><span style='font-size:14px;color:{nivel_color}'>{nivel_txt}</span>"},
            gauge={"axis": {"range": [0, 100]}, "bar": {"color": nivel_color},
                   "steps": [{"range": [0, 40], "color": GREEN_BG}, {"range": [40, 70], "color": AMBER_BG},
                             {"range": [70, 100], "color": RED_BG}]},
            number={"suffix": " / 100"},
        ))
        fig_gauge.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={"color": TEXT_DARK}, height=280)
        st.plotly_chart(fig_gauge, use_container_width=True)
    with g2:
        fig_map = go.Figure(go.Scattermapbox(
            lat=[v["lat"] for v in ZONAS.values()], lon=[v["lon"] for v in ZONAS.values()],
            mode="markers+text", text=list(ZONAS.keys()), textposition="top center",
            marker=dict(size=17, color=[RED if "alto" in v["estado"] else AMBER if "medio" in v["estado"] else GREEN for v in ZONAS.values()]),
        ))
        fig_map.update_layout(mapbox=dict(style="carto-positron", center=dict(lat=4.333, lon=-73.833), zoom=11.5),
                               margin=dict(l=0, r=0, t=0, b=0), height=280, paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_map, use_container_width=True)
        st.caption("Ubicación referencial de sensores (aproximada, con fines ilustrativos).")

    fig_ts = px.line(df_ts, x="Hora", y=["Precipitación (mm/h)", "Humedad del suelo (%)", "Nivel de río (cm)"],
                      template=PLOTLY_TEMPLATE, height=380,
                      color_discrete_sequence=[ORANGE, BLUE, PURPLE])
    fig_ts.add_hline(y=40, line_dash="dot", line_color=RED, annotation_text="umbral de precaución (40 mm/h)")
    fig_ts.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", legend_title="")
    st.plotly_chart(fig_ts, use_container_width=True)

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        with st.expander("🗂 Ver historial de alertas simuladas (tabla emergente)"):
            hist = pd.DataFrame({
                "Fecha": pd.date_range(end=datetime.now(), periods=8, freq="3D").strftime("%Y-%m-%d %H:%M"),
                "Zona": rng.choice(list(ZONAS.keys()), 8),
                "Nivel": rng.choice(["🟢 Normal", "🟡 Precaución", "🔴 Alerta"], 8, p=[0.5, 0.35, 0.15]),
                "Canal de difusión": rng.choice(["SMS + Sirena", "WhatsApp", "App móvil", "Sirena comunitaria"], 8),
            })
            busq_hist = st.text_input("🔎 Buscar en el historial", key="busq_hist")
            st.dataframe(filtro_texto(hist, busq_hist), use_container_width=True, hide_index=True)
    with c2:
        with st.expander("🖥️ Ver payload crudo (MQTT/JSON) del último mensaje — ¿para qué sirve?"):
            st.caption("Así es exactamente el mensaje técnico que un sensor real enviaría a la plataforma (formato "
                       "estándar de dispositivos IoT). Sirve para demostrar que la integración es técnicamente real "
                       "y no solo una simulación visual — es lo que vería un ingeniero de datos en la plataforma.")
            sensor_ej = zinfo["sensores"][0]
            payload = {
                "sensor_id": sensor_ej.split()[-1],
                "tipo": "pluviometro",
                "zona": zona_sel,
                "valor": round(float(lluvia[-1]), 1),
                "unidad": "mm/h",
                "bateria_pct": lecturas_actuales[sensor_ej]["bateria"],
                "rssi_dbm": lecturas_actuales[sensor_ej]["rssi"],
                "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
                "protocolo": "LoRaWAN → MQTT/TLS",
            }
            st.code(json.dumps(payload, indent=2, ensure_ascii=False), language="json")

# ---------------------------------------------------------------- TAB SIMULACRO
with tab_sim:
    st.markdown(f"""
    <div class="card fill-orange">
    <span class="eyebrow o">MÓDULO DE SIMULACRO</span>
    <h3>🌧️ De la lluvia a la respuesta institucional, en vivo</h3>
    <p>Configura un escenario de lluvia y observa, paso a paso, cómo el dato viaja desde el sensor hasta que
    <b>los cuatro actores</b> (Alcaldía, Comunidad, Bomberos/Defensa Civil y UNGRD) reaccionan a la alerta.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### ⚙️ Configura los supuestos del escenario")
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        intensidad = st.slider("🌧️ Intensidad de lluvia pico (mm/h)", 10, 100, 45)
        zona_sim = st.selectbox("📍 Zona simulada", list(ZONAS.keys()), key="zona_sim")
    with sc2:
        duracion = st.slider("⏱️ Duración del evento (horas)", 1, 12, 4)
        humedad_previa = st.slider("💧 Humedad del suelo previa (%)", 20, 90, 55)
    with sc3:
        umbral_ia = st.slider("🧠 Umbral de alerta del modelo de IA", 50, 90, 70)
        velocidad = st.select_slider("🎬 Velocidad de la animación", options=["Lenta", "Normal", "Rápida"], value="Normal")

    st.markdown("#### 🧪 Supuestos adicionales (prueba de estrés del sistema)")
    sc4, sc5 = st.columns(2)
    with sc4:
        falla_sensor = st.checkbox(
            "🔧 Simular falla de un sensor durante el evento",
            value=False,
            help="Activa esto para ver si la red aguanta cuando un sensor deja de reportar en plena tormenta — "
                 "así se prueba si la redundancia funciona como está diseñada.",
        )
    with sc5:
        conectividad_debil = st.checkbox(
            "📡 Simular conectividad débil en la zona (picos de latencia)",
            value=False,
            help="Simula que el gateway LoRaWAN/4G tarda más de lo normal en subir los datos a la nube.",
        )

    with st.expander("📊 Ver datos históricos usados para calibrar el modelo (datos de ejemplo)"):
        st.caption("Datos ilustrativos de calibración — todos son sintéticos con fines demostrativos, excepto el "
                   "evento del 17 de julio de 2023 en Naranjal, que sí es real.")
        st.dataframe(HIST_CALIBRACION, use_container_width=True, hide_index=True)

    riesgo_pico = min(100, round(intensidad / 100 * 55 + humedad_previa / 100 * 35 + duracion / 12 * 10))
    lluvia_acumulada_sim = round(intensidad * duracion * 0.55, 1)
    confianza_modelo, evento_similar = analizar_similitud_historica(lluvia_acumulada_sim, humedad_previa)
    st.caption(f"Con estos supuestos, el índice de riesgo proyectado llegaría a **{riesgo_pico}/100** "
               f"({'🔴 superaría' if riesgo_pico > umbral_ia else '🟢 no superaría'} el umbral de {umbral_ia}). "
               f"Lluvia acumulada estimada: **{lluvia_acumulada_sim} mm** · Confianza del modelo vs. histórico: "
               f"**{confianza_modelo}%** — el escenario más parecido es el de *{evento_similar['Fecha']}* "
               f"en {evento_similar['Zona']} ({evento_similar['Resultado']}).")

    delay = {"Lenta": 0.9, "Normal": 0.5, "Rápida": 0.2}[velocidad]
    ejecutar = st.button("▶️ Ejecutar simulacro completo", type="primary", use_container_width=False)
    placeholder_sim = st.empty()

    if ejecutar:
        st.session_state.sim_ran = True
        n_pasos = 10
        curva = np.linspace(riesgo_pico * 0.12, riesgo_pico, n_pasos)
        lluvia_curva = np.linspace(intensidad * 0.15, intensidad, n_pasos)
        nivel_rio_curva = np.clip(20 + np.cumsum(lluvia_curva) * 0.16 + (humedad_previa - 50) * 0.05, 15, None)
        nivel_critico = 55  # cm — nivel de referencia para el tanque visual
        horas_sim = [f"+{int(i*8/60)}m{i*8%60:02d}s" for i in range(n_pasos)]

        t0 = datetime.now()
        log_lines = []
        chat = []  # (autor, texto, tipo)
        disparado = False
        trigger_step = None
        actores_status = {"🏛 Alcaldía": "⏳ En espera", "👥 Comunidad": "⏳ En espera",
                           "🚒 Bomberos / Defensa Civil": "⏳ En espera", "🏢 UNGRD": "⏳ En espera"}
        post_msgs = [
            ("Doña Marleny 👵", "Recibido, ya vamos saliendo con la familia 🙏"),
            ("Carlos, líder JAC 🧑‍🤝‍🧑", "Vamos al punto de encuentro, avisen a los del sector alto"),
            ("Don Jairo 👨‍🌾", "Bomberos ya llegaron a la vía principal 🚒"),
            ("Doña Rosa 👵", "Estoy saliendo, gracias por avisar a tiempo"),
            ("Profe Ana - Escuela Rural 👩‍🏫", "Ya abrimos la escuela como punto de encuentro, hay agua y café"),
            ("Carlos, líder JAC 🧑‍🤝‍🧑", "Conteo: 18 familias ya evacuadas, faltan 4 por confirmar"),
        ]

        # --- supuestos de estrés (v9.0): falla de sensor y conectividad débil ---
        sensor_falla_nombre = ZONAS[zona_sim]["sensores"][-1]
        fail_step = max(2, n_pasos // 2) if falla_sensor else None
        recuperado_step = (fail_step + 2) if falla_sensor else None
        fallo_ocurrido = False
        fallo_recuperado = False
        pasos_con_latencia = 0

        for i in range(n_pasos):
            ts = (t0 + timedelta(seconds=i * 8)).strftime("%H:%M:%S")
            r = curva[i]
            lv = lluvia_curva[i]
            rio = nivel_rio_curva[i]
            color = RED if r > umbral_ia else (AMBER if r > 40 else GREEN)
            log_lines.append(f"{ts}  ·  Sensor capta {lv:.1f} mm/h · nivel río {rio:.0f} cm en {zona_sim}")
            if conectividad_debil and i % 3 == 0:
                pasos_con_latencia += 1
                log_lines.append(f"{ts}  ·  🐢 Latencia elevada en el enlace LoRaWAN/4G — reintentando transmisión")
            else:
                log_lines.append(f"{ts}  ·  Gateway LoRaWAN transmite el dato → nube (MQTT/TLS)")
            log_lines.append(f"{ts}  ·  Context Broker consolida con histórico + IDEAM")
            log_lines.append(f"{ts}  ·  Motor de IA recalcula índice de riesgo: {r:.0f}/100")

            if falla_sensor and i == fail_step:
                fallo_ocurrido = True
                log_lines.append(f"{ts}  ·  ⚠️ {sensor_falla_nombre} deja de reportar (batería agotada / posible daño físico)")
                log_lines.append(f"{ts}  ·  🔁 El sistema conmuta automáticamente al sensor redundante de la zona — sin pérdida de datos")
                chat.append(("🛠️ Sistema de Alertas Quetame",
                              f"Aviso técnico: {sensor_falla_nombre} sin señal. Sensor redundante activado, monitoreo continúa sin interrupción.",
                              "system"))
            if falla_sensor and i == recuperado_step:
                fallo_recuperado = True
                log_lines.append(f"{ts}  ·  ✅ {sensor_falla_nombre} vuelve a reportar con normalidad")

            if i == 2 and not disparado:
                chat.append(("Doña Marleny 👵", "Está lloviendo muy duro por acá 😟", "user"))
            if i == 4 and not disparado:
                chat.append(("Don Jairo 👨‍🌾", "El río se ve más alto de lo normal, ojo con eso", "user"))

            if r > umbral_ia and not disparado:
                disparado = True
                trigger_step = i
                log_lines.append(f"{ts}  ·  🚨 UMBRAL SUPERADO — Sistema dispara ALERTA en {zona_sim}")
                log_lines.append(f"{ts}  ·  🏛 Alcaldía recibe la alerta en su panel de control")
                log_lines.append(f"{ts}  ·  📱 Comunidad notificada por SMS + WhatsApp + sirena")
                log_lines.append(f"{ts}  ·  🚒 Bomberos y Defensa Civil activan protocolo de evacuación")
                log_lines.append(f"{ts}  ·  🏢 UNGRD notificada para coordinación regional")
                actores_status = {"🏛 Alcaldía": f"✅ Notificada a las {ts}", "👥 Comunidad": f"✅ Alertada a las {ts}",
                                   "🚒 Bomberos / Defensa Civil": f"✅ Activados a las {ts}", "🏢 UNGRD": f"✅ Informada a las {ts}"}
                chat.append(("🚨 Sistema de Alertas Quetame", f"ALERTA ROJA: riesgo de deslizamiento en {zona_sim}. "
                             f"Evacúe hacia el punto de encuentro. No use vehículo.", "system"))
            elif disparado:
                post_idx = i - trigger_step - 1
                if 0 <= post_idx < len(post_msgs):
                    autor, txt = post_msgs[post_idx]
                    chat.append((autor, txt, "user"))

            with placeholder_sim.container():
                st.markdown("**⛰️ Escalada del deslizamiento (en vivo):**")
                st.markdown(render_escalada(etapa_idx(r, umbral_ia)), unsafe_allow_html=True)
                st.write("")
                gcol, chcol = st.columns([1.3, 1.1])
                with gcol:
                    figg = go.Figure(go.Indicator(
                        mode="gauge+number", value=r,
                        title={"text": f"Índice de riesgo — {zona_sim}"},
                        gauge={"axis": {"range": [0, 100]}, "bar": {"color": color},
                               "steps": [{"range": [0, 40], "color": GREEN_BG}, {"range": [40, umbral_ia], "color": AMBER_BG},
                                         {"range": [umbral_ia, 100], "color": RED_BG}]},
                    ))
                    figg.update_layout(height=210, paper_bgcolor="rgba(0,0,0,0)", font={"color": TEXT_DARK}, margin=dict(l=10, r=10, t=50, b=10))
                    st.plotly_chart(figg, use_container_width=True, key=f"simcompleto_gauge_{i}")

                    fig_mon = go.Figure()
                    fig_mon.add_trace(go.Scatter(x=horas_sim[:i+1], y=lluvia_curva[:i+1], name="Lluvia (mm/h)",
                                                  mode="lines+markers", line=dict(color=ORANGE, width=3)))
                    fig_mon.add_trace(go.Scatter(x=horas_sim[:i+1], y=nivel_rio_curva[:i+1], name="Nivel río (cm)",
                                                  mode="lines+markers", line=dict(color=BLUE, width=3), yaxis="y2"))
                    fig_mon.update_layout(
                        height=200, template=PLOTLY_TEMPLATE, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", y=1.25, font=dict(size=10)),
                        title=dict(text="📈 Así se vería en el monitor en vivo", font=dict(size=12, color=TEXT_GRAY)),
                        yaxis=dict(title=dict(text="mm/h", font=dict(size=9))),
                        yaxis2=dict(title=dict(text="cm", font=dict(size=9)), overlaying="y", side="right"),
                    )
                    st.plotly_chart(fig_mon, use_container_width=True, key=f"simcompleto_mon_{i}")

                with chcol:
                    st.markdown("**🖥️ Registro del sistema en vivo:**")
                    st.code("\n".join(log_lines[-8:]), language=None)
                    miembros_activos = 12 + min(35, len(chat) * 6)
                    st.markdown(f'**📱 Grupo comunitario "Alerta El Algodonal"** · 47 miembros, {miembros_activos} en línea')
                    bubbles_html = ""
                    for j, (autor, texto, tipo) in enumerate(chat[-7:]):
                        cls = "bubble-red" if tipo == "system" else "bubble-user"
                        who = "" if tipo == "system" else f'<span class="who">{autor}</span>'
                        hora_msg = (t0 + timedelta(seconds=(len(chat) - len(chat[-7:]) + j) * 8)).strftime("%H:%M")
                        bubbles_html += (f'<div class="{cls}">{who}{texto}'
                                         f'<div style="font-size:9px;opacity:0.7;text-align:right;margin-top:3px;">{hora_msg}</div></div>')
                    if not disparado and i in (1, 3):
                        bubbles_html += '<div class="bubble-user" style="font-style:italic;color:#9aa0a8;">Carlos, líder JAC está escribiendo…</div>'
                    st.markdown(f'<div class="phone" style="width:100%;"><div class="screen" style="min-height:0;">{bubbles_html}</div></div>', unsafe_allow_html=True)

                st.write("")
                st.markdown(f"**🌊 El río en 3D — nivel actual: {rio:.0f} cm** (crítico: {nivel_critico} cm)")
                st.plotly_chart(river_3d_figure(rio, nivel_critico), use_container_width=True, key=f"river3d_{i}")

                if disparado:
                    st.markdown(f"""
                    <div class="card fill-red">
                    <h4>🚨 Alerta activa — respuesta institucional en curso</h4>
                    <p>Índice de riesgo: <b>{r:.0f}/100</b> · Zona: <b>{zona_sim}</b> · Umbral configurado: <b>{umbral_ia}</b></p>
                    </div>
                    """, unsafe_allow_html=True)
            time.sleep(delay)

        # Guardar resultados en session_state para que sobrevivan a reruns
        # causados por los botones de abajo (que están fuera de este bloque).
        st.session_state.sim_actores_status = actores_status
        st.session_state.sim_disparado = disparado
        st.session_state.sim_tiempo_total = (n_pasos - 1) * 8 if disparado else 0
        st.session_state.sim_zona = zona_sim
        st.session_state.sim_tiempo_hasta_alerta = (trigger_step * 8) if disparado else None
        st.session_state.sim_riesgo_pico = riesgo_pico
        st.session_state.sim_umbral_ia = umbral_ia
        st.session_state.sim_confianza = confianza_modelo
        st.session_state.sim_evento_similar = dict(evento_similar)
        st.session_state.sim_falla_activada = falla_sensor
        st.session_state.sim_fallo_ocurrido = fallo_ocurrido
        st.session_state.sim_fallo_recuperado = fallo_recuperado
        st.session_state.sim_sensor_falla_nombre = sensor_falla_nombre
        st.session_state.sim_conectividad_debil = conectividad_debil
        st.session_state.sim_pasos_con_latencia = pasos_con_latencia
        st.session_state.sim_lluvia_acumulada = lluvia_acumulada_sim

    # --------------------------------------------------------------
    # Resultados y botones — FUERA del bloque "if ejecutar" a propósito,
    # para que no desaparezcan ni se rompan al hacer clic en ellos.
    # --------------------------------------------------------------
    if st.session_state.get("sim_ran"):
        st.divider()
        disparado_r = st.session_state.get("sim_disparado", False)
        actores_status_r = st.session_state.get("sim_actores_status", {})

        st.markdown("#### 👥 Estado final de cada actor")
        acols = st.columns(4)
        for col, (actor, estado) in zip(acols, actores_status_r.items()):
            with col:
                ok = "✅" in estado
                st.markdown(f"""
                <div class="card {'teal' if ok else 'red'}">
                <b>{actor}</b><br><span style="font-size:12.5px;color:{TEXT_GRAY};">{estado}</span>
                </div>
                """, unsafe_allow_html=True)

        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Tiempo total simulado", f"{st.session_state.get('sim_tiempo_total', 0)} s")
        r2.metric("Actores notificados", "4 / 4" if disparado_r else "0 / 4")
        r3.metric("Canales usados", "4" if disparado_r else "0")
        r4.metric("Nivel de alerta alcanzado", "🔴 Roja" if disparado_r else "🟢 Normal")

        # ------------------------------------------------------------
        # 🩺 Diagnóstico del simulacro — identifica errores/riesgos y
        # propone decisiones a partir del escenario simulado (v9.0).
        # ------------------------------------------------------------
        st.write("")
        st.markdown('<p class="big-title" style="font-size:19px;">🩺 Diagnóstico del simulacro — hallazgos y decisiones sugeridas</p>', unsafe_allow_html=True)
        st.caption("Análisis generado automáticamente a partir de los supuestos configurados. No reemplaza un estudio técnico real, "
                   "pero ilustra cómo el sistema apoyaría la toma de decisiones con datos.")

        tiempo_alerta_r = st.session_state.get("sim_tiempo_hasta_alerta")
        riesgo_pico_r = st.session_state.get("sim_riesgo_pico", 0)
        umbral_r = st.session_state.get("sim_umbral_ia", 70)
        confianza_r = st.session_state.get("sim_confianza", 0)
        evento_similar_r = st.session_state.get("sim_evento_similar", {})
        falla_activada_r = st.session_state.get("sim_falla_activada", False)
        fallo_ocurrido_r = st.session_state.get("sim_fallo_ocurrido", False)
        fallo_recuperado_r = st.session_state.get("sim_fallo_recuperado", False)
        sensor_falla_r = st.session_state.get("sim_sensor_falla_nombre", "el sensor")
        conectividad_debil_r = st.session_state.get("sim_conectividad_debil", False)
        pasos_latencia_r = st.session_state.get("sim_pasos_con_latencia", 0)

        hallazgos = []  # (nivel, texto)  nivel: "red" | "amber" | "green" | "blue"

        if disparado_r:
            frac = tiempo_alerta_r / ((9) * 8) if tiempo_alerta_r is not None else 1
            if frac <= 0.3:
                hallazgos.append(("green", f"⏱️ **Margen de reacción amplio**: la alerta se dispara muy pronto en el escenario "
                                            f"(a los {tiempo_alerta_r}s de simulación). Esto valida el umbral de IA configurado ({umbral_r}) para este tipo de lluvia."))
            elif frac >= 0.75:
                hallazgos.append(("red", f"🚨 **Aviso tardío**: con estos supuestos la alerta solo se dispara a los {tiempo_alerta_r}s, "
                                          f"casi al final del evento simulado. **Decisión sugerida:** bajar el umbral de IA o aumentar la "
                                          f"frecuencia de muestreo de sensores para ganar minutos de reacción."))
            else:
                hallazgos.append(("amber", f"⚠️ **Margen de reacción moderado**: la alerta se dispara a los {tiempo_alerta_r}s. "
                                            f"Aceptable, pero conviene monitorear si escenarios más agresivos reducen ese margen."))
            if (riesgo_pico_r - umbral_r) < 8:
                hallazgos.append(("amber", f"⚠️ **Zona gris umbral/riesgo**: el pico de riesgo ({riesgo_pico_r}/100) quedó muy cerca del "
                                            f"umbral configurado ({umbral_r}). **Decisión sugerida:** validar el evento cruzando con datos del "
                                            f"IDEAM antes de notificar, para reducir el riesgo de falsas alarmas."))
        else:
            hallazgos.append(("amber", f"🟡 **El escenario no dispara alerta**: con estos supuestos el riesgo llega a {riesgo_pico_r}/100, "
                                        f"por debajo del umbral ({umbral_r}). Si en campo el riesgo real suele ser mayor a lo aquí asumido, "
                                        f"**considera revisar si el umbral está demasiado alto** para esta zona."))

        if falla_activada_r:
            if fallo_ocurrido_r and fallo_recuperado_r:
                hallazgos.append(("green", f"🔁 **Prueba de resiliencia superada**: {sensor_falla_r} dejó de reportar durante el simulacro y "
                                            f"el sistema conmutó al sensor redundante sin perder monitoreo. Esto valida la decisión de diseño de "
                                            f"instalar **doble sensor en variables críticas**."))
            elif fallo_ocurrido_r:
                hallazgos.append(("amber", f"⚠️ {sensor_falla_r} falló y no se recuperó dentro de la ventana simulada. "
                                            f"**Decisión sugerida:** definir un protocolo de reemplazo/mantenimiento en menos de X horas."))
        else:
            hallazgos.append(("blue", "ℹ️ No se probó ninguna falla de sensor en este escenario. Activa la casilla "
                                       "**\"Simular falla de un sensor\"** arriba para evaluar la resiliencia de la red antes de decidir "
                                       "cuántos sensores redundantes instalar por zona."))

        if conectividad_debil_r and pasos_latencia_r > 0:
            hallazgos.append(("amber", f"🐢 **Latencia detectada**: se registraron {pasos_latencia_r} reintentos de transmisión por "
                                        f"conectividad débil. En un evento real esto podría retrasar la alerta. **Decisión sugerida:** "
                                        f"garantizar un enlace redundante (LoRaWAN + 4G/5G) en {zona_sim}."))

        if confianza_r >= 85:
            hallazgos.append(("green", f"📊 **Alta confianza del modelo** ({confianza_r}%): el escenario es consistente con el evento de "
                                        f"*{evento_similar_r.get('Fecha', '—')}* en {evento_similar_r.get('Zona', '—')} "
                                        f"({evento_similar_r.get('Resultado', '—')})."))
        elif confianza_r < 60:
            hallazgos.append(("red", f"📊 **Confianza baja del modelo** ({confianza_r}%): este escenario se aleja bastante de los datos "
                                      f"históricos de calibración. **Decisión sugerida:** tratar el resultado con cautela y reforzar la "
                                      f"recolección de datos reales en campo antes de fijar el umbral definitivo."))

        color_map = {"red": (RED_BG, RED_DARK), "amber": (AMBER_BG, AMBER_DARK), "green": (GREEN_BG, GREEN_DARK), "blue": (BLUE_BG, BLUE_DARK)}
        for nivel, texto in hallazgos:
            bg, fg = color_map[nivel]
            st.markdown(f'<div style="background:{bg};border-radius:12px;padding:12px 16px;margin-bottom:8px;'
                        f'color:{TEXT_DARK};font-size:13.5px;line-height:1.55;border-left:5px solid {fg};">{texto}</div>',
                        unsafe_allow_html=True)

        n_alertas = sum(1 for n, _ in hallazgos if n in ("red", "amber"))
        if n_alertas == 0:
            st.success("✅ No se identificaron riesgos relevantes en este escenario — el sistema respondería como está diseñado.")
        else:
            st.warning(f"Se identificaron **{n_alertas}** punto(s) a revisar antes de dar por validado este escenario. "
                       f"Ajusta los supuestos arriba y vuelve a ejecutar el simulacro para comparar decisiones.")

        st.write("")
        st.markdown("**Revive cómo se vería la alerta desde otros puntos de vista:**")
        b1, b2 = st.columns(2)
        with b1:
            if st.button("📱 Ver la alerta tal como llegaría al celular", use_container_width=True, type="primary", key="btn_celular_sim"):
                dialog_celular()
        with b2:
            if st.button("🏛 Ver el panel de control de la Alcaldía", use_container_width=True, type="primary", key="btn_alcaldia_sim"):
                dialog_alcaldia()

        st.success("✅ Simulacro completo — así fluye la información desde el sensor hasta la decisión institucional.")

# ---------------------------------------------------------------- TAB 3
with tab3:
    st.subheader("Arquitectura del sistema: de la montaña a la nube")
    capas = [
        ("orange", "CAPA 1&2", "Captura y Comunicación (IoT Edge)",
         "Pluviómetros, sensores de nivel de río, sensores de humedad del suelo y cámaras en las laderas críticas "
         "transmiten datos vía LoRaWAN y 4G/5G. Cada nodo lleva panel solar y batería de respaldo con autonomía "
         "≥72 h, para operar en zonas rurales sin red eléctrica estable."),
        ("blue", "CAPA 3", "Plataforma Central de Datos",
         "Un Context Broker (estándar NGSI) integra en una única fuente de verdad los datos del IDEAM, el histórico "
         "climático, los sensores IoT y los reportes ciudadanos. Incluye un modo degradado: si se pierde la conexión "
         "a la nube, el gateway local mantiene un umbral de alerta autónomo."),
        ("purple", "CAPA 4", "Inteligencia Artificial y Procesamiento",
         "Algoritmos predictivos cruzan lluvia acumulada, humedad del suelo y movimiento del terreno para generar "
         "el índice de riesgo de deslizamiento."),
        ("orange", "CAPA 5", "Gestión de Alertas Inteligentes",
         "Notificación automática por SMS, WhatsApp, sirenas comunitarias y app móvil cuando el índice de riesgo "
         "supera el umbral."),
        ("teal", "CAPA 6", "Toma de Decisiones y Acción",
         "Alcaldía, UNGRD, Bomberos, Defensa Civil y la comunidad coordinan la respuesta y activan protocolos de "
         "evacuación."),
    ]
    for color, badge, title, desc in capas:
        with st.expander(f"**{badge} · {title}**"):
            st.markdown(f'<div class="card {color}"><p>{desc}</p></div>', unsafe_allow_html=True)

    st.markdown('<p class="big-title">🔀 Flujo de datos de extremo a extremo</p>', unsafe_allow_html=True)
    nodos = ["Pluviómetro", "Sensor humedad", "Sensor movimiento", "Gateway LoRaWAN", "Context Broker (NGSI)",
              "Motor de IA", "Sistema de Alertas", "SMS", "WhatsApp", "Sirena", "App móvil",
              "Alcaldía", "UNGRD", "Comunidad"]
    idx = {n: i for i, n in enumerate(nodos)}
    links_src = ["Pluviómetro", "Sensor humedad", "Sensor movimiento", "Gateway LoRaWAN", "Context Broker (NGSI)",
                 "Motor de IA", "Sistema de Alertas", "Sistema de Alertas", "Sistema de Alertas", "Sistema de Alertas",
                 "SMS", "WhatsApp", "Sirena", "App móvil"]
    links_dst = ["Gateway LoRaWAN", "Gateway LoRaWAN", "Gateway LoRaWAN", "Context Broker (NGSI)", "Motor de IA",
                 "Sistema de Alertas", "SMS", "WhatsApp", "Sirena", "App móvil",
                 "Comunidad", "Comunidad", "Comunidad", "Alcaldía"]
    fig_sankey = go.Figure(go.Sankey(
        node=dict(label=nodos, pad=16, thickness=18,
                  color=[ORANGE]*3 + [BLUE, PURPLE, "#5B21B6", AMBER] + [GREEN]*4 + [BLUE, BLUE, GREEN],
                  line=dict(color=TEXT_DARK, width=0.5)),
        link=dict(source=[idx[s] for s in links_src], target=[idx[d] for d in links_dst],
                  value=[3]*len(links_src), color="rgba(255,68,31,0.20)"),
        textfont=dict(color=TEXT_DARK, size=14, family="Arial Black"),
    ))
    fig_sankey.update_layout(height=440, paper_bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT_DARK, size=13))
    st.plotly_chart(fig_sankey, use_container_width=True)

    st.subheader("Especificaciones técnicas por capa")
    busq_spec = st.text_input("🔎 Buscar especificación", key="busq_spec")
    st.dataframe(filtro_texto(ESPECIFICACIONES, busq_spec), use_container_width=True, hide_index=True)

    st.subheader("Ficha técnica de integración y protocolos")
    busq_proto = st.text_input("🔎 Buscar tecnología o protocolo", key="busq_proto")
    st.dataframe(filtro_texto(PROTOCOLOS, busq_proto), use_container_width=True, hide_index=True)

# ---------------------------------------------------------------- TAB 4
with tab4:
    st.subheader("Matriz de cuatro hélices")
    cols = st.columns(4)
    for col, a in zip(cols, ACTORES):
        with col:
            funciones_html = "".join(f"<li>{f}</li>" for f in a["Funciones"][:2])
            st.markdown(f"""
            <div class="card {a['color']}" style="min-height:280px;">
            <div class="actor-head">
              <div class="actor-icon" style="background:{a['fill']};">{a['icon']}</div>
              <h4 style="margin:0;">{a['Hélice']}</h4>
            </div>
            <p style="font-size:12.5px;color:{TEXT_GRAY};">{a['Actores']}</p>
            <p style="font-size:13px;"><b>Aporta:</b> {a['Aporta']}</p>
            <ul>{funciones_html}<li>… y más (ver detalle)</li></ul>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Ver funciones completas ↗", key=f"actor_btn_{a['Hélice']}", use_container_width=True):
                dialog_actor(a)

    st.markdown("#### Tabla completa (filtrable y ordenable)")
    filtro = st.multiselect("Filtrar por hélice", ACTORES_DF["Hélice"].tolist(), default=ACTORES_DF["Hélice"].tolist())
    st.dataframe(ACTORES_DF[ACTORES_DF["Hélice"].isin(filtro)], use_container_width=True, hide_index=True)

# ---------------------------------------------------------------- TAB 5
with tab5:
    st.subheader("Gestión de riesgos técnicos")
    sev_filtro = st.multiselect("Filtrar por severidad", RIESGOS["Severidad"].unique().tolist(),
                                 default=RIESGOS["Severidad"].unique().tolist())
    riesgos_f = RIESGOS[RIESGOS["Severidad"].isin(sev_filtro)].reset_index(drop=True)
    st.dataframe(riesgos_f, use_container_width=True, hide_index=True)

    sel_riesgo = st.selectbox("Selecciona un riesgo para ver el detalle en una ventana emergente",
                               riesgos_f["Riesgo técnico"].tolist())
    if st.button("🔍 Abrir detalle del riesgo"):
        fila = riesgos_f[riesgos_f["Riesgo técnico"] == sel_riesgo].iloc[0]
        dialog_riesgo(fila)

    st.subheader("Hoja de ruta del proyecto (24 meses)")
    fm1, fm2, fm3 = st.columns(3)
    fm1.metric("Actividades totales", len(crono))
    fm2.metric("Fases", crono["Fase"].nunique())
    fm3.metric("Duración total", "24 meses")

    fase_filtro = st.multiselect("Filtrar por fase", crono["Fase"].unique().tolist(),
                                  default=crono["Fase"].unique().tolist())
    crono_f = crono[crono["Fase"].isin(fase_filtro)]

    fig_gantt = px.timeline(
        crono_f, x_start="Inicio", x_end="Fin", y="Actividad", color="Fase",
        hover_data={"Responsable": True, "Entregable": True, "Mes inicio": True, "Mes fin": True, "Inicio": False, "Fin": False},
        template=PLOTLY_TEMPLATE,
        color_discrete_sequence=[ORANGE, BLUE, PURPLE, GREEN],
    )
    fig_gantt.update_yaxes(autorange="reversed", title="")
    fig_gantt.update_layout(height=520, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                             legend=dict(orientation="h", y=-0.15))
    st.plotly_chart(fig_gantt, use_container_width=True)

    st.markdown("**Selecciona una actividad para ver su ficha completa (cuadro emergente):**")
    sel_act = st.selectbox("Actividad", crono_f["Actividad"].tolist(), label_visibility="collapsed")
    if st.button("📋 Abrir ficha de la actividad"):
        fila_act = crono_f[crono_f["Actividad"] == sel_act].iloc[0]
        dialog_actividad(fila_act)

    with st.expander("📋 Ver tabla completa del cronograma (con entregables)"):
        busq_crono = st.text_input("🔎 Buscar actividad, responsable o entregable", key="busq_crono")
        st.dataframe(filtro_texto(crono[["Fase", "Actividad", "Responsable", "Entregable", "Mes inicio", "Mes fin"]], busq_crono),
                     use_container_width=True, hide_index=True)

# ---------------------------------------------------------------- TAB 6
with tab6:
    st.markdown('<p class="big-title">📊 Indicadores clave — vista tipo Power BI</p>', unsafe_allow_html=True)
    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Tiempo de respuesta", "5 min", delta="-97% vs. hoy (180 min)", delta_color="inverse")
    d2.metric("Cobertura de sensores", "100%", delta="+100 pp vs. hoy (0%)")
    d3.metric("Canales de alerta", "4", delta="+4 vs. hoy (0)")
    d4.metric("Actores coordinados", "4", delta="+3 vs. hoy (1)")

    fig_kpi = px.bar(
        COMPARATIVA_KPI.melt(id_vars="Indicador", var_name="Momento", value_name="Valor"),
        x="Indicador", y="Valor", color="Momento", barmode="group", template=PLOTLY_TEMPLATE,
        color_discrete_map={"Antes (hoy)": RED, "Meta a 24 meses": GREEN}, height=380,
    )
    fig_kpi.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", legend_title="",
                           xaxis_title="", yaxis_title="")
    st.plotly_chart(fig_kpi, use_container_width=True)

    st.subheader("Antes vs. después del sistema")
    st.dataframe(ANTES_DESPUES, use_container_width=True, hide_index=True)

    st.subheader("🧮 Simulador de impacto (ilustrativo)")
    st.caption("Ejercicio ilustrativo para dimensionar el alcance — no es una predicción estadística.")
    viviendas_cubiertas = st.slider("Viviendas en zona de riesgo cubiertas por el sistema", 0, 100, 50, step=5)
    minutos_anticipacion = st.slider("Minutos de anticipación promedio de la alerta", 0, 30, 12, step=1)
    familias_protegidas = int(viviendas_cubiertas * 1.0)
    sim1, sim2, sim3 = st.columns(3)
    sim1.metric("Familias potencialmente protegidas", f"{familias_protegidas}")
    sim2.metric("Minutos ganados para evacuar", f"{minutos_anticipacion} min")
    sim3.metric("Nivel de cobertura", f"{viviendas_cubiertas}%")

    st.subheader("El valor público que Quetame puede ganar")
    impactos = [
        ("blue", "Protección de vidas", "Alertas oportunas que permiten evacuar antes de que el deslizamiento ocurra."),
        ("teal", "Menos pérdidas materiales", "Reducción de daños en vivienda e infraestructura mediante anticipación."),
        ("purple", "Mejor toma de decisiones", "Información en tiempo real para la Alcaldía y los organismos de socorro."),
        ("orange", "Cultura de prevención", "Una comunidad capacitada, informada y activa frente al riesgo."),
        ("blue", "Fortalecimiento institucional", "Articulación real entre Alcaldía, UNGRD, academia y sector privado."),
        ("pink", "Innovación pública rural", "Quetame como referente nacional de transformación digital en gestión del riesgo."),
    ]
    cols = st.columns(3)
    for i, (color, title, desc) in enumerate(impactos):
        with cols[i % 3]:
            st.markdown(f'<div class="card {color}"><h4>{title}</h4><p style="font-size:13px;">{desc}</p></div>',
                        unsafe_allow_html=True)

    st.markdown("#### Metas propuestas (indicadores cuantificados)")
    st.caption("El «Avance actual» parte en 0% porque el sistema aún no ha sido instalado — se actualizaría con datos reales durante la operación.")
    st.dataframe(
        KPIS, use_container_width=True, hide_index=True,
        column_config={"Avance actual": st.column_config.ProgressColumn("Avance actual", min_value=0, max_value=100, format="%d%%")},
    )

    with st.expander("💰 Ver estimación referencial de costos en COP (no es una cotización oficial)"):
        st.caption("Convertido con la TRM oficial del Banco de la República del 23 de julio de 2026: $3.206,86 COP/USD.")
        st.dataframe(COSTOS, use_container_width=True, hide_index=True)

    st.markdown(f"""
    <div class="card blue" style="margin-top:10px;">
    <p style="font-size:16px;">Más allá de una solución tecnológica, este proyecto propone un cambio de enfoque
    en la gestión pública de Quetame: pasar <b style="color:{ORANGE_DARK}">de la reacción a la anticipación</b>,
    de la improvisación a la planificación basada en evidencia, y de la vulnerabilidad a la
    <b style="color:{ORANGE_DARK}">resiliencia territorial</b>. Cada evento sin sistema de alerta temprana es una
    oportunidad perdida para salvar vidas.</p>
    </div>
    """, unsafe_allow_html=True)
