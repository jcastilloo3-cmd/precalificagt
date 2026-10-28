// =============================================================================
// PrecalificaGT — Pipeline de integración y despliegue continuo (E13)
// Tipo de trabajo: Multibranch Pipeline (GitHub Branch Source) en Jenkins local.
// Ramas: DEV (integración), QA (pruebas) y main (producción). Los PR también se
// construyen y su resultado bloquea el merge mediante la protección de ramas de GitHub.
//
// Orden exigido: compilación → pruebas unitarias → análisis estático + quality gate
//                → pruebas de API → despliegue al ambiente correspondiente.
//
// Variables globales opcionales (Manage Jenkins → System → Global properties):
//   PYTHON_EXE  ruta a python.exe (3.12+)      p. ej. C:\Python314\python.exe
//   PHP_EXE     ruta a php.exe (8.1+)          p. ej. C:\wamp64\bin\php\php8.1.31\php.exe
// =============================================================================

def ejecutar(String comando) {
    if (isUnix()) {
        sh comando
    } else {
        bat comando
    }
}

def pythonVenv() {
    return isUnix() ? '.venv/bin/python' : '.venv\\Scripts\\python.exe'
}

def ambienteDeRama(String rama) {
    switch (rama) {
        case 'main': return 'PROD'
        case 'QA':   return 'QA'
        case 'DEV':  return 'DEV'
        default:     return 'PR'
    }
}

pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '20'))
        timeout(time: 45, unit: 'MINUTES')
    }

    environment {
        // URL pública de la API en cada ambiente cloud (Render)
        QA_API_URL   = 'https://precalificagt-api-qa.onrender.com'
        PROD_API_URL = 'https://precalificagt-api.onrender.com'
    }

    stages {
        stage('1. Compilación') {
            steps {
                script {
                    // DEV y los PR usan el ambiente de integración efímero de la etapa 4;
                    // QA y main además se despliegan en Render (etapa 5)
                    env.AMBIENTE = ambienteDeRama(env.BRANCH_NAME)
                    env.PY_BASE = env.PYTHON_EXE ? "\"${env.PYTHON_EXE}\"" : (isUnix() ? 'python3' : 'py -3')
                    env.PHP_BIN = env.PHP_EXE ?: 'php'
                    echo "Rama ${env.BRANCH_NAME} → ambiente ${env.AMBIENTE}"
                    ejecutar "${env.PY_BASE} -m venv .venv"
                    ejecutar "${pythonVenv()} -m pip install --disable-pip-version-check -q -r backend/requirements-dev.txt"
                    ejecutar "${pythonVenv()} -m compileall -q backend/app"
                    ejecutar "${pythonVenv()} ci/lint_php.py \"${env.PHP_BIN}\""
                }
            }
        }

        stage('2. Pruebas unitarias') {
            steps {
                script {
                    // Backend: pytest + cobertura (incluye las pruebas de integración de componentes)
                    ejecutar "${pythonVenv()} -m pytest --cov --cov-report=xml:reports/coverage.xml --cov-report=term --junitxml=reports/pytest.xml"
                    // Meta de E10: +20 pp sobre la línea base (0 %) en los módulos críticos
                    ejecutar "${pythonVenv()} ci/cobertura_criticos.py reports/coverage.xml"
                    // Frontend: PHPUnit
                    ejecutar "${pythonVenv()} ci/obtener_phpunit.py"
                    ejecutar "\"${env.PHP_BIN}\" tools/phpunit.phar -c frontend/phpunit.xml --log-junit reports/phpunit.xml"
                }
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'reports/pytest.xml, reports/phpunit.xml'
                    archiveArtifacts allowEmptyArchive: true, artifacts: 'reports/coverage.xml, reports/cobertura_criticos.md'
                }
            }
        }

        stage('3. Análisis estático y quality gate') {
            steps {
                script {
                    def scanner = tool 'SonarScanner2026A'
                    def comando = isUnix() ? "${scanner}/bin/sonar-scanner" : "\"${scanner}\\bin\\sonar-scanner.bat\""
                    // El plan gratuito de SonarCloud solo expone la rama principal de cada proyecto
                    // ("Organization is not allowed to access data from non main branches"). Por eso
                    // main se analiza en el proyecto principal (estado de producción, antes/después de
                    // E12) y los PR, DEV y QA en un proyecto de integración con su propio quality gate.
                    // autoconfig.disabled: evita que el scanner detecte la rama de Jenkins y la
                    // envíe como rama secundaria
                    def parametros = '-Dsonar.branch.autoconfig.disabled=true '
                    if (env.BRANCH_NAME != 'main') {
                        parametros += "-Dsonar.projectKey=jcastilloo3-cmd_precalificagt-ci " +
                                     "-Dsonar.projectName=PrecalificaGT-CI " +
                                     "-Dsonar.projectVersion=${env.BRANCH_NAME}-${env.BUILD_NUMBER}"
                    }
                    withSonarQubeEnv('SonarQube2026A') {
                        // sonar.qualitygate.wait: el scanner espera el resultado y falla si el gate no pasa
                        ejecutar "${comando} -Dsonar.qualitygate.wait=true -Dsonar.qualitygate.timeout=300 ${parametros}"
                    }
                }
            }
        }

        stage('4. Pruebas de API (Newman)') {
            steps {
                script {
                    ejecutar "${pythonVenv()} ci/run_api_tests.py"
                }
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'reports/newman.xml'
                }
            }
        }

        stage('5. Despliegue') {
            when {
                anyOf { branch 'QA'; branch 'main' }
            }
            steps {
                script {
                    def esProd = env.BRANCH_NAME == 'main'
                    def credencial = esProd ? 'render-deploy-hooks-prod' : 'render-deploy-hooks-qa'
                    def apiUrl = esProd ? env.PROD_API_URL : env.QA_API_URL
                    withCredentials([string(credentialsId: credencial, variable: 'RENDER_DEPLOY_HOOKS')]) {
                        ejecutar "${pythonVenv()} ci/desplegar_render.py --ambiente ${env.AMBIENTE} --api-url ${apiUrl} --commit ${env.GIT_COMMIT}"
                    }
                    if (!esProd) {
                        // Prueba de humo sobre QA desplegado: la misma colección contra la nube
                        ejecutar "${pythonVenv()} ci/run_api_tests.py --base-url ${apiUrl}"
                    }
                }
            }
        }
    }

    post {
        success {
            script { notificar('good', "✅ ${env.JOB_NAME} #${env.BUILD_NUMBER} (${env.AMBIENTE}) exitoso") }
        }
        failure {
            script { notificar('danger', "❌ ${env.JOB_NAME} #${env.BUILD_NUMBER} (${env.AMBIENTE}) falló — ${env.BUILD_URL}") }
        }
    }
}

// Notificación a Slack (configurada en el laboratorio de Jenkins); si falla, no rompe el build
def notificar(String color, String mensaje) {
    try {
        slackSend(color: color, message: mensaje)
    } catch (err) {
        echo "Aviso: no se pudo notificar a Slack (${err.message})"
    }
}
