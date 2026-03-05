#!/usr/bin/env python3
"""
Pipeline B: Onboarding Call → Agent Update (v2)

Processes onboarding call/form and updates existing agent:
1. Loads v1 account memo
2. Extracts onboarding updates
3. Generates updated account memo (v2)
4. Generates updated agent spec (v2)
5. Creates detailed changelog
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


def find_account_directory(account_id: str) -> Path:
    """Find existing account directory"""
    output_base = Path(os.getenv('STORAGE_PATH', './outputs'))
    accounts_dir = output_base / 'accounts'
    
    if not accounts_dir.exists():
        raise FileNotFoundError(f"Accounts directory not found: {accounts_dir}")
    
    # Find directory matching account_id
    for account_dir in accounts_dir.iterdir():
        if account_dir.is_dir() and account_dir.name.startswith(account_id):
            return account_dir
    
    raise FileNotFoundError(
        f"No account directory found for {account_id}. "
        f"Please run Pipeline A first."
    )


def load_v1_memo(account_dir: Path) -> dict:
    """Load v1 account memo"""
    v1_memo_path = account_dir / 'v1' / 'account_memo.json'
    
    if not v1_memo_path.exists():
        raise FileNotFoundError(
            f"v1 account memo not found: {v1_memo_path}. "
            f"Please run Pipeline A first."
        )
    
    with open(v1_memo_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def process_onboarding_call(transcript_path: str, account_id: str, force: bool = False) -> dict:
    """
    Process onboarding call through Pipeline B
    
    Args:
        transcript_path: Path to onboarding transcript/form
        account_id: Unique account identifier
        force: Overwrite existing v2 if present
        
    Returns:
        Dictionary with paths to generated files
    """
    
    print(f"\n{'='*60}")
    print(f"Pipeline B: Processing Onboarding Update")
    print(f"Account ID: {account_id}")
    print(f"Onboarding Data: {transcript_path}")
    print(f"{'='*60}\n")
    
    # Find account directory
    print("🔍 Locating account directory...")
    try:
        account_dir = find_account_directory(account_id)
        print(f"   ✓ Found: {account_dir}\n")
    except FileNotFoundError as e:
        print(f"   ✗ Error: {e}")
        sys.exit(1)
    
    # Load v1 memo
    print("📄 Loading v1 account memo...")
    try:
        v1_memo = load_v1_memo(account_dir)
        company_name = v1_memo.get('company_name', 'unknown')
        print(f"   ✓ Loaded v1 for: {company_name}\n")
    except FileNotFoundError as e:
        print(f"   ✗ Error: {e}")
        sys.exit(1)
    
    # Check if v2 already exists
    v2_dir = account_dir / 'v2'
    if v2_dir.exists() and not force:
        print("⚠️  v2 already exists!")
        print(f"   Location: {v2_dir}")
        response = input("   Overwrite? [y/N]: ")
        if response.lower() != 'y':
            print("   Aborted. Use --force to overwrite without prompt.")
            sys.exit(0)
    
    # Create v2 directory
    v2_dir.mkdir(exist_ok=True)
    
    # Load onboarding transcript
    print("📄 Loading onboarding data...")
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
    
    # Extract onboarding updates
    print("🔍 Extracting onboarding updates...")
    print("   (Merging with v1 data...)")
    try:
        v2_memo = extractor.extract_onboarding_data(transcript, account_id, v1_memo)
        print("   ✓ Extraction and merge complete\n")
    except Exception as e:
        print(f"   ✗ Extraction failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Save v2 account memo
    print("💾 Saving account memo (v2)...")
    v2_memo_path = v2_dir / 'account_memo.json'
    with open(v2_memo_path, 'w', encoding='utf-8') as f:
        json.dump(v2_memo, f, indent=2, ensure_ascii=False)
    print(f"   ✓ Saved to: {v2_memo_path}\n")
    
    # Generate changelog
    print("📝 Generating changelog...")
    changelog = extractor.generate_changelog(v1_memo, v2_memo)
    
    changelog_path = account_dir / 'changelog.json'
    with open(changelog_path, 'w', encoding='utf-8') as f:
        json.dump(changelog, f, indent=2, ensure_ascii=False)
    print(f"   ✓ Saved to: {changelog_path}\n")
    
    # Generate v2 agent spec
    print("🎯 Generating updated Retell agent specification...")
    generator = PromptGenerator()
    v2_agent_spec = generator.generate_agent_spec(v2_memo)
    print("   ✓ Agent spec generated\n")
    
    # Save v2 agent spec
    print("💾 Saving agent spec (v2)...")
    v2_spec_path = v2_dir / 'agent_spec.json'
    with open(v2_spec_path, 'w', encoding='utf-8') as f:
        json.dump(v2_agent_spec, f, indent=2, ensure_ascii=False)
    print(f"   ✓ Saved to: {v2_spec_path}\n")
    
    # Save extraction log
    print("📋 Saving extraction log...")
    log_data = {
        'pipeline': 'B',
        'stage': 'onboarding_update',
        'account_id': account_id,
        'company_name': company_name,
        'onboarding_data_path': str(transcript_path),
        'transcript_length': len(transcript),
        'extraction_timestamp': datetime.utcnow().isoformat() + 'Z',
        'output_files': {
            'account_memo_v2': str(v2_memo_path),
            'agent_spec_v2': str(v2_spec_path),
            'changelog': str(changelog_path)
        },
        'extraction_metadata': v2_memo.get('_extraction_metadata', {}),
        'remaining_unknowns': v2_memo.get('questions_or_unknowns', [])
    }
    
    log_path = v2_dir / 'extraction_log.json'
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)
    print(f"   ✓ Saved to: {log_path}\n")
    
    # Print summary
    print(f"{'='*60}")
    print("✅ Pipeline B Complete - Summary")
    print(f"{'='*60}")
    print(f"Company: {company_name}")
    print(f"Account ID: {account_id}")
    print(f"Version: v1 → v2 (onboarding-refined)")
    
    # Print changelog summary
    changes = changelog.get('changes', [])
    if changes:
        latest_change = changes[-1]
        modifications = latest_change.get('modifications', [])
        print(f"\n📊 Changes Applied: {len(modifications)}")
        print(f"   Summary: {latest_change.get('summary', 'No summary')}")
        
        if modifications:
            print(f"\n   Top changes:")
            for mod in modifications[:5]:  # Show first 5
                action = mod['action'].upper()
                field = mod['field']
                print(f"   • {action}: {field}")
            
            if len(modifications) > 5:
                print(f"   ... and {len(modifications) - 5} more")
    
    print(f"\nGenerated Files:")
    print(f"  - Account Memo (v2): {v2_memo_path}")
    print(f"  - Agent Spec (v2): {v2_spec_path}")
    print(f"  - Changelog: {changelog_path}")
    print(f"  - Extraction Log: {log_path}")
    
    # Highlight remaining unknowns
    unknowns = v2_memo.get('questions_or_unknowns', [])
    if unknowns:
        print(f"\n⚠️  Remaining Questions/Unknowns ({len(unknowns)}):")
        for i, unknown in enumerate(unknowns, 1):
            print(f"  {i}. {unknown}")
        print("\n   → May need follow-up clarification")
    else:
        print("\n✓ All questions resolved - agent is production-ready")
    
    print(f"\n{'='*60}\n")
    
    return {
        'account_id': account_id,
        'company_name': company_name,
        'account_dir': str(account_dir),
        'v2_memo_path': str(v2_memo_path),
        'v2_spec_path': str(v2_spec_path),
        'changelog_path': str(changelog_path),
        'modifications_count': len(modifications) if changes else 0
    }


def main():
    """Main entry point for Pipeline B"""
    
    parser = argparse.ArgumentParser(
        description='Pipeline B: Process onboarding and update agent to v2'
    )
    parser.add_argument(
        '--input',
        required=True,
        help='Path to onboarding call transcript or form data file'
    )
    parser.add_argument(
        '--account-id',
        required=True,
        help='Unique account identifier (must match Pipeline A)'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Overwrite existing v2 without prompting'
    )
    
    args = parser.parse_args()
    
    # Load environment
    load_dotenv()
    
    # Validate input file
    if not os.path.exists(args.input):
        print(f"Error: Onboarding data file not found: {args.input}")
        sys.exit(1)
    
    # Process onboarding
    try:
        result = process_onboarding_call(args.input, args.account_id, args.force)
        print("Pipeline B completed successfully!")
        
        # Print next steps
        print("\n" + "="*60)
        print("NEXT STEPS")
        print("="*60)
        print("\n1. Review the updated v2 files in:")
        print(f"   {result['account_dir']}/v2/")
        print("\n2. Review changelog.json to see what changed:")
        print(f"   {result['changelog_path']}")
        print("\n3. Compare v1 and v2:")
        print(f"   python scripts/compare_versions.py --account-id {result['account_id']}")
        print("\n4. Deploy to Retell:")
        print("   - Use v2/agent_spec.json")
        print("   - Copy system_prompt to Retell dashboard")
        print("   - Configure voice and transfer settings")
        print("\n5. Test the agent with sample scenarios")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Pipeline B failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
