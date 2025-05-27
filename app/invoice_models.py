from uagents import Model


class PDFRequest(Model):
    path: str  
    content_b64: str

class PDFResponse(Model):
    resultado: dict
    errores: dict