#!/usr/bin/env python3
"""
Audio Transcription Script (Optional)

Converts audio files to text transcripts using OpenAI Whisper (free, local)
Run this BEFORE the main pipeline if you have audio files instead of transcripts.
"""

import os
import sys
import argparse
from pathlib import Path

try:
    import whisper
except ImportError:
    print("❌ Whisper not installed. Install with:")
    print("   pip install openai-whisper")
    print("\nNote: This also requires ffmpeg:")
    print("   macOS: brew install ffmpeg")
    print("   Ubuntu: sudo apt install ffmpeg")
    print("   Windows: https://ffmpeg.org/download.html")
    sys.exit(1)


def transcribe_audio(audio_path: str, output_dir: str, model_size: str = "base") -> str:
    """
    Transcribe audio file to text using Whisper
    
    Args:
        audio_path: Path to audio file (.mp3, .wav, .m4a, etc.)
        output_dir: Directory to save transcript
        model_size: Whisper model size (tiny, base, small, medium, large)
                   tiny = fastest, least accurate
                   base = good balance (recommended for free tier)
                   large = best quality but slow
    
    Returns:
        Path to generated transcript file
    """
    
    print(f"\n{'='*60}")
    print(f"Audio Transcription with Whisper")
    print(f"{'='*60}\n")
    
    audio_path = Path(audio_path)
    if not audio_path.exists():
        print(f"❌ Audio file not found: {audio_path}")
        sys.exit(1)
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Input: {audio_path}")
    print(f"📁 Output Directory: {output_dir}")
    print(f"🤖 Model: {model_size}")
    print()
    
    # Load Whisper model
    print(f"Loading Whisper model '{model_size}'...")
    print("(First run will download model - this may take a few minutes)")
    model = whisper.load_model(model_size)
    print("✓ Model loaded\n")
    
    # Transcribe
    print("🎙️  Transcribing audio...")
    print("This may take a few minutes depending on file length...")
    result = model.transcribe(str(audio_path))
    print("✓ Transcription complete\n")
    
    # Save transcript
    transcript_filename = audio_path.stem + "_transcript.txt"
    transcript_path = output_dir / transcript_filename
    
    with open(transcript_path, 'w', encoding='utf-8') as f:
        f.write(result["text"])
    
    print(f"💾 Transcript saved: {transcript_path}")
    print(f"📊 Length: {len(result['text'])} characters")
    
    # Show preview
    preview = result["text"][:300] + "..." if len(result["text"]) > 300 else result["text"]
    print(f"\n📝 Preview:")
    print("-" * 60)
    print(preview)
    print("-" * 60)
    print()
    
    return str(transcript_path)


def batch_transcribe(audio_dir: str, output_dir: str, model_size: str = "base"):
    """Batch transcribe all audio files in a directory"""
    
    print(f"\n{'='*60}")
    print(f"Batch Audio Transcription")
    print(f"{'='*60}\n")
    
    audio_dir = Path(audio_dir)
    output_dir = Path(output_dir)
    
    # Find audio files
    audio_extensions = ['.mp3', '.wav', '.m4a', '.mp4', '.avi', '.flac', '.ogg']
    audio_files = []
    for ext in audio_extensions:
        audio_files.extend(audio_dir.glob(f"*{ext}"))
    
    if not audio_files:
        print(f"❌ No audio files found in {audio_dir}")
        print(f"   Looking for: {', '.join(audio_extensions)}")
        sys.exit(1)
    
    print(f"📁 Found {len(audio_files)} audio file(s)")
    print()
    
    results = []
    
    for i, audio_file in enumerate(audio_files, 1):
        print(f"\n{'─'*60}")
        print(f"Processing {i}/{len(audio_files)}: {audio_file.name}")
        print(f"{'─'*60}")
        
        try:
            transcript_path = transcribe_audio(str(audio_file), str(output_dir), model_size)
            results.append({
                'audio': str(audio_file),
                'transcript': transcript_path,
                'status': 'success'
            })
        except Exception as e:
            print(f"❌ Failed to transcribe {audio_file.name}: {e}")
            results.append({
                'audio': str(audio_file),
                'transcript': None,
                'status': 'failed',
                'error': str(e)
            })
    
    # Summary
    print(f"\n{'='*60}")
    print("Batch Transcription Complete")
    print(f"{'='*60}\n")
    
    successful = sum(1 for r in results if r['status'] == 'success')
    failed = len(results) - successful
    
    print(f"Total: {len(results)}")
    print(f"✅ Success: {successful}")
    print(f"❌ Failed: {failed}")
    
    if successful > 0:
        print(f"\n📝 Generated Transcripts:")
        for result in results:
            if result['status'] == 'success':
                print(f"  • {Path(result['transcript']).name}")
        
        print(f"\n💡 Next Step: Run the Clara pipeline on these transcripts:")
        print(f"   python scripts/batch_process.py \\")
        print(f"     --mode demo \\")
        print(f"     --input-dir {output_dir}")
    
    print()


def main():
    parser = argparse.ArgumentParser(
        description='Transcribe audio files to text using Whisper (free, local)'
    )
    parser.add_argument(
        '--input',
        required=True,
        help='Path to audio file or directory of audio files'
    )
    parser.add_argument(
        '--output-dir',
        default='./transcripts',
        help='Directory to save transcripts (default: ./transcripts)'
    )
    parser.add_argument(
        '--model',
        choices=['tiny', 'base', 'small', 'medium', 'large'],
        default='base',
        help='Whisper model size (default: base). Larger = better quality but slower'
    )
    parser.add_argument(
        '--batch',
        action='store_true',
        help='Batch process all audio files in input directory'
    )
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    
    try:
        if args.batch or input_path.is_dir():
            batch_transcribe(str(input_path), args.output_dir, args.model)
        else:
            transcript_path = transcribe_audio(str(input_path), args.output_dir, args.model)
            print(f"\n✅ Done! Now run the Clara pipeline:")
            print(f"   python scripts/pipeline_a_demo.py \\")
            print(f"     --input {transcript_path} \\")
            print(f"     --account-id ACC001")
            print()
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Transcription interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Transcription failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
