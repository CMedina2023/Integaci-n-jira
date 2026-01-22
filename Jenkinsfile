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
                echo '✅ Pruebas exitosas. Analizando mensaje para múltiples tickets...'

                // 1. Obtenemos el mensaje
                def commitMsg = bat(returnStdout: true, script: '@git log -1 --pretty=%%B').trim()

                // 2. BUSCAR TODOS LOS TICKETS (findAll devuelve una lista)
                // .unique() sirve para que si escribes IN-11 dos veces, solo lo mande una vez.
                def issues = commitMsg.findAll(/[A-Z]+-[0-9]+/).unique()

                if (issues) {
                    echo "🎫 Tickets encontrados: ${issues}"

                    // 3. RECORREMOS LA LISTA (Bucle)
                    issues.each { issueKey ->
                        echo "🚀 Enviando reporte para: ${issueKey}"

                        // Generamos un JSON específico para ESTE ticket del bucle
                        def payloadContent = """
                        {
                          "event_type": "jenkins-test-finished",
                          "client_payload": {
                            "jira_issue": "${issueKey}",
                            "jenkins_status": "success",
                            "jenkins_build": "${env.BUILD_NUMBER}",
                            "jenkins_url": "${env.BUILD_URL}"
                          }
                        }
                        """

                        // Guardamos el archivo (se sobrescribe en cada vuelta, no pasa nada)
                        writeFile file: 'payload.json', text: payloadContent

                        // Enviamos la señal a GitHub para ESTE ticket
                        bat '''
                            curl --ssl-no-revoke -X POST -H "Accept: application/vnd.github+json" -H "Authorization: token %GITHUB_TOKEN%" https://api.github.com/repos/CMedina2023/Integaci-n-jira/dispatches -d @payload.json
                        '''

                        // Pequeña pausa de seguridad para no saturar si son muchos
                        sleep 1
                    }

                } else {
                    echo "⚠️ No se encontraron IDs de Jira en el commit."
                }
            }
        }
        failure {
            echo '❌ Las pruebas fallaron. No se dispara la acción en GitHub.'
        }
    }
}
