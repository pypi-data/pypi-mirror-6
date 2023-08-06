server {
    listen 80;
    server_name {%  for server in servers %} {{server}} {{server}};

    root /path/to/hello;

    access_log {{access_log}};
    error_log {{error_log}};

    location / {
        proxy_set_header X-Forward-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        if (!-f $request_filename) {
            proxy_pass http://127.0.0.1:{{port}};
            break;
        }
    }
}