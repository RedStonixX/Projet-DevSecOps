pipeline {
    agent any

    environment {
        ZAP_PATH = "/opt/zaproxy/zap.sh"
        REPORT_DIR = "zap-reports"
        TARGET_URL = "http://localhost:5000"
    }

    stages {

        stage('Setup Environment') {
            steps {
                sh '''
                rm -rf .venv
                python3 -m venv .venv
                . .venv/bin/activate
                pip install -r requirements.txt
                '''
            }
        }

        stage('Run Flask App') {
            steps {
                sh '''
                . .venv/bin/activate
                python run.py & echo $! > flask.pid && sleep 10 && curl -I $TARGET_URL || { echo "Flask did not start correctly, stopping pipeline."; exit 1; }
                '''
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('sonarqube') {
                    script {
                        def scannerHome = tool name: 'SonarQubeScanner', type: 'hudson.plugins.sonar.SonarRunnerInstallation'
                        sh """
                        . .venv/bin/activate
                        ${scannerHome}/bin/sonar-scanner \
                            -Dsonar.projectKey=flask-app \
                            -Dsonar.sources=. \
                            -Dsonar.python.version=3.13 \
                            -Dsonar.host.url=$SONAR_HOST_URL \
                            -Dsonar.token=$SONAR_AUTH_TOKEN
                        """
                    }
                }
            }
        }

        stage('Dependency Check') {
            steps {
                script {
                    if (fileExists('requirements.txt')) {
                        sh 'mkdir -p dependency-check-report'
                        dependencyCheck additionalArguments: '''
                            --project "FlaskApp"
                            --scan .
                            --format HTML
                            --format XML
                            --out "dependency-check-report"
                            --disableCentral
                            --disableArchive
                            --enableExperimental
                            --nvdApiKey $NVD_API_KEY
                            --exclude "**/.venv/**"
                            --exclude "**/__pycache__/**"
                        ''', odcInstallation: 'OWASP-Check'

                        dependencyCheckPublisher pattern: 'dependency-check-report/dependency-check-report.xml'
                    } else {
                        error "Le fichier requirements.txt est manquant. Impossible d'analyser les dépendances Python."
                    }
                }
            }
        }

        stage('Run OWASP ZAP Scan') {
            steps {
                script {
                    sh """
                    mkdir -p $REPORT_DIR
                    sudo $ZAP_PATH -daemon -config api.disablekey=true &
                    sleep 15  # Laisser ZAP démarrer

                    sudo zap-cli --zap-url http://localhost open-url $TARGET_URL

                    # Lancer un scan automatique
                    sudo zap-cli --zap-url http://localhost active-scan --scanners all --recursive $TARGET_URL

                    # # Générer un rapport
                    curl "http://localhost:8090/JSON/core/view/alerts/?baseurl=$TARGET_URL" -o $REPORT_DIR/zap_report.json
                    """
                }
            }
        }

        stage('Import ZAP Report into SonarQube') {
            steps {
                script {
                    withSonarQubeEnv('sonarqube') {
                        sh """
                        curl -X POST -u $SONAR_AUTH_TOKEN: -H "Content-Type: application/json" -d @$REPORT_DIR/zap-report.json "$SONAR_HOST_URL/api/issues/import"
                        """
                    }
                }
            }
        }

        stage('Archive Artifacts') {
            steps {
                script {
                    archiveArtifacts artifacts: "$REPORT_DIR/zap_report.json", allowEmptyArchive: true
                    archiveArtifacts artifacts: "dependency-check-report/*", allowEmptyArchive: true
                }
            }
        }

        stage('Cleanup') {
            steps {
                script {
                    sh "sudo kill -9 \$(pgrep -f 'zap.sh') || true"
                    sh "sudo kill -9 \$(pgrep -f '/opt/zaproxy/zap-2.16.0.jar') || true"
                    sh "sudo kill -9 \$(cat flask.pid) || true"

                    cleanWs()
                }
            }
        }
    }
}
