# Lanzo SonarQube con el nombre de proyecto "sonar"
podman-compose -f sonar.yml -p sonar up -d

# Lanzo Jenkins con el nombre de proyecto "jenkins"
podman-compose -f jenkins.yml -p jenkins up -d

sqp_f949b42e0bfbea09204d41311eefdccdaeb74d6b

podman run \
    --rm \
    --network host \
    -v "$(pwd):/usr/src:Z" \
    sonarsource/sonar-scanner-cli \
    -Dsonar.projectKey=cosmitos1 \
    -Dsonar.sources=. \
    -Dsonar.host.url=http://localhost:9000 \
    -Dsonar.token=sqp_f949b42e0bfbea09204d41311eefdccdaeb74d6b

uv run pytest --cov=src --cov-report=xml:coverage.xml tests/ -q