pipeline {
    agent any

    stages {
        stage('Instalar Dependencias') {
            steps {
                // El requirements.txt parece estar en la raíz según tu imagen,
                // así que lo ejecutamos normal.
                bat 'pip install -r requirements.txt'
            }
        }
        
        stage('Ejecutar Test') {
            steps {
                // El comando 'dir' es la forma segura de Jenkins para "entrar" a una carpeta
                dir('tests') {
                    // Ahora que estamos dentro de 'tests', corremos el script
                    bat 'python prueba.py'
                }
            }
        }
    }
}
