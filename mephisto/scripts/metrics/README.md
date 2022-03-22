# Metrics

This directory is the expected location to house a [Prometheus installation](https://prometheus.io/download/) and a [Grafana installation](https://grafana.com/grafana/download/7.3.0-381ff45epre?platform=mac), such that you can use Mephisto's full metrics. 

All of the resources for the default installation (launched via `./install_mac.sh` or `./install_linux.sh`) are available in the `resources` folder. 

The quickest way to view metrics is with the `python view_metrics.py` script. It will create a prometheus and grafana server if they're not already running, then direct you to the right place to view the dashboard. If you have existing server resources you'd like to shutdown, run `python shutdown_metrics.py`.