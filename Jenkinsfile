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
                
                def commitMsg = bat(returnStdout: true, script: '@git log -1 --pretty=%%B').trim()

                // 1. Buscamos el ID
                def matcher = (commitMsg =~ /[A-Z]+-[0-9]+/)
                def JIRA_ISSUE = null

                if (matcher) {
                    // Extraemos el texto (String) que SÍ se puede guardar
                    JIRA_ISSUE = matcher[0]
                }

                // 🔥 EL TRUCO MÁGICO 🔥
                // Establecemos el matcher a null explícitamente.
                // Esto elimina el objeto "tóxico" antes de que Jenkins intente guardar el estado.
                matcher = null

                // Ahora validamos si tenemos el ID (Ya sin el matcher estorbando)
                if (JIRA_ISSUE) {
                    echo "🎫 Ticket detectado: ${JIRA_ISSUE}"

                    def payloadContent = """
                    {
                      "event_type": "jenkins-test-finished",
                      "client_payload": {
                        "jira_issue": "${JIRA_ISSUE}",
                        "jenkins_status": "success",
                        "jenkins_build": "${env.BUILD_NUMBER}",
                        "jenkins_url": "${env.BUILD_URL}"
                      }
                    }
                    """
                    writeFile file: 'payload.json', text: payloadContent

                    // Al ejecutar este bat, el 'matcher' ya no existe, así que Jenkins no fallará al guardar estado
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
