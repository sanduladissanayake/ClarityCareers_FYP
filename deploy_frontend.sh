#!/bin/bash
# ClarityCareers Frontend + Nginx Automated Deployment Script
# Run this on your Oracle Cloud Ubuntu VM (after backend is deployed)

set -e

echo "🚀 Starting ClarityCareers Frontend Deployment..."

# Install Nginx
echo "📥 Installing Nginx web server..."
sudo apt-get install -y nginx

# Enable and start Nginx
echo "🚀 Starting Nginx..."
sudo systemctl enable nginx
sudo systemctl start nginx

# Copy frontend files to Nginx directory
echo "📁 Copying frontend files..."
sudo mkdir -p /var/www/ClarityCareers
sudo cp -r /home/ubuntu/ClarityCareers/frontend/* /var/www/ClarityCareers/

# Set proper permissions
sudo chown -R www-data:www-data /var/www/ClarityCareers
sudo chmod -R 755 /var/www/ClarityCareers

# Create Nginx configuration
echo "⚙️  Configuring Nginx..."
sudo tee /etc/nginx/sites-available/ClarityCareers > /dev/null << 'EOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;

    server_name _;

    # Frontend files
    root /var/www/ClarityCareers;
    index index.html;

    # Serve static files with caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # HTML files - no caching
    location ~* \.html$ {
        expires -1;
    }

    # Route all other requests to index.html (for SPA routing)
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy API requests to backend
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts for long-running operations
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # API docs
    location /docs {
        proxy_pass http://127.0.0.1:8000/docs;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Redoc API docs
    location /redoc {
        proxy_pass http://127.0.0.1:8000/redoc;
        proxy_set_header Host $host;
    }

    # OpenAPI schema
    location /openapi.json {
        proxy_pass http://127.0.0.1:8000/openapi.json;
        proxy_set_header Host $host;
    }

    # Deny access to sensitive files
    location ~ /\. {
        deny all;
    }

    location ~ ~$ {
        deny all;
    }
}
EOF

# Enable the site
echo "🔗 Enabling Nginx configuration..."
sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -sf /etc/nginx/sites-available/ClarityCareers /etc/nginx/sites-enabled/

# Test Nginx configuration
echo "🔍 Testing Nginx configuration..."
sudo nginx -t

# Reload Nginx
echo "🔄 Reloading Nginx..."
sudo systemctl reload nginx

# Get server IP
HOSTNAME=$(hostname -I | awk '{print $1}')

echo ""
echo "✅ Frontend deployment complete!"
echo ""
echo "🌐 Access your application:"
echo "   Frontend: http://$HOSTNAME"
echo "   API Docs: http://$HOSTNAME/docs"
echo ""
echo "📊 Monitor services:"
echo "   Backend logs:  sudo journalctl -u ClarityCareers-Backend -f"
echo "   Nginx logs:    sudo tail -f /var/log/nginx/error.log"
echo ""
echo "🔄 Restart Nginx: sudo systemctl reload nginx"
