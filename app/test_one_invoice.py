from invoice_agent import InvoiceExtractor
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

ASI1_API_KEY = os.getenv("ASI1_API_KEY")

# Crear una instancia del extractor
extractor = InvoiceExtractor(api_key=ASI1_API_KEY)

# Extraer datos de una factura
resultado, errores = extractor.extraer_datos("../data/raw/error/49853.pdf")
print(resultado)
print(errores)
