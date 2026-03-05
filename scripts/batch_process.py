#!/usr/bin/env python3
"""
Batch Processor for Clara Automation Pipeline

Processes multiple demo and onboarding calls in batch mode.
Generates summary reports and handles errors gracefully.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import time

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from pipeline_a_demo import process_demo_call
from pipeline_b_onboarding import process_onboarding_call


def batch_process_demos(input_dir: str, account_prefix: str = "ACC") -> dict:
    """
    Batch process all demo call transcripts in a directory
    
    Args:
        input_dir: Directory containing demo call transcript files
        account_prefix: Prefix for auto-generated account IDs
        
    Returns:
        Summary statistics dictionary
    """
    
    print(f"\n{'='*70}")
    print("BATCH PROCESSING: Demo Calls → v1 Agents")
    print(f"{'='*70}\n")
    
    input_path = Path(input_dir)
    if not input_path.exists():
        print(f"❌ Error: Input directory not found: {input_dir}")
        sys.exit(1)
    
    # Find all transcript files
    transcript_files = sorted(list(input_path.glob('*.txt')) + list(input_path.glob('*.md')))
    
    if not transcript_files:
        print(f"❌ No transcript files found in {input_dir}")
        print("   Looking for: *.txt, *.md")
        sys.exit(1)
    
    print(f"📁 Found {len(transcript_files)} demo call transcript(s)\n")
    
    results = {
        'total': len(transcript_files),
        'successful': 0,
        'failed': 0,
        'accounts': [],
        'errors': [],
        'start_time': datetime.utcnow().isoformat() + 'Z'
    }
    
    # Process each file
    for i, transcript_file in enumerate(transcript_files, 1):
        # Generate account ID
        account_id = f"{account_prefix}{i:03d}"
        
        print(f"\n{'─'*70}")
        print(f"Processing {i}/{len(transcript_files)}: {transcript_file.name}")
        print(f"Account ID: {account_id}")
        print(f"{'─'*70}")
        
        try:
            result = process_demo_call(str(transcript_file), account_id)
            results['successful'] += 1
            results['accounts'].append({
                'account_id': account_id,
                'company_name': result['company_name'],
                'transcript_file': str(transcript_file),
                'status': 'success',
                'output_dir': result['output_dir']
            })
            
            # Brief pause to respect API rate limits
            time.sleep(1)
            
        except Exception as e:
            results['failed'] += 1
            error_msg = str(e)
            results['errors'].append({
                'account_id': account_id,
                'transcript_file': str(transcript_file),
                'error': error_msg
            })
            print(f"\n❌ Failed to process {transcript_file.name}: {error_msg}\n")
    
    results['end_time'] = datetime.utcnow().isoformat() + 'Z'
    
    # Print summary
    print(f"\n{'='*70}")
    print("BATCH PROCESSING COMPLETE - Summary")
    print(f"{'='*70}")
    print(f"Total Files: {results['total']}")
    print(f"✅ Successful: {results['successful']}")
    print(f"❌ Failed: {results['failed']}")
    
    if results['successful'] > 0:
        print(f"\n📊 Successfully Created Accounts:")
        for account in results['accounts']:
            print(f"  • {account['account_id']}: {account['company_name']}")
    
    if results['errors']:
        print(f"\n⚠️  Errors:")
        for error in results['errors']:
            print(f"  • {error['account_id']}: {error['error']}")
    
    print(f"\n{'='*70}\n")
    
    # Save summary report
    output_base = Path(os.getenv('STORAGE_PATH', './outputs'))
    report_path = output_base / 'batch_reports' / f"demo_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"📄 Batch report saved: {report_path}\n")
    
    return results


def batch_process_onboarding(input_dir: str, account_mapping: dict = None, force: bool = False) -> dict:
    """
    Batch process onboarding calls/forms
    
    Args:
        input_dir: Directory containing onboarding transcripts
        account_mapping: Dict mapping filename to account_id, or None for auto-detection
        force: Overwrite existing v2 without prompting
        
    Returns:
        Summary statistics dictionary
    """
    
    print(f"\n{'='*70}")
    print("BATCH PROCESSING: Onboarding Updates → v2 Agents")
    print(f"{'='*70}\n")
    
    input_path = Path(input_dir)
    if not input_path.exists():
        print(f"❌ Error: Input directory not found: {input_dir}")
        sys.exit(1)
    
    # Find all transcript files
    transcript_files = sorted(list(input_path.glob('*.txt')) + list(input_path.glob('*.md')))
    
    if not transcript_files:
        print(f"❌ No transcript files found in {input_dir}")
        sys.exit(1)
    
    print(f"📁 Found {len(transcript_files)} onboarding transcript(s)\n")
    
    # If no mapping provided, try to auto-match based on filename or numbering
    if account_mapping is None:
        print("⚠️  No account mapping provided. Using auto-detection:")
        print("   Files should be named: onboarding_ACC001.txt, onboarding_ACC002.txt, etc.")
        print("   Or will map sequentially to ACC001, ACC002, ...\n")
        
        account_mapping = {}
        for i, transcript_file in enumerate(transcript_files, 1):
            # Try to extract account ID from filename
            filename = transcript_file.stem
            if 'ACC' in filename.upper():
                # Extract ACC### pattern
                import re
                match = re.search(r'ACC\d{3}', filename.upper())
                if match:
                    account_mapping[transcript_file.name] = match.group()
                else:
                    account_mapping[transcript_file.name] = f"ACC{i:03d}"
            else:
                account_mapping[transcript_file.name] = f"ACC{i:03d}"
    
    results = {
        'total': len(transcript_files),
        'successful': 0,
        'failed': 0,
        'updates': [],
        'errors': [],
        'start_time': datetime.utcnow().isoformat() + 'Z'
    }
    
    # Process each file
    for i, transcript_file in enumerate(transcript_files, 1):
        account_id = account_mapping.get(transcript_file.name)
        
        if not account_id:
            print(f"\n⚠️  Skipping {transcript_file.name}: No account_id mapping")
            results['failed'] += 1
            results['errors'].append({
                'transcript_file': str(transcript_file),
                'error': 'No account_id mapping found'
            })
            continue
        
        print(f"\n{'─'*70}")
        print(f"Processing {i}/{len(transcript_files)}: {transcript_file.name}")
        print(f"Account ID: {account_id}")
        print(f"{'─'*70}")
        
        try:
            result = process_onboarding_call(str(transcript_file), account_id, force=force)
            results['successful'] += 1
            results['updates'].append({
                'account_id': account_id,
                'company_name': result['company_name'],
                'transcript_file': str(transcript_file),
                'status': 'success',
                'modifications_count': result.get('modifications_count', 0),
                'v2_output_dir': result['account_dir']
            })
            
            # Brief pause to respect API rate limits
            time.sleep(1)
            
        except Exception as e:
            results['failed'] += 1
            error_msg = str(e)
            results['errors'].append({
                'account_id': account_id,
                'transcript_file': str(transcript_file),
                'error': error_msg
            })
            print(f"\n❌ Failed to process {transcript_file.name}: {error_msg}\n")
    
    results['end_time'] = datetime.utcnow().isoformat() + 'Z'
    
    # Print summary
    print(f"\n{'='*70}")
    print("BATCH PROCESSING COMPLETE - Summary")
    print(f"{'='*70}")
    print(f"Total Files: {results['total']}")
    print(f"✅ Successful: {results['successful']}")
    print(f"❌ Failed: {results['failed']}")
    
    if results['successful'] > 0:
        print(f"\n📊 Successfully Updated Accounts:")
        for update in results['updates']:
            print(f"  • {update['account_id']}: {update['company_name']} "
                  f"({update['modifications_count']} changes)")
    
    if results['errors']:
        print(f"\n⚠️  Errors:")
        for error in results['errors']:
            print(f"  • {error.get('account_id', 'Unknown')}: {error['error']}")
    
    print(f"\n{'='*70}\n")
    
    # Save summary report
    output_base = Path(os.getenv('STORAGE_PATH', './outputs'))
    report_path = output_base / 'batch_reports' / f"onboarding_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"📄 Batch report saved: {report_path}\n")
    
    return results


def main():
    """Main entry point for batch processing"""
    
    parser = argparse.ArgumentParser(
        description='Batch process demo or onboarding calls'
    )
    parser.add_argument(
        '--mode',
        required=True,
        choices=['demo', 'onboarding'],
        help='Processing mode: demo (Pipeline A) or onboarding (Pipeline B)'
    )
    parser.add_argument(
        '--input-dir',
        required=True,
        help='Directory containing transcript files'
    )
    parser.add_argument(
        '--account-prefix',
        default='ACC',
        help='Prefix for auto-generated account IDs (demo mode only)'
    )
    parser.add_argument(
        '--mapping-file',
        help='JSON file mapping transcript filenames to account IDs (onboarding mode only)'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Overwrite existing v2 without prompting (onboarding mode only)'
    )
    
    args = parser.parse_args()
    
    # Load environment
    load_dotenv()
    
    # Validate API key
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("❌ Error: ANTHROPIC_API_KEY not set in environment")
        print("   Please add it to .env file")
        sys.exit(1)
    
    try:
        if args.mode == 'demo':
            results = batch_process_demos(args.input_dir, args.account_prefix)
            
            if results['successful'] > 0:
                print("\n✅ Next: Process onboarding calls with:")
                print(f"   python scripts/batch_process.py \\")
                print(f"     --mode onboarding \\")
                print(f"     --input-dir <onboarding_dir>")
        
        elif args.mode == 'onboarding':
            # Load account mapping if provided
            account_mapping = None
            if args.mapping_file:
                with open(args.mapping_file, 'r') as f:
                    account_mapping = json.load(f)
            
            results = batch_process_onboarding(args.input_dir, account_mapping, args.force)
            
            if results['successful'] > 0:
                print("\n✅ Batch processing complete!")
                print("   Review outputs in: ./outputs/accounts/")
        
        # Exit with appropriate code
        sys.exit(0 if results['failed'] == 0 else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Batch processing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Batch processing failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
