import pandas as pd
import time
import random
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def conectar_a_chrome_real():
    """Conexión Modo Dios por el puerto 9222 para evadir DataDome de Idealista"""
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def extraer_modo_dios_idealista(driver, url):
    try:
        driver.execute_script(f"window.location.href = '{url}';")
        time.sleep(random.uniform(8, 12))
        
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/3);")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/1.5);")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        texto_pantalla = driver.execute_script("return document.body.innerText;")
        
        datos = {
            "Enlace": url, "Precio": "", "Superficie_Construida": "", "Superficie_Util": "",
            "Habitaciones": "", "Banos": "", "Planta": "", "Antiguedad": "", "Referencia": "",
            "Descripcion": "", "Ascensor": "No", "Garaje": "No", "Trastero": "No", "Terraza": "No",
            "Balcon": "No", "Jardin": "No", "Piscina": "No", "Aire_Acondicionado": "No",
            "Estado": "", "Exterior": "", "Gastos_Comunidad": ""
        }

        if not texto_pantalla or "Inmueble no encontrado" in texto_pantalla or "Robot" in texto_pantalla:
            print("   [!] Pantalla vacía, bloqueada o CAPTCHA.")
            return None

        # --- EXTRACCIÓN BÁSICA POR REGEX ---
        match_precio = re.search(r'([\d\.]+)\s*€', texto_pantalla)
        if match_precio:
            datos["Precio"] = match_precio.group(1).replace('.', '')

        caracteristicas_buscar = {
            r"(\d+)\s*m² construidos": "Superficie_Construida",
            r"(\d+)\s*m² útiles": "Superficie_Util",
            r"(\d+)\s*habitaci": "Habitaciones",
            r"(\d+)\s*baño": "Banos",
            r"Planta\s*(\d+)": "Planta",
            r"Referencia del anuncio\s*([A-Za-z0-9\-]+)": "Referencia",
            r"(Segunda mano/buen estado|Para reformar|Promoción de obra nueva)": "Estado",
            r"Gastos de comunidad:\s*(\d+)\s*€": "Gastos_Comunidad"
        }

        for regex, columna in caracteristicas_buscar.items():
            match = re.search(regex, texto_pantalla, re.IGNORECASE)
            if match:
                datos[columna] = match.group(1).strip()

        match_anyo = re.search(r"Construido en\s*(\d{4})", texto_pantalla, re.IGNORECASE)
        if match_anyo:
            anyo = int(match_anyo.group(1))
            if anyo < 1976:
                datos["Antiguedad"] = "Más de 50 años"
            elif anyo < 1996:
                datos["Antiguedad"] = "Entre 30 y 50 años"
            elif anyo < 2016:
                datos["Antiguedad"] = "Entre 10 y 20 años"
            else:
                datos["Antiguedad"] = "Menos de 10 años"

        if re.search(r'\bexterior\b', texto_pantalla, re.IGNORECASE):
            datos["Exterior"] = "Sí"
        elif re.search(r'\binterior\b', texto_pantalla, re.IGNORECASE):
            datos["Exterior"] = "No"

        # --- EXTRACCIÓN DE LA DESCRIPCIÓN Y BLOQUE ANTI-SEO ---
        try:
            script_desc = """
            var el = document.querySelector('.adCommentsLanguage');
            if (el && el.textContent.length > 20) return el.textContent;
            var padre = document.querySelector('.comment');
            if (padre && padre.textContent.length > 20) return padre.textContent;
            return 'Vacio';
            """
            texto_bruto = driver.execute_script(script_desc)
            if texto_bruto != 'Vacio':
                texto_limpio = re.sub(r'\s+', ' ', texto_bruto).strip()
                datos["Descripcion"] = texto_limpio.replace('"', "'") 
            else:
                datos["Descripcion"] = "Oculta en DOM"
        except Exception:
             datos["Descripcion"] = "Error"

        # AISLAMIENTO: Capturamos solo las cajas de detalles reales (ignorando el pie de página)
        script_detalles = """
        var texto = "";
        var elementos = document.querySelectorAll('.details-property, .details-property-feature-one, .details-property-feature-two');
        for(var i=0; i<elementos.length; i++){
            texto += elementos[i].innerText + " ";
        }
        return texto;
        """
        texto_caracteristicas = driver.execute_script(script_detalles)

        # TEXTO DE BÚSQUEDA SANEADO
        texto_total = (str(texto_caracteristicas) + " " + str(datos.get("Descripcion", ""))).lower()
        
        datos["Ascensor"] = "Sí" if re.search(r'ascensor|elevador', texto_total) else "No"
        datos["Garaje"] = "Sí" if re.search(r'plaza de garaje|parking|aparcamiento|garaje', texto_total) else "No"
        datos["Trastero"] = "Sí" if re.search(r'trastero', texto_total) else "No"
        datos["Terraza"] = "Sí" if re.search(r'terraza', texto_total) else "No"
        datos["Balcon"] = "Sí" if re.search(r'balcón|balcon', texto_total) else "No"
        datos["Piscina"] = "Sí" if re.search(r'piscina', texto_total) else "No"
        datos["Aire_Acondicionado"] = "Sí" if re.search(r'aire acondicionado|splits|climatización', texto_total) else "No"

        # --- EL BORRADOR MÁGICO INTEGRADO (Filtro NLP anti-trampas) ---
        def tiene_jardin_real(texto):
            if re.search(r'jardín privado|jardin privado|jardín comunitario|jardin comunitario|jardín propio|zonas comunes con jardín', texto):
                return "Sí"
                
            trampas = [
                r'jardin(?:es)?\s+(?:del?|como\s+el\s+de|como)?\s*(?:turia|viveros|bot[aá]nico|real|ayora|monforte|cabecera)',
                r'jardin(?:es)?\s+del\s+real\s*\(viveros\)',
                r'antiguo cauce del r[ií]o turia',
                r'viejo cauce del r[ií]o turia',
                r'cauce del r[ií]o',
                r'(?:vistas a|junto a|rodeado de|cerca de|a pocos metros del?|proximidad a)(?:l| los)?\s+(?:parques?|jard[ií]n(?:es)?|zonas verdes)',
                r'jardines\s+(?:del entorno|de la zona|de los alrededores|p[úu]blicos)',
                r'agradable por los jardines',
                r'amplios jardines y zonas de paseo',
                r'parques y jardines'
            ]
            
            texto_limpio = texto
            for trampa in trampas:
                texto_limpio = re.sub(trampa, ' ', texto_limpio)
                
            if re.search(r'\bjard[ií]n\b|\bjardines\b|\bzonas verdes\b', texto_limpio):
                return "Sí"
            elif re.search(r'\bpatio\b(?!\s*(?:de luces|de manzanas|interior))', texto_limpio):
                return "Sí"
                
            return "No"
            
        datos["Jardin"] = tiene_jardin_real(texto_total)

        print(f"   [ÉXITO] Extracción completada para: {datos.get('Precio')}€")
        return datos

    except Exception as e:
        print(f"   [!] Error fatal en la URL: {e}")
        return None

if __name__ == "__main__":
    print("Conectando al Chrome Humano en el puerto 9222...")
    driver = conectar_a_chrome_real()
    
    try:
        # Asegúrate de que el nombre coincide con tu CSV de 4800 registros
        df_base = pd.read_csv("enlaces_idealista_brutos.csv")
        lista_final = []

        # CORTAMOS LA LISTA: Empezamos desde el registro 399 (que es el piso 400)
        enlaces_pendientes = df_base['Enlace'][399:] 
        
        for i, enlace in enumerate(enlaces_pendientes):
            # i empieza en 0 para esta nueva sub-lista, le sumamos 400 para saber el registro real
            num_actual = i + 400
            print(f"\n>>> Procesando {num_actual} | Idealista (Spoofing IP Nueva)")
            resultado = extraer_modo_dios_idealista(driver, enlace)
            
            if resultado:
                lista_final.append(resultado)
                # Guardado de seguridad en un archivo NUEVO (PARTE 2)
                pd.DataFrame(lista_final).to_csv("dataset_idealista_PARTE2.csv", index=False, encoding='utf-8-sig')
            
            # PAUSA ANTIBOT SEVERA (15 a 25 segundos)
            pausa = random.uniform(15, 25)
            print(f"   [Zzz] Pausa antibot de {pausa:.1f} segundos...")
            time.sleep(pausa)

        if lista_final:
            df_final = pd.DataFrame(lista_final)
            df_final.to_csv("dataset_idealista_FINAL_PARTE2.csv", index=False, encoding='utf-8-sig')
            print("\n¡HACKEO COMPLETADO! Revisa 'dataset_idealista_FINAL_PARTE2.csv'.")

    finally:
        print("\nProceso terminado.")