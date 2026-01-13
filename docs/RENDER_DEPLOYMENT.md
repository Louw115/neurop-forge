# Deploying Neurop Forge API to Render

This guide explains how to deploy the Neurop Forge API to Render's free tier.

## Prerequisites

1. A Render account (free at render.com)
2. Your GitHub repository with Neurop Forge
3. The `.neurop_expanded_library/` folder (NOT in public GitHub)

## Step 1: Prepare the Library

The library must be present on Render but NOT in your public GitHub repo.

**Option A: Private Git Repository**
- Create a private repo with just the library files
- Render can clone from private repos

**Option B: Manual Upload**
- After initial deploy, SSH into Render and upload the library
- Use `render ssh` or the web shell

**Option C: S3/Cloud Storage**
- Store library in S3 bucket
- Modify API to load from S3 on startup

## Step 2: Connect to Render

1. Go to render.com and sign in
2. Click "New" -> "Web Service"
3. Connect your GitHub repository
4. Render will auto-detect the `render.yaml` configuration

## Step 3: Environment Variables

Set these in Render dashboard:

```
PYTHON_VERSION=3.11.0
PORT=10000 (Render assigns this automatically)
```

## Step 4: Deploy

Click "Deploy" and Render will:
1. Clone your repository
2. Run `pip install -r requirements-api.txt`
3. Start the API with `uvicorn api.main:app`

## API Endpoints

Once deployed, your API will be available at:
`https://neurop-forge-api.onrender.com`

### Health Check
```bash
curl https://your-app.onrender.com/health
```

### Execute Block (requires API key)
```bash
curl -X POST https://your-app.onrender.com/execute \
  -H "Content-Type: application/json" \
  -H "X-API-Key: demo_key" \
  -d '{"query": "validate email", "inputs": {"email": "test@example.com"}}'
```

### Search Blocks
```bash
curl -X POST https://your-app.onrender.com/search \
  -H "Content-Type: application/json" \
  -H "X-API-Key: demo_key" \
  -d '{"query": "password validation", "limit": 5}'
```

## Free Tier Limitations

Render's free tier includes:
- 750 hours/month of compute
- Spins down after 15 min of inactivity
- First request after spin-down takes ~30 seconds
- Perfect for demos and proof-of-concept

## Production Considerations

For production use:
1. Use Render's paid tier ($7/month) for always-on
2. Add proper API key management (database-backed)
3. Add rate limiting per API key
4. Store library in encrypted cloud storage
5. Add monitoring and alerting

## Troubleshooting

**"Library not loaded" error:**
- Check that `.neurop_expanded_library/` exists on the server
- Verify path in `api/main.py` matches your setup

**Slow first request:**
- Normal on free tier - server spins down after inactivity
- Consider paid tier for production use

**Memory errors:**
- 4,500+ blocks may exceed free tier memory
- Consider lazy loading or paid tier with more RAM
