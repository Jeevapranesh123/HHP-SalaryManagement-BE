#!/bin/sh

# Function to check if a Docker network exists
network_exists() {
    docker network ls | grep -q "$1"
}

# The name of your Docker network
network_name="hindustan_applications"

# Check if the first argument is "up" or the entire argument string is "up -d"
if [ "$1" = "up" ] || [ "$*" = "up -d" ]; then
    # Create the network only if it does not exist
    if ! network_exists "$network_name"; then
        echo "Creating Docker network: $network_name"
        docker network create "$network_name"
    else
        echo "Docker network $network_name already exists."
    fi
fi

# Run docker-compose with passed arguments
docker-compose -f infra/traefik-compose.yml -f infra/traefik-compose.staging.yml "$@"

docker-compose -f infra/services-compose.yml -f infra/services-compose.staging.yml "$@"