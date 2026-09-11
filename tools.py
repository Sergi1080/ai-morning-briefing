import warnings
from langchain_core.tools import tool
from ddgs import DDGS

warnings.filterwarnings("ignore", category=RuntimeWarning)

@tool
def search_web(query: str, max_results: int = 5) -> list[dict]:
    """
    Busca noticias recientes en internet sobre un tema.
    Devuelve una lista de diccionarios con el título, url, fecha y resumen (body) de la noticia.
    """
    print(f"[Herramienta Ejecutándose] Buscando noticias sobre: '{query}'...")
    
    try:
        with DDGS() as ddgs:
            #.news en lugar de .text
            results = list(ddgs.news(query, max_results=max_results))
            
            if not results:
                return [{"error": "DuckDuckGo no devolvió resultados."}]
                
            return results
    except Exception as e:
        return [{"error": f"Error al buscar noticias: {str(e)}"}]

# --- BLOQUE DE PRUEBA ---
if __name__ == "__main__":
    print("Iniciando prueba de la herramienta de búsqueda de noticias...\n")
    
    resultados_prueba = search_web.invoke({"query": "vulnerabilidad ciberseguridad ataque"})
    
    print("\n--- RESULTADOS OBTENIDOS ---")
    for i, res in enumerate(resultados_prueba, 1):
        print(f"\nResultado {i}:")
        if "error" in res:
            print(f"{res['error']}")
        else:
            print(f"Título: {res.get('title')}")
            print(f"URL: {res.get('url')}") # Usamos 'url'
            print(f"Fecha: {res.get('date', 'Desconocida')}") # Añadimos la fecha
            print(f"Resumen: {res.get('body')}")