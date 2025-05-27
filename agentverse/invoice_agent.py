# Agentverse code
### Write code for the new module here and import it from agent.py. 
#import os
import requests
#import pdfplumber
import json
import re
import numpy as np

class InvoiceExtractor:
    def __init__(self, api_key=None):
        """
        Inicializa el extractor de facturas.
        
        Args:
            model_name (str): Nombre del modelo ASI1 a utilizar
            api_key (str): API key para ASI1. Si es None, se intentará obtener de las variables de entorno
        """

        #self.api_key = api_key or os.getenv("ASI1_API_KEY")
        self.api_key = api_key
        if not self.api_key:
            raise ValueError("Se requiere una API key para ASI1. Proporciona una o configura la variable de entorno ASI1_API_KEY")
        
        self.model_name = "asi1-mini"
        self.api_url = "https://api.asi1.ai/v1/chat/completions"
        self.headers = {
            "Authorization": f"bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def _call_api(self, prompt):
        """
        Realiza una llamada directa a la API de ASI1.
        
        Args:
            prompt (str): El prompt a enviar al modelo
            
        Returns:
            str: La respuesta del modelo
        """
        payload = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "stream": False,
            "max_tokens": 1024
        }
        
        try:
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            
            response_json = response.json()
            if not response_json or "choices" not in response_json or not response_json["choices"]:
                print(f"Respuesta inesperada de la API: {response_json}")
                raise ValueError("La API devolvió una respuesta inválida o vacía")
                
            content = response_json["choices"][0]["message"]["content"]
            if not content or not content.strip():
                print("La API devolvió un contenido vacío")
                raise ValueError("La API devolvió un contenido vacío")
                
            return content
            
        except requests.exceptions.Timeout:
            print("La llamada a la API excedió el tiempo de espera")
            raise
        except requests.exceptions.RequestException as e:
            print(f"Error en la llamada a la API: {str(e)}")
            if hasattr(e.response, 'text'):
                print(f"Respuesta del servidor: {e.response.text}")
            raise
        except Exception as e:
            print(f"Error inesperado en la llamada a la API: {str(e)}")
            raise

    '''
    def _leer_texto_pdf(self, path_pdf):
        """
        Lee el texto de un archivo PDF.
        
        Args:
            path_pdf (str): Ruta al archivo PDF
            
        Returns:
            str: Texto extraído del PDF
        """
        with pdfplumber.open(path_pdf) as pdf:
            texto = "\n".join([pagina.extract_text() for pagina in pdf.pages if pagina.extract_text()])

        words_pdf = texto.split()
        return texto, words_pdf
    '''

    def _construir_prompt(self, texto_factura):
        """
        Construye el prompt para el modelo ASI1.
        
        Args:
            texto_factura (str): Texto de la factura
            
        Returns:
            str: Prompt formateado
        """
        prompt = f"""
        Extrae los siguientes campos de esta factura:

        - Nombre de la empresa emisora (quien emite la factura) (si no está, poner 0)
        - Nombre de la empresa receptora (a quien va dirigida la factura) (si no está, poner 0)
        - UUID de la factura (si esta en minusculas, ponerlo en mayusculas) (si no está, poner 0)
        - Moneda (Estandarizar a USD o MXN) (si no está, poner 0)
        - Subtotal (si no está, poner 0)
        - IVA trasladado (si no está, poner 0)
        - IVA retenido (si no está, poner 0)
        - Total (si no está, poner 0)

        Factura:
        ---
        {texto_factura}
        ---

        Responde solo en formato JSON válido y sin ningún comentario adicional.
        Que siga la siguiente estructura:

        {{
            "pdf_billed_company_name": "string",
            "pdf_billing_company_name": "string",
            "pdf_provider_bill_uuid": "string",
            "pdf_currency_code": "string",
            "pdf_sub_total": "float",
            "pdf_traslado": "float",
            "pdf_retencion": "float",
            "pdf_total": "float"
        }}
        """
        return prompt

    def _process_json(self, json_str):
        """
        Procesa el JSON de respuesta y genera el diccionario de datos y errores.
        
        Args:
            json_str (str): JSON en formato string
            
        Returns:
            tuple: (diccionario de datos, diccionario de errores)
        """
        # Convertir el string JSON a diccionario
        data_dict = json.loads(json_str)
        
        # Crear diccionario de errores con la misma estructura
        error_dict = {
            "pdf_billed_company_name": data_dict["pdf_billed_company_name"] == "0",
            "pdf_billed_company_rfc": len(data_dict["pdf_billed_company_rfc"]) == "0",
            "pdf_billing_company_name": data_dict["pdf_billing_company_name"] == "0",
            "pdf_billing_company_rfc": data_dict["pdf_billing_company_rfc"] == "0",
            "pdf_provider_bill_uuid": data_dict["pdf_provider_bill_uuid"] == "0",
            "pdf_currency_code": data_dict["pdf_currency_code"] == "0",
            "pdf_sub_total": data_dict["pdf_sub_total"] == 0,
            "pdf_traslado": data_dict["pdf_traslado"] == 0,
            "pdf_retencion": data_dict["pdf_retencion"] == 0,
            "pdf_total": data_dict["pdf_total"] == 0
        }
        
        # Convertir campos numéricos a float
        numeric_fields = ["pdf_sub_total", "pdf_traslado", "pdf_retencion", "pdf_total"]
        for field in numeric_fields:
            data_dict[field] = float(data_dict[field])
            
        return data_dict, error_dict
    
    def _find_rfc(self,words_pdf):
        """
        Finds possible RFCs in the extracted words.
        
        Parameters:
        - words_pdf (list): List of words extracted from the PDF.
        
        Returns:
        - possible_rfc (list): List of possible RFCs found in the PDF.
        """

        rfc_pattern = re.compile(r'\b([A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3})\b')
        possible_rfc = []
        for word in words_pdf:
            if rfc_pattern.match(word):
                possible_rfc.append(word)
        
        if len(possible_rfc) == 0:
            self.error = True
        return np.unique(possible_rfc).tolist()
    
    #def extraer_datos(self, path_pdf):
    def extraer_datos(self, texto_factura):
        """
        Extrae los datos de una factura en formato PDF.

        Args:
            path_pdf (str): Ruta al archivo PDF de la factura

        Returns:
            tuple: (diccionario con datos extraídos, diccionario con errores de captura)
        """
        #texto_factura, words_pdf = self._leer_texto_pdf(path_pdf)
        if not texto_factura or not texto_factura.strip():
            raise ValueError("No se pudo extraer texto del PDF o el PDF está vacío")

        words_pdf = texto_factura.split()
        prompt = self._construir_prompt(texto_factura)
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                respuesta = self._call_api(prompt)
                possible_rfc = self._find_rfc(words_pdf)

                # Detectar RFCs
                if "FHM190118EN7" in possible_rfc:
                    pdf_billing_company_rfc = "FHM190118EN7"
                    possible_rfc.remove("FHM190118EN7")
                else:
                    pdf_billing_company_rfc = "0"

                pdf_billed_company_rfc = possible_rfc if len(possible_rfc) > 0 else "0"

                # Procesar respuesta JSON según su formato
                if respuesta.strip().startswith('{'):
                    json_data = json.loads(respuesta)
                elif '```json' in respuesta:
                    json_str = respuesta.split('```json\n')[1].split('\n```')[0]
                    json_data = json.loads(json_str)
                elif '```' in respuesta:
                    json_str = respuesta.split('```\n')[1].split('\n```')[0]
                    json_data = json.loads(json_str)
                else:
                    json_data = json.loads(respuesta)

                json_data["pdf_billing_company_rfc"] = pdf_billing_company_rfc
                json_data["pdf_billed_company_rfc"] = pdf_billed_company_rfc
                # Serializar nuevamente a string
                data_json_str = json.dumps(json_data)

                # Procesar el JSON
                data_dict, error_dict = self._process_json(data_json_str)

                return data_dict, error_dict

            except json.JSONDecodeError as e:
                retry_count += 1
                if retry_count >= max_retries:
                    print(f"Error al decodificar JSON después de {max_retries} intentos: {str(e)}")
                    print("Contenido original:", respuesta)
                    raise ValueError(f"La respuesta no es un JSON válido después de {max_retries} intentos: {str(e)}")
                print(f"Intento {retry_count} fallido. Reintentando...")
                continue
            except Exception as e:
                print(f"Error al procesar la respuesta: {str(e)}")
                print("Contenido original:", respuesta)
                raise