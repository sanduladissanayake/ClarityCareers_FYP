#!/bin/bash
# ClarityCareers Quick Update Script
# Run this on your server to pull latest changes and restart services

set -e

echo "🔄 Updating ClarityCareers..."

# Update backend
echo "📦 Updating backend code..."
cd /home/ubuntu/ClarityCareers

# If using git
if [ -d .git ]; then
    git pull origin main
else
    echo "⚠️  Git not configured. Assuming manual file copy."
fi

# Update Python dependencies if changed
echo "📚 Installing any new dependencies..."
cd backend
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Restart backend service
echo "🔄 Restarting backend..."
sudo systemctl restart ClarityCareers-Backend

# Wait for backend to start
sleep 3

# Check if backend is running
if sudo systemctl is-active --quiet ClarityCareers-Backend; then
    echo "✅ Backend restarted successfully"
else
    echo "❌ Backend failed to start. Check logs:"
    sudo journalctl -u ClarityCareers-Backend -n 20
    exit 1
fi

# Update frontend if changed
echo "📥 Updating frontend files..."
sudo cp -r /home/ubuntu/ClarityCareers/frontend/* /var/www/ClarityCareers/
sudo chown -R www-data:www-data /var/www/ClarityCareers

# Reload Nginx
echo "🔄 Reloading Nginx..."
sudo systemctl reload nginx

echo ""
echo "✅ Update complete!"
echo ""
echo "🌐 Your changes are now LIVE:"
echo "   http://$(hostname -I | awk '{print $1}')"
echo ""
echo "📊 Verify everything:"
echo "   curl http://localhost:8000/health"
echo ""
echo "🔍 View backend logs:"
echo "   sudo journalctl -u ClarityCareers-Backend -f"
