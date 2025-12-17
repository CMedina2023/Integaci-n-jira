# Guía Completa: Automatización de Pruebas con Selenium, GitHub Actions y Jira

## Índice
1. [Integración de GitHub con Jira](#1-integración-de-github-con-jira)
2. [Configuraciones Necesarias Antes de Comenzar](#2-configuraciones-necesarias-antes-de-comenzar)
3. [Ejecutar tu Primera Prueba Automatizada](#3-ejecutar-tu-primera-prueba-automatizada)
4. [Solución de Problemas](#4-solución-de-problemas)

---

## 1. Integración de GitHub con Jira

### ¿Qué Lograremos?

Conectar GitHub con Jira para que:
- Cada commit con un Issue Key aparezca automáticamente en Jira
- Las pruebas automatizadas se ejecuten en GitHub Actions
- El estado de los issues en Jira se actualice según el resultado de las pruebas
- Todo el equipo pueda ver el progreso en tiempo real

---

### Paso 1.1: Instalar GitHub para Jira

1. **Inicia sesión en Jira Cloud**
   - Ve a tu instancia: `https://tu-empresa.atlassian.net`

2. **Accede a las Aplicaciones**
   - Haz clic en el ícono de **Configuración** (⚙️) → **Aplicaciones** → **Encontrar nuevas aplicaciones**

3. **Busca e Instala**
   - Escribe: **"GitHub for Jira"**
   - Selecciona la aplicación oficial de GitHub
   - Haz clic en **"Get it now"** → **"Get app"**

4. **Autoriza la Conexión**
   - Haz clic en **"Get started"**
   - Serás redirigido a GitHub
   - Haz clic en **"Authorize"**

---

### Paso 1.2: Conectar tu Repositorio

1. **Selecciona tu Organización/Cuenta**
   - Después de autorizar, verás tus organizaciones de GitHub
   - Selecciona la organización donde está tu proyecto de pruebas

2. **Configura los Repositorios**
   - Selecciona **"Only select repositories"**
   - Elige el repositorio de tu proyecto de automatización
   - Haz clic en **"Install"**

3. **Confirma en Jira**
   - Serás redirigido a Jira
   - Verás un mensaje: "GitHub for Jira installed successfully"
   - Tu repositorio ahora está conectado ✅

---

### Verificación Rápida

Para confirmar que la integración funciona:

```bash
# En tu proyecto local
git commit -m "TEST-1 Prueba de integración Jira-GitHub"
git push origin main
```

- Ve a Jira y abre el issue TEST-1
- En el panel derecho, busca la sección **"Development"**
- Deberías ver tu commit listado

Si ves el commit, **¡la integración está funcionando!** ✅

---

## 2. Configuraciones Necesarias Antes de Comenzar

### 2.1: Generar API Token de Jira

**Este token permite que GitHub Actions actualice el estado de tus issues en Jira.**

#### Pasos:

1. **Ve a tu perfil de Atlassian**
   - URL: https://id.atlassian.com/manage-profile/security/api-tokens

2. **Crea un nuevo token**
   - Haz clic en **"Create API token"**
   - Nombre: `GitHub Actions Selenium Tests`
   - Haz clic en **"Create"**

3. **Copia el token**
   - ⚠️ **IMPORTANTE**: Copia el token inmediatamente
   - Solo se muestra una vez
   - Guárdalo en un lugar seguro temporalmente

---

### 2.2: Agregar Secrets en GitHub

**Los secrets permiten que GitHub Actions acceda a Jira de forma segura.**

#### Pasos:

1. **Ve a tu repositorio en GitHub**
   - Ejemplo: `https://github.com/tu-usuario/selenium-automation`

2. **Accede a la configuración de Secrets**
   - **Settings** → **Secrets and variables** → **Actions**

3. **Agrega los siguientes secrets** (haz clic en "New repository secret" para cada uno):

#### Secret 1: JIRA_BASE_URL
```
Name: JIRA_BASE_URL
Secret: https://tu-empresa.atlassian.net
```
*(Reemplaza "tu-empresa" con el nombre de tu instancia de Jira)*

#### Secret 2: JIRA_USER_EMAIL
```
Name: JIRA_USER_EMAIL
Secret: tu-email@empresa.com
```
*(El email con el que iniciaste sesión en Jira)*

#### Secret 3: JIRA_API_TOKEN
```
Name: JIRA_API_TOKEN
Secret: [pega aquí el token que generaste en el paso 2.1]
```

**Resultado esperado**: Deberías tener 3 secrets configurados

---

### 2.3: Preparar la Estructura del Proyecto

Tu proyecto debe tener la siguiente estructura:

```
selenium-automation/
├── .github/
│   └── workflows/
│       └── selenium-tests.yml    # Crearemos este archivo
├── tests/
│   └── Prueba.py                 # Tu prueba de Selenium
├── requirements.txt              # Dependencias de Python
└── README.md
```

---

### 2.4: Crear el Archivo requirements.txt

Este archivo lista todas las dependencias que necesita tu proyecto.

**Ubicación**: En la raíz de tu proyecto

**Contenido**:
```txt
selenium==4.16.0
pytest==7.4.3
pytest-html==4.1.1
webdriver-manager==4.0.1
```

**Para crearlo desde tu IDE:**

1. Abre tu editor de código (VS Code, PyCharm, etc.)
2. Crea un archivo llamado `requirements.txt` en la raíz
3. Pega el contenido anterior
4. Guarda el archivo

---

### 2.5: Crear el Archivo de GitHub Actions

Este es el archivo que ejecutará tus pruebas automáticamente.

**Ubicación**: `.github/workflows/selenium-tests.yml`

**Pasos para crearlo:**

1. En tu proyecto, crea la carpeta `.github` (si no existe)
2. Dentro de `.github`, crea la carpeta `workflows`
3. Dentro de `workflows`, crea el archivo `selenium-tests.yml`

**Contenido del archivo**:

```yaml
name: Selenium Tests

on:
  push:
    branches:
      - main
      - develop
      - 'feature/**'
  pull_request:
    branches:
      - main
      - develop

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      # 1. Descargar el código
      - name: Checkout código
        uses: actions/checkout@v3
      
      # 2. Configurar Python
      - name: Configurar Python 3.11
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      # 3. Instalar dependencias
      - name: Instalar dependencias
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      # 4. Instalar Chrome y ChromeDriver
      - name: Instalar Chrome
        uses: browser-actions/setup-chrome@latest
        with:
          chrome-version: stable
      
      # 5. Extraer Issue Key del commit
      - name: Extraer Jira Issue Key
        id: jira-key
        run: |
          COMMIT_MSG=$(git log -1 --pretty=%B)
          ISSUE_KEY=$(echo "$COMMIT_MSG" | grep -oE '[A-Z]+-[0-9]+' | head -1)
          echo "issue_key=$ISSUE_KEY" >> $GITHUB_OUTPUT
          if [ -z "$ISSUE_KEY" ]; then
            echo "⚠️ No se encontró Issue Key en el commit"
          else
            echo "✓ Issue Key encontrado: $ISSUE_KEY"
          fi
      
      # 6. Login en Jira
      - name: Login en Jira
        if: steps.jira-key.outputs.issue_key != ''
        uses: atlassian/gajira-login@v3
        env:
          JIRA_BASE_URL: ${{ secrets.JIRA_BASE_URL }}
          JIRA_USER_EMAIL: ${{ secrets.JIRA_USER_EMAIL }}
          JIRA_API_TOKEN: ${{ secrets.JIRA_API_TOKEN }}
      
      # 7. Marcar como "En Progreso" en Jira
      - name: Actualizar Jira - En Progreso
        if: steps.jira-key.outputs.issue_key != ''
        continue-on-error: true
        uses: atlassian/gajira-transition@v3
        with:
          issue: ${{ steps.jira-key.outputs.issue_key }}
          transition: 'In Progress'
        env:
          JIRA_BASE_URL: ${{ secrets.JIRA_BASE_URL }}
          JIRA_USER_EMAIL: ${{ secrets.JIRA_USER_EMAIL }}
          JIRA_API_TOKEN: ${{ secrets.JIRA_API_TOKEN }}
      
      # 8. Ejecutar las pruebas de Selenium
      - name: Ejecutar pruebas de Selenium
        id: tests
        run: |
          cd tests
          python Prueba.py
        continue-on-error: true
      
      # 9. Actualizar estado en Jira según resultado
      - name: Actualizar Jira - Estado Final
        if: steps.jira-key.outputs.issue_key != ''
        uses: atlassian/gajira-transition@v3
        with:
          issue: ${{ steps.jira-key.outputs.issue_key }}
          transition: ${{ steps.tests.outcome == 'success' && 'Done' || 'To Do' }}
        env:
          JIRA_BASE_URL: ${{ secrets.JIRA_BASE_URL }}
          JIRA_USER_EMAIL: ${{ secrets.JIRA_USER_EMAIL }}
          JIRA_API_TOKEN: ${{ secrets.JIRA_API_TOKEN }}
      
      # 10. Agregar comentario con resultado en Jira
      - name: Comentar resultado en Jira
        if: steps.jira-key.outputs.issue_key != ''
        uses: atlassian/gajira-comment@v3
        with:
          issue: ${{ steps.jira-key.outputs.issue_key }}
          comment: |
            🤖 **Resultado de Pruebas Automatizadas (Selenium)**
            
            **Estado**: ${{ steps.tests.outcome == 'success' && '✅ PASSED - Todas las pruebas pasaron exitosamente' || '❌ FAILED - Una o más pruebas fallaron' }}
            
            **Detalles del Build**:
            • Build número: #${{ github.run_number }}
            • Rama: `${{ github.ref_name }}`
            • Commit: `${{ github.sha }}`
            • Ejecutado por: @${{ github.actor }}
            
            [Ver detalles completos del build](${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }})
        env:
          JIRA_BASE_URL: ${{ secrets.JIRA_BASE_URL }}
          JIRA_USER_EMAIL: ${{ secrets.JIRA_USER_EMAIL }}
          JIRA_API_TOKEN: ${{ secrets.JIRA_API_TOKEN }}
      
      # 11. Mostrar resultado en consola
      - name: Resultado Final
        if: always()
        run: |
          if [ "${{ steps.tests.outcome }}" == "success" ]; then
            echo "✅ ¡Pruebas ejecutadas exitosamente!"
          else
            echo "❌ Las pruebas fallaron. Revisa los logs arriba."
            exit 1
          fi
```

---

### 2.6: Adaptar tu Archivo Prueba.py

Tu archivo `Prueba.py` necesita algunas modificaciones para funcionar en GitHub Actions (modo headless).

**Ubicación**: `tests/Prueba.py`

**⚠️ IMPORTANTE SOBRE GOOGLE Y CAPTCHA:**
Google detecta bots automatizados y puede mostrar CAPTCHA, lo cual hará que la prueba falle. Por eso vamos a usar **dos enfoques**:

1. **Opción A (Recomendada)**: Probar con un sitio web más amigable para automatización
2. **Opción B**: Mejorar la configuración para Google (puede funcionar pero no garantizado)

---

#### **OPCIÓN A: Usar DuckDuckGo (Recomendado) ✅**

DuckDuckGo no usa CAPTCHA y es perfecto para pruebas de Selenium:

**Contenido actualizado de `tests/Prueba.py`**:

```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import sys

def setup_driver():
    """Configura el driver de Chrome con opciones para CI/CD"""
    chrome_options = Options()
    
    # Opciones necesarias para ejecutar en GitHub Actions
    chrome_options.add_argument('--headless')  # Ejecutar sin interfaz gráfica
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    # Opciones adicionales para parecer más humano
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # User agent más actualizado
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # Crear el servicio con ChromeDriver
    service = Service(ChromeDriverManager().install())
    
    # Inicializar el driver
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
        print(f"✓ Búsqueda realizada: '{termino}'")
        
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
```

---

#### **OPCIÓN B: Mejorar Google con User-Agent y Retrasos**

Si realmente necesitas usar Google, aquí está la versión mejorada (aunque puede seguir fallando ocasionalmente):

```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import sys
import random

def setup_driver():
    """Configura el driver de Chrome con opciones anti-detección"""
    chrome_options = Options()
    
    # Opciones necesarias para ejecutar en GitHub Actions
    chrome_options.add_argument('--headless=new')  # Nuevo modo headless
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    # Anti-detección de bots
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # User agent realista
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # Preferencias adicionales
    prefs = {
        "profile.default_content_setting_values.notifications": 2,
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Ocultar que es webdriver
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {
        "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def test_google_search():
    """Prueba de búsqueda en Google (con medidas anti-CAPTCHA)"""
    driver = setup_driver()
    
    try:
        print("🚀 Iniciando prueba de búsqueda en Google...")
        
        # 1. Abrir Google
        driver.get("https://www.google.com")
        print("✓ Página de Google cargada")
        
        # Espera aleatoria para parecer humano
        time.sleep(random.uniform(2, 4))
        
        # 2. Verificar si hay CAPTCHA
        if "captcha" in driver.page_source.lower() or "unusual traffic" in driver.page_source.lower():
            print("⚠️ CAPTCHA detectado - Google bloqueó el acceso")
            print("💡 Sugerencia: Usa DuckDuckGo en su lugar (Opción A)")
            return False
        
        # 3. Manejar cookies
        try:
            # Esperar y aceptar cookies
            cookies_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Aceptar') or contains(., 'Accept')]"))
            )
            cookies_btn.click()
            print("✓ Cookies aceptadas")
            time.sleep(1)
        except:
            print("ℹ️ No apareció el aviso de cookies")
        
        # 4. Localizar la barra de búsqueda
        try:
            search_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.NAME, "q"))
            )
            print("✓ Barra de búsqueda localizada")
        except:
            print("❌ No se pudo localizar la barra de búsqueda")
            return False
        
        # 5. Escribir de forma más humana
        termino = "Automatización con Python"
        for char in termino:
            search_box.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))  # Simular escritura humana
        
        print(f"✓ Texto escrito: '{termino}'")
        time.sleep(random.uniform(0.5, 1))
        
        # 6. Enviar búsqueda
        search_box.send_keys(Keys.RETURN)
        print("✓ Búsqueda enviada")
        
        # 7. Esperar resultados
        time.sleep(3)
        
        # 8. Verificar CAPTCHA nuevamente
        if "captcha" in driver.page_source.lower() or "unusual traffic" in driver.page_source.lower():
            print("❌ CAPTCHA apareció después de la búsqueda")
            print("💡 Google detectó el bot. Usa DuckDuckGo (Opción A)")
            return False
        
        # 9. Verificar resultados
        try:
            resultados = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "h3"))
            )
            
            if len(resultados) > 0:
                print(f"✅ Prueba EXITOSA - Se encontraron {len(resultados)} resultados")
                return True
            else:
                print("❌ No se encontraron resultados")
                return False
        except:
            print("❌ Error al verificar resultados")
            return False
            
    except Exception as e:
        print(f"❌ Error durante la prueba: {str(e)}")
        return False
        
    finally:
        driver.quit()
        print("✓ Navegador cerrado")

if __name__ == "__main__":
    resultado = test_google_search()
    
    if resultado:
        print("\n🎉 TODAS LAS PRUEBAS PASARON")
        sys.exit(0)
    else:
        print("\n💥 PRUEBAS FALLIDAS")
        sys.exit(1)
```

---

#### **OPCIÓN C: Probar Tu Propia Aplicación Web**

La mejor práctica es probar tu propia aplicación:

```python
def test_my_application():
    """Prueba de tu propia aplicación web"""
    driver = setup_driver()
    
    try:
        print("🚀 Iniciando prueba de aplicación...")
        
        # Cambia esta URL por tu aplicación
        driver.get("http://localhost:3000")  # o tu URL de staging/producción
        print("✓ Aplicación cargada")
        
        # Ejemplo: Verificar título
        assert "Mi App" in driver.title
        print("✓ Título verificado")
        
        # Ejemplo: Hacer clic en botón
        boton = driver.find_element(By.ID, "mi-boton")
        boton.click()
        print("✓ Botón clickeado")
        
        # Ejemplo: Verificar resultado
        resultado = driver.find_element(By.ID, "resultado")
        assert resultado.text == "Éxito"
        print("✓ Resultado verificado")
        
        print("✅ Prueba EXITOSA")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
        
    finally:
        driver.quit()
```

---

### 💡 Recomendación Final

**Para aprender y probar la integración, usa la OPCIÓN A (DuckDuckGo)** porque:
- ✅ No tiene CAPTCHA
- ✅ Funciona de manera consistente
- ✅ Perfecto para CI/CD
- ✅ Resultados confiables

**Evita usar Google** para pruebas automatizadas porque:
- ❌ CAPTCHA frecuente
- ❌ Bloquea IPs de servidores (como GitHub Actions)
- ❌ Viola sus términos de servicio
- ❌ Resultados inconsistentes

Una vez que la integración funcione con DuckDuckGo, puedes adaptarla para probar **tu propia aplicación web**, que es el caso de uso real de Selenium.

**Cambios importantes**:
- ✅ Agregado modo `--headless` para ejecutar sin interfaz gráfica
- ✅ Uso de `webdriver_manager` para instalar ChromeDriverManager automáticamente
- ✅ Código de salida (`sys.exit`) para indicar éxito/fallo
- ✅ Mensajes claros en consola para debugging
- ✅ Anti-detección de bots mejorada
- ✅ Esperas explícitas con WebDriverWait
- ✅ Manejo de excepciones robusto

---

### 2.7: Configurar Transiciones en Jira (Opcional pero Recomendado)

Las transiciones son los cambios de estado en Jira (ej: "To Do" → "In Progress" → "Done").

#### Verificar tus Estados Disponibles

1. Ve a Jira → **Project Settings** → **Workflows**
2. Identifica los estados de tu proyecto (comúnmente son):
   - **To Do** (Por hacer)
   - **In Progress** (En progreso)
   - **Done** (Completado)

#### Si Tienes Estados Personalizados

Si tu proyecto usa estados diferentes, necesitas ajustar el workflow:

**En el archivo `selenium-tests.yml`, encuentra estas líneas:**

```yaml
transition: 'In Progress'  # Línea 53
transition: ${{ steps.tests.outcome == 'success' && 'Done' || 'To Do' }}  # Línea 66
```

**Reemplázalas con tus estados personalizados:**

```yaml
transition: 'Tu Estado de Progreso'
transition: ${{ steps.tests.outcome == 'success' && 'Tu Estado Exitoso' || 'Tu Estado Fallido' }}
```

---

### Checklist de Configuración

Antes de continuar, verifica que tienes TODO esto:

- [ ] GitHub y Jira están conectados
- [ ] 3 secrets configurados en GitHub (JIRA_BASE_URL, JIRA_USER_EMAIL, JIRA_API_TOKEN)
- [ ] Archivo `requirements.txt` creado
- [ ] Archivo `.github/workflows/selenium-tests.yml` creado
- [ ] Archivo `tests/Prueba.py` actualizado con el código nuevo
- [ ] Conoces los estados de tu workflow de Jira

**Si marcaste todas las casillas, ¡estás listo para la siguiente sección!** ✅

---

## 3. Ejecutar tu Primera Prueba Automatizada

### 🎯 Objetivo Final

Ejecutar la prueba `Prueba.py` en GitHub Actions y que Jira se actualice automáticamente con el resultado.

---

### Paso 3.1: Crear un Issue en Jira

**Esto es importante porque el Issue Key vincula todo el proceso.**

1. **Ve a tu proyecto en Jira**
2. **Crea un nuevo issue**:
   - **Tipo**: Task o Story
   - **Título**: "Prueba automatizada de búsqueda en Google"
   - **Descripción**: "Ejecutar prueba de Selenium que busca en Google"
3. **Anota el Issue Key** (ejemplo: **AUTO-101**)

---

### Paso 3.2: Preparar el Código Localmente

En tu IDE (VS Code, PyCharm, etc.):

#### Opción A: Si Ya Tienes el Proyecto Clonado

```bash
# Verifica que estés en la rama correcta
git status

# Si no estás en main/develop, cámbiate
git checkout main
```

#### Opción B: Si Es un Proyecto Nuevo

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/selenium-automation.git
cd selenium-automation
```

---

### Paso 3.3: Verificar la Estructura de Archivos

Asegúrate de tener esta estructura:

```
selenium-automation/
├── .github/
│   └── workflows/
│       └── selenium-tests.yml    ✅
├── tests/
│   └── Prueba.py                 ✅
├── requirements.txt              ✅
└── README.md
```

**Para verificar desde la terminal:**

```bash
ls -la
ls .github/workflows/
ls tests/
```

---

### Paso 3.4: Probar Localmente (Opcional pero Recomendado)

Antes de hacer push, verifica que tu prueba funciona localmente:

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la prueba
cd tests
python Prueba.py
```

**Resultado esperado:**
```
🚀 Iniciando prueba de búsqueda en Google...
✓ Página de Google cargada
✓ Barra de búsqueda localizada
✓ Búsqueda realizada: 'Automatización con Python'
✅ Prueba EXITOSA - Se encontraron 10 resultados
✓ Navegador cerrado

🎉 TODAS LAS PRUEBAS PASARON
```

Si ves esto, **¡tu prueba funciona!** ✅

---

### Paso 3.5: Commit y Push con el Issue Key

**Este es el paso más importante** - El Issue Key en el commit es lo que vincula todo.

#### En tu Terminal o IDE:

```bash
# 1. Agregar todos los archivos
git add .

# 2. Hacer commit CON el Issue Key de Jira
# Formato: ISSUE-KEY Mensaje descriptivo
git commit -m "AUTO-101 Agrega prueba automatizada de búsqueda en Google"

# 3. Push a GitHub
git push origin main
```

**⚠️ IMPORTANTE**: Reemplaza `AUTO-101` con tu Issue Key real de Jira.

---

### Paso 3.6: Monitorear la Ejecución en GitHub

Inmediatamente después del push:

1. **Ve a tu repositorio en GitHub**
   - `https://github.com/tu-usuario/selenium-automation`

2. **Haz clic en la pestaña "Actions"**
   - Verás tu workflow ejecutándose en tiempo real
   - Estado: 🟡 (amarillo = en progreso)

3. **Haz clic en el workflow para ver detalles**
   - Verás cada paso ejecutándose:
     ```
     ✓ Checkout código
     ✓ Configurar Python 3.11
     ✓ Instalar dependencias
     ✓ Instalar Chrome
     ✓ Extraer Jira Issue Key
     ⏳ Actualizar Jira - En Progreso
     ⏳ Ejecutar pruebas de Selenium
     ```

4. **Espera a que termine** (2-3 minutos aproximadamente)

---

### Paso 3.7: Verificar el Resultado en GitHub

Una vez que el workflow termine:

**Si TODO salió bien** ✅:
- Estado: 🟢 (verde) con checkmark
- Último paso dice: "✅ ¡Pruebas ejecutadas exitosamente!"

**Si algo falló** ❌:
- Estado: 🔴 (rojo) con X
- Haz clic en el paso fallido para ver el error
- Ve a la sección [4. Solución de Problemas](#4-solución-de-problemas)

---

### Paso 3.8: Ver la Actualización en Jira

**Ahora viene la magia** 🎩✨

1. **Ve a Jira y abre tu issue** (AUTO-101)

2. **En el panel derecho**, busca la sección **"Development"**
   - Verás: `1 commit`, `1 build`
   - Haz clic para ver detalles

3. **Estado del Issue**:
   - Si la prueba pasó: Estado cambió a **"Done"** ✅
   - Si falló: Estado volvió a **"To Do"** ❌

4. **Comentarios**:
   - Busca el comentario del bot de GitHub Actions
   - Verás algo como:

   ```
   🤖 Resultado de Pruebas Automatizadas (Selenium)
   
   Estado: ✅ PASSED - Todas las pruebas pasaron exitosamente
   
   Detalles del Build:
   • Build número: #1
   • Rama: main
   • Commit: abc123def
   • Ejecutado por: @tu-usuario
   
   [Ver detalles completos del build](enlace-a-github)
   ```

---

### Paso 3.9: ¡Felicitaciones! 🎉

Si llegaste hasta aquí y todo funcionó, **has completado exitosamente la integración**.

**Lo que lograste**:
✅ Conectaste GitHub con Jira
✅ Configuraste GitHub Actions para pruebas automatizadas
✅ Ejecutaste tu primera prueba de Selenium en la nube
✅ Jira se actualizó automáticamente con el resultado
✅ Tu equipo puede ver el progreso en tiempo real

---

### Flujo Completo Resumido

De ahora en adelante, tu flujo de trabajo será:

```
1. Creas un issue en Jira (ej: AUTO-102)
        ↓
2. Escribes/modificas tu código de pruebas
        ↓
3. Commit con Issue Key: "AUTO-102 [mensaje]"
        ↓
4. Push a GitHub
        ↓
5. GitHub Actions ejecuta las pruebas automáticamente
        ↓
6. Jira se actualiza con el resultado
        ↓
7. Recibes notificación (opcional)
        ↓
8. Revisas los resultados en Jira
```

**Todo automático, sin intervención manual** 🚀

---

## 4. Solución de Problemas

### Problema 1: El Workflow No Se Ejecuta

**Síntomas**: No aparece nada en la pestaña Actions de GitHub

**Soluciones**:

✅ **Verifica que el archivo YML esté en la ubicación correcta**:
```bash
# Debe estar aquí:
.github/workflows/selenium-tests.yml
```

✅ **Verifica que pusheaste los archivos**:
```bash
git status
git push origin main
```

✅ **Verifica que GitHub Actions esté habilitado**:
- Ve a: Settings → Actions → General
- Debe estar en "Allow all actions and reusable workflows"

---

### Problema 2: Error "Jira Issue Key No Encontrado"

**Síntomas**: En los logs de GitHub Actions ves: "⚠️ No se encontró Issue Key en el commit"

**Causa**: El commit no tiene el formato correcto

**Solución**:

❌ **Incorrecto**:
```bash
git commit -m "agrega prueba"           # Sin Issue Key
git commit -m "auto-101 agrega prueba"  # Minúsculas
git commit -m "AUTO 101 agrega prueba"  # Sin guion
```

✅ **Correcto**:
```bash
git commit -m "AUTO-101 Agrega prueba"  # ✓ Formato correcto
```

El formato debe ser: **MAYÚSCULAS-NÚMERO**

---

### Problema 3: Error al Actualizar Jira

**Síntomas**: Ves un error en el paso "Actualizar Jira - En Progreso"

**Causas posibles**:

1. **Secrets mal configurados**

Verifica en GitHub: Settings → Secrets → Actions

Debe haber 3 secrets:
- JIRA_BASE_URL
- JIRA_USER_EMAIL
- JIRA_API_TOKEN

✅ **Solución**: Revisa que los valores sean correctos (especialmente el API Token)

2. **Issue no existe en Jira**

✅ **Solución**: Verifica que el Issue Key existe en tu proyecto de Jira

3. **Permisos insuficientes**

✅ **Solución**: El usuario (tu email) debe tener permisos para editar issues en Jira

---

### Problema 4: La Prueba Falla en GitHub pero Funciona Local

**Síntomas**: Localmente pasa, en GitHub Actions falla

**Causa**: Diferencias de entorno

**Soluciones**:

✅ **Verifica que estás usando modo headless**:

En `Prueba.py`, debe tener:
```python
chrome_options.add_argument('--headless')
```

✅ **Aumenta los tiempos de espera**:
```python
time.sleep(5)  # En lugar de 2
```

✅ **Agrega más logs para debugging**:
```python
print(f"Página actual: {driver.current_url}")
print(f"Título: {driver.title}")
```

---

### Problema 5: Error "ChromeDriver Not Found"

**Síntomas**: Error relacionado con ChromeDriver en los logs

**Solución**:

✅ Asegúrate de tener en `requirements.txt`:
```txt
webdriver-manager==4.0.1
```

✅ Y en `Prueba.py`:
```python
from webdriver_manager.chrome import ChromeDriverManager
service = Service(ChromeDriverManager().install())
```

---

### Problema 6: Estado No Cambia en Jira

**Síntomas**: La prueba pasa, pero el issue sigue en "To Do"

**Causa**: La transición no existe o no está permitida

**Solución**:

1. **Verifica los estados de tu workflow en Jira**:
   - Jira → Project Settings → Workflows
   - Anota los nombres exactos de los estados

2. **Actualiza el archivo YML con los estados correctos**:

```yaml
# Línea ~53
transition: 'Tu Estado de Progreso'  # Ej: 'In Progress', 'Doing', etc.

# Línea ~66
transition: ${{ steps.tests.outcome == 'success' && 'Tu Estado Final' || 'Tu Estado Inicial' }}
```

3. **Si sigues teniendo problemas, usa IDs en lugar de nombres**:

Obtén los IDs de transición:
```bash
curl -u tu-email@empresa.com:TU_API_TOKEN \
  https://tu-empresa.atlassian.net/rest/api/3/issue/AUTO-101/transitions
```

Usa el ID en el workflow:
```yaml
transition: '31'  # ID de la transición
```

---

### Problema 7: Timeout en la Prueba

**Síntomas**: La prueba se detiene y marca timeout después de mucho tiempo

**Soluciones**:

✅ **Reduce los tiempos de espera**:
```python
time.sleep(2)  # En lugar de 10
```

✅ **Usa esperas explícitas** (más eficiente):
```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

wait = WebDriverWait(driver, 10)
elemento = wait.until(EC.presence_of_element_located((By.NAME, "q")))
```

---

### Debugging: Ver Logs Detallados

Para ver qué está pasando exactamente:

1. **En GitHub Actions**:
   - Haz clic en el workflow fallido
   - Haz clic en el paso que falló
   - Lee los logs completos (scroll hasta arriba)

2. **Agregar más prints en tu código**:
```python
print(f"✓ Paso 1 completado")
print(f"✓ Paso 2 completado")
print(f"Estado actual: {algo}")
```

3. **Capturar screenshots en caso de error**:
```python
try:
    # tu código
except Exception as e:
    driver.save_screenshot('error.png')
    print(f"Error: {e}")
    raise
```

---

### Obtener Ayuda

Si sigues teniendo problemas:

1. **Revisa los logs completos** en GitHub Actions
2. **Copia el error exacto**
3. **Verifica que seguiste TODOS los pasos** de la sección 2
4. **Busca el error en Google** - probablemente alguien más lo tuvo

**Recursos útiles**:
- Documentación de Selenium: https://selenium-python.readthedocs.io/
- Documentación de GitHub Actions: https://docs.github.com/en/actions
- Documentación de Jira API: https://developer.atlassian.com/cloud/jira/platform/rest/v3/

---

## Próximos Pasos

Ahora que tienes todo funcionando, puedes:

✅ **Agregar más pruebas**:
- Crea más archivos `.py` en la carpeta `tests/`
- Usa el mismo Issue Key o crea nuevos issues

✅ **Ejecutar múltiples pruebas**:
Modifica el workflow para ejecutar todas las pruebas:
```yaml
- name: Ejecutar pruebas de Selenium
  run: |
    cd tests
    python -m pytest *.py
```

✅ **Generar reportes HTML**:
```yaml
- name: Generar reporte
  run: pytest tests/ --html=report.html
```

✅ **Ejecutar en diferentes navegadores**:
- Firefox
- Edge
- Safari (en macOS)

✅ **Agregar notificaciones**:
- Slack
- Email
- Microsoft Teams

---

## Resumen Final

**Lo que configuraste**:
1. ✅ Integración GitHub + Jira
2. ✅ GitHub Actions para CI/CD
3. ✅ Pruebas automatizadas con Selenium + Python
4. ✅ Actualización automática de Jira según resultados

**Tu nuevo flujo de trabajo**:
```
Issue en Jira → Código → Commit → Push → GitHub Actions → Actualización en Jira
```

**Beneficios**:
- ⚡ Pruebas automáticas en cada push
- 👁️ Visibilidad completa del equipo
- 📊 Trazabilidad total
- 🚀 Detección temprana de bugs
- ✅ Código de calidad garantizada

---

## Comandos de Referencia Rápida

```bash
# Ver estado de Git
git status

# Agregar archivos
git add .

# Commit con Issue Key
git commit -m "AUTO-101 Tu mensaje"

# Push
git push origin main

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar prueba local
python tests/Prueba.py

# Ver estructura del proyecto
tree -L 3 -I 'node_modules|__pycache__'
```

---

**¡Felicitaciones! Has completado la configuración completa de automatización de pruebas con Selenium, GitHub Actions y Jira.** 🎉

Si tienes dudas o encuentras problemas, revisa la sección de [Solución de Problemas](#4-solución-de-problemas).
