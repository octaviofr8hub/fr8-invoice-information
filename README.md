# fr8-invoices-information

Este proyecto es una aplicación FastAPI que procesa facturas en PDF, las envía a un agente de AgentVerse para extraer datos y recibe los resultados por un webhook. Usa ngrok para exponer el servidor FastAPI local a internet. Sigue estos pasos pa’ configurarlo y correrlo.

## Requisitos
- **Python 3.8+**: Descárgalo de [python.org](https://www.python.org/downloads/).
- **ngrok**: Regístrate gratis en [ngrok.com](https://ngrok.com) e instala el CLI.
- **Cuenta en AgentVerse**: Consigue una API key en [AgentVerse](https://agentverse.ai).
- **API Key de ASI1**: Obtén una API key pa’l `InvoiceExtractor` (cámbialo por los datos de tu proveedor).

## Instalación
1. **Clona el repositorio**:
   ```bash
   git clone <url-de-tu-repo>
   cd fr8-invoices-information
   ```

2. **Crea un entorno virtual**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. **Instala las dependencias**:
   ```bash
   pip install fastapi uvicorn pdfplumber uagents python-dotenv fetchai
   ```

4. **Instala ngrok**:
   - Descarga e instala ngrok desde [ngrok.com](https://ngrok.com).
   - Autentica ngrok:
     ```bash
     ngrok authtoken <tu-token-de-ngrok>
     ```

5. **Configura las variables de entorno**:
   Crea un archivo `.env` en la carpeta `app` con esto:
   ```env
   AGENTVERSE_API_KEY=<tu-api-key-de-agentverse>
   ASI1_API_KEY=<tu-api-key-de-asi1>
   WEBHOOK_URL=https://<tu-url-de-ngrok>/api/webhook
   TARGET_AGENT_ADDRESS=<direccion-de-tu-agente>
   ```
   - Cambia `<tu-url-de-ngrok>` por la URL que te dé ngrok (mira el paso 7).
   - Cambia `<direccion-de-tu-agente>` por la dirección del agente que obtengas al correr `proxy_agent.py` (mira el paso 8).

## Correr la aplicación
1. **Arranca el servidor FastAPI**:
   ```bash
   cd app
   uvicorn invoice_api:app --host 0.0.0.0 --port 8000 --reload
   ```
   Esto inicia el servidor en `http://localhost:8000`.

2. **Arranca ngrok**:
   ```bash
   ngrok http 8000
   ```
   Copia la URL de ngrok (p.ej., `https://f652-2806-2f0-a6a1-f8b3-d075-7e7a-969c-bcb5.ngrok-free.app`) y actualiza `WEBHOOK_URL` en `.env` añadiendo `/api/webhook` (p.ej., `https://f652-.../api/webhook`).

3. **Registra el webhook**:
   Corre el script pa’ registrar el webhook:
   ```bash
   python register_webhook.py
   ```
   Esto registra el webhook en AgentVerse con la `WEBHOOK_URL`.

4. **Arranca el agente de AgentVerse**:
   Corre el script del agente:
   ```bash
   python proxy_agent.py
   ```
   Anota la dirección del agente de los logs (p.ej., `agent1q_nueva_direccion...`) y actualiza `TARGET_AGENT_ADDRESS` en `.env`.

5. **Prueba la aplicación**:
   Manda un PDF de prueba al endpoint `/upload-pdf`:
   ```bash
   curl -X POST https://<tu-url-de-ngrok>/upload-pdf -F "file=@ruta/a/tu/factura.pdf"
   ```
   Revisa los logs de `invoice_api.py`, `proxy_agent.py` y ngrok (`http://127.0.0.1:4040`) pa’ verificar el flujo:
   - FastAPI envía el contenido del PDF a AgentVerse.
   - El agente procesa el PDF y manda los resultados al webhook.
   - El webhook (`/api/webhook`) recibe la respuesta.

## Solución de problemas
- **AgentVerse no recibe mensajes**:
  - Asegúrate que `TARGET_AGENT_ADDRESS` coincida con la dirección del agente en los logs de `proxy_agent.py`.
  - Verifica que `AGENTVERSE_API_KEY` sea válida.
  - Checa el panel de AgentVerse pa’l estado del agente.
- **Webhook no recibe respuestas**:
  - Confirma que `WEBHOOK_URL` coincida con la URL de ngrok más `/api/webhook`.
  - Prueba el webhook:
    ```bash
    curl -X POST https://<tu-url-de-ngrok>/api/webhook -H "Content-Type: application/json" -d '{"payload": {"resultado": {"test": "data"}, "errores": {}}}'
    ```
  - Contacta al soporte de AgentVerse si la URL del webhook no se actualiza.
- **Problemas con ngrok**:
  - Asegúrate que solo haya un túnel de ngrok corriendo:
    ```bash
    pkill ngrok
    ngrok http 8000
    ```
  - Revisa conflictos de puertos:
    ```bash
    netstat -tuln | grep 8000
    ```

## Notas
- El plan gratis de ngrok genera una URL nueva cada vez que lo corres. Actualiza `WEBHOOK_URL` y vuelve a correr `register_webhook.py` después de reiniciar ngrok.
- Contacta al soporte de AgentVerse si el registro del agente o webhook falla constantemente.
