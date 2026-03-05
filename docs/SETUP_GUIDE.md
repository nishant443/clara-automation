# Clara Automation Pipeline - Setup Guide

## Prerequisites Checklist

Before you begin, ensure you have:

- [ ] Python 3.9 or higher installed
- [ ] Git installed
- [ ] Anthropic API account (free tier)
- [ ] Text editor or IDE
- [ ] Terminal/command line access

## Step-by-Step Setup

### 1. Get Anthropic API Key (Free)

1. Go to https://console.anthropic.com/
2. Sign up for a free account
3. Navigate to API Keys section
4. Click "Create Key"
5. Copy your API key (starts with `sk-ant-api03-...`)

**Note**: Free tier includes generous usage limits suitable for this assignment.

### 2. Clone or Download Repository

```bash
# If using git
git clone <repository-url>
cd clara-automation-pipeline

# Or download and extract ZIP, then:
cd clara-automation-pipeline
```

### 3. Install Python Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file and add your API key
nano .env
# or use your preferred editor
```

Add your Anthropic API key:
```
ANTHROPIC_API_KEY=sk-ant-api03-YOUR_KEY_HERE
STORAGE_PATH=./outputs
LOG_LEVEL=INFO
```

### 5. Make Scripts Executable (macOS/Linux)

```bash
chmod +x scripts/*.py
```

### 6. Verify Installation

```bash
# Test that Python can import required modules
python -c "import anthropic; print('✓ Anthropic SDK installed')"
python -c "from dotenv import load_dotenv; print('✓ python-dotenv installed')"
python -c "import yaml; print('✓ PyYAML installed')"

# Verify API key is loaded
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('✓ API key loaded' if os.getenv('ANTHROPIC_API_KEY') else '✗ API key not found')"
```

You should see:
```
✓ Anthropic SDK installed
✓ python-dotenv installed
✓ PyYAML installed
✓ API key loaded
```

## Quick Start - Process Sample Data

The repository includes sample demo and onboarding calls for Acme Fire Protection.

### Run Pipeline A (Demo → v1)

```bash
python scripts/pipeline_a_demo.py \
  --input sample_data/demo_call_1_acme.txt \
  --account-id ACC001
```

**Expected output**:
- `outputs/accounts/ACC001_acme_fire_protection/v1/account_memo.json`
- `outputs/accounts/ACC001_acme_fire_protection/v1/agent_spec.json`
- `outputs/accounts/ACC001_acme_fire_protection/v1/extraction_log.json`

### Run Pipeline B (Onboarding → v2)

```bash
python scripts/pipeline_b_onboarding.py \
  --input sample_data/onboarding_call_1_acme.txt \
  --account-id ACC001
```

**Expected output**:
- `outputs/accounts/ACC001_acme_fire_protection/v2/account_memo.json`
- `outputs/accounts/ACC001_acme_fire_protection/v2/agent_spec.json`
- `outputs/accounts/ACC001_acme_fire_protection/changelog.json`

### Compare Versions

```bash
python scripts/compare_versions.py --account-id ACC001 --detailed
```

## Processing Your Own Data

### Prepare Your Transcripts

1. Create transcripts in plain text format (.txt or .md)
2. Organize into directories:
   ```
   my_data/
   ├── demo_calls/
   │   ├── company1_demo.txt
   │   ├── company2_demo.txt
   │   └── company3_demo.txt
   └── onboarding_calls/
       ├── company1_onboarding.txt
       ├── company2_onboarding.txt
       └── company3_onboarding.txt
   ```

### Batch Process Demo Calls

```bash
python scripts/batch_process.py \
  --mode demo \
  --input-dir my_data/demo_calls/ \
  --account-prefix ACC
```

This will:
- Process all `.txt` and `.md` files in the directory
- Auto-generate account IDs: ACC001, ACC002, ACC003, etc.
- Create v1 account memos and agent specs for each
- Generate a batch processing report

### Batch Process Onboarding Calls

**Option 1: Auto-matching by filename**

Name your files: `onboarding_ACC001.txt`, `onboarding_ACC002.txt`, etc.

```bash
python scripts/batch_process.py \
  --mode onboarding \
  --input-dir my_data/onboarding_calls/
```

**Option 2: Custom mapping file**

Create `mapping.json`:
```json
{
  "company1_onboarding.txt": "ACC001",
  "company2_onboarding.txt": "ACC002",
  "company3_onboarding.txt": "ACC003"
}
```

Then run:
```bash
python scripts/batch_process.py \
  --mode onboarding \
  --input-dir my_data/onboarding_calls/ \
  --mapping-file mapping.json
```

## Understanding the Output

### Account Memo Structure

The account memo is the structured representation of the business requirements:

```
account_memo.json
├── account_id: Unique identifier
├── version: "v1" or "v2"
├── company_name: Business name
├── business_hours: Operating hours with timezone
├── services_supported: List of services
├── emergency_definition: What counts as emergency
├── emergency_routing_rules: Who to call for emergencies
├── non_emergency_routing_rules: Regular call handling
├── call_transfer_rules: Timeouts and retry logic
├── integration_constraints: System limitations (e.g., ServiceTrade)
├── questions_or_unknowns: Missing information flagged
└── notes: Additional context
```

### Agent Spec Structure

The agent spec is ready-to-use Retell configuration:

```
agent_spec.json
├── agent_name: Display name for the agent
├── version: "v1" or "v2"
├── voice_config: Voice settings
├── system_prompt: Complete conversational AI prompt
├── variables: Key data for templating
├── conversation_config: Call behavior settings
├── tool_placeholders: Transfer and integration hooks
└── fallback_protocol: What to do when things fail
```

### Changelog Structure

The changelog tracks every change from v1 to v2:

```
changelog.json
└── changes: Array of change events
    └── [0]: Latest change
        ├── timestamp: When the change was made
        ├── from_version: "v1"
        ├── to_version: "v2"
        ├── change_type: "onboarding_update"
        ├── modifications: Array of field changes
        │   └── [0]:
        │       ├── field: "business_hours.schedule"
        │       ├── action: "updated" | "added" | "removed"
        │       ├── old_value: Previous value
        │       ├── new_value: New value
        │       └── reason: Why it changed
        └── summary: Human-readable summary
```

## Importing to Retell (Manual Process)

Since we're using free tier, agent creation may be manual:

### 1. Log into Retell Dashboard

Go to your Retell account at https://app.retellai.com/

### 2. Create New Agent

1. Click "Agents" → "Create Agent"
2. Give it a name (use the `agent_name` from agent_spec.json)

### 3. Configure System Prompt

1. Open `outputs/accounts/ACC001_.../v2/agent_spec.json`
2. Copy the entire `system_prompt` field
3. Paste into Retell's "System Prompt" text area

### 4. Configure Voice Settings

From `voice_config` in agent_spec.json:
- Voice Provider: Eleven Labs (or as specified)
- Voice ID: professional_female (or as specified)
- Speed: 1.0
- Stability: 0.8

### 5. Set Transfer Numbers

From `variables` and routing rules:
- Add transfer destinations
- Set timeout values
- Configure fallback behavior

### 6. Test the Agent

Use Retell's test interface to make a sample call and verify behavior.

## Troubleshooting

### API Rate Limits

If you hit rate limits:
1. The scripts have 1-second delays between API calls
2. For batch processing, process in smaller chunks
3. Free tier typically allows 50 requests/minute

### Missing Data in Outputs

If account memos have many `questions_or_unknowns`:
1. This is expected for demo calls (v1)
2. Review the transcript - was the information actually mentioned?
3. Onboarding calls (v2) should resolve most unknowns

### JSON Parse Errors

If extraction fails with JSON errors:
1. Check the extraction_log.json for details
2. The API response may have markdown formatting
3. Scripts automatically handle ```json``` wrapping

### File Not Found Errors

For Pipeline B:
1. Ensure Pipeline A ran successfully first
2. Check that account_id matches exactly
3. Verify the outputs/accounts/ directory exists

### Permission Errors (macOS/Linux)

```bash
# Make scripts executable
chmod +x scripts/*.py

# Or run with python explicitly
python scripts/pipeline_a_demo.py ...
```

## Advanced Usage

### Custom Account IDs

Use meaningful prefixes:
```bash
python scripts/pipeline_a_demo.py \
  --input demo.txt \
  --account-id FIRE001
```

### Force Overwrite v2

```bash
python scripts/pipeline_b_onboarding.py \
  --input onboarding.txt \
  --account-id ACC001 \
  --force
```

### Custom Storage Path

Edit `.env`:
```
STORAGE_PATH=/path/to/custom/output
```

## Next Steps

After setup:

1. **Process the 5 demo + 5 onboarding dataset** provided
2. **Review outputs** in `outputs/accounts/`
3. **Generate comparison reports** for each account
4. **Create submission video** showing the pipeline in action
5. **Document any edge cases** or interesting findings

## Getting Help

- Review README.md for architecture overview
- Check script docstrings: `python scripts/pipeline_a_demo.py --help`
- Examine sample outputs in `outputs/examples/` (if provided)
- Review extraction_log.json files for debugging

## Production Considerations

For production deployment, consider:

1. **Database**: Migrate from JSON to PostgreSQL/Supabase
2. **API Integration**: Use Retell API directly (if available)
3. **Monitoring**: Add logging and error alerting
4. **Testing**: Create test suites for extraction accuracy
5. **UI**: Build web dashboard for non-technical users
6. **Webhooks**: Auto-trigger on new call recordings
7. **Version Control**: Implement proper git workflow
