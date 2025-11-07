# Project Overview

This project is the AIL (Analysis of Information Leaks) framework, a modular framework for analyzing potential information leaks from unstructured data sources. It is written in Python and uses a variety of technologies for data storage, processing, and analysis.

The framework is designed to be extensible, with a modular architecture that allows for the addition of new functionalities. It supports various data sources, including ZMQ feeds, and has importers for different data types. The core of the framework is a set of modules that process and analyze the data, extracting information such as URLs, credit card numbers, credentials, and email addresses.

AIL uses Redis and Kvrocks for in-memory data storage and as a message broker for the processing modules. The framework also includes a web interface built with Flask for visualizing the analyzed data.

# Building and Running

## Dependencies

The project has a number of system-level dependencies that need to be installed. The `installing_deps.sh` script is provided for Debian/Ubuntu-based systems. This script installs packages such as `python3-pip`, `virtualenv`, `redis-server`, and builds several components from source, including:

*   Redis
*   tlsh
*   pgpdump
*   Yara
*   Kvrocks

The Python dependencies are listed in the `requirements.txt` file and can be installed using pip.

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/ail-project/ail-framework.git
    cd ail-framework
    git submodule update --init --recursive
    ```

2.  Install the dependencies:
    ```bash
    ./installing_deps.sh
    ```

3.  Install the Python packages into a virtual environment:
    ```bash
    ./install_virtualenv.sh
    ```

## Running the Application

The AIL framework is launched and managed using the `LAUNCH.sh` script in the `bin` directory.

*   **Launch all components:**
    ```bash
    cd bin/
    ./LAUNCH.sh -l
    ```

*   **Kill all components:**
    ```bash
    cd bin/
    ./LAUNCH.sh -k
    ```

*   **Restart the framework:**
    ```bash
    cd bin/
    ./LAUNCH.sh -r
    ```

The web interface will be available at `https://localhost:7000/`.

## Testing

To run the tests, use the following command:

```bash
cd bin/
./LAUNCH.sh -t
```

# Development Conventions

The project uses a virtual environment for managing Python dependencies, which is a standard practice in Python development. The `install_virtualenv.sh` script creates and populates this environment.

The codebase is organized into several directories, including:

*   `bin`: Contains the main scripts for running and managing the framework.
*   `configs`: Configuration files for the various components.
*   `doc`: Documentation.
*   `modules`: The processing modules.
*   `tests`: Unit tests.

The use of `screen` in the `LAUNCH.sh` script suggests that the application is intended to be run as a set of background processes.
