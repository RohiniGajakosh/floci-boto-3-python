#!/bin/bash
set -e
if command -v dnf &> /dev/null; then
    dnf install -y nginx
    web_root=/usr/share/nginx/html
elif command -v yum &> /dev/null; then
    yum install -y nginx
    web_root=/usr/share/nginx/html
elif command -v apt-get &> /dev/null; then
    apt-get update -y
    apt-get install -y nginx
    web_root=/var/www/html
else
    echo "No supported package manager found; cannot install nginx." >&2
    exit 1
fi

mkdir -p "$web_root"
cat > "$web_root/index.html" <<EOF
<!DOCTYPE html>
<html>
<head><title>Boto3 Nginx Server</title></head>
<body style="font-family: Arial; text-align: center; margin-top: 50px;">
    <h1>Nginx is Live on EC2!</h1>
    <p>Provisioned automatically via Python Boto3 & UserData Bootstrap Script.</p>
    <p>Guest hostname: $(uname -n)</p>
</body>
</html>
EOF

if command -v systemctl &> /dev/null && systemctl is-system-running &> /dev/null; then
    systemctl enable --now nginx
else
    nginx -t
    if ! nginx -s reload &> /dev/null; then
        nginx
    fi
fi
