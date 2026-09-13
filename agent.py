import os
from datetime import datetime
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from tools import search_web

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    os.environ["GOOGLE_API_KEY"] = api_key

# Inicializar modelo
llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash"
)

def format_llm_response(content) -> str:
    """Normaliza la salida del LLM a texto plano sin bloques de diccionario."""
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        text_parts = []
        for part in content:
            if isinstance(part, dict) and "text" in part:
                text_parts.append(part["text"])
            elif isinstance(part, str):
                text_parts.append(part)
            else:
                text_parts.append(str(part))
        return "".join(text_parts).strip()
    if isinstance(content, dict) and "text" in content:
        return content["text"].strip()
    return str(content).strip()

def build_analysis_prompt(topic: str, raw_context: str) -> str:
    """Prompt adaptado para análisis tecnológico generalista y riguroso."""
    today = datetime.now().strftime("%d-%m-%Y")
    
    return f"""Eres un Lead Technology Analyst redactando el briefing diario de tecnología ({today}).

OBJETIVO:
Sintetizar las novedades más relevantes del sector tecnológico global basadas en el material provisto.

RESTRICCIONES:
- Tono analítico, objetivo y sobrio. Sin introducciones de cortesía ni despedidas.
- Prohibidas frases vacías de relleno publicitario o entusiasmo artificial.
- Si un dato o enlace no aparece en el extracto, no lo inventes ni asumas.
- Idioma: Español técnico profesional.

ESTRUCTURA (Markdown estricto):

# Tech Morning Briefing
*Fecha: {today} | Cobertura: {topic}*

## 1. Panorama Global
(Un único párrafo de 3-4 líneas resumiendo las corrientes dominantes de la jornada en la industria tech).

## 2. Novedades y Movimientos Clave
Para cada noticia relevante recopilada:
- **Titular / Movimiento:** [Qué ocurrió de forma concreta]
  - **Área:** [Inteligencia Artificial | Hardware & Semiconductores | Software & Cloud | Industria & Regulación | Ciberseguridad]
  - **Detalle Técnico/Estratégico:** [1-2 líneas explicando el impacto, lanzamiento, cambio arquitectónico o cifra clave]
  - **Repercusión en el Ecosistema:** [Qué significa para desarrolladores, empresas o el mercado]

## 3. Fuentes
- [[Título del artículo]](URL_completa)

MATERIAL RECOPILADO:
{raw_context}
"""

def generate_morning_briefing(topic: str, max_results: int = 5) -> str:
    print(f"[*] Rastreador: Extrayendo {max_results} noticias sobre '{topic}'...")
    news_items = search_web.invoke({"query": topic, "max_results": max_results})
    
    if not news_items:
        return "No se localizaron registros recientes para el tema consultado."

    context_lines = []
    for idx, item in enumerate(news_items, start=1):
        context_lines.append(
            f"Item #{idx}:\n"
            f"- Titular: {item.get('title')}\n"
            f"- Fecha: {item.get('date', 'N/D')}\n"
            f"- Enlace: {item.get('url')}\n"
            f"- Extracto: {item.get('body')}\n"
        )
    raw_context = "\n".join(context_lines)

    print("[*] Motor IA: Procesando matriz de inteligencia...")
    prompt = build_analysis_prompt(topic, raw_context)
    response = llm.invoke(prompt)
    return format_llm_response(response.content)

def save_report(content: str, filename_prefix: str = "briefing") -> str:
    """Exporta el reporte a un directorio dedicado."""
    os.makedirs("reports", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    filepath = os.path.join("reports", f"{filename_prefix}_{timestamp}.md")
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return filepath

if __name__ == "__main__":
    # Query amplia orientada a noticias tecnológicas destacadas
    tema = "technology news AI hardware software big tech"
    
    print("=" * 60)
    print("AI TECH BRIEFING - EJECUCIÓN GENERAL")
    print("=" * 60)
    
    # max_results=6 o 7 para dar mayor variedad temática al informe
    informe = generate_morning_briefing(tema, max_results=6)
    ruta_archivo = save_report(informe, filename_prefix="tech_briefing")
    
    print("\n" + "=" * 60)
    print(f"REPORTE GUARDADO EN: {ruta_archivo}")
    print("=" * 60 + "\n")
    print(informe)