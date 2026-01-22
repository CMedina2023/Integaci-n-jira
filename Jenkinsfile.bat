pipeline {
    agent any 

    stages {
        stage('Instalar Dependencias') {
            steps {
                // Instala selenium en el entorno local
                bat 'pip install -r requirements.txt'
            }
        }
        
        stage('Ejecutar Test') {
            steps {
                // Ejecuta el script
                bat 'python test_google.py'
            }
        }
    }
}
