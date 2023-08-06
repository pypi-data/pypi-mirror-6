[program:{{ app_name }}]
command=/path/to/virtual/env/bin/gunicorn {{ appname }}:app
directory={{app_dir}}
autostart=true
autorestart=true
stdout_logfile={{ log_file }}
redirect_stderr=true
stopsignal=QUIT