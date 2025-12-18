# OpenAI Integration Setup

This branch adds support for using OpenAI models instead of Ollama for LLM-based intent classification.

## Configuration

The application can use either OpenAI or Ollama based on environment variables.

### Option 1: Use OpenAI (Recommended for production)

1. Create a `.env` file in the project root:

```bash
cp .env.example .env
```

2. Edit `.env` and set your OpenAI API key:

```env
USE_OPENAI=true
OPENAI_API_KEY=sk-your-actual-api-key-here
OPENAI_MODEL=gpt-4o-mini  # or gpt-4o for better accuracy
```

### Option 2: Use Ollama (Default, for local development)

```env
USE_OPENAI=false
OLLAMA_URL=http://ollama:11434/v1/chat/completions
OLLAMA_MODEL=llama3.2:latest
```

## Running Locally with OpenAI

```bash
# Set environment variables
export USE_OPENAI=true
export OPENAI_API_KEY=sk-your-key-here

# Start with Docker Compose (Ollama won't be needed but will start anyway)
docker compose up -d

# Or run just the API without Ollama
docker compose up -d api
```

## Running Locally with Python (without Docker)

```bash
# Create .env file with OpenAI settings
echo "USE_OPENAI=true" > .env
echo "OPENAI_API_KEY=sk-your-key-here" >> .env

# Start the API
uvicorn src.app:app --reload --port 8000
```

## Deploying to Production with OpenAI

1. On the production server, create `.env` file:

```bash
ssh root@157.245.115.120
cd /root/OnlineBankingAIEngine
nano .env  # Add your OpenAI key
```

2. Set these environment variables in `.env`:

```env
USE_OPENAI=true
OPENAI_API_KEY=sk-your-actual-production-key
OPENAI_MODEL=gpt-4o-mini
```

3. Deploy:

```bash
git pull origin feature/openai-integration
docker compose down
docker compose up -d api  # Only start API, Ollama not needed
```

## Testing

Test locally:
```bash
curl -H "Content-Type: application/json" http://localhost:8000/chat \
  -d '{"accountId":"A123","message":"Show me my spending this month"}'
```

Run the test suite:
```bash
./tests/run_tests_v2.sh http://localhost:8000
```

## Benefits of OpenAI vs Ollama

- **Better Accuracy**: OpenAI models (especially gpt-4o) follow complex instructions more reliably
- **Faster Response**: Typically 1-3 seconds vs 5-10 seconds with Ollama
- **No GPU Required**: API-based, no local compute needed
- **More Consistent**: Less variation in intent classification

## Cost Comparison

- gpt-4o-mini: ~$0.0001 per query (very cheap)
- gpt-4o: ~$0.0005 per query (better accuracy)
- Ollama: Free but requires server resources

For typical usage (100-1000 queries/day), OpenAI costs are minimal.
