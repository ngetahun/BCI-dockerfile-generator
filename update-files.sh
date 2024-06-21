#!/bin/bash -e

mkdir -p src/bci_build/package/{postgres,nginx,grafana,mariadb}

curl -sf -o src/bci_build/package/postgres/entrypoint.sh https://raw.githubusercontent.com/docker-library/postgres/master/docker-entrypoint.sh
curl -sf -o src/bci_build/package/postgres/LICENSE https://raw.githubusercontent.com/docker-library/postgres/master/LICENSE

curl -sf -o src/bci_build/package/nginx/docker-entrypoint.sh https://raw.githubusercontent.com/nginxinc/docker-nginx/master/entrypoint/docker-entrypoint.sh
curl -sf -o src/bci_build/package/nginx/LICENSE https://raw.githubusercontent.com/nginxinc/docker-nginx/master/LICENSE
curl -sf -o src/bci_build/package/nginx/20-envsubst-on-templates.sh https://raw.githubusercontent.com/nginxinc/docker-nginx/master/entrypoint/20-envsubst-on-templates.sh
curl -sf -o src/bci_build/package/nginx/30-tune-worker-processes.sh https://raw.githubusercontent.com/nginxinc/docker-nginx/master/entrypoint/30-tune-worker-processes.sh

curl -sf -o src/bci_build/package/grafana/run.sh https://raw.githubusercontent.com/grafana/grafana/main/packaging/docker/run.sh

command -v jq > /dev/null || { echo "we need jq installed for update to work"; exit 1; }
rm -f src/bci_build/package/mariadb/*/entrypoint.sh src/bci_build/package/mariadb/*/healthcheck.sh
for v in $(jq -r '.mariadb|.[]' src/bci_build/package/package_versions.json | cut -d. -f1-2 | sort -u); do
    mkdir -p "src/bci_build/package/mariadb/$v"
    curl -sf -o "src/bci_build/package/mariadb/$v/entrypoint.sh" "https://raw.githubusercontent.com/MariaDB/mariadb-docker/master/$v/docker-entrypoint.sh"
    curl -sf -o "src/bci_build/package/mariadb/$v/healthcheck.sh" "https://raw.githubusercontent.com/MariaDB/mariadb-docker/master/$v/healthcheck.sh"
done

curl -sf -o src/bci_build/package/templates/rmt_helm_chart_readme.j2 https://raw.githubusercontent.com/SUSE/helm-charts/main/rmt-helm/README.md
