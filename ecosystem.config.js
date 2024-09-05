module.exports = {
    apps: [
      {
        name: 'streamlit',
        script: 'streamlit',
        args: 'run app.py',
        cwd: '/path/to/your/project',
        watch: true,
        log_file: 'app/streamlit/logs/streamlit-combined.log',
        merge_logs: true
      },
      {
        name: 'fastapi',
        script: 'uvicorn',
        args: 'backend.app.main:app --reload',
        cwd: '/path/to/your/project',
        watch: true,
        log_file: 'app/fastapi/logs/fastapi-combined.log',
        merge_logs: true
      }
    ]
  };
