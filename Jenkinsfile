pipeline {
    agent any

    // Uncomment if SCM polling is required
    /*
    //triggers {
    //    pollSCM('H/5 * * * *')
    //}
    */

    environment {
        PLATFORM       = 'vs'
        SONIC_REPO     = 'https://github.com/sonic-net/sonic-buildimage'
        BUILD_LOG      = 'pipeline_build.log'
        OPENAI_API_KEY = credentials('openai-api-key')
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup') {
            steps {
                sh '''
                    python3 -m pip install --upgrade pip
                    pip3 install -q -r requirements.txt
                '''
            }
        }

        stage('Init Submodules') {
            steps {
                sh '''
                    make init 2>&1 | tee "$BUILD_LOG"
                '''
            }
        }

        stage('Configure') {
            steps {
                sh '''
                    make configure PLATFORM=$PLATFORM 2>&1 | tee -a "$BUILD_LOG"
                '''
            }
        }

        stage('Build sonic-vs.img') {
            steps {
                sh '''
                    make target/sonic-vs.img 2>&1 | tee -a "$BUILD_LOG"
                '''
            }
        }

        stage('Test SONiC VS') {
            steps {
                sh '''
                    make target/sonic-vs-rpc.img 2>&1 | tee -a "$BUILD_LOG"
                '''
            }
        }
    }

    post {

        failure {
            echo '======================================================='
            echo 'Pipeline FAILED — running AI log analyser...'
            echo '======================================================='

            sh '''
                if [ -f analyze.py ]; then
                    python3 analyze.py "$BUILD_LOG" || true
                else
                    echo "analyze.py not found."
                fi
            '''
        }

        success {
            echo 'Pipeline PASSED. No log analysis needed.'
        }

        always {
            archiveArtifacts(
                artifacts: "${BUILD_LOG}",
                allowEmptyArchive: true
            )
        }
    }
}
