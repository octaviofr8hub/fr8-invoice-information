from uagents import Model


class PDFRequest(Model):
    path: str  
    content: str

class PDFResponse(Model):
    resultado: dict
    errores: dict