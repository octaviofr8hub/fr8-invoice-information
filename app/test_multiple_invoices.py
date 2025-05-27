from invoice_agent import InvoiceExtractor
import os
from dotenv import load_dotenv
import json
from datetime import datetime

# Cargar variables de entorno desde .env
load_dotenv()

def print_results(invoice_name, datos, errores):
    """
    Imprime los resultados de manera formateada
    """
    print("\n" + "="*50)
    print(f"Factura: {invoice_name}")
    print("="*50)
    
    print("\nDatos extraídos:")
    print(json.dumps(datos, indent=2, ensure_ascii=False))
    
    print("\nErrores de captura:")
    print(json.dumps(errores, indent=2, ensure_ascii=False))
    
    # Mostrar resumen de errores
    campos_con_error = [campo for campo, tiene_error in errores.items() if tiene_error]
    if campos_con_error:
        print("\nResumen de errores:")
        print(f"Se encontraron {len(campos_con_error)} campos con errores:")
        for campo in campos_con_error:
            print(f"- {campo}")
    else:
        print("\nNo se encontraron errores de captura")
    print("\n" + "-"*50)

def main():
    ASI1_API_KEY = os.getenv("ASI1_API_KEY")
    if not ASI1_API_KEY:
        raise ValueError("No se encontró la API key de ASI1 en las variables de entorno")

    # Crear una instancia del extractor
    extractor = InvoiceExtractor(api_key=ASI1_API_KEY)

    # Directorio de facturas
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "raw", "error")
    
    # Verificar que el directorio existe
    if not os.path.exists(data_dir):
        raise FileNotFoundError(f"No se encontró el directorio: {data_dir}")

    # Procesar cada factura
    invoice_paths = [f for f in os.listdir(data_dir) if f.endswith('.pdf')]
    
    if not invoice_paths:
        print("No se encontraron archivos PDF en el directorio")
        return

    print(f"Procesando {len(invoice_paths)} facturas...")
    
    # Estadísticas
    total_errores = 0
    facturas_con_error = 0
    
    for invoice_path in invoice_paths:
        ruta_completa = os.path.join(data_dir, invoice_path)
        try:
            datos, errores = extractor.extraer_datos(ruta_completa)
            print_results(invoice_path, datos, errores)
            
            # Actualizar estadísticas
            if any(errores.values()):
                facturas_con_error += 1
                total_errores += sum(1 for error in errores.values() if error)
                
        except Exception as e:
            print(f"\nError al procesar {invoice_path}:")
            print(f"Error: {str(e)}")
    
    # Mostrar resumen final
    print("\nResumen del procesamiento:")
    print(f"Total de facturas procesadas: {len(invoice_paths)}")
    print(f"Facturas con errores: {facturas_con_error}")
    print(f"Total de errores encontrados: {total_errores}")
    print(f"Promedio de errores por factura: {total_errores/len(invoice_paths):.2f}")

if __name__ == "__main__":
    main()
