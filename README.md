# KSG-INFRASOLUTIONS Deployment Guide

This document outlines the steps required to deploy the KSG-INFRASOLUTIONS application using Docker Compose. It covers the prerequisites, configuration, and deployment process.

## Prerequisites

Before you begin, ensure you have the following installed:

*   **Docker:** Docker is a platform for running applications in containers.  Installation instructions can be found [here](https://docs.docker.com/get-docker/).
*   **Docker Compose:** Docker Compose is a tool for defining and running multi-container Docker applications. It's usually installed along with Docker Desktop or can be installed separately.  See [here](https://docs.docker.com/compose/install/).
*   **Bash:** A shell interpreter (typically available on Linux and macOS). Windows users may need to use Git Bash or WSL (Windows Subsystem for Linux).

## Repository Structure

The repository contains the following key files:

*   **`docker-compose.yml`:** Defines the services, networks, and volumes for the application.
*   **`Dockerfile`:** Specifies how to build the Docker image for the application.
*   **`logger.py`:** The main Python script for logging.
*   **`requirements.txt`:** (Optional) Lists the Python dependencies for the application.
*   **`deploy.sh`:** A shell script to simplify the deployment process (prompts for environment variables and starts the Docker Compose application).

## Configuration

The application requires the following environment variables:

*   `OPENOBSERVE_URL`: The URL for the OpenObserve service.
*   `USERNAME`: The username for authentication with OpenObserve.
*   `PASSWORD`: The password for authentication with OpenObserve.

These variables can be configured in two ways:

1.  **Using the `deploy.sh` script (Recommended):** The `deploy.sh` script prompts you for each variable and stores them in a `.env` file.

2.  **Directly Setting Environment Variables:** You can directly set the environment variables in your shell before running `docker-compose`.

    ```bash
    export OPENOBSERVE_URL="your_openobserve_url"
    export USERNAME="your_username"
    export PASSWORD="your_password"
    ```

    This is not recommended, as it's easy to forget to set them, and storing passwords in your shell history is a security risk.

**Security Note:** It is *strongly discouraged* to store passwords in plain text in the `.env` file or directly in your shell environment for production deployments. Use a secrets management system like HashiCorp Vault, AWS Secrets Manager, or similar.

## Deployment Steps

Follow these steps to deploy the application:

1.  **Clone the Repository:**

    ```bash
    git clone https://github.com/ksginfrasolutions/gpon-logger
    cd  gpon-logger
    ```

2.  **Run the Deployment Script:**

    ```bash
    chmod +x deploy.sh
    ./deploy.sh
    ```

    The script will prompt you for the required environment variables. It will create/overwrite .env file. It will then create a `.env` file with the provided values, verify that all the environment variables are present and start the Docker Compose application.

    **Note:** The deployment script will enforce that the PASSWORD environment variable is set.  If it is not set, the deployment will fail.

3.  **Verify the Deployment:**

    After the deployment is complete, verify that the application is running by checking the Docker containers:

    ```bash
    docker ps
    ```

    You should see a container named `syslog-logger` running.

4.  **Check Logs:**

    You can view the application logs using:

    ```bash
    docker logs gpon-logger
    ```

    This will show the logs from the Python script. If you're using a volume mount to persist the logs, you can find them on the host system in that volume.

## Docker Compose Configuration

The `docker-compose.yml` file defines the following:

*   **`syslog-logger` Service:**
    *   Builds the Docker image from the current directory (`.`).
    *   Maps ports 514 (UDP and TCP) on the host to ports 514 (UDP and TCP) in the container.
    *   Mounts a Docker volume named `syslog_volume` to `/var/log` inside the container for persistent log storage.
    *   Sets the environment variables `OPENOBSERVE_URL`, `USERNAME`, and `PASSWORD` using the values provided (either from the prompt or pre-set environment).
    *   Configures the container to restart automatically if it fails.
*   **`volumes`:** Defines the `syslog_volume` for storing logs.

## Security Considerations

*   **Plain Text Passwords:** This deployment guide utilizes environment variables, including a `PASSWORD`. Storing passwords in plain text is a security risk. Consider using a secrets management solution for production environments.
*   **Network Security:** Ensure your network is configured to restrict access to the ports exposed by the container (514/UDP, 514/TCP), especially if the container is exposed to the public internet.
*   **Log Injection:**  Be aware of potential log injection attacks, particularly if you're receiving logs from untrusted sources.  Implement proper log validation and sanitization.

## Troubleshooting

*   **Image Build Errors:** If you encounter errors during the image build process, check your `Dockerfile` for syntax errors or missing dependencies.
*   **Container Start Failures:** If the container fails to start, check the Docker logs for error messages.  Common causes include missing environment variables, port conflicts, or incorrect file permissions.
*   **Connectivity Issues:** If you cannot connect to the application, ensure that the ports are correctly mapped in the `docker-compose.yml` file and that no firewalls are blocking the traffic.

## Contributing

Contributions to this project are welcome! Please submit pull requests with clear descriptions of the changes.