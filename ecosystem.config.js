const dotenv = require('dotenv');
dotenv.config({ path: './config/.env' });

module.exports = {
  apps: [
    {
      name: "FastAPI",
      script: "/bin/bash",
      args: ["-c", "/opt/homebrew/Caskroom/miniconda/base/envs/epita-dsp-final/bin/pipenv run fastapi dev app/fastapi/main.py"],
      env: {
        PORT: process.env.PORT || 8000
      }
    },
    {
      name: "Streamlit",
      script: "/bin/bash",
      args: ["-c", "/opt/homebrew/Caskroom/miniconda/base/envs/epita-dsp-final/bin/pipenv run streamlit run app/streamlit/app.py"],
      env: {
        PORT: process.env.STREAMLIT_PORT || 8501
      }
    },
    {
      name: "Airflow",
      script: "/bin/bash",
      args: ["-c", "/opt/homebrew/Caskroom/miniconda/base/envs/epita-dsp-final/bin/pipenv run airflow standalone"],
      env: {
        AIRFLOW_HOME: process.env.AIRFLOW_HOME,
        PORT: process.env.AIRFLOW_PORT || 8080
      }
    }
  ]
};
