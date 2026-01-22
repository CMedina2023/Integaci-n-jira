pipeline {
    agent any
    environment {
        GITHUB_TOKEN = credentials('GITHUB_PAT') 
    }

    stages {
        stage('Instalar Dependencias') {
            steps {
                bat 'pip install -r requirements.txt'
            }
        }
        
        stage('Ejecutar Test') {
            steps {
                dir('tests') {
                    bat 'set PYTHONIOENCODING=utf-8 && python prueba.py'
                }
            }
        }
    }

    post {
        success {
            script {
                echo '✅ Pruebas exitosas. Iniciando conexión con GitHub...'
                
                // 1. OBTENER MENSAJE DEL COMMIT (Versión Windows)
                // Usamos @ para que no imprima el comando, solo el resultado
                def commitMsg = bat(returnStdout: true, script: '@git log -1 --pretty=%B').trim()
                echo "Mensaje analizado: ${commitMsg}"
                
                // 2. BUSCAR TICKET (Ej: IN-4)
                def matcher = (commitMsg =~ /[A-Z]+-[0-9]+/)
                
                if (matcher) {
                    def JIRA_ISSUE = matcher[0]
                    echo "🎫 Ticket detectado: ${JIRA_ISSUE}"
                    
                    // 3. CREAR EL JSON (Versión segura para Windows)
                    // Escribimos el contenido en un archivo para evitar errores de comillas en la consola CMD
                    def payloadContent = """
                    {
                      "event_type": "jenkins-test-finished",
                      "client_payload": {
                        "jira_issue": "${JIRA_ISSUE}",
                        "jenkins_status": "EXITOSO",
                        "jenkins_build": "${env.BUILD_NUMBER}",
                        "jenkins_url": "${env.BUILD_URL}"
                      }
                    }
                    """
                    writeFile file: 'payload.json', text: payloadContent
                    
                    // 4. ENVIAR A GITHUB
                    // Usamos '@payload.json' para decirle a curl que lea del archivo
                    // %GITHUB_TOKEN% usa la variable de entorno de forma segura en Windows
                    bat '''
                        curl -X POST -H "Accept: application/vnd.github+json" -H "Authorization: token %GITHUB_TOKEN%" https://api.github.com/repos/CMedina2023/Integaci-n-jira/dispatches -d @payload.json
                    '''
                    
                } else {
                    echo "⚠️ No se encontró ID de Jira en el commit. No se envía nada."
                }
            }
        }
        failure {
            echo '❌ Las pruebas fallaron. No se dispara la acción en GitHub.'
        }
    }
}
