NGINX_SITES_AVAILABLE = "/etc/nginx/sites-available/"
NGINX_SITES_ENABLED = "/etc/nginx/sites-enabled/"

STATIC_SERVER_BLOCK = """
server {{
    listen 80;
    server_name {domain};

    root {html_path};
    index index.html index.htm;

    location / {{
        try_files $uri $uri/ =404;
    }}
}}
"""

PROXY_SERVER_BLOCK = """
server {{
    listen 80;
    server_name {domain};

    location / {{
        proxy_pass {proxy_url};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }}
}}
"""

SUBFOLDER_CONFIG = """
    location /{subfolder} {{
        alias {html_path};
        index index.html index.htm;
        try_files $uri $uri/ =404;
    }}
"""
