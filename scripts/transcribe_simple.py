import requests
import time
import json
from pathlib import Path

# Your AssemblyAI API key
  # Replace with your actual key
API_KEY = "your_api_key_here"  # Instead of the actual key

# File paths
audio_file = "audio/onboarding_calls/onboarding_call.m4a"
output_file = "transcripts/onboarding_call_transcript.txt"

print("\n" + "="*60)
print("Transcribing Audio with AssemblyAI")
print("="*60 + "\n")

# Step 1: Upload the audio file
print("📤 Step 1: Uploading audio file...")
headers = {"authorization": API_KEY}

with open(audio_file, "rb") as f:
    response = requests.post(
        "https://api.assemblyai.com/v2/upload",
        headers=headers,
        data=f
    )

# Parse upload response
upload_response = response.json()
print(f"Upload response: {upload_response}")  # Debug

# Get upload URL - handle different response formats
if "upload_url" in upload_response:
    upload_url = upload_response["upload_url"]
elif "url" in upload_response:
    upload_url = upload_response["url"]
else:
    print(f"❌ Error: Unexpected response: {upload_response}")
    exit(1)

print(f"✅ Upload complete!\n")

# Step 2: Request transcription
print("🎙️  Step 2: Starting transcription...")
endpoint = "https://api.assemblyai.com/v2/transcript"
json_data = {
    "audio_url": upload_url,
    "speech_models": ["universal-2"]  # Fixed: must be a list with valid model
}

response = requests.post(endpoint, json=json_data, headers=headers)
transcript_response = response.json()

print(f"Transcript response: {transcript_response}")  # Debug

# Check for errors
if "error" in transcript_response:
    print(f"❌ Error: {transcript_response['error']}")
    exit(1)

# Get transcript ID - handle different response formats
if "id" in transcript_response:
    transcript_id = transcript_response["id"]
else:
    print(f"❌ Error: No transcript ID. Response: {transcript_response}")
    exit(1)

print(f"✅ Transcription started! ID: {transcript_id}\n")

# Step 3: Wait for transcription to complete
print("⏳ Step 3: Waiting for transcription to complete...")
print("This may take 2-5 minutes...\n")

polling_endpoint = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"

while True:
    response = requests.get(polling_endpoint, headers=headers)
    result = response.json()
    status = result.get("status", "unknown")
    
    if status == "completed":
        print("✅ Transcription completed!\n")
        transcript_text = result["text"]
        break
    elif status == "error":
        error_msg = result.get("error", "Unknown error")
        print(f"❌ Error: {error_msg}")
        exit(1)
    else:
        print(f"   Status: {status}...")
        time.sleep(5)

# Step 4: Save the transcript
print("💾 Step 4: Saving transcript...")

Path(output_file).parent.mkdir(parents=True, exist_ok=True)
with open(output_file, "w", encoding="utf-8") as f:
    f.write(transcript_text)

print(f"✅ Saved to: {output_file}")
print(f"📊 Length: {len(transcript_text)} characters\n")

# Preview
preview = transcript_text[:300] + "..." if len(transcript_text) > 300 else transcript_text
print("📝 Preview:")
print("-" * 60)
print(preview)
print("-" * 60)

print("\n" + "="*60)
print("✅ DONE!")
print("="*60)
print("\nNext step:")
print("python scripts/pipeline_b_onboarding.py --input transcripts/onboarding_call_transcript.txt --account-id BEN001")
print()