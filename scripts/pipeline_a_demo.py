#!/usr/bin/env python3
"""
Pipeline A: Demo Call → Preliminary Agent (v1)

Processes demo call transcripts and generates:
1. Account Memo (v1) - structured account data
2. Agent Spec (v1) - Retell agent configuration with system prompt
3. Extraction log for debugging
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from extraction_engine import ExtractionEngine
from prompt_generator import PromptGenerator


def ensure_output_directory(account_id: str, company_name: str) -> Path:
    """Create output directory structure for account"""
    # Sanitize company name for directory
    safe_name = "".join(c if c.isalnum() else "_" for c in company_name.lower())
    dir_name = f"{account_id}_{safe_name}"
    
    output_base = Path(os.getenv('STORAGE_PATH', './outputs'))
    account_dir = output_base / 'accounts' / dir_name / 'v1'
    account_dir.mkdir(parents=True, exist_ok=True)
    
    return account_dir


def process_demo_call(transcript_path: str, account_id: str) -> dict:
    """
    Process a single demo call through Pipeline A
    
    Args:
        transcript_path: Path to transcript file
        account_id: Unique account identifier
        
    Returns:
        Dictionary with paths to generated files
    """
    
    print(f"\n{'='*60}")
    print(f"Pipeline A: Processing Demo Call")
    print(f"Account ID: {account_id}")
    print(f"Transcript: {transcript_path}")
    print(f"{'='*60}\n")
    
    # Load transcript
    print("📄 Loading transcript...")
    with open(transcript_path, 'r', encoding='utf-8') as f:
        transcript = f.read()
    
    print(f"   Transcript length: {len(transcript)} characters\n")
    
    # Initialize extraction engine
    print("🤖 Initializing extraction engine...")
    try:
        extractor = ExtractionEngine()
        print("   ✓ Connected to Claude API\n")
    except ValueError as e:
        print(f"   ✗ Error: {e}")
        print("   Please set ANTHROPIC_API_KEY in .env file")
        sys.exit(1)
    
    # Extract structured data
    print("🔍 Extracting structured account data...")
    try:
        account_memo = extractor.extract_demo_data(transcript, account_id)
        print("   ✓ Extraction complete\n")
    except Exception as e:
        print(f"   ✗ Extraction failed: {e}")
        sys.exit(1)
    
    # Create output directory
    company_name = account_memo.get('company_name', 'unknown')
    output_dir = ensure_output_directory(account_id, company_name)
    print(f"📁 Output directory: {output_dir}\n")
    
    # Save account memo
    print("💾 Saving account memo (v1)...")
    memo_path = output_dir / 'account_memo.json'
    with open(memo_path, 'w', encoding='utf-8') as f:
        json.dump(account_memo, f, indent=2, ensure_ascii=False)
    print(f"   ✓ Saved to: {memo_path}\n")
    
    # Generate agent spec
    print("🎯 Generating Retell agent specification...")
    generator = PromptGenerator()
    agent_spec = generator.generate_agent_spec(account_memo)
    print("   ✓ Agent spec generated\n")
    
    # Save agent spec
    print("💾 Saving agent spec (v1)...")
    spec_path = output_dir / 'agent_spec.json'
    with open(spec_path, 'w', encoding='utf-8') as f:
        json.dump(agent_spec, f, indent=2, ensure_ascii=False)
    print(f"   ✓ Saved to: {spec_path}\n")
    
    # Save extraction log
    print("📋 Saving extraction log...")
    log_data = {
        'pipeline': 'A',
        'stage': 'demo_call',
        'account_id': account_id,
        'transcript_path': str(transcript_path),
        'transcript_length': len(transcript),
        'company_name': company_name,
        'extraction_timestamp': datetime.utcnow().isoformat() + 'Z',
        'output_files': {
            'account_memo': str(memo_path),
            'agent_spec': str(spec_path)
        },
        'extraction_metadata': account_memo.get('_extraction_metadata', {}),
        'questions_or_unknowns': account_memo.get('questions_or_unknowns', [])
    }
    
    log_path = output_dir / 'extraction_log.json'
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)
    print(f"   ✓ Saved to: {log_path}\n")
    
    # Print summary
    print(f"{'='*60}")
    print("✅ Pipeline A Complete - Summary")
    print(f"{'='*60}")
    print(f"Company: {company_name}")
    print(f"Account ID: {account_id}")
    print(f"Version: v1 (demo-derived)")
    print(f"\nGenerated Files:")
    print(f"  - Account Memo: {memo_path}")
    print(f"  - Agent Spec: {spec_path}")
    print(f"  - Extraction Log: {log_path}")
    
    # Highlight unknowns
    unknowns = account_memo.get('questions_or_unknowns', [])
    if unknowns:
        print(f"\n⚠️  Questions/Unknowns ({len(unknowns)}):")
        for i, unknown in enumerate(unknowns, 1):
            print(f"  {i}. {unknown}")
        print("\n   → These should be clarified during onboarding")
    else:
        print("\n✓ No critical unknowns flagged")
    
    print(f"\n{'='*60}\n")
    
    return {
        'account_id': account_id,
        'company_name': company_name,
        'output_dir': str(output_dir),
        'memo_path': str(memo_path),
        'spec_path': str(spec_path),
        'log_path': str(log_path)
    }


def main():
    """Main entry point for Pipeline A"""
    
    parser = argparse.ArgumentParser(
        description='Pipeline A: Process demo call and generate v1 agent'
    )
    parser.add_argument(
        '--input',
        required=True,
        help='Path to demo call transcript file'
    )
    parser.add_argument(
        '--account-id',
        required=True,
        help='Unique account identifier (e.g., ACC001)'
    )
    
    args = parser.parse_args()
    
    # Load environment
    load_dotenv()
    
    # Validate input file
    if not os.path.exists(args.input):
        print(f"Error: Transcript file not found: {args.input}")
        sys.exit(1)
    
    # Process demo call
    try:
        result = process_demo_call(args.input, args.account_id)
        print("Pipeline A completed successfully!")
        
        # Print next steps
        print("\n" + "="*60)
        print("NEXT STEPS")
        print("="*60)
        print("\n1. Review the generated files in:")
        print(f"   {result['output_dir']}")
        print("\n2. Check questions_or_unknowns in account_memo.json")
        print("\n3. When onboarding call/form is ready, run:")
        print(f"   python scripts/pipeline_b_onboarding.py \\")
        print(f"     --input <onboarding_transcript.txt> \\")
        print(f"     --account-id {result['account_id']}")
        print("\n4. Optional: Import agent_spec.json into Retell dashboard")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Pipeline A failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
