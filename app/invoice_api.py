from fastapi import FastAPI, UploadFile, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from uagents import Model
from fetchai.communication import send_message_to_agent, parse_message_from_agent
from fetchai.registration import register_with_agentverse
from uagents_core.identity import Identity
from invoice_models import PDFRequest
import base64
import uuid
import os
import json
import logging
from dotenv import load_dotenv
import asyncio
import pdfplumber
import shutil
import unicodedata

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

webhook_responses: dict[str, dict] = {}

# Almacenamos la ultima respuesta del webhook
latest_response = None
response_event = asyncio.Event()

load_dotenv()
AGENTVERSE_API_KEY = os.getenv("AGENTVERSE_API_KEY")
TARGET_AGENT_ADDRESS = os.getenv("TARGET_AGENT_ADDRESS") 
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  

TMP_DIR = "tmp"
os.makedirs(TMP_DIR, exist_ok=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

# Registrar webhook con Agentverse
def register_webhook():
    identity = Identity.from_seed("API PDF Processing", 1)
    logger.info(f"Client agent started with address: {identity.address}")
    register_with_agentverse(
        identity=identity,
        #url="http://localhost:5002/api/webhook",
        url=WEBHOOK_URL,
        agentverse_token=AGENTVERSE_API_KEY,
        agent_title="FastAPI Webhook",
        readme="Recibe respuestas de PDF desde Agentverse."
    )
    logger.info("Webhook registrado con Agentverse")
register_webhook()

def leer_texto_pdf(path_pdf):
    """
    Lee el texto de un archivo PDF.
    
    Args:
        path_pdf (str): Ruta al archivo PDF
        
    Returns:
        str: Texto extraído del PDF
    """
    # with pdfplumber.open(path_pdf) as pdf:
    #    texto = "\n".join([pagina.extract_text() for pagina in pdf.pages if pagina.extract_text()])
    #return texto
    try:
        with pdfplumber.open(path_pdf) as pdf:
            texto = "\n".join([pagina.extract_text() or "" for pagina in pdf.pages])
        # return texto
        #texto_normalizado = unicodedata.normalize('NFKD', texto)
        return texto
    except Exception as e:
        logger.error(f"Error al leer PDF: {e}")
        return ""

# Tarea para procesar PDF y enviar texto a Agentverse
async def process_and_send_pdf(file_content: bytes, filename: str):
    global latest_response, response_event
    try:
        # Guardar PDF temporalmente
        temp_path = os.path.join(TMP_DIR, f"{uuid.uuid4()}_{filename}")
        with open(temp_path, "wb") as f:
            f.write(file_content)
        
        # Extraer texto del PDF
        texto = leer_texto_pdf(temp_path)
        #print(texto)
        # Eliminar archivo temporal
        os.remove(temp_path)
        
        if not texto:
            return {"status": "error", "message": "No se pudo extraer texto del PDF"}

        # Enviar texto a Agentverse
        message = {
            "path": filename,
            "content_b64": texto  # Enviar texto en lugar de base64
        }
        model_digest = Model.build_schema_digest(PDFRequest)

        # Resetear la respuesta y el evento
        latest_response = None
        response_event.clear()

        send_message_to_agent(
            sender=Identity.from_seed("FastAPIWebhook", 0),
            target=TARGET_AGENT_ADDRESS,
            payload=message,
            model_digest=model_digest
        )
        logger.info(f"Texto de {filename} enviado a Agentverse")

        # Esperar la respuesta del webhook (máximo 30 segundos)
        try:
            await asyncio.wait_for(response_event.wait(), timeout=300.0)
            if latest_response:
                return latest_response
            else:
                return {"status": "error", "message": "No se recibió respuesta a tiempo"}
        except asyncio.TimeoutError:
            return {"status": "error", "message": "Tiempo de espera agotado para la respuesta"}

    except Exception as e:
        logger.error(f"Error procesando PDF: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        # Asegurar que el archivo temporal se elimine
        if os.path.exists(temp_path):
            os.remove(temp_path)


# Endpoint para recibir PDF desde React o alguna otra fuente
@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile, background_tasks: BackgroundTasks):
#async def upload_pdf(file: PDFRequest, background_tasks: BackgroundTasks):
    try:
        file_content = await file.read()
        #file_content = base64.b64decode(file.content_b64)
        filename = file.filename
        
        #background_tasks.add_task(process_and_send_pdf, file_content, filename, request_id)
        result = await process_and_send_pdf(file_content, filename)
        return JSONResponse(result)
        #return JSONResponse({"status": "PDF recibido, procesando en segundo plano"})
    except Exception as e:
        logger.error(f"Error recibiendo PDF: {e}")
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)


'''
# Webhook para respuestas de Agentverse
@app.post("/api/webhook")
async def webhook(request: Request):
    global latest_response
    global response_event
    try:
        
        # Leer el cuerpo como bytes y decodificar a string
        body = await request.body()
        if not body:
            logger.error("Cuerpo del request vacío")
            return JSONResponse({"status": "error", "message": "Empty request body"}, status_code=400)

        body_str = body.decode("utf-8")
        #logger.info(f"Cuerpo recibido: {body_str}")

        # Parsear el mensaje con parse_message_from_agent
        message = parse_message_from_agent(body_str)
        payload = message.payload
        if not payload:
            logger.error("No se encontro payload en el mensaje")
            return JSONResponse({"status": "error", "message": "No payload in message"}, status_code=400)

        # Extraer resultado y errores
        resultado = payload.get("resultado", {})
        errores = payload.get("errores", {})
        logger.info(f"Respuesta de Agentverse - Resultado: {resultado}, Errores: {errores}")

        # Almacenar la respuesta y señalar que la respuesta llego
        latest_response = {
            "status": "received",
            "resultado": resultado,
            "errores": errores
        }
        response_event.set()

        # Devolver respuesta
        return JSONResponse({
            "status": "received",
            "resultado": resultado,
            "errores": errores
        })
    except Exception as e:
        logger.error(f"Error en webhook: {e}")
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)
'''

@app.post("/api/webhook")
async def webhook(request: Request):
    global latest_response, response_event
    try:
        # Leer el cuerpo como bytes y decodificar a string
        body = await request.body()
        if not body:
            logger.error("Cuerpo del request vacío")
            return JSONResponse({"status": "error", "message": "Empty request body"}, status_code=400)

        body_str = body.decode("utf-8")
        logger.info(f"Cuerpo recibido: {body_str}")

        # Parsear el cuerpo como JSON directamente
        try:
            payload = json.loads(body_str)
        except json.JSONDecodeError as e:
            logger.error(f"Error al parsear JSON: {e}")
            return JSONResponse({"status": "error", "message": "Invalid JSON body"}, status_code=400)

        # Extraer resultado y errores del payload
        resultado = payload.get("resultado", {})
        errores = payload.get("errores", {})
        logger.info(f"Respuesta de Agentverse - Resultado: {resultado}, Errores: {errores}")

        # Almacenar la respuesta y señalar que la respuesta llegó
        latest_response = {
            "status": "received",
            "resultado": resultado,
            "errores": errores
        }
        response_event.set()

        # Devolver respuesta al agente
        return JSONResponse({
            "status": "received",
            "message": "Webhook processed successfully",
            "resultado": resultado,
            "errores": errores
        })
    except Exception as e:
        logger.error(f"Error en webhook: {e}")
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

if __name__ == "__main__":
    register_webhook()
    