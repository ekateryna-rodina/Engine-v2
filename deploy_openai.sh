#!/bin/bash

# Deploy OpenAI-enabled version to DigitalOcean production

echo "============================================"
echo "Deploying OpenAI Integration to Production"
echo "============================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create .env with your OpenAI key first."
    exit 1
fi

# Extract API key from local .env to verify it's set
OPENAI_KEY=$(grep OPENAI_API_KEY .env | cut -d '=' -f2)
if [ -z "$OPENAI_KEY" ] || [ "$OPENAI_KEY" = "sk-your-actual-key-here" ]; then
    echo "❌ Error: OPENAI_API_KEY not set in .env!"
    echo "Please edit .env and add your actual OpenAI API key."
    exit 1
fi

echo "✓ Local .env file found with API key"
echo ""

SERVER="root@157.245.115.120"
REMOTE_DIR="/root/OnlineBankingAIEngine"

echo "📤 Step 1: Pushing code to GitHub..."
git add -A
git commit -m "Update for OpenAI integration" || echo "No changes to commit"
git push origin feature/openai-integration
echo ""

echo "📥 Step 2: Connecting to production server..."
ssh $SERVER << EOF
cd $REMOTE_DIR

echo "📥 Pulling latest code..."
git fetch origin
git checkout feature/openai-integration
git pull origin feature/openai-integration

echo ""
echo "🔑 Step 3: Setting up .env file on server..."
# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << 'ENVFILE'
USE_OPENAI=true
OPENAI_API_KEY=${OPENAI_KEY}
OPENAI_MODEL=gpt-4o-mini
TOOL_BASE_URL=http://api:8000
ENVFILE
    echo "✓ .env created"
else
    echo "✓ .env already exists"
fi

echo ""
echo "🐳 Step 4: Rebuilding and restarting services..."
docker compose down
docker compose build --no-cache api
# Only start API service, don't need Ollama
docker compose up -d api

echo ""
echo "⏳ Step 5: Waiting for API to be ready..."
sleep 10

echo ""
echo "✅ Step 6: Health check..."
curl -s http://localhost:8000/health || echo "Health check failed!"

EOF

echo ""
echo "============================================"
echo "✅ Deployment Complete!"
echo "============================================"
echo ""
echo "Test the production API:"
echo "curl -H 'Content-Type: application/json' http://157.245.115.120:8000/chat \\"
echo "  -d '{\"accountId\":\"A123\",\"message\":\"Show me my spending this month\"}'"
echo ""
