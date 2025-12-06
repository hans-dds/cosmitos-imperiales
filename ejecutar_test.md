# Ejectuar sonarqube
cd sonarqube/ && podman-compose up -d

# Ejecutar test
cd .. && uv run pytest --cov=src --cov-report=xml:coverage.xml tests/ -q

# Ejecutar SonarQube Scanner
podman run \
    --rm \
    --network host \
    -v "$(pwd):/usr/src:Z" \
    sonarsource/sonar-scanner-cli \
    -Dsonar.projectKey=cosmitos1 \
    -Dsonar.sources=. \
    -Dsonar.host.url=http://localhost:9000 \
    -Dsonar.token=sqp_f949b42e0bfbea09204d41311eefdccdaeb74d6b
