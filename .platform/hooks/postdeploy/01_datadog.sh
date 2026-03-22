#!/bin/bash
set -e

DD_API_KEY="ca6e64f43cc7f1f92bac2c772a57533d" \
DD_SITE="datadoghq.com" \
DD_APM_ENABLED=true \
DD_LOGS_ENABLED=true \
bash -c "$(curl -L https://s3.amazonaws.com/dd-agent/scripts/install_script.sh)"

echo "Datadog Agent installed"