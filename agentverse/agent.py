### Write code for the new module here and import it from agent.py.
from uagents import Agent, Context
from invoice_models import PDFRequest, PDFResponse
import httpx
from invoice_agent import InvoiceExtractor
import unicodedata
import numpy as np
import re

extractor = InvoiceExtractor(api_key="your_api_key")
agent = Agent(
    name="agent_1",
    seed="seed_1"
)

@agent.on_message(model=PDFRequest, replies=PDFResponse)
async def proxy_handler(ctx: Context, sender: str, msg: PDFRequest):
    ctx.logger.info(f"Recibido texto de {msg.path}, procesando con InvoiceExtractor")
    try:
        texto = msg.content_b64
        # Usar InvoiceExtractor para procesar el texto
        resultados_response, errores_response = extractor.extraer_datos(texto)
        resultado = resultados_response
        errores = errores_response
        ctx.logger.info(f"Sender {sender}")
        await ctx.send(sender, PDFResponse(resultado=resultado, errores=errores))

    except Exception as e:
        ctx.logger.error(f"Error al procesar texto: {str(e)}")
        await ctx.send(sender, PDFResponse(resultado={}, errores={"error": str(e)}))

if __name__ == "__main__":
    agent.run()