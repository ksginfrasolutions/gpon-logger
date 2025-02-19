#!/bin/bash

# Function to prompt for and set environment variables
prompt_env() {
  local var_name="$1"
  local prompt_text="$2"
  read -p "$prompt_text" value
  if [ -z "$value" ]; then
    echo "Error: $var_name cannot be empty. Please provide a value."
    exit 1
  else
    echo "$var_name=$value" >> .env
  fi
}

# Delete existing .env if it exists.
if [ -f ".env" ]; then
  rm .env
fi

# Create the .env file.
touch .env

# Prompt for environment variables
prompt_env "OPENOBSERVE_URL" "Enter OpenObserve URL: "
prompt_env "USERNAME" "Enter Username: "
prompt_env "PASSWORD" "Enter Password: "

# Check if .env contains the required variables
check_env_vars() {
  if ! grep -q "^OPENOBSERVE_URL=" .env; then
    echo "Error: .env is missing OPENOBSERVE_URL variable."
    exit 1
  fi

  if ! grep -q "^USERNAME=" .env; then
    echo "Error: .env is missing USERNAME variable."
    exit 1
  fi

  if ! grep -q "^PASSWORD=" .env; then
    echo "Error: .env is missing PASSWORD variable."
    exit 1
  fi
}

# Check .env file
check_env_vars

# Check if docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
  echo "Error: docker-compose.yml file not found."
  exit 1
fi

# Run docker-compose up -d
docker compose up -d

echo "Docker Compose started in detached mode."