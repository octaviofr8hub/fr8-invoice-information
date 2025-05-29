### Write code for the new module here and import it from agent.py.
from uagents import Agent, Context
from invoice_models import PDFRequest, PDFResponse
import httpx
from invoice_agent import InvoiceExtractor
from dotenv import load_dotenv
import os
load_dotenv()
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
ASI1_API_KEY = os.getenv('ASI1_API_KEY')
extractor = InvoiceExtractor(api_key=ASI1_API_KEY) 
agent = Agent(
    name="agent_1",
    seed="seed_1"
)
@agent.on_message(model=PDFRequest, replies=PDFResponse)
async def proxy_handler(ctx: Context, sender: str, msg: PDFRequest):
    ctx.logger.info(f"Recibido texto de {msg.path}, procesando con InvoiceExtractor")
    try:
        # Obtener el texto del mensaje
        texto = msg.content
        resultados_response, errores_response = extractor.extraer_datos(texto)
        resultado = resultados_response
        errores = errores_response
        ctx.logger.info(f"Sender {sender}")
        # Enviar respuesta manualmente al webhook
        async with httpx.AsyncClient() as client:
            response = await client.post(
                WEBHOOK_URL,
                json={"status": "received", "resultado": resultado, "errores": errores}
            )
            ctx.logger.info(f"Respuesta manual enviada a {WEBHOOK_URL}: {response.status_code}")
        #await ctx.send(sender, PDFResponse(resultado=resultado, errores=errores))
    except Exception as e:
        ctx.logger.error(f"Error al procesar texto: {str(e)}")
        #await ctx.send(sender, PDFResponse(resultado={}, errores={"error": str(e)}))

if __name__ == "__main__":
    agent.run()