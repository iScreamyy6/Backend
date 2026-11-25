cat << 'EOF' | sudo tee /etc/systemd/system/sgr-django.service
[Unit]
Description=SGR Municipalidad Django Server
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/SGR-Municipalidad
ExecStart=/home/ubuntu/SGR-Municipalidad/venv/bin/python manage.py runserver 0.0.0.0:8000
Restart=always
RestartSec=5
StandardOutput=append:/home/ubuntu/django.log
StandardError=append:/home/ubuntu/django.log

[Install]
WantedBy=multi-user.target
EOF

cat << 'EOF' | sudo tee /etc/nginx/sites-available/default
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;

    location /static/ {
        alias /home/ubuntu/SGR-Municipalidad/static/;
    }

    location /media/ {
        alias /home/ubuntu/SGR-Municipalidad/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

sudo systemctl daemon-reload
sudo systemctl enable sgr-django.service
sudo systemctl restart sgr-django.service
sudo systemctl restart nginx
