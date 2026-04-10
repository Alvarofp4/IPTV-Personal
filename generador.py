import urllib.request
import re

# ==========================================
# 1. PARÁMETROS DE CONFIGURACIÓN
# ==========================================
SOURCE_URL = "https://iptv-org.github.io/iptv/countries/es.m3u"

# Define aquí tu topología exacta. El algoritmo respetará este vector de orden.
ORDEN_DESEADO = [
    "La 1", 
    "La 2", 
    "Antena 3", 
    "Cuatro", 
    "Telecinco", 
    "La Sexta"
]

# ==========================================
# 2. MOTOR ETL (Extract, Transform, Load)
# ==========================================
def extraer_datos_red():
    """Extrae el flujo M3U en bruto desde el nodo origen."""
    print("[INFO] Descargando base de datos origen...")
    # Añadimos cabeceras para evitar bloqueos básicos de servidor
    req = urllib.request.Request(SOURCE_URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        return response.read().decode('utf-8')

def parsear_m3u(contenido_bruto):
    """
    Transforma el texto plano en un Hash Map (diccionario).
    Complejidad temporal de búsqueda resultante: $O(1)$ por canal.
    """
    canales = {}
    
    # Expresión regular calibrada para separar:
    # 1. Atributos (duración, logos, grupos)
    # 2. Nombre exacto (después de la última coma)
    # 3. URL de transmisión
    patron = re.compile(r'#EXTINF:(.*),(.*)\n(http.*)', re.MULTILINE)
    coincidencias = patron.findall(contenido_bruto)
    
    for atributos, nombre, url in coincidencias:
        nombre_limpio = nombre.strip()
        # Si la fuente tiene varios enlaces para el mismo canal, los almacenamos todos en una lista
        if nombre_limpio not in canales:
            canales[nombre_limpio] = []
        canales[nombre_limpio].append((atributos.strip(), url.strip()))
        
    return canales

def compilar_lista(diccionario_canales):
    """Ensambla el nuevo archivo M3U siguiendo el vector de orden estricto."""
    print("[INFO] Compilando archivo de salida...")
    buffer_salida = "#EXTM3U\n"
    canales_procesados = 0
    
    for nombre in ORDEN_DESEADO:
        if nombre in diccionario_canales and len(diccionario_canales[nombre]) > 0:
            # Seleccionamos la primera opción de enlace disponible
            atributos, url = diccionario_canales[nombre][0]
            
            # Reconstruimos la sintaxis exacta de la directiva M3U
            buffer_salida += f"#EXTINF:{atributos},{nombre}\n{url}\n"
            canales_procesados += 1
        else:
            print(f"[WARN] No se encontró flujo de red para: '{nombre}'")
            
    return buffer_salida, canales_procesados

# ==========================================
# 3. EJECUCIÓN PRINCIPAL
# ==========================================
def main():
    try:
        bruto = extraer_datos_red()
        diccionario = parsear_m3u(bruto)
        nuevo_m3u, conteo = compilar_lista(diccionario)
        
        # Volcado a disco
        with open("mi_lista_personalizada.m3u", "w", encoding="utf-8") as f:
            f.write(nuevo_m3u)
            
        print(f"\n[ÉXITO] Archivo generado con precisión. Canales integrados: {conteo}/{len(ORDEN_DESEADO)}")
        
    except Exception as e:
        print(f"\n[ERROR CRÍTICO] Fallo en la ejecución: {e}")

if __name__ == "__main__":
    main()
