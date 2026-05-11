import pandas as pd
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def conectar_a_chrome_real():
    """Conexión Modo Dios por el puerto 9222 para evadir DataDome"""
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def extraer_datos_pagina_idealista(driver, url):
    try:
        # Spoofing de navegación
        driver.execute_script(f"window.location.href = '{url}';")
        time.sleep(random.uniform(7, 10))

        # Scroll humano en 3 pasos para cargar todas las fotos y evitar bloqueos
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/3);")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/1.5);")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        # Inyección JavaScript basada en tu captura del DOM (F12)
        script_extraccion = """
        var articulos = document.querySelectorAll('article.item');
        var lista = [];
        for (var i = 0; i < articulos.length; i++) {
            var linkEl = articulos[i].querySelector('a.item-link');
            var priceEl = articulos[i].querySelector('.item-price');
            var detailEls = articulos[i].querySelectorAll('.item-detail');

            // Solo cogemos pisos reales (descartamos publicidad intercalada)
            if (linkEl && priceEl) {
                var detalles = [];
                for (var j=0; j<detailEls.length; j++) {
                    detalles.push(detailEls[j].innerText.trim());
                }
                lista.push({
                    "Título": linkEl.innerText.trim(),
                    "Precio": priceEl.innerText.trim(),
                    "Detalles": detalles.join(' | '),
                    "Enlace": linkEl.href.split('?')[0] // Quitamos parámetros de rastreo
                });
            }
        }
        return lista;
        """
        
        datos = driver.execute_script(script_extraccion)
        print(f"   [ÉXITO] {len(datos)} pisos capturados en esta página.")
        return datos

    except Exception as e:
        print(f"   [!] Error en la extracción: {e}")
        return []

if __name__ == "__main__":
    print("Conectando al Chrome Humano (Puerto 9222)...")
    driver = conectar_a_chrome_real()
    
    url_base = "https://www.idealista.com/venta-viviendas/valencia-valencia/"
    total_datos = []
    
    # Para la primera prueba, vamos a escanear solo 3 páginas (aprox 90 pisos)
    # Cuando veas que funciona perfecto, súbelo a 60 o 70 para sacar los 2000
    paginas_a_procesar = 160
    
    try:
        for pagina in range(1, paginas_a_procesar + 1):
            print(f"\n--- INICIANDO PÁGINA {pagina} ---")
            
            # Lógica de paginación de Idealista
            if pagina == 1:
                url_actual = url_base
            else:
                url_actual = f"{url_base}pagina-{pagina}.htm"
                
            datos_pagina = extraer_datos_pagina_idealista(driver, url_actual)
            total_datos.extend(datos_pagina)
            
            # Pausa OBLIGATORIA entre páginas. Idealista banea si vas muy rápido.
            espera = random.uniform(10, 15)
            print(f"   [Zzz] Pausa antibot de {espera:.1f} segundos...")
            time.sleep(espera)

        if total_datos:
            df = pd.DataFrame(total_datos)
            
            # Limpiamos duplicados (a veces Idealista repite pisos en la página siguiente)
            original = len(df)
            df = df.drop_duplicates(subset=['Enlace'], keep='first')
            print(f"\n[INFO] Registros capturados: {original}")
            print(f"[INFO] Registros únicos reales: {len(df)}")
            
            df.to_csv("enlaces_idealista_brutos.csv", index=False, encoding='utf-8-sig')
            print("\n¡PROCESO COMPLETADO! Archivo 'enlaces_idealista_brutos.csv' generado.")
        else:
            print("\n[!] ERROR: No se han podido recolectar datos.")
            
    finally:
        print("Proceso finalizado. El navegador sigue abierto por si necesitas verificar.")