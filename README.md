
# Project Setup

## Overview

This project uses various Python packages to build and run a Streamlit application.
The dependencies are managed using Pipenv and Conda for a hassle-free setup and environment management.

## Prerequisites

- Python 3.12
- Conda (for environment management)
- PostgreSQL (for database management)

## Installation

To set up the project, follow these steps:

### 1. Clone the Repository

First, clone the repository to your local machine:

```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Set Up the Conda Environment

Create and activate a Conda environment with the required Python version:

```bash
conda create --name myenv python=3.12
conda activate myenv
```

Alternatively, you can create and activate the environment using a `environment.yml` file if provided:

```bash
conda env create -f environment.yml
conda activate myenv
```

### 3. Install Dependencies Using Pipenv

Install Pipenv if you haven't already:

```bash
pip install pipenv
```

Use Pipenv to install the project dependencies specified in the `Pipfile`:

```bash
pipenv install
```

For development dependencies, run:

```bash
pipenv install --dev
```

### 4. Set Up PostgreSQL

Make sure PostgreSQL is installed and running on your machine. You may need to create a database and configure your application to connect to it.

### 5. Run the Application

After installing the dependencies, you can run the Streamlit application:

```bash
streamlit run app.py
```

## Development

For development purposes, you might need to use additional tools and configurations. Make sure to follow these steps:

1. Install development dependencies:

    ```bash
    pipenv install --dev
    ```

2. Run linters or other development tools as needed.
