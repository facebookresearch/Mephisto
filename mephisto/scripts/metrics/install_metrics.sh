# Copyright (c) Meta Platforms and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

command_exists() {
  type "$1" &> /dev/null ;
}

# 1. Check OS type
if [ -z "$OSTYPE" ]
then
  OSTYPE=$(uname)
  echo "Checking OS type returned ${OSTYPE}..."
fi
case "$OSTYPE" in
  darwin* | Darwin*)
    platform='darwin'
    ;;
  linux* | Linux*)
    platform='linux'
    ;;
  *)
    echo "Unable to automate install for $OSTYPE"
    exit 1
    ;;
esac

# 2. Check if CURL installed.
# Some systems may have not installed CURL. In Docker we install it on building image
if ! command_exists "curl"
then
  echo "Please install 'curl'"
  exit 0
fi

# 3. Check if metrics were already installed
if [ -d "prometheus" ]
then
  echo "Prometheus directory already exists, skipping install\n"
  exit 0
fi

# 4. Download and unpack Grafana
echo "\nInstalling Grafana..."

curl -O "https://dl.grafana.com/oss/release/grafana-8.4.2.$platform-amd64.tar.gz"
tar -zxvf "grafana-8.4.2.$platform-amd64.tar.gz" > /dev/null 2>&1
mv grafana-8.4.2 grafana
rm "grafana-8.4.2.$platform-amd64.tar.gz"
cp resources/grafana_defaults.ini grafana/conf/defaults.ini

echo "Installing Grafana finished!\n"


# 5. Download and unpack Prometheus
echo "\nInstalling Prometheus..."

curl -L -O "https://github.com/prometheus/prometheus/releases/download/v2.33.4/prometheus-2.33.4.$platform-amd64.tar.gz"
tar xvfz prometheus-*.tar.gz > /dev/null 2>&1
mv "prometheus-2.33.4.$platform-amd64" prometheus
rm "prometheus-2.33.4.$platform-amd64.tar.gz"
cp resources/mephisto-prometheus-config.yml prometheus/prometheus.yml

echo "Installing Prometheus finished!\n"

# 6. Run grafana in background to receive the desired defaults
cd grafana
./bin/grafana-server > /dev/null 2>&1 &
GRAFANA_PID=$!
cd ..

grafana_url=http://$GRAFANA_HOST:$GRAFANA_PORT
until curl --output /dev/null --silent --head --fail $grafana_url; do
  printf '.'
  sleep 1
done

# 7. Copy over the Mephisto datasource
curl -X "POST" "${grafana_url}/api/datasources" \
  -H "Content-Type: application/json" \
  --user $GRAFANA_USER:$GRAFANA_PASSWORD \
  --data-binary @resources/mephisto_source.json

# 8. Copy over the mephisto default dashboard
curl --fail -k -X "POST" "${grafana_url}/api/dashboards/db" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  --user $GRAFANA_USER:$GRAFANA_PASSWORD \
  --data-binary @resources/default_mephisto_dash.json

# 9. Close grafana
kill $GRAFANA_PID

sleep 3

echo "\nInstall should have completed, please view above for errors"
