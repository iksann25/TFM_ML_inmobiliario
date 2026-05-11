import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def configurar_driver():
    """Configuración profesional del navegador para evitar detecciones básicas."""
    chrome_options = Options()
    # chrome_options.add_argument("--headless") # Descomentar para ejecución en segundo plano
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--start-maximized")
    # User-Agent de escritorio para evitar que el servidor nos envíe la versión móvil
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

def gestionar_cookies(driver):
    """Localiza y pulsa el botón de aceptar cookies para limpiar la interfaz."""
    try:
        boton = WebDriverWait(driver, 7).until(
            EC.element_to_be_clickable((By.ID, "didomi-notice-agree-button"))
        )
        boton.click()
        print("   [OK] Consentimiento de cookies procesado.")
    except:
        pass # Si no aparece el banner, continuamos sin error

def extraer_datos_pagina(driver, url_objetivo):
    driver.get(url_objetivo)
    gestionar_cookies(driver)
    time.sleep(6) 

    # Scroll más agresivo para cargar TODO el contenido
    driver.execute_script("window.scrollTo(0, 2000);")
    time.sleep(3)
    
    lista_inmuebles = []
    # Selector de contenedor principal
    anuncios = driver.find_elements(By.CSS_SELECTOR, "div.ad-preview")
    
    print(f"   [DEBUG] Elementos detectados: {len(anuncios)}")
    
    for i, anuncio in enumerate(anuncios):
        try:
            # 1. Buscamos el título específicamente por su clase, no solo por etiqueta 'a'
            try:
                el_titulo = anuncio.find_element(By.CSS_SELECTOR, ".ad-preview__title, a[class*='title']")
                titulo = el_titulo.text.strip()
                enlace = el_titulo.get_attribute("href")
            except:
                continue # Si no hay título real, saltamos

            # FILTRO: Solo saltar si es publicidad de hipoteca
            if "Calcula" in titulo or "hipoteca" in titulo.lower():
                continue
            
            # 2. Precio (intentando varios formatos)
            try:
                precio = anuncio.find_element(By.CSS_SELECTOR, ".p-price, .ad-preview__price").text.strip()
            except:
                precio = "0"

            # 3. DETALLES (Ajustado según inspección del DOM en Ilustración 23)
            try:
                # Buscamos todos los párrafos que tienen la clase de características
                items_detalle = anuncio.find_elements(By.CSS_SELECTOR, "p.ad-preview__char")
                
                if items_detalle:
                    # Unimos el texto de todos los <p> encontrados (m2, hab, baños, planta)
                    detalles = " | ".join([item.text.strip() for item in items_detalle if item.text])
                else:
                    detalles = "Información no estructurada"
            except Exception:
                detalles = "Error de acceso al nodo de características"
            
            lista_inmuebles.append({
                "Título": titulo,
                "Precio": precio,
                "Detalles": detalles,
                "Enlace": enlace
            })
            print(f"   [OK] {len(lista_inmuebles)}: {titulo[:20]} | {precio}")
            
        except Exception as e:
            continue
            
    return lista_inmuebles

if __name__ == "__main__":
    driver = configurar_driver()
    # Estructura de URL real descubierta tras inspección
    base_url = "https://www.pisos.com/venta/pisos-valencia_capital_zona_urbana/"
    
    total_datos = []
    # Definir el rango de páginas (1 a 4 para pruebas; hasta 60 para el dataset final)
    paginas_a_procesar = 100
    
    try:
        for pagina in range(1, paginas_a_procesar + 1):
            url = base_url if pagina == 1 else f"{base_url}{pagina}/"
            print(f"\n--- INICIANDO PÁGINA {pagina} ---")
            
            datos_pagina = extraer_datos_pagina(driver, url)
            total_datos.extend(datos_pagina)
            
            # Pausa de seguridad para evitar bloqueos del servidor (Anti-bot)
            time.sleep(4) 

        if total_datos:
            df = pd.DataFrame(total_datos)
            
            # PROCESO DE DEDUPLICACIÓN TÉCNICA
            original = len(df)
            df = df.drop_duplicates(subset=['Título', 'Precio'], keep='first')
            print(f"\n[INFO] Registros capturados: {original}")
            print(f"[INFO] Registros tras eliminar duplicados: {len(df)}")
            
            # Guardado final con codificación segura
            df.to_csv("datos_brutos_valencia.csv", index=False, encoding='utf-8-sig')
            print("\n¡PROCESO COMPLETADO! Archivo 'datos_brutos_valencia.csv' generado.")
        else:
            print("\n[!] ERROR: No se han podido recolectar datos.")
            
    finally:
        driver.quit()