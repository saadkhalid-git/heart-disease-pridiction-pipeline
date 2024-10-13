
# Project Setup

## Overview
Heat Disease Pridiction Pipeline
The dependencies of the project are managed using Pipenv and Conda for a hassle-free setup and environment management.

```![width-1600](https://github.com/user-attachments/assets/4bd362c8-f2fc-4996-acc4-3d991eb7b891)

## Prerequisites

- Python 3.9
- pipenv (for environment management)
- PostgreSQL (for database management)

## Installation

To set up the project, follow these steps:

### 1. Clone the Repository

First, clone the repository to your local machine:

```bash
git clone git@github.com:saadkhalid-git/heart-disease-pridiction-pipeline.git
cd heart-disease-pridiction-pipeline
```

### 2. Set Up the Pipenv Environment

Create and activate a pipenv environment with the required Python version:

```bash
pip install pipenv
pipenv --python 3.9
pipenv shell
```

Alternatively, you can create and activate the environment using conda for MAC users:

```bash
brew install pipenv
pipenv shell
pipenv --python 3.9
```

### 3. Install Dependencies Using Pipenv

Use Pipenv to install the project dependencies specified in the `Pipfile`:

```bash
pipenv install
```

For development dependencies, run:

```bash
pipenv install --dev


### 4. Set Up PostgreSQL

Make sure PostgreSQL is installed and running on your machine. You may need to create a database and configure your application to connect to it.

## You need to set your database URL in the `app/config.env` against `DB_URL` variable

### 5. Run the Application

To run all applications at once you need to install node and `pm2`

```bash
npm install pm2 -g
```
Then

```bash
pm2 start ecosystem.config.js
```

To monitor logs

```bash
pm2 logs
```


After installing the dependencies, you can run the individually

Streamlit application:

```bash
streamlit run app/streamlit/app.py
```

FastAPI:

```bash
streamlit run app/fastapi/main.py
```

Airflow:

You must in project root directory before runing below command

```bash
export AIRFLOW_HOME=${PWD}/airflow
airflow standalone
```
