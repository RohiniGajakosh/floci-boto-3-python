#!/bin/bash
set -e
if command -v dnf &> /dev/null; then
    dnf update -y
    dnf install -y nginx
elif command -v yum &> /dev/null; then
    yum update -y
    yum install -y nginx
elif command -v apt-get &> /dev/null; then
    apt-get update -y
    apt-get install -y nginx
fi

systemctl enable nginx
systemctl start nginx

cat << 'EOF' > /usr/share/nginx/html/index.html
<!DOCTYPE html>
<html>
<head><title>Boto3 Nginx Server</title></head>
<body style="font-family: Arial; text-align: center; margin-top: 50px;">
    <h1>Nginx is Live on EC2!</h1>
    <p>Provisioned automatically via Python Boto3 & UserData Bootstrap Script.</p>
</body>
</html>
EOF

mkdir -p /var/www/html
cp /usr/share/nginx/html/index.html /var/www/html/index.html
