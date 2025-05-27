# FR8 Invoices Information

Este proyecto es un sistema de extracción de información de facturas utilizando inteligencia artificial. El sistema está diseñado para procesar facturas en formato PDF y extraer información relevante como datos del emisor, receptor, montos y detalles fiscales. El **backend** (FastAPI) extrae el texto de los PDFs, lo envía a un agente de AgentVerse (tecnologia de fetch.ai) para extraer datos mediante el modelo ASI1 y recibe los resultados por un webhook. El **frontend** (React) permite subir los PDFs y muestra los datos extraídos en una tabla. Usa ngrok para exponer el backend local a internet. Sigue estos pasos para configurarlo y correrlo.

## Características

- Extracción automática de datos de facturas PDF
- Procesamiento de múltiples facturas
- Extracción de información clave como:
  - Nombre y RFC del emisor
  - Nombre y RFC del receptor
  - Fecha de emisión
  - UUID
  - Montos (subtotal, IVA, total)
  - Moneda
- Salida en formato JSON estructurado
- Detección automática de RFCs mediante expresiones regulares
- Manejo robusto de errores y reintentos en llamadas a la API
- Procesamiento de respuestas JSON en múltiples formatos


## Requisitos
- **Python 3.8+**: Descárgalo de [python.org](https://www.python.org/downloads/).
- **Node.js 14+**: Descárgalo de [nodejs.org](https://nodejs.org).
- **ngrok**: Regístrate gratis en [ngrok.com](https://ngrok.com) e instala el CLI.
- **Cuenta en AgentVerse**: Consigue una API key en [AgentVerse](https://agentverse.ai).
- **API Key de ASI1**: Obtén una API key para `InvoiceExtractor` (cámbialo por los datos de tu proveedor).
- **Navegador moderno**: Chrome, Firefox, Edge, etc.

## Estructura del proyecto
```
fr8-invoices-information/
├──agentverse/                # Directorio que contiene el codigo que se debe alojar en agentverse
|  ├── invoice_agent.py       # Clase principal de AGENTE AI para extracción de facturas
|  ├── invoice_models.py      # Modelos para peticion y respuesta (empaquetan la informacion)
|  └── agent.py
├── app/
│   ├── invoice_agent.py       # Clase principal de AGENTE AI para extracción de facturas (para pruebas locales, en realidad va en Agentverse)
│   ├── invoice_api.py         # Modulo principal que contiene la logica de la API 
│   ├── test_one_invoice.py    # Script de prueba para una factura
│   └── test_multiple_invoices.py # Script de prueba para múltiples facturas
├── data/
│   └── raw/                   # Directorio para facturas PDF
├── frontend/                  # Frontend del proyecto desarrollado en React
├── notebooks/                 # Jupyter notebooks para análisis
├── requirements.txt          # Dependencias del proyecto
└── .env                      # Variables de entorno (no incluido en git)
```

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

3. **Arranca el agente de AgentVerse**:
   Ingresa a Agentverse -> Agents -> Create Agent esto para alojar un agente en los servicios de fetch.ai, ya que ahi es donde alojaremos nuestro codigo
   del directorio "agentverse"

   Build de agentverse:
   ```bash
   |_agent.py
   |_invoice_extractor.py
   |_invoice_models.py
   ```
   Anota la dirección del agente esta se encuentra en la seccion Overview del agente seleccionado y actualizala en el backend (`TARGET_AGENT_ADDRESS` en `app/.env`).

4. **Arranca el frontend React**:
   ```bash
   cd ../frontend
   npm start
   ```
   Esto abre la app en tu navegador en `http://localhost:3000`.

6. **Usa la aplicación**:
   - Abre `http://localhost:3000` en tu navegador.
   - Selecciona un archivo PDF de factura (de la carpeta data/raw/ de este proyecto) con el botón de carga.
   - Haz clic en “Enviar al agente” para mandar el PDF al backend.
   - Espera a que el backend procese el archivo y devuelva los resultados. El frontend mostrará una tabla con los campos extraídos, valores y errores (✅ o ❌).
   - Si ves un mensaje de error o el spinner no desaparece, revisa la sección de “Solución de problemas”.

## Solución de problemas
- **AgentVerse no recibe mensajes**:
  - Asegúrate que `TARGET_AGENT_ADDRESS` coincida con la dirección del agente de Agentverse.
  - Verifica que `AGENTVERSE_API_KEY` sea válida.
  - Checa el panel de AgentVerse para el estado del agente.
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
  - Abre la consola del navegador (F12 > Console) para ver errores de red.

- **El PDF no se procesa**:
  - Confirma que el archivo es un PDF válido.
  - Revisa los logs del backend (`invoice_api.py`) para ver si el PDF se recibió y se envió a AgentVerse.
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
- El plan gratis de ngrok genera una URL nueva cada vez que lo corres. Actualiza `WEBHOOK_URL` en `app/.env` y `frontend/src/App.js`, y vuelve a correr `invoice_api.py` después de reiniciar ngrok.
- Asegúrate que el backend y el agente de AgentVerse estén corriendo antes de usar el frontend.
- Contacta al soporte de AgentVerse si el registro del agente o webhook falla constantemente.

