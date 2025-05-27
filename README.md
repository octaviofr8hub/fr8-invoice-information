# fr8-invoices-information

Este proyecto es una aplicación pa’ procesar facturas en PDF. El **backend** (FastAPI) extrae el texto de los PDFs, lo envía a un agente de AgentVerse pa’ extraer datos y recibe los resultados por un webhook. El **frontend** (React) permite subir los PDFs y muestra los datos extraídos en una tabla. Usa ngrok pa’ exponer el backend local a internet. Sigue estos pasos pa’ configurarlo y correrlo.

## Requisitos
- **Python 3.8+**: Descárgalo de [python.org](https://www.python.org/downloads/).
- **Node.js 14+**: Descárgalo de [nodejs.org](https://nodejs.org).
- **ngrok**: Regístrate gratis en [ngrok.com](https://ngrok.com) e instala el CLI.
- **Cuenta en AgentVerse**: Consigue una API key en [AgentVerse](https://agentverse.ai).
- **API Key de ASI1**: Obtén una API key pa’l `InvoiceExtractor` (cámbialo por los datos de tu proveedor).
- **Navegador moderno**: Chrome, Firefox, Edge, etc.

## Estructura del proyecto
- `app/`: Contiene el backend (FastAPI, scripts de agente y webhook).
- `frontend/`: Contiene el frontend (React).

## Instalación
1. **Clona el repositorio**:
   ```bash
   git clone <url-de-tu-repo>
   cd fr8-invoices-information
   ```

2. **Configura el backend**:
   - **Crea un entorno virtual**:
     ```bash
     cd app
     python -m venv venv
     source venv/bin/activate  # En Windows: venv\Scripts\activate
     ```
   - **Instala las dependencias**:
     ```bash
     pip install fastapi uvicorn pdfplumber uagents python-dotenv fetchai
     ```
   - **Configura las variables de entorno**:
     Crea un archivo `.env` en `app/` con esto:
     ```env
     AGENTVERSE_API_KEY=<tu-api-key-de-agentverse>
     ASI1_API_KEY=<tu-api-key-de-asi1>
     WEBHOOK_URL=https://<tu-url-de-ngrok>/api/webhook
     TARGET_AGENT_ADDRESS=<direccion-de-tu-agente>
     ```
     - `<tu-url-de-ngrok>` se obtiene al correr ngrok (mira el paso 6).
     - `<direccion-de-tu-agente>` se obtiene al correr `proxy_agent.py` (mira el paso 8).

3. **Configura el frontend**:
   - **Ve a la carpeta del frontend**:
     ```bash
     cd ../frontend
     ```
   - **Instala las dependencias**:
     ```bash
     npm install
     ```
   - **Configura la URL del backend**:
     Si usas ngrok o el backend no está en `http://localhost:8000`, edita `frontend/src/App.js`:
     ```javascript
     const res = await fetch('https://<tu-url-de-ngrok>/upload-pdf', {
     ```
     Reemplaza `<tu-url-de-ngrok>` con la URL de ngrok (p.ej., `https://f652-2806-2f0-a6a1-f8b3-d075-7e7a-969c-bcb5.ngrok-free.app`) o déjalo como `http://localhost:8000` si el backend corre local.

4. **Instala ngrok**:
   - Descarga e instala ngrok desde [ngrok.com](https://ngrok.com).
   - Autentica ngrok:
     ```bash
     ngrok authtoken <tu-token-de-ngrok>
     ```

## Correr la aplicación
1. **Arranca el backend FastAPI**:
   ```bash
   cd app
   uvicorn invoice_api:app --host 0.0.0.0 --port 8000 --reload
   ```
   Esto inicia el servidor en `http://localhost:8000`.

2. **Arranca ngrok**:
   ```bash
   ngrok http 8000
   ```
   Copia la URL de ngrok (p.ej., `https://f652-2806-2f0-a6a1-f8b3-d075-7e7a-969c-bcb5.ngrok-free.app`) y actualiza `WEBHOOK_URL` en `app/.env` añadiendo `/api/webhook` (p.ej., `https://f652-.../api/webhook`). Si usas ngrok, también actualiza la URL en `frontend/src/App.js`.

3. **Registra el webhook**:
   Corre el script pa’ registrar el webhook en AgentVerse:
   ```bash
   python register_webhook.py
   ```
   Revisa los logs pa’ confirmar que se registró chido.

4. **Arranca el agente de AgentVerse**:
   Corre el script del agente:
   ```bash
   python proxy_agent.py
   ```
   Anota la dirección del agente de los logs (p.ej., `agent1q_nueva_direccion...`) y actualiza `TARGET_AGENT_ADDRESS` en `app/.env`.

5. **Arranca el frontend React**:
   ```bash
   cd ../frontend
   npm start
   ```
   Esto abre la app en tu navegador en `http://localhost:3000`.

6. **Usa la aplicación**:
   - Abre `http://localhost:3000` en tu navegador.
   - Selecciona un archivo PDF de factura con el botón de carga.
   - Haz clic en “Enviar al agente” pa’ mandar el PDF al backend.
   - Espera a que el backend procese el archivo y devuelva los resultados. El frontend mostrará una tabla con los campos extraídos, valores y errores (✅ o ❌).
   - Si ves un mensaje de error o el spinner no desaparece, revisa la sección de “Solución de problemas”.

## Solución de problemas
- **AgentVerse no recibe mensajes**:
  - Asegúrate que `TARGET_AGENT_ADDRESS` coincida con la dirección del agente en los logs de `proxy_agent.py`.
  - Verifica que `AGENTVERSE_API_KEY` sea válida.
  - Checa el panel de AgentVerse pa’l estado del agente.
  - Contacta al soporte de AgentVerse si el agente no recibe mensajes.

- **Webhook no recibe respuestas**:
  - Confirma que `WEBHOOK_URL` coincida con la URL de ngrok más `/api/webhook`.
  - Prueba el webhook:
    ```bash
    curl -X POST https://<tu-url-de-ngrok>/api/webhook -H "Content-Type: application/json" -d '{"payload": {"resultado": {"test": "data"}, "errores": {}}}'
    ```
  - Contacta al soporte de AgentVerse si la URL del webhook no se actualiza.

- **El frontend no conecta con el backend**:
  - Asegúrate que el backend esté corriendo:
    ```bash
    uvicorn invoice_api:app --host 0.0.0.0 --port 8000 --reload
    ```
  - Verifica que la URL en `frontend/src/App.js` coincida con la URL del backend (local o ngrok).
  - Abre la consola del navegador (F12 > Console) pa’ ver errores de red.

- **El PDF no se procesa**:
  - Confirma que el archivo es un PDF válido.
  - Revisa los logs del backend (`invoice_api.py`) pa’ ver si el PDF se recibió y se envió a AgentVerse.
  - Checa que el agente de AgentVerse esté activo.

- **Problemas con ngrok**:
  - Asegúrate que solo haya un túnel corriendo:
    ```bash
    pkill ngrok
    ngrok http 8000
    ```
  - Revisa conflictos de puertos:
    ```bash
    netstat -tuln | grep 8000
    ```

## Notas
- El plan gratis de ngrok genera una URL nueva cada vez que lo corres. Actualiza `WEBHOOK_URL` en `app/.env` y `frontend/src/App.js`, y vuelve a correr `register_webhook.py` después de reiniciar ngrok.
- Asegúrate que el backend y el agente de AgentVerse estén corriendo antes de usar el frontend.
- Contacta al soporte de AgentVerse si el registro del agente o webhook falla constantemente.

## Licencia
MIT License
