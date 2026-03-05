# Clara Answers - Zero-Cost Automation Pipeline

**Demo Call → Retell Agent Draft → Onboarding Updates → Agent Revision**

## Overview

This automation pipeline converts customer demo and onboarding calls into production-ready Retell AI agent configurations. It handles the full lifecycle from initial discovery to operational precision.

### What This Does

1. **Pipeline A (Demo → v1 Agent)**: Processes demo call transcripts to generate preliminary agent configurations
2. **Pipeline B (Onboarding → v2 Agent)**: Updates agents with operational details from onboarding calls
3. **Version Control**: Maintains clean v1→v2 transitions with detailed changelogs
4. **Zero Cost**: Uses only free-tier services and APIs

## Architecture

```
┌─────────────────┐
│  Demo Call      │
│  Transcript     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│  Extraction Engine      │
│  (Claude API - Free)    │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Account Memo (v1)      │
│  + Agent Spec (v1)      │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Storage (JSON/SQLite)  │
└────────┬────────────────┘
         │
         ▼
┌─────────────────┐
│  Onboarding     │
│  Call/Form      │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│  Update Engine          │
│  (Merge + Diff)         │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Account Memo (v2)      │
│  + Agent Spec (v2)      │
│  + Changelog            │
└─────────────────────────┘
```

## Data Flow

1. **Input**: Audio/transcript files in `/sample_data`
2. **Processing**: Python scripts extract structured data using Claude API
3. **Storage**: Outputs saved to `/outputs/accounts/<account_id>/`
4. **Versioning**: v1 (demo), v2 (onboarding) with diff tracking

## Tech Stack (All Free Tier)

- **LLM**: Anthropic Claude API (free tier)
- **Orchestration**: Python scripts + n8n (self-hosted)
- **Storage**: Local JSON files + SQLite
- **Transcription**: Accepts pre-transcribed text (no cost)
- **Version Control**: Git + custom diff engine

## Quick Start

### Prerequisites

- Python 3.9+
- Docker (for n8n, optional)
- Anthropic API key (free tier)
- Git

### Installation

```bash
# Clone repository
git clone <your-repo-url>
cd clara-automation-pipeline

# Install Python dependencies
pip install anthropic python-dotenv pyyaml

# Set up environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Make scripts executable
chmod +x scripts/*.py
```

### Environment Variables

Create `.env` file:

```env
ANTHROPIC_API_KEY=your_key_here
STORAGE_PATH=./outputs
LOG_LEVEL=INFO
```

### Running Pipeline A (Demo → v1 Agent)

```bash
# Single demo call
python scripts/pipeline_a_demo.py --input sample_data/demo_call_1.txt --account-id ACC001

# Batch process all demo calls
python scripts/batch_process.py --mode demo --input-dir sample_data/demo_calls/
```

### Running Pipeline B (Onboarding → v2 Agent)

```bash
# Single onboarding call
python scripts/pipeline_b_onboarding.py --input sample_data/onboarding_1.txt --account-id ACC001

# Batch process all onboarding calls
python scripts/batch_process.py --mode onboarding --input-dir sample_data/onboarding_calls/
```

## Output Structure

```
outputs/
└── accounts/
    └── ACC001_acme_sprinkler/
        ├── v1/
        │   ├── account_memo.json
        │   ├── agent_spec.json
        │   └── extraction_log.json
        ├── v2/
        │   ├── account_memo.json
        │   ├── agent_spec.json
        │   └── extraction_log.json
        └── changelog.json
```

## Schema Documentation

### Account Memo JSON

```json
{
  "account_id": "ACC001",
  "version": "v1",
  "company_name": "Acme Sprinkler Services",
  "business_hours": {
    "timezone": "America/New_York",
    "schedule": [
      {"day": "Monday", "open": "08:00", "close": "17:00"},
      {"day": "Tuesday", "open": "08:00", "close": "17:00"}
    ]
  },
  "office_address": {
    "street": "123 Main St",
    "city": "Boston",
    "state": "MA",
    "zip": "02101"
  },
  "services_supported": ["sprinkler_repair", "alarm_installation"],
  "emergency_definition": ["sprinkler_leak", "fire_alarm_triggered"],
  "emergency_routing_rules": {
    "primary": {"name": "On-call tech", "phone": "+1-555-0100"},
    "fallback": {"action": "take_message", "notify": "dispatch@acme.com"}
  },
  "non_emergency_routing_rules": {
    "during_hours": {"action": "transfer", "destination": "main_office"},
    "after_hours": {"action": "collect_details"}
  },
  "call_transfer_rules": {
    "timeout_seconds": 60,
    "max_retries": 2,
    "failure_message": "I apologize, I'm unable to reach anyone right now..."
  },
  "integration_constraints": [
    "Never create sprinkler jobs in ServiceTrade",
    "All emergency calls must go to phone tree"
  ],
  "after_hours_flow_summary": "Greet → Identify emergency → Collect details → Transfer or message",
  "office_hours_flow_summary": "Greet → Purpose → Collect info → Transfer → Confirm",
  "questions_or_unknowns": [
    "Exact after-hours phone number not specified",
    "ServiceTrade integration details unclear"
  ],
  "notes": "Client emphasized quick response for emergencies",
  "created_at": "2025-03-04T10:30:00Z",
  "updated_at": "2025-03-04T10:30:00Z"
}
```

### Retell Agent Spec JSON

```json
{
  "agent_name": "Clara - Acme Sprinkler Services",
  "version": "v1",
  "voice_config": {
    "provider": "eleven_labs",
    "voice_id": "professional_female",
    "speed": 1.0,
    "stability": 0.8
  },
  "system_prompt": "...(generated prompt)...",
  "variables": {
    "company_name": "Acme Sprinkler Services",
    "timezone": "America/New_York",
    "business_hours": "Monday-Friday 8am-5pm",
    "emergency_phone": "+1-555-0100"
  },
  "conversation_config": {
    "max_duration_minutes": 10,
    "interruption_sensitivity": "medium",
    "end_call_phrases": ["goodbye", "that's all", "nothing else"]
  },
  "tool_placeholders": {
    "transfer_call": {"enabled": true, "timeout": 60},
    "create_ticket": {"enabled": false}
  },
  "fallback_protocol": "If transfer fails after 60 seconds, apologize and assure callback within 30 minutes",
  "created_at": "2025-03-04T10:30:00Z"
}
```

### Changelog Format

```json
{
  "account_id": "ACC001",
  "changes": [
    {
      "timestamp": "2025-03-04T14:20:00Z",
      "from_version": "v1",
      "to_version": "v2",
      "change_type": "onboarding_update",
      "modifications": [
        {
          "field": "business_hours.schedule",
          "action": "updated",
          "old_value": "...",
          "new_value": "...",
          "reason": "Confirmed exact hours during onboarding"
        },
        {
          "field": "emergency_routing_rules.primary.phone",
          "action": "updated",
          "old_value": null,
          "new_value": "+1-555-9999",
          "reason": "Emergency contact number provided"
        }
      ],
      "summary": "Added confirmed business hours and emergency routing"
    }
  ]
}
```

## Prompt Template Guidelines

All generated agent prompts follow this structure:

### Business Hours Flow
1. Greeting with company name
2. Ask purpose of call
3. Collect caller name and phone number
4. Route or transfer based on inquiry
5. Fallback protocol if transfer fails
6. "Is there anything else I can help you with?"
7. Close call professionally

### After-Hours Flow
1. Greeting with company name
2. Ask purpose of call
3. **Immediately confirm if emergency**
4. If emergency: collect name, number, address
5. Attempt transfer to on-call
6. If transfer fails: apologize, assure quick follow-up
7. If non-emergency: collect details, confirm next-day callback
8. "Is there anything else?"
9. Close call

### Prompt Hygiene Rules
- Never mention "function calls" or technical operations to caller
- Keep questions minimal - only collect what's needed for routing
- Clear transfer protocol with timeout handling
- Empathetic fallback language when transfer fails
- Natural conversation flow, not robotic

## n8n Workflow (Optional)

If you want to use n8n for orchestration:

```bash
# Start n8n with Docker
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  n8nio/n8n

# Import workflow
# 1. Open http://localhost:5678
# 2. Go to Workflows → Import from File
# 3. Select workflows/clara_pipeline.json
```

The n8n workflow includes:
- File trigger for new transcripts
- Python script execution nodes
- Error handling and logging
- Output file management

## Testing

```bash
# Run test suite
python scripts/test_pipeline.py

# Validate output schemas
python scripts/validate_outputs.py --account-id ACC001

# Generate test report
python scripts/generate_report.py --input-dir outputs/accounts/
```

## Retell Integration

### Manual Import (Free Tier)

Since Retell free tier may not support API agent creation:

1. Log into Retell dashboard
2. Navigate to Agents → Create New Agent
3. Copy content from `outputs/accounts/<account_id>/v2/agent_spec.json`
4. Paste system prompt into Retell's prompt field
5. Configure voice settings from `voice_config`
6. Set up transfer numbers from routing rules
7. Save and test

### API Integration (If Available)

```python
# If Retell API is accessible on free tier
import os
from retell import RetellClient

client = RetellClient(api_key=os.getenv('RETELL_API_KEY'))

# Load agent spec
with open('outputs/accounts/ACC001/v2/agent_spec.json') as f:
    spec = json.load(f)

# Create or update agent
agent = client.agents.create(
    agent_name=spec['agent_name'],
    system_prompt=spec['system_prompt'],
    voice_id=spec['voice_config']['voice_id']
)
```

## Known Limitations

1. **Transcription**: Requires pre-transcribed text. For audio files, use:
   - Whisper (local, free): `whisper audio.mp3 --model base`
   - AssemblyAI (free tier): 5 hours/month
   - Google Speech-to-Text (free tier): 60 minutes/month

2. **LLM Usage**: Uses Claude API free tier. Rate limits:
   - ~50 requests/min
   - Monitor usage in Anthropic console

3. **Storage**: Local JSON files. For production:
   - Migrate to Supabase (free tier: 500MB)
   - Or Airtable (free tier: 1,200 records)

4. **No UI**: Command-line only. Bonus: simple web dashboard available

## Production Improvements

With production access, I would add:

1. **Real-time transcription** via Deepgram/AssemblyAI webhooks
2. **Retell API integration** for automatic agent deployment
3. **Database** (Supabase/PostgreSQL) with proper indexing
4. **Monitoring** with error alerting and usage dashboards
5. **Web UI** for reviewing and editing agent configs
6. **Automated testing** with synthetic call scenarios
7. **A/B testing** framework for prompt variations
8. **Integration with Asana/Linear** for task tracking

## Troubleshooting

### "API Key Invalid"
- Check `.env` file has correct `ANTHROPIC_API_KEY`
- Verify key at console.anthropic.com

### "No outputs generated"
- Check input file paths are correct
- Verify transcript format (plain text)
- Check logs in `outputs/accounts/<account_id>/v1/extraction_log.json`

### "Version conflict"
- Run with `--force` flag to overwrite
- Or manually delete `outputs/accounts/<account_id>/v2/`

### "Schema validation failed"
- Check JSON syntax in account memo
- Run `python scripts/validate_outputs.py` for details

## Contributing

This is an intern assignment submission. For questions:
- Review architecture diagram
- Check script docstrings
- See example outputs in `/outputs/examples/`

## License

MIT License - Educational/Assignment Use

---

**Assignment Completed By**: [Your Name]  
**Submission Date**: March 4, 2026  
**Demo Video**: [Loom link here]
