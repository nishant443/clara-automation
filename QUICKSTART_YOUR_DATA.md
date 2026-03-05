# Quick Start Guide - Your Data

You have:
- ✅ Demo call **transcript** (text file)
- 🎵 Onboarding call **audio** (needs transcription)

## Step-by-Step Workflow

### Step 1: Process Demo Call (Already Have Transcript)

Since you already have the demo call transcript as text, you can skip transcription and go straight to Pipeline A:

```bash
# Save your demo transcript as a .txt file
# Example: demo_bens_electric.txt

# Run Pipeline A
python scripts/pipeline_a_demo.py \
  --input demo_bens_electric.txt \
  --account-id BEN001
```

**Output**: 
- `outputs/accounts/BEN001_bens_electric_solutions/v1/account_memo.json`
- `outputs/accounts/BEN001_bens_electric_solutions/v1/agent_spec.json`

### Step 2: Transcribe Onboarding Audio

Since you have the onboarding call as audio, transcribe it first:

```bash
# Install Whisper (one-time setup)
pip install openai-whisper
brew install ffmpeg  # or sudo apt install ffmpeg on Linux

# Transcribe your onboarding audio
python scripts/transcribe_audio.py \
  --input onboarding_bens_electric.mp3 \
  --output-dir transcripts/ \
  --model base
```

**Output**: `transcripts/onboarding_bens_electric_transcript.txt`

### Step 3: Process Onboarding Call

Now run Pipeline B with the generated transcript:

```bash
python scripts/pipeline_b_onboarding.py \
  --input transcripts/onboarding_bens_electric_transcript.txt \
  --account-id BEN001
```

**Output**:
- `outputs/accounts/BEN001_bens_electric_solutions/v2/account_memo.json`
- `outputs/accounts/BEN001_bens_electric_solutions/v2/agent_spec.json`
- `outputs/accounts/BEN001_bens_electric_solutions/changelog.json`

### Step 4: Compare Versions

```bash
python scripts/compare_versions.py --account-id BEN001 --detailed
```

### Step 5: Validate Everything

```bash
python scripts/validate_outputs.py --account-id BEN001
```

## Complete Example

```bash
# 1. Process demo (you already have transcript)
python scripts/pipeline_a_demo.py \
  --input demo_bens_electric.txt \
  --account-id BEN001

# 2. Transcribe onboarding audio
python scripts/transcribe_audio.py \
  --input onboarding_bens_electric.mp3 \
  --output-dir transcripts/

# 3. Process onboarding transcript
python scripts/pipeline_b_onboarding.py \
  --input transcripts/onboarding_bens_electric_transcript.txt \
  --account-id BEN001

# 4. Review changes
python scripts/compare_versions.py --account-id BEN001
```

## If You Have Multiple Accounts

### All Demo Calls as Text
```bash
# Put all demo transcripts in a folder
mkdir sample_data/demo_calls/
# Copy your .txt files there

# Batch process
python scripts/batch_process.py \
  --mode demo \
  --input-dir sample_data/demo_calls/
```

### All Onboarding Calls as Audio
```bash
# Put all audio files in a folder
mkdir audio/onboarding_calls/

# Step 1: Batch transcribe all audio
python scripts/transcribe_audio.py \
  --input audio/onboarding_calls/ \
  --output-dir transcripts/onboarding_calls/ \
  --batch

# Step 2: Batch process transcripts
python scripts/batch_process.py \
  --mode onboarding \
  --input-dir transcripts/onboarding_calls/
```

## Tips for Your Data

### Demo Call Transcript
Your demo call transcript looks like it has:
- Company: Ben's Electric Solutions
- Owner: Ben Penoyer
- Services: Residential/commercial electrical, EV chargers, hot tubs, etc.
- Current system: Jobber CRM
- Pain points: Handling calls, especially after hours

**This is perfect for Pipeline A!** It will extract all this structured data.

### Onboarding Audio
Your onboarding call likely has:
- Exact business hours
- Emergency contact numbers
- Specific routing rules
- Integration details with Jobber
- Special constraints

**After transcription, Pipeline B will merge this with v1!**

## Troubleshooting

### "Whisper is slow"
Try the `tiny` model for faster transcription:
```bash
python scripts/transcribe_audio.py \
  --input audio.mp3 \
  --output-dir transcripts/ \
  --model tiny
```

### "Audio file too large"
Compress it first or split into chunks, then transcribe separately.

### "Need better transcription quality"
Use the `medium` or `large` model:
```bash
python scripts/transcribe_audio.py \
  --input audio.mp3 \
  --output-dir transcripts/ \
  --model medium
```

## Expected Timeline

| Step | Time |
|------|------|
| Demo processing | ~5 seconds |
| Audio transcription (base model) | ~2-5 minutes per 30min audio |
| Onboarding processing | ~5 seconds |
| Total | ~5-10 minutes for one account |

## Next Steps

After processing your data:

1. **Review outputs** in `outputs/accounts/BEN001.../`
2. **Check the changelog** to see what changed from v1 to v2
3. **Validate everything** with the validation script
4. **Import to Retell** using the v2 agent_spec.json

---

**You're all set! The pipeline handles your mixed input types (text + audio) seamlessly.**
