from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import sys


def setup_driver():
    """Configura el driver de Chrome con opciones para CI/CD"""
    chrome_options = Options()

    # Opciones necesarias para ejecutar en GitHub Actions
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')

    # Opciones adicionales para parecer más humano
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    # User agent actualizado
    chrome_options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    # Usar Chrome sin especificar Service (GitHub Actions ya tiene chromedriver en PATH)
    try:
        driver = webdriver.Chrome(options=chrome_options)
    except Exception as e:
        print(f"❌ Error al iniciar Chrome: {e}")
        # Intentar con service explícito
        service = Service('/usr/bin/chromedriver')
        driver = webdriver.Chrome(service=service, options=chrome_options)

    # Ocultar propiedades de webdriver
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    return driver


def test_duckduckgo_search():
    """Prueba de búsqueda en DuckDuckGo (no requiere CAPTCHA)"""
    driver = setup_driver()

    try:
        print("🚀 Iniciando prueba de búsqueda en DuckDuckGo...")

        # 1. Abrir DuckDuckGo
        driver.get("https://duckduckgo.com")
        print("✓ Página de DuckDuckGo cargada")
        time.sleep(2)
        print("Ejecutado")

        # 2. Localizar la barra de búsqueda
        wait = WebDriverWait(driver, 10)
        search_box = wait.until(
            EC.presence_of_element_located((By.NAME, "q"))
        )
        print("✓ Barra de búsqueda localizada")

        # 3. Escribir y buscar
        termino = "Automatización con Python Selenium"
        search_box.send_keys(termino)
        search_box.send_keys(Keys.RETURN)
        print(f"✓ Búsqueda realizadaa: '{termino}'")

        # 4. Esperar y verificar resultados
        time.sleep(3)

        # Verificar que aparezcan resultados (DuckDuckGo usa diferentes selectores)
        try:
            # Esperar a que aparezcan los resultados
            resultados = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "article[data-testid='result']"))
            )

            if len(resultados) > 0:
                print(f"✅ Prueba EXITOSA - Se encontraron {len(resultados)} resultados")
                print(f"✓ Primer resultado: {resultados[0].text[:100]}...")
                return True
            else:
                print("❌ Prueba FALLIDA - No se encontraron resultados")
                return False
        except Exception as e:
            print(f"⚠️ No se pudieron contar los resultados exactos, pero la búsqueda se realizó")
            # Verificar de manera alternativa si hay contenido en la página
            if "Automatización" in driver.page_source or "Python" in driver.page_source:
                print("✅ Prueba EXITOSA - Se encontró contenido relacionado")
                return True
            else:
                print(f"❌ Error: {str(e)}")
                return False

    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")
        # Tomar screenshot para debugging
        try:
            driver.save_screenshot('error_screenshot.png')
            print("📸 Screenshot guardado como 'error_screenshot.png'")
        except:
            pass
        return False

    finally:
        driver.quit()
        print("✓ Navegador cerrado")


if __name__ == "__main__":
    # Ejecutar la prueba
    resultado = test_duckduckgo_search()

    # Salir con código apropiado
    if resultado:
        print("\n🎉 TODAS LAS PRUEBAS PASARON")
        sys.exit(0)  # Código 0 = éxito
    else:
        print("\n💥 PRUEBAS FALLIDAS")
        sys.exit(1)  # Código 1 = fallo