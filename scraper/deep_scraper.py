import pandas as pd
import time
import random
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def conectar_a_chrome_real():
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def extraer_modo_dios(driver, url):
    try:
        # Navegamos haciendo Spoofing
        driver.execute_script(f"window.location.href = '{url}';")
        
        # Espera para que la página cargue visualmente
        espera_carga = random.uniform(8, 12)
        time.sleep(espera_carga)
        
        # Hacemos scroll para asegurar que todas las características sean visibles
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
        time.sleep(3) # Pausa tras el scroll

        # 1. Capturamos el texto visible
        texto_pantalla = driver.execute_script("return document.body.innerText;")
        
        # 2. Capturamos TODO el texto de la web (incluyendo modales ocultos como el del garaje)
        texto_oculto = driver.execute_script("return document.body.textContent;")
        
        datos = {"Enlace": url}

        if not texto_pantalla or ("€" not in texto_pantalla and "m²" not in texto_pantalla):
            print("   [!] Pantalla vacía o CAPTCHA.")
            return None

        # --- EXTRACCIÓN AVANZADA POR EXPRESIONES REGULARES ---

        # Precio
        match_precio = re.search(r'([\d\.]+)\s*€', texto_pantalla)
        if match_precio:
            datos["Precio"] = match_precio.group(1).replace('.', '')

        # Diccionario de características a buscar
        caracteristicas_buscar = {
            r"Superficie construida:\s*(.*)": "Superficie_Construida",
            r"Superficie útil:\s*(.*)": "Superficie_Util",
            r"Habitaciones:\s*(\d+)": "Habitaciones",
            r"Baños:\s*(\d+)": "Banos",
            r"Planta:\s*(.*)": "Planta",
            r"Antigüedad:\s*(.*)": "Antiguedad",
            r"Conservación:\s*(.*)": "Estado",
            r"Gastos de comunidad:\s*(.*)": "Gastos_Comunidad",
            r"Referencia:\s*(.*)": "Referencia"
        }

        # Buscamos cada característica en el texto visible
        for regex, columna in caracteristicas_buscar.items():
            match = re.search(regex, texto_pantalla, re.IGNORECASE)
            if match:
                datos[columna] = match.group(1).split('\n')[0].strip()

        # Booleano para Exterior/Interior
        if re.search(r'\bExterior\b', texto_pantalla, re.IGNORECASE):
            datos["Exterior"] = "Sí"
        elif re.search(r'\bInterior\b', texto_pantalla, re.IGNORECASE):
            datos["Exterior"] = "No"

        # --- EXTRACCIÓN DE LA DESCRIPCIÓN (Fuerza Bruta JS) ---
        try:
            script_desc = """
            var el = document.querySelector('.description__content');
            if (el && el.textContent.length > 20) return el.textContent;
            
            var padre = document.getElementById('descriptionSelector') || document.querySelector('.description');
            if (padre && padre.textContent.length > 20) return padre.textContent;
            
            return 'Vacio';
            """
            texto_bruto = driver.execute_script(script_desc)
            
            if texto_bruto != 'Vacio':
                texto_limpio = re.sub(r'\s+', ' ', texto_bruto).strip()
                texto_limpio = texto_limpio.replace('"', "'") 
                datos["Descripcion"] = texto_limpio
            else:
                datos["Descripcion"] = "Oculta en DOM"
        except Exception as e:
             datos["Descripcion"] = "Error"

        # --- EXTRACCIÓN DE CARACTERÍSTICAS PREMIUM (Modo Todo Terreno) ---
        # Sumamos TODO: Pantalla, Descripción y el DOM oculto. Lo pasamos a minúsculas.
        texto_total = (texto_pantalla + " " + datos.get("Descripcion", "") + " " + texto_oculto).lower()
        
        # Regex relajado: sin los límites \b para que detecte "Garaje1" o textos pegados en el HTML
        datos["Ascensor"] = "Sí" if re.search(r'ascensor|elevador', texto_total) else "No"
        datos["Garaje"] = "Sí" if re.search(r'garaje|parking|aparcamiento', texto_total) else "No"
        datos["Trastero"] = "Sí" if re.search(r'trastero', texto_total) else "No"
        datos["Terraza"] = "Sí" if re.search(r'terraza', texto_total) else "No"
        datos["Balcon"] = "Sí" if re.search(r'balcón|balcon', texto_total) else "No"
        datos["Jardin"] = "Sí" if re.search(r'jardín|jardin|patio', texto_total) else "No"
        datos["Piscina"] = "Sí" if re.search(r'piscina', texto_total) else "No"
        datos["Aire_Acondicionado"] = "Sí" if re.search(r'aire acondicionado|splits', texto_total) else "No"

        if len(datos) > 2:
            print(f"   [ÉXITO] {len(datos)-2} variables capturadas + Descripción.")
            return datos
        else:
            return None

    except Exception as e:
        print(f"   [!] Error: {e}")
        return None

if __name__ == "__main__":
    print("Conectando al Chrome Humano en el puerto 9222...")
    driver = conectar_a_chrome_real()
    
    try:
        df_base = pd.read_csv("datos_brutos_valencia.csv")
        lista_final = []

        # ¡RECUERDA! Cuando quieras lanzar los 2000, borra el ".head(5)" de esta línea
        for i, enlace in enumerate(df_base['Enlace'].head(2007)):
            print(f"\n>>> Procesando {i+1} | Lectura Óptica + DOM Oculto")
            resultado = extraer_modo_dios(driver, enlace)
            
            if resultado:
                lista_final.append(resultado)
            
            time.sleep(random.uniform(5, 8))

        if lista_final:
            df_final = pd.DataFrame(lista_final)
            df_final.to_csv("dataset_optico_completo.csv", index=False, encoding='utf-8-sig')
            print("\n¡HACKEO COMPLETADO! Revisa 'dataset_optico_completo.csv'.")

    finally:
        print("\nProceso terminado.")