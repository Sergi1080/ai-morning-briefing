import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from tools import search_web

load_dotenv()

# Configurar credencial para el SDK
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    os.environ["GOOGLE_API_KEY"] = api_key

# 1. Inicializar el LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash"
)

def format_llm_response(content) -> str:
    """Normaliza la salida del LLM a texto plano legible."""
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

def generate_morning_briefing(topic: str, max_results: int = 4) -> str:
    """
    Extrae noticias usando tools.py y genera un resumen ejecutivo estructurado con Gemini.
    """
    print(f"[*] Buscando noticias recientes sobre: '{topic}'...")
    news_items = search_web.invoke({"query": topic, "max_results": max_results})
    
    if not news_items:
        return "No se encontraron noticias recientes sobre el tema especificado."

    # Estructuramos el contexto recopilado por el buscador
    context_lines = []
    for idx, item in enumerate(news_items, start=1):
        context_lines.append(
            f"[{idx}] Titulo: {item.get('title')}\n"
            f"    Fecha: {item.get('date', 'Desconocida')}\n"
            f"    Fuente: {item.get('url')}\n"
            f"    Extracto: {item.get('body')}\n"
        )
    raw_context = "\n".join(context_lines)

    # Prompt disenado para analisis tecnico y profesional
    prompt = f"""Eres un analista de inteligencia y tecnologia. Analiza las siguientes noticias recientes recopiladas de internet y elabora un briefing ejecutivo estructurado.

REGLAS DE FORMATO:
- Tono sobrio, tecnico y objetivo (sin introducciones conversacionales ni lenguaje informal).
- Estructura:
  1. Resumen Ejecutivo (un parrafo sintetizando el panorama global).
  2. Puntos Clave / Hallazgos (lista con lo mas critico).
  3. Fuentes de Referencia (titulos y enlaces de origen).
- No inventes informacion ajena a los extractos proporcionados.

NOTICIAS RECOPILADAS:
{raw_context}
"""

    print("[*] Sintetizando informacion con Gemini...")
    response = llm.invoke(prompt)
    return format_llm_response(response.content)

# --- EJECUCION PRINCIPAL ---
if __name__ == "__main__":
    tema_interes = "cybersecurity vulnerabilities"
    print("=" * 60)
    print("AI MORNING BRIEFING - INICIANDO SISTEMA")
    print("=" * 60)
    
    informe = generate_morning_briefing(tema_interes, max_results=4)
    
    print("\n" + "=" * 60)
    print("INFORME GENERADO:")
    print("=" * 60 + "\n")
    print(informe)