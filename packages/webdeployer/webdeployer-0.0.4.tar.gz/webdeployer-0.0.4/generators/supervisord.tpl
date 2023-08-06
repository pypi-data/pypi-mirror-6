[program:{{ ['app_name'] }}]
command=/path/to/virtual/env/bin/gunicorn {{ settings['app_name'] }}:app
directory={{settings['app_dir']}}
autostart=true
autorestart=true
stdout_logfile={{ settings['log_file'] }}
redirect_stderr=true
stopsignal=QUIT