# Architecture & Design Decisions

## System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Clara Automation Pipeline                 │
└─────────────────────────────────────────────────────────────┘

┌────────────────┐         ┌────────────────────────────────┐
│  Input Layer   │         │     Processing Layer           │
├────────────────┤         ├────────────────────────────────┤
│ - Demo Calls   │────────>│  Extraction Engine             │
│ - Onboarding   │         │  (Claude API)                  │
│ - Transcripts  │         │                                │
└────────────────┘         │  - Demo Parser                 │
                           │  - Onboarding Parser           │
                           │  - Data Validation             │
                           └───────────┬────────────────────┘
                                       │
                                       v
                           ┌────────────────────────────────┐
                           │    Transformation Layer        │
                           ├────────────────────────────────┤
                           │  Prompt Generator              │
                           │  - Business Hours Flow         │
                           │  - After-Hours Flow            │
                           │  - Transfer Protocol           │
                           │  - Fallback Protocol           │
                           └───────────┬────────────────────┘
                                       │
                                       v
                           ┌────────────────────────────────┐
                           │     Storage Layer              │
                           ├────────────────────────────────┤
                           │  - Account Memos (JSON)        │
                           │  - Agent Specs (JSON)          │
                           │  - Changelogs (JSON)           │
                           │  - Extraction Logs             │
                           └───────────┬────────────────────┘
                                       │
                                       v
                           ┌────────────────────────────────┐
                           │      Output Layer              │
                           ├────────────────────────────────┤
                           │  - Retell Agent Configs        │
                           │  - Batch Reports               │
                           │  - Validation Reports          │
                           └────────────────────────────────┘
```

## Core Design Principles

### 1. Separation of Concerns

**Why**: Modularity enables testing, debugging, and reuse

**Implementation**:
- `extraction_engine.py`: Pure extraction logic, no I/O
- `prompt_generator.py`: Pure transformation, no API calls
- `pipeline_*.py`: Orchestration only, delegates to modules

**Benefit**: Can swap out Claude API for another LLM without touching prompt generation

### 2. Explicit Over Implicit

**Why**: Assignment emphasizes handling ambiguity and missing data

**Implementation**:
- `questions_or_unknowns` field explicitly lists gaps
- No default values or assumptions
- Clear distinction between empty ("") and unknown (null)

**Example**:
```json
{
  "business_hours": {
    "timezone": "",  // Not mentioned in demo
    "schedule": []   // Not provided
  },
  "questions_or_unknowns": [
    "Exact business hours not specified",
    "Timezone not confirmed"
  ]
}
```

### 3. Version Control as First-Class Concept

**Why**: Assignment requires v1 → v2 tracking with clear diffs

**Implementation**:
- Separate v1/ and v2/ directories
- Immutable v1 (never modified)
- Changelog generated algorithmically by comparing JSON

**Benefit**: Can roll back, audit changes, understand evolution

### 4. Fail-Fast Validation

**Why**: Better to catch errors early than propagate bad data

**Implementation**:
- Schema validation at each step
- `validate_outputs.py` checks structure before Retell import
- Extraction logs capture API responses for debugging

### 5. Idempotency

**Why**: Re-running should be safe and predictable

**Implementation**:
- Pipeline B prompts before overwriting v2
- Batch processing skips already-processed files (optional)
- Account IDs prevent collision

## Key Design Decisions

### Decision 1: JSON vs Database

**Choice**: Local JSON files

**Rationale**:
- Zero-cost constraint
- Simple setup (no database server)
- Human-readable outputs
- Git-friendly for version control
- Sufficient for 10-file dataset

**Production Alternative**: PostgreSQL/Supabase for scale

### Decision 2: Synchronous vs Async Processing

**Choice**: Synchronous with rate limit delays

**Rationale**:
- Simpler code (no async/await complexity)
- Easier debugging
- Free tier has generous rate limits
- 1-second delays prevent hitting limits

**Production Alternative**: Async with queue (Celery/RQ)

### Decision 3: Structured Prompts vs Fine-Tuning

**Choice**: Structured prompts with explicit JSON schema

**Rationale**:
- Zero-cost (fine-tuning requires paid API)
- Immediate results (no training time)
- Easy to iterate and debug
- Claude Sonnet 4 is excellent at instruction following

**Production Alternative**: Fine-tuned model for consistency

### Decision 4: Python Scripts vs Web API

**Choice**: CLI scripts with optional n8n orchestration

**Rationale**:
- Zero infrastructure cost
- Easy to test and debug locally
- Can be wrapped in API later
- Meets assignment requirement for automation

**Production Alternative**: FastAPI service with webhooks

### Decision 5: No LLM Hallucination Mitigation

**Choice**: Prompt engineering only, no verification layer

**Rationale**:
- Temperature = 0.0 for determinism
- Explicit instructions: "Extract ONLY explicitly stated information"
- `questions_or_unknowns` field for missing data

**Production Alternative**: Dual-LLM verification or human-in-the-loop

## Data Model

### Account Memo Schema

**Philosophy**: Comprehensive but flexible

```
Account Memo
├── Identity
│   ├── account_id: Unique identifier
│   ├── company_name: Business name
│   └── business_type: Industry category
│
├── Operations
│   ├── business_hours: Schedule + timezone
│   ├── office_address: Physical location
│   └── services_supported: What they do
│
├── Routing Logic
│   ├── emergency_definition: Triggers
│   ├── emergency_routing_rules: Who to call
│   ├── non_emergency_routing_rules: Regular routing
│   └── call_transfer_rules: Timeouts, retries
│
├── Constraints
│   ├── integration_constraints: System limits
│   └── special_rules: Edge cases
│
├── Metadata
│   ├── questions_or_unknowns: Gaps
│   ├── notes: Context
│   ├── created_at: Timestamp
│   └── updated_at: Timestamp
│
└── Internal
    └── _extraction_metadata: API call info
```

### Agent Spec Schema

**Philosophy**: Retell-compatible + extensible

```
Agent Spec
├── Identity
│   ├── agent_name: Display name
│   └── version: v1 or v2
│
├── Voice Configuration
│   ├── provider: TTS service
│   ├── voice_id: Voice selection
│   ├── speed: Talking speed
│   └── stability: Voice consistency
│
├── Conversation
│   ├── system_prompt: Full AI instructions
│   ├── variables: Template data
│   └── conversation_config: Behavior settings
│
├── Integration
│   ├── tool_placeholders: Function hooks
│   ├── transfer_protocol: How to transfer
│   └── fallback_protocol: When transfer fails
│
└── Metadata
    ├── created_at: Timestamp
    └── updated_at: Timestamp
```

## Prompt Engineering Strategy

### System Prompt Structure

**Philosophy**: Hierarchical with clear sections

1. **Role Definition**: Who Clara is
2. **Context**: Business info and services
3. **Conversation Flows**: Step-by-step scripts
4. **Rules**: Non-negotiable constraints
5. **Edge Cases**: How to handle exceptions
6. **Tone & Style**: Personality guidelines

### Extraction Prompt Strategy

**Philosophy**: Constrained generation with schema

```
[Context about Clara and the business]

CRITICAL RULES:
1. Extract ONLY explicitly stated information
2. Do NOT invent or assume missing details
3. Flag gaps in questions_or_unknowns

TRANSCRIPT:
[Full transcript]

Extract the following and respond ONLY with valid JSON:

{
  "account_id": "...",
  "company_name": "",
  ...
}

EXTRACTION GUIDELINES:
- company_name: Exact name mentioned
- business_hours: Only if explicitly stated
...
```

**Key Techniques**:
- Temperature 0 for consistency
- JSON-only output (no markdown)
- Explicit schema with field descriptions
- Examples of what NOT to do

## Error Handling Strategy

### Levels of Error Handling

1. **API Errors**: Retry with exponential backoff
2. **JSON Parse Errors**: Strip markdown, retry parse
3. **Schema Validation Errors**: Log and flag for manual review
4. **File Not Found**: Clear error message with suggestion
5. **Missing v1**: Instruct to run Pipeline A first

### Logging Strategy

**Philosophy**: Structured logs for debugging

```python
{
  "pipeline": "A" or "B",
  "stage": "demo_call" or "onboarding_update",
  "account_id": "ACC001",
  "timestamp": "ISO 8601",
  "status": "success" or "error",
  "extraction_metadata": {
    "model": "claude-sonnet-4-20250514",
    "transcript_length": 5000,
    "api_response_time": 2.5
  },
  "errors": []
}
```

## Testing Strategy

### Manual Testing

**What**: Run on sample data and verify outputs

```bash
# Happy path
python scripts/pipeline_a_demo.py --input sample_data/demo_call_1_acme.txt --account-id ACC001
python scripts/pipeline_b_onboarding.py --input sample_data/onboarding_call_1_acme.txt --account-id ACC001
python scripts/compare_versions.py --account-id ACC001

# Validation
python scripts/validate_outputs.py --account-id ACC001
```

### Schema Validation Testing

**What**: Ensure outputs match expected structure

```bash
python scripts/validate_outputs.py
```

Checks:
- Required fields present
- Types correct (list vs dict vs string)
- No prompt hygiene violations
- Reasonable value ranges

### Edge Case Testing

**Scenarios**:
1. Empty transcript → Should fail gracefully
2. Transcript with no business info → Many unknowns
3. Conflicting info in onboarding → Onboarding wins
4. Missing v1 for Pipeline B → Clear error message

## Performance Considerations

### API Rate Limits

**Claude Free Tier**:
- ~50 requests/minute
- ~1000 requests/day

**Mitigation**:
- 1-second delay between requests
- Batch processing in chunks
- Retry with exponential backoff

### Memory Usage

**Current**: Minimal (single transcript at a time)

**Scale**: For 100+ calls, consider:
- Streaming JSON writes
- Chunked batch processing
- Database instead of file I/O

### Processing Time

**Single Call**: ~3-5 seconds
- 2s API call
- 1s JSON processing
- 1s file I/O

**Batch (10 calls)**: ~40-50 seconds
- Serial processing
- Rate limit delays

**Optimization**: Parallel processing (with rate limit management)

## Production Roadmap

If this were production, next steps:

### Phase 1: MVP Enhancements
- [ ] Web UI for non-technical users
- [ ] Retell API integration (if available)
- [ ] Email notifications on completion
- [ ] PostgreSQL storage

### Phase 2: Reliability
- [ ] Error monitoring (Sentry)
- [ ] Automated testing suite
- [ ] CI/CD pipeline
- [ ] Backup and recovery

### Phase 3: Scale
- [ ] Async processing queue
- [ ] Webhook integrations
- [ ] Multi-tenant support
- [ ] Analytics dashboard

### Phase 4: Intelligence
- [ ] Active learning from corrections
- [ ] Confidence scores
- [ ] Suggested improvements
- [ ] A/B testing for prompts

## Conclusion

This architecture prioritizes:
1. **Simplicity**: Easy to understand and run
2. **Reliability**: Handles errors gracefully
3. **Traceability**: Every change is logged
4. **Cost**: Completely free
5. **Extensibility**: Easy to enhance

The design choices align with the assignment goals: demonstrate systems thinking, handle ambiguity, and build production-ready automation on zero budget.
