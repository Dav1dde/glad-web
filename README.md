Glad-Web
========

This is a webservice for [glad](https://github.com/Dav1dde/glad), a multi-language
GL/GLES/EGL/GLX/WGL loader-generator based on the official specifications.

Check out the demo at: http://glad.dav1d.de/


## Nginx ##

    server {
        listen 80;
        server_name localhost;
    
        root /path/to/glad-web/;
    
        location / {
            try_files $uri @proxy_to_app;
        }
    
        location /static {
            alias /path/to/glad-web/gladweb/static;
        }
        
        # 'frozen' html files 
        location /generated {
            default_type text/plain;
            alias /path/to/glad-web/temp;
        }
       
        # served by flask-silk 
        location /generated/icons {
            try_files $uri @proxy_to_app;
        }
    
        location @proxy_to_app {
            proxy_set_header Host $http_host;
            proxy_set_header X-Forwarded-For  $proxy_add_x_forwarded_for;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_redirect off;
    
            proxy_pass http://localhost:5000;
        }
    }

