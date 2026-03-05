# Audio Transcription Guide

## Overview

The Clara pipeline accepts **text transcripts** as input. If you have audio files (MP3, WAV, etc.), you need to transcribe them to text first.

## Option 1: Use Provided Transcripts (Zero Cost)

If the assignment provides transcripts, use them directly:

```bash
python scripts/pipeline_a_demo.py \
  --input transcripts/demo_call_1.txt \
  --account-id ACC001
```

**Cost**: $0.00 ✓

## Option 2: Transcribe Audio with Whisper (Zero Cost, Local)

If you have audio files, use OpenAI's Whisper model (runs locally, completely free):

### Setup

```bash
# Install Whisper
pip install openai-whisper

# Install ffmpeg (required by Whisper)
# macOS:
brew install ffmpeg

# Ubuntu/Debian:
sudo apt install ffmpeg

# Windows:
# Download from https://ffmpeg.org/download.html
```

### Transcribe Single Audio File

```bash
python scripts/transcribe_audio.py \
  --input audio/demo_call_1.mp3 \
  --output-dir transcripts/ \
  --model base
```

**Output**: `transcripts/demo_call_1_transcript.txt`

### Batch Transcribe Multiple Files

```bash
python scripts/transcribe_audio.py \
  --input audio/ \
  --output-dir transcripts/ \
  --batch \
  --model base
```

### Model Options

| Model | Speed | Accuracy | Size | Use Case |
|-------|-------|----------|------|----------|
| `tiny` | Fastest | Good | 39 MB | Quick testing |
| `base` | Fast | Better | 74 MB | **Recommended** |
| `small` | Medium | Great | 244 MB | High quality |
| `medium` | Slow | Excellent | 769 MB | Best quality |
| `large` | Very Slow | Best | 1550 MB | Maximum accuracy |

**Recommendation**: Use `base` for good balance of speed and accuracy.

### Complete Workflow with Audio

```bash
# Step 1: Transcribe audio files
python scripts/transcribe_audio.py \
  --input audio/demo_calls/ \
  --output-dir transcripts/demo_calls/ \
  --batch \
  --model base

# Step 2: Process transcripts through Clara pipeline
python scripts/batch_process.py \
  --mode demo \
  --input-dir transcripts/demo_calls/

# Step 3: Transcribe onboarding audio
python scripts/transcribe_audio.py \
  --input audio/onboarding_calls/ \
  --output-dir transcripts/onboarding_calls/ \
  --batch \
  --model base

# Step 4: Process onboarding transcripts
python scripts/batch_process.py \
  --mode onboarding \
  --input-dir transcripts/onboarding_calls/
```

## Option 3: Cloud Transcription (Free Tier)

If Whisper is too complex, use cloud services with free tiers:

### AssemblyAI (5 hours free/month)

```python
import assemblyai as aai

aai.settings.api_key = "your_free_api_key"
transcriber = aai.Transcriber()
transcript = transcriber.transcribe("demo_call.mp3")

with open("demo_call_transcript.txt", "w") as f:
    f.write(transcript.text)
```

### Google Speech-to-Text (60 minutes free/month)

```python
from google.cloud import speech

client = speech.SpeechClient()

with open("demo_call.mp3", "rb") as f:
    audio = speech.RecognitionAudio(content=f.read())

config = speech.RecognitionConfig(
    encoding=speech.RecognitionConfig.AudioEncoding.MP3,
    language_code="en-US",
)

response = client.recognize(config=config, audio=audio)

with open("demo_call_transcript.txt", "w") as f:
    for result in response.results:
        f.write(result.alternatives[0].transcript)
```

## Cost Comparison

| Method | Cost | Setup Complexity | Accuracy |
|--------|------|-----------------|----------|
| Provided transcripts | $0 | None | N/A |
| Whisper (local) | $0 | Medium | Very Good |
| AssemblyAI free tier | $0 (5hr/mo) | Low | Excellent |
| Google STT free tier | $0 (60min/mo) | Medium | Excellent |

## Audio File Requirements

### Supported Formats
- MP3, WAV, M4A, FLAC
- MP4, AVI (if video with audio)
- OGG, WMA

### Recommendations
- **Length**: Under 30 minutes per file
- **Quality**: Clear audio, minimal background noise
- **Sample Rate**: 16kHz or higher
- **Channels**: Mono or stereo

### Poor Audio Quality?

If your audio is low quality:
1. Use `medium` or `large` Whisper model (better accuracy)
2. Pre-process audio to reduce noise
3. Consider manual transcription for critical calls

## Troubleshooting

### "ffmpeg not found"

Install ffmpeg:
```bash
# macOS
brew install ffmpeg

# Ubuntu
sudo apt install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
# Add to PATH
```

### Whisper is too slow

- Use `tiny` or `base` model
- Run on GPU (CUDA) if available
- Consider cloud transcription instead

### Out of memory

- Use smaller Whisper model (`tiny` or `base`)
- Close other applications
- Process files one at a time instead of batch

### Transcription is inaccurate

- Use larger model (`medium` or `large`)
- Improve audio quality
- Check if audio is in English (Whisper supports many languages)

## Example: Full Pipeline with Audio

```bash
# Directory structure
audio_files/
├── demo_calls/
│   ├── acme_demo.mp3
│   ├── beta_demo.mp3
│   └── gamma_demo.mp3
└── onboarding_calls/
    ├── acme_onboarding.mp3
    ├── beta_onboarding.mp3
    └── gamma_onboarding.mp3

# Step 1: Transcribe all audio
python scripts/transcribe_audio.py \
  --input audio_files/demo_calls/ \
  --output-dir transcripts/demo_calls/ \
  --batch --model base

python scripts/transcribe_audio.py \
  --input audio_files/onboarding_calls/ \
  --output-dir transcripts/onboarding_calls/ \
  --batch --model base

# Step 2: Run Clara pipelines
python scripts/batch_process.py \
  --mode demo \
  --input-dir transcripts/demo_calls/

python scripts/batch_process.py \
  --mode onboarding \
  --input-dir transcripts/onboarding_calls/

# Step 3: Review outputs
python scripts/validate_outputs.py
```

## Best Practice: Hybrid Approach

For the assignment:
1. **If transcripts provided**: Use them directly (zero cost, zero setup)
2. **If audio provided**: 
   - Transcribe with Whisper `base` model (free, local)
   - Or use AssemblyAI free tier for better quality
3. **Store transcripts**: Keep them for debugging and re-running pipeline

## Assignment Compliance

From the Clara Answers assignment PDF:

> "If we provide transcripts: use them directly"
> "If only audio is provided: you can use a free speech-to-text approach, but do not pay"

✅ **Whisper is compliant**: Free, local, no payment required
✅ **Cloud free tiers are compliant**: Within free limits
✅ **Transcripts are preferred**: Simpler and faster

## Questions?

- **Do I need audio files?** No, transcripts are sufficient
- **Can I submit without transcribing?** Yes, if you have transcripts
- **Is Whisper required?** No, only if you have audio files
- **Cost of transcription?** $0 with Whisper or cloud free tiers

---

**Bottom Line**: The pipeline works with text transcripts. Audio transcription is an optional preprocessing step if needed.
