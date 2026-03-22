#!/bin/bash
set -e

if [ -z "$DD_API_KEY" ]; then
  echo "DD_API_KEY is not set, skipping Datadog install"
  exit 0
fi

echo "Installing Datadog Agent..."

DD_API_KEY=$DD_API_KEY \
DD_SITE="datadoghq.com" \
DD_APM_ENABLED=true \
DD_LOGS_ENABLED=true \
bash -c "$(curl -L https://s3.amazonaws.com/dd-agent/scripts/install_script.sh)"

echo "Datadog Agent installed"