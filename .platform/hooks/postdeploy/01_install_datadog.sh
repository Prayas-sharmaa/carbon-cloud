#!/bin/bash
set -e

echo "Installing Datadog Agent with APM enabled..."

# Ensure environment variables are exported
export DD_API_KEY=${DD_API_KEY}
export DD_SITE="us5.datadoghq.com"
export DD_APM_ENABLED=true

# Install Datadog Agent
DD_API_KEY=${DD_API_KEY} DD_SITE=${DD_SITE} DD_APM_ENABLED=true bash -c "$(curl -L https://s3.amazonaws.com/dd-agent/scripts/install_script.sh)"

# Enable and start the Datadog agent
systemctl enable datadog-agent
systemctl start datadog-agent

echo "Datadog Agent installed and started successfully."