# n8n Workflow Setup for Clara Automation Pipeline

## Overview

This directory contains n8n workflows for automating the Clara pipeline. n8n provides a visual workflow editor and can be self-hosted for free.

## Installation Options

### Option 1: Docker (Recommended)

```bash
# Run n8n with Docker
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  -v $(pwd):/data \
  n8nio/n8n

# Access n8n at http://localhost:5678
```

### Option 2: npm

```bash
# Install n8n globally
npm install -g n8n

# Start n8n
n8n start

# Access n8n at http://localhost:5678
```

## Workflow Structure

The Clara automation pipeline is split into two main workflows:

### 1. Demo Processing Workflow
- **Trigger**: New file added to `sample_data/demo_calls/`
- **Steps**:
  1. Read transcript file
  2. Execute `pipeline_a_demo.py` script
  3. Validate outputs
  4. Send notification (optional)
  5. Create task in Asana/Linear (optional)

### 2. Onboarding Processing Workflow
- **Trigger**: New file added to `sample_data/onboarding_calls/`
- **Steps**:
  1. Read transcript file
  2. Match to existing account
  3. Execute `pipeline_b_onboarding.py` script
  4. Generate changelog
  5. Validate outputs
  6. Send notification (optional)

## Manual Workflow Creation

Since we're using free tier, here's how to manually create the workflows:

### Demo Processing Workflow

1. **Create New Workflow** in n8n
2. **Add File Trigger Node**:
   - Path to watch: `/data/sample_data/demo_calls/`
   - File pattern: `*.txt`
3. **Add Python Execute Node**:
   - Command: 
     ```bash
     python /data/scripts/pipeline_a_demo.py \
       --input "{{ $json.path }}" \
       --account-id "{{ $json.path | extractAccountId }}"
     ```
4. **Add Validation Node** (Python):
   - Command:
     ```bash
     python /data/scripts/validate_outputs.py \
       --account-id "{{ $json.account_id }}" \
       --v1-only
     ```
5. **Add Notification Node** (optional):
   - Email/Slack notification on success or failure

### Onboarding Processing Workflow

Similar structure, but calls `pipeline_b_onboarding.py` instead.

## Environment Variables in n8n

Configure these in n8n Settings → Environment Variables:

```
ANTHROPIC_API_KEY=your_key_here
STORAGE_PATH=/data/outputs
```

## Batch Processing Alternative

If n8n is not available or preferred, use the batch processing script:

```bash
# Process all demo calls
python scripts/batch_process.py \
  --mode demo \
  --input-dir sample_data/demo_calls/

# Process all onboarding calls
python scripts/batch_process.py \
  --mode onboarding \
  --input-dir sample_data/onboarding_calls/
```

## Webhook Integration (Advanced)

For production use, you can set up webhooks:

1. **n8n Webhook Node**:
   - Listen for incoming POST requests
   - Expect JSON payload with transcript URL or content

2. **Example Payload**:
   ```json
   {
     "type": "demo",
     "account_id": "ACC001",
     "transcript": "Full transcript text...",
     "metadata": {
       "call_date": "2026-03-04",
       "duration_minutes": 18
     }
   }
   ```

3. **Workflow Actions**:
   - Parse payload
   - Save transcript to temp file
   - Run appropriate pipeline script
   - Return results via webhook response

## Monitoring and Logging

n8n provides built-in:
- Execution history
- Error logs
- Retry mechanisms
- Manual workflow testing

Access these via the n8n UI at http://localhost:5678

## Cost Considerations

- n8n self-hosted: **$0** (free)
- n8n cloud free tier: **$0** (limited executions)
- All our scripts: **$0** (using free Claude API)

Total cost: **$0** ✓

## Troubleshooting

### n8n Can't Access Scripts

Make sure volume mounting is correct:
```bash
docker run ... -v $(pwd):/data ...
```

### Python Not Found in n8n

Install Python in the n8n Docker container or use the npm version with system Python.

### File Permissions

```bash
chmod +x scripts/*.py
```

## Alternative: GitHub Actions

If n8n is too complex, you can use GitHub Actions for automation:

```yaml
# .github/workflows/process-transcripts.yml
name: Process Transcripts

on:
  push:
    paths:
      - 'sample_data/**/*.txt'

jobs:
  process:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run batch processing
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          python scripts/batch_process.py --mode demo --input-dir sample_data/demo_calls/
          python scripts/batch_process.py --mode onboarding --input-dir sample_data/onboarding_calls/
      - name: Commit outputs
        run: |
          git config user.name "GitHub Actions"
          git add outputs/
          git commit -m "Auto-generate agent configs" || true
          git push
```

This is also completely free!

## Recommendation

For this assignment:
- **Use batch processing scripts** (simplest, zero setup)
- Document n8n as "production enhancement"
- Demonstrate batch processing in video

n8n is powerful but adds complexity. The Python scripts alone meet all requirements.
