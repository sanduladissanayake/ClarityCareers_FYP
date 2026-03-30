#!/bin/bash
# ClarityCareers Backend Automated Deployment Script
# Run this on your Oracle Cloud Ubuntu VM

set -e

echo "🚀 Starting ClarityCareers Backend Deployment..."

# Update system
echo "📦 Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install dependencies
echo "📥 Installing Python, MySQL, and Git..."
sudo apt-get install -y python3.10 python3-pip mysql-server git curl

# Create directory
echo "📁 Creating project directory..."
mkdir -p /home/ubuntu/ClarityCareers
cd /home/ubuntu/ClarityCareers

# Clone repository (change URL to your repo)
echo "📥 Downloading code..."
# If using git:
# git clone https://github.com/YOUR_USERNAME/ClarityCareers.git

# If uploading manually, assume files are already here
cd backend

# Create virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python packages
echo "📚 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Download Spacy model
echo "📥 Downloading Spacy English model (this takes ~2 min)..."
python -m spacy download en_core_web_sm

# Configure database
echo "🗄️  Configuring MySQL database..."
sudo systemctl start mysql
sudo systemctl enable mysql

# Create database and user
sudo mysql -e "CREATE DATABASE IF NOT EXISTS ClarityCareers;"
sudo mysql -e "CREATE USER IF NOT EXISTS 'clarity'@'localhost' IDENTIFIED BY 'clarity_secure_2024';"
sudo mysql -e "GRANT ALL PRIVILEGES ON ClarityCareers.* TO 'clarity'@'localhost';"
sudo mysql -e "FLUSH PRIVILEGES;"

# Initialize database tables
echo "🗂️  Initializing database tables..."
python create_db.py

# Create environment file
echo "⚙️  Creating .env file..."
cat > .env << 'EOF'
DATABASE_URL=mysql://clarity:clarity_secure_2024@localhost:3306/ClarityCareers
SECRET_KEY=your-super-secret-key-change-this-in-production-12345678
ALGORITHM=HS256
FINE_TUNED_MODEL_PATH=../models/advanced-model
EOF

# Create systemd service
echo "⚙️  Creating systemd service..."
sudo tee /etc/systemd/system/ClarityCareers-Backend.service > /dev/null << 'EOF'
[Unit]
Description=ClarityCareers Backend API
After=network.target mysql.service

[Service]
Type=notify
User=ubuntu
WorkingDirectory=/home/ubuntu/ClarityCareers/backend
ExecStart=/home/ubuntu/ClarityCareers/backend/venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=on-failure
RestartSec=5s
Environment="PATH=/home/ubuntu/ClarityCareers/backend/venv/bin"

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
echo "🚀 Starting backend service..."
sudo systemctl daemon-reload
sudo systemctl enable ClarityCareers-Backend
sudo systemctl start ClarityCareers-Backend

# Wait for service to start
sleep 3

# Check status
echo "✅ Checking service status..."
sudo systemctl status ClarityCareers-Backend --no-pager

# Get server IP
echo ""
echo "✅ Backend deployment complete!"
echo ""
echo "📍 API URL: http://$(hostname -I | awk '{print $1}'):8000"
echo "📚 API Docs: http://$(hostname -I | awk '{print $1}'):8000/docs"
echo ""
echo "🔍 View logs: sudo journalctl -u ClarityCareers-Backend -f"
echo "🔄 Restart service: sudo systemctl restart ClarityCareers-Backend"
