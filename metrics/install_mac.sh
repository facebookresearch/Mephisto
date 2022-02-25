curl -O https://dl.grafana.com/oss/release/grafana-8.4.2.darwin-amd64.tar.gz
tar -zxvf grafana-8.4.2.darwin-amd64.tar.gz
mv grafana-8.4.2 grafana
rm grafana-8.4.2.darwin-amd64.tar.gz
curl -L -O https://github.com/prometheus/prometheus/releases/download/v2.33.4/prometheus-2.33.4.darwin-amd64.tar.gz
tar xvfz prometheus-*.tar.gz
mv prometheus-2.33.4.darwin-amd64 prometheus
rm prometheus-2.33.4.darwin-amd64.tar.gz
cp mephisto-prometheus-config.yml prometheus/prometheus-config.yml
cp grafana_defaults.ini grafana/conf/defaults.ini

# TODO run grafana in background, then import the defaults via the following
#
# curl -X "POST" "http://localhost:3032/api/datasources" \
# -H "Content-Type: application/json" \
#     --user admin:admin \
#     --data-binary @mephisto_source.json

# curl --fail -k -X "POST" "http://localhost:3032/api/dashboards" \
#          -H "Content-Type: application/json" \
#          -H "Accept: application/json" \
#          --user admin:admin \
#          --data-binary @mephisto_default_dash.json
