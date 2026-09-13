import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from tools import search_web
from notifier import send_email_report

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    os.environ["GOOGLE_API_KEY"] = api_key

# 1. Inicializar Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash"
)

# Categorias y sus respectivas consultas de busqueda
TOPICS = {
    "Inteligencia Artificial": "artificial intelligence LLM machine learning news",
    "Hardware y Semiconductores": "semiconductor chips hardware computing news",
    "Big Tech, Cloud y Software": "big tech cloud computing enterprise software news"
}

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

def fetch_category_news(category_name: str, query: str, max_results: int = 3) -> dict:
    """Extrae noticias para una categoria especifica."""
    print(f"[*] Rastreador [{category_name}]: buscando noticias...")
    results = search_web.invoke({"query": query, "max_results": max_results})
    return {"category": category_name, "items": results or []}

def gather_multi_topic_news(topics_dict: dict, max_results_per_topic: int = 3) -> dict:
    """Ejecuta las busquedas de cada tematica en hilos paralelos."""
    aggregated_results = {}
    
    with ThreadPoolExecutor(max_workers=len(topics_dict)) as executor:
        future_to_cat = {
            executor.submit(fetch_category_news, cat, query, max_results_per_topic): cat
            for cat, query in topics_dict.items()
        }
        for future in as_completed(future_to_cat):
            try:
                res = future.result()
                aggregated_results[res["category"]] = res["items"]
            except Exception as e:
                cat_name = future_to_cat[future]
                print(f"[!] Error extrayendo categoria '{cat_name}': {e}")
                aggregated_results[cat_name] = []
                
    return aggregated_results

def build_multi_topic_prompt(gathered_news: dict) -> str:
    """Genera el prompt alimentado con el contexto de multiples categorias."""
    today = datetime.now().strftime("%d-%m-%Y")
    
    raw_context_blocks = []
    for category, items in gathered_news.items():
        raw_context_blocks.append(f"\n=== CATEGORÍA: {category.upper()} ===")
        if not items:
            raw_context_blocks.append("Sin registros recientes disponibles.")
            continue
        for idx, item in enumerate(items, start=1):
            raw_context_blocks.append(
                f"[{idx}] Titular: {item.get('title')}\n"
                f"    Fecha: {item.get('date', 'N/D')}\n"
                f"    URL: {item.get('url')}\n"
                f"    Extracto: {item.get('body')}\n"
            )
            
    full_context = "\n".join(raw_context_blocks)

    return f"""Eres un Lead Technology Analyst redactando el Tech Morning Briefing consolidado del día ({today}).

OBJETIVO:
Analizar la información sectorial provista y generar un informe estratégico, denso y objetivo dividido por verticales.

REGLAS DE REDACCIÓN:
- Idioma: Español técnico formal.
- Tono neutral, sobrio y directo. Prohibido relleno editorial, metáforas o introducciones vacías.
- Basa tus conclusiones únicamente en el material recopilado.

ESTRUCTURA OBLIGATORIA (Markdown estricto):

# Global Tech Morning Briefing
*Fecha: {today}*

## 1. Panorama Ejecutivo
(Párrafo de síntesis global conectando los puntos más relevantes de las distintas áreas de la jornada).

## 2. Novedades por Vertical
Organiza el análisis respetando las siguientes subsecciones:

### A. Inteligencia Artificial & Algoritmos
(Desglosa los hallazgos principales con viñetas: titular, impacto técnico y relevancia).

### B. Semiconductores & Infraestructura Hardware
(Desglosa avances en chips, nodos de fabricación, rendimiento o servidores).

### C. Big Tech, Software & Cloud Enterprise
(Movimientos de plataformas, negocio, arquitectura o lanzamientos).

## 3. Fuentes y Lecturas Recomendadas
(Lista limpia de enlaces recopilados ordenados por título con formato Markdown).

NOTICIAS RECOPILADAS EN TIEMPO REAL:
{full_context}
"""

def generate_consolidated_briefing() -> str:
    print("[*] Iniciando recopilacion paralela multi-topico...")
    news_by_category = gather_multi_topic_news(TOPICS, max_results_per_topic=3)
    
    print("[*] Sintetizando matriz tecnologica con Gemini...")
    prompt = build_multi_topic_prompt(news_by_category)
    response = llm.invoke(prompt)
    return format_llm_response(response.content)

def save_report(content: str, filename_prefix: str = "tech_briefing") -> str:
    """Exporta el reporte a un directorio dedicado."""
    os.makedirs("reports", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    filepath = os.path.join("reports", f"{filename_prefix}_{timestamp}.md")
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return filepath

# --- EJECUCION ---
if __name__ == "__main__":
    print("=" * 60)
    print("AI MULTI-TOPIC BRIEFING ENGINE - EJECUCIÓN")
    print("=" * 60)
    
    informe = generate_consolidated_briefing()
    ruta_archivo = save_report(informe, filename_prefix="briefing_global")
    
    print("\n" + "=" * 60)
    print(f"REPORTE COMPLETO GENERADO Y GUARDADO EN: {ruta_archivo}")
    print("=" * 60 + "\n")
    print(informe)

    # Envío automático a Gmail
    print("\n[*] Despachando briefing por correo electrónico...")
    send_email_report(informe)