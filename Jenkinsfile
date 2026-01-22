pipeline {
    agent any

    stages {
        stage('Instalar Dependencias') {
            steps {
                // Instala las librerías necesarias (selenium)
                // Asume que requirements.txt está en la carpeta principal
                bat 'pip install -r requirements.txt'
            }
        }
        
        stage('Ejecutar Test') {
            steps {
                // Le decimos a Jenkins que entre a la carpeta 'tests'
                dir('tests') {
                    // 1. set PYTHONIOENCODING=utf-8: Arregla el error de los emojis
                    // 2. python prueba.py: Ejecuta tu script original sin cambios
                    bat 'set PYTHONIOENCODING=utf-8 && python prueba.py'
                }
            }
        }
    }
}
