# #!/usr/bin/env python3
# """
# AssemblyAI Transcription Script - Fixed Version
# Transcribes audio files using AssemblyAI's free tier
# """

# import assemblyai as aai
# import sys
# import os
# from pathlib import Path

# # Set your API key here
# aai.settings.api_key = "4949450ebc854b7a80c74cca112087b9"  # Replace with your actual key

# def transcribe_file(audio_path, output_dir):
#     """Transcribe audio file using AssemblyAI"""
    
#     print(f"\n{'='*60}")
#     print(f"AssemblyAI Audio Transcription")
#     print(f"{'='*60}\n")
    
#     print(f"🎙️  Uploading: {audio_path}")
#     print("This may take a few minutes...\n")
    
#     # Create transcriber with config
#     config = aai.TranscriptionConfig(
#         language_code="en"  # English language
#     )
    
#     transcriber = aai.Transcriber(config=config)
    
#     # Transcribe
#     try:
#         transcript = transcriber.transcribe(audio_path)
        
#         # Check status
#         if transcript.status == aai.TranscriptStatus.error:
#             print(f"❌ Transcription Error: {transcript.error}")
#             sys.exit(1)
        
#         # Save transcript
#         output_path = Path(output_dir) / f"{Path(audio_path).stem}_transcript.txt"
#         output_path.parent.mkdir(parents=True, exist_ok=True)
        
#         with open(output_path, 'w', encoding='utf-8') as f:
#             f.write(transcript.text)
        
#         print(f"✅ Transcription complete!")
#         print(f"📄 Saved to: {output_path}")
#         print(f"📊 Length: {len(transcript.text)} characters")
        
#         # Preview
#         preview = transcript.text[:300] + "..." if len(transcript.text) > 300 else transcript.text
#         print(f"\n📝 Preview:")
#         print("-" * 60)
#         print(preview)
#         print("-" * 60)
#         print()
        
#         return str(output_path)
        
#     except Exception as e:
#         print(f"❌ Error during transcription: {e}")
#         sys.exit(1)


# if __name__ == "__main__":
#     # Configuration
#     audio_path = "audio/onboarding_calls/onboarding_call.m4a"
#     output_dir = "transcripts"
    
#     # Check if audio file exists
#     if not os.path.exists(audio_path):
#         print(f"❌ Error: Audio file not found: {audio_path}")
#         print("\nPlease make sure the file exists at:")
#         print(f"  {os.path.abspath(audio_path)}")
#         sys.exit(1)
    
#     # Transcribe
#     transcribe_file(audio_path, output_dir)
    
#     print(f"\n{'='*60}")
#     print("✅ DONE!")
#     print(f"{'='*60}")
#     print("\nNext step: Run Pipeline B")
#     print("  python scripts/pipeline_b_onboarding.py \\")
#     print("    --input transcripts/onboarding_call_transcript.txt \\")
#     print("    --account-id BEN001")
#     print()


#!/usr/bin/env python3
"""
Simple AssemblyAI Transcription - No complex config
"""

import assemblyai as aai
from pathlib import Path

# SET YOUR API KEY HERE
aai.settings.api_key = "4949450ebc854b7a80c74cca112087b9"

# Paths
audio_path = "audio/onboarding_calls/onboarding_call.m4a"
output_dir = "transcripts"

print("\n" + "="*60)
print("AssemblyAI Audio Transcription")
print("="*60 + "\n")

print(f"🎙️  Uploading: {audio_path}")
print("This may take a few minutes...\n")

# Simple transcription - no config needed
transcriber = aai.Transcriber()

try:
    # Just transcribe with defaults
    transcript = transcriber.transcribe(audio_path)
    
    if transcript.status == aai.TranscriptStatus.error:
        print(f"❌ Error: {transcript.error}")
    else:
        # Save
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        output_file = output_path / "onboarding_call_transcript.txt"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(transcript.text)
        
        print(f"✅ Success!")
        print(f"📄 Saved to: {output_file}")
        print(f"📊 Length: {len(transcript.text)} characters\n")
        
        # Preview
        preview = transcript.text[:300] + "..."
        print("📝 Preview:")
        print("-" * 60)
        print(preview)
        print("-" * 60)

except Exception as e:
    print(f"❌ Error: {e}")
    print("\nTrying alternative method...")
    
    # Alternative: Direct URL upload
    transcript = transcriber.transcribe(str(Path(audio_path).absolute()))