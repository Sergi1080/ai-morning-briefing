# AI Morning Briefing Agent

Un agente autónomo de inteligencia artificial diseñado para ayudar con el esfuerzo informativo matutino y facilitar la ingesta de información. Rastrea la web de forma inteligente, filtra y sintetiza las noticias más importantes sobre Ciberseguridad, Inteligencia Artificial y Tecnología General (con tópicos intercambiables), entregando finalmente un informe estructurado de forma automatizada.

## ¿Qué problemas resuelve?

Cada día se publican cientos de artículos, papers y noticias tecnológicas. Revisar múltiples portales, blogs y redes sociales toma demasiado tiempo y genera una gran cantidad de ruido irrelevante.

Este proyecto automatiza un modelo de IA de forma que el agente actúa como un analista que busca, contrasta, sintetiza y entrega únicamente la información de alto valor bajo una plantilla estricta y limpia.

## Arquitectura y flujo de sistema

* **Trigger (Activación):** Desatendido mediante GitHub Actions. Ejecución automatizada de lunes a viernes a las 08:00 AM (CEST) utilizando una máquina virtual efímera, sin requerir hardware local.
* **Fase 1 - Two-Tier Retrieval (Búsqueda y Extracción):**
  * Búsqueda dinámica basada en los pilares temáticos configurados.
  * Extracción profunda de contenido web (evitando confiar únicamente en fragmentos superficiales).
* **Fase 2 - Memoria de Corto Período (Decaimiento de Novedad):**
  * Historial deslizante de los últimos 5 días almacenado en JSON.
  * Permite detectar evoluciones o seguimientos de noticias previas, etiquetándolas como actualización en lugar de descartarlas o repetirlas ciegamente.
* **Fase 3 - Motor de Síntesis:**
  * Invocación de Gemini (vía LangChain) aplicando una plantilla estricta para eliminar ruido.
  * Prevención de alucinaciones y obligación de adjuntar fuentes verificadas.
* **Fase 4 - Canal de Entrega:**
  * Generación de archivo local en formato Markdown (`reports/`).
  * Notificación automática despachada por correo electrónico (Gmail SMTP) con maquetación HTML limpia para fácil lectura en dispositivos móviles.

## Estructura del briefing generado

El sistema produce un informe categorizado por áreas temáticas. Cada noticia se condensa en un título directo, un resumen ejecutivo de un párrafo eliminando redundancias, y un enlace directo a la fuente original. 


<img width="858" height="650" alt="image" src="https://github.com/user-attachments/assets/2a1d148e-8a71-43ae-9477-8a59f163687b" />



*Arriba un ejemplo de la estructura del mail recibido*

## Guía de funcionamiento

### 1. Despliegue en la Nube (Recomendado)
El sistema está diseñado para ejecutarse solo en la nube a coste cero mediante GitHub Actions. Para activarlo en un *fork* o clon:
1. Ve a **Settings** > **Secrets and variables** > **Actions** en tu repositorio de GitHub.
2. Añade los siguientes `Repository secrets`:
   * `GEMINI_API_KEY`: Tu clave de Google Developer API.
   * `EMAIL_SENDER`: Tu dirección de Gmail desde la que se enviará.
   * `EMAIL_PASSWORD`: La "Contraseña de aplicación" de Google.
   * `EMAIL_RECEIVER`: El correo donde deseas recibir el reporte.
3. El agente se activará solo de lunes a viernes o manualmente desde la pestaña **Actions** > **Run workflow**.

### 2. Ejecución Local (Para pruebas o desarrollo)
Si deseas ejecutar el agente en tu propia máquina:
```bash
# 1. Clona el repositorio y entra en la carpeta
git clone <URL_DEL_REPOSITORIO>
cd ai-morning-briefing

# 2. Crea y activa un entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows usa: venv\Scripts\activate

# 3. Instala las dependencias
pip install -r requirements.txt

# 4. Configura tus variables de entorno creando un archivo .env en la raíz
# con GEMINI_API_KEY, EMAIL_SENDER, EMAIL_PASSWORD y EMAIL_RECEIVER.

# 5. Ejecuta el agente
python agent.py

