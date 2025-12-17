from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# 1. Configuración del navegador
driver = webdriver.Chrome()

try:
    # 2. Abrir Google
    driver.get("https://www.google.com")
    time.sleep(2) # Espera pequeña para que cargue la página

    # 3. Manejar el cuadro de cookies (Opcional, depende de tu región)
    try:
        # Busca el botón de "Aceptar todo" por su ID o texto
        boton_cookies = driver.find_element(By.XPATH, "//button[contains(., 'Aceptar')]")
        boton_cookies.click()
    except:
        pass # Si no aparece el aviso, continúa

    # 4. Localizar la barra de búsqueda
    # El nombre del elemento de búsqueda en Google suele ser 'q'
    busqueda = driver.find_element(By.NAME, "q")

    # 5. Escribir y buscar
    termino = "Automatización con Python"
    busqueda.send_keys(termino)
    busqueda.send_keys(Keys.RETURN)

    # Esperar unos segundos para ver los resultados
    time.sleep(5)

finally:
    # 6. Cerrar el navegador
    driver.quit()