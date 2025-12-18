#!/bin/bash

# Deployment script for DigitalOcean
# Usage: ./deploy.sh
# Note: Push your changes to GitHub manually before running this script

set -e

SERVER="root@157.245.115.120"
APP_DIR="/root/OnlineBankingAIEngine"

echo "============================================"
echo "Deploying to Production Server"
echo "============================================"
echo ""

# Step 1: Pull changes on server
echo "📥 Pulling latest code on server..."
ssh $SERVER "cd $APP_DIR && git pull origin main"
echo "✅ Code updated on server"
echo ""

# Step 2: Stop existing containers
echo "🛑 Stopping existing containers..."
ssh $SERVER "cd $APP_DIR && docker compose down"
echo "✅ Containers stopped"
echo ""

# Step 3: Start containers
echo "🚀 Starting containers..."
ssh $SERVER "cd $APP_DIR && docker compose build --no-cache api && docker compose up -d"
echo "✅ Containers started"
echo ""

# Step 4: Wait for services to be ready
echo "⏳ Waiting for services to start (30 seconds)..."
sleep 30
echo ""

# Step 5: Check container status
echo "📊 Container status:"
ssh $SERVER "docker ps"
echo ""

# Step 6: Check API health
echo "🏥 Checking API health..."
if curl -s http://157.245.115.120:8000/health | grep -q "ok"; then
    echo "✅ API is healthy"
else
    echo "⚠️  API health check failed"
fi
echo ""

# Step 7: Show recent logs
echo "📜 Recent API logs:"
ssh $SERVER "docker logs banking_api --tail 20"
echo ""

echo "============================================"
echo "✅ Deployment Complete!"
echo "============================================"
echo ""
echo "API: http://157.245.115.120:8000"
echo "Health: http://157.245.115.120:8000/health"
echo ""
echo "To view logs: ssh $SERVER 'docker logs banking_api -f'"
echo "To check status: ssh $SERVER 'docker ps'"
