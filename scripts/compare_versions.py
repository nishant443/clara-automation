#!/usr/bin/env python3
"""
Version Comparison Utility

Compare v1 and v2 account memos side-by-side
Visualize changes and provide detailed diff
"""

import os
import sys
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv


def find_account_directory(account_id: str) -> Path:
    """Find existing account directory"""
    output_base = Path(os.getenv('STORAGE_PATH', './outputs'))
    accounts_dir = output_base / 'accounts'
    
    for account_dir in accounts_dir.iterdir():
        if account_dir.is_dir() and account_dir.name.startswith(account_id):
            return account_dir
    
    raise FileNotFoundError(f"Account directory not found for {account_id}")


def load_memos(account_dir: Path) -> tuple:
    """Load v1 and v2 memos"""
    v1_path = account_dir / 'v1' / 'account_memo.json'
    v2_path = account_dir / 'v2' / 'account_memo.json'
    
    if not v1_path.exists():
        raise FileNotFoundError(f"v1 memo not found: {v1_path}")
    
    with open(v1_path, 'r') as f:
        v1_memo = json.load(f)
    
    v2_memo = None
    if v2_path.exists():
        with open(v2_path, 'r') as f:
            v2_memo = json.load(f)
    
    return v1_memo, v2_memo


def load_changelog(account_dir: Path) -> dict:
    """Load changelog if exists"""
    changelog_path = account_dir / 'changelog.json'
    
    if not changelog_path.exists():
        return None
    
    with open(changelog_path, 'r') as f:
        return json.load(f)


def format_value(value, indent=0):
    """Format value for display"""
    spaces = "  " * indent
    
    if value is None or value == "":
        return f"{spaces}(empty)"
    elif isinstance(value, list):
        if not value:
            return f"{spaces}[]"
        formatted_items = [f"{spaces}  - {item}" for item in value]
        return "\n".join(formatted_items)
    elif isinstance(value, dict):
        if not value:
            return f"{spaces}{{}}"
        formatted_items = [f"{spaces}  {k}: {v}" for k, v in value.items()]
        return "\n".join(formatted_items)
    else:
        return f"{spaces}{value}"


def compare_versions(account_id: str, detailed: bool = False):
    """Compare v1 and v2 for an account"""
    
    print(f"\n{'='*70}")
    print(f"Version Comparison: {account_id}")
    print(f"{'='*70}\n")
    
    # Find account
    try:
        account_dir = find_account_directory(account_id)
        print(f"📁 Account Directory: {account_dir}\n")
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    
    # Load memos
    try:
        v1_memo, v2_memo = load_memos(account_dir)
        company_name = v1_memo.get('company_name', 'Unknown')
        print(f"🏢 Company: {company_name}\n")
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    
    if not v2_memo:
        print("⚠️  v2 not yet created. Run Pipeline B first.")
        print(f"\nv1 Summary:")
        print(f"  Version: {v1_memo.get('version')}")
        print(f"  Created: {v1_memo.get('created_at')}")
        print(f"  Unknowns: {len(v1_memo.get('questions_or_unknowns', []))}")
        return
    
    # Load changelog
    changelog = load_changelog(account_dir)
    
    print(f"{'─'*70}")
    print("VERSION OVERVIEW")
    print(f"{'─'*70}\n")
    
    print("v1 (Demo-derived):")
    print(f"  Created: {v1_memo.get('created_at')}")
    print(f"  Unknowns: {len(v1_memo.get('questions_or_unknowns', []))}")
    
    print("\nv2 (Onboarding-refined):")
    print(f"  Updated: {v2_memo.get('updated_at')}")
    print(f"  Remaining Unknowns: {len(v2_memo.get('questions_or_unknowns', []))}")
    
    # Show changelog summary
    if changelog and changelog.get('changes'):
        latest = changelog['changes'][-1]
        mods = latest.get('modifications', [])
        print(f"\nChanges Applied: {len(mods)}")
        print(f"  Summary: {latest.get('summary', 'N/A')}")
    
    print(f"\n{'─'*70}")
    print("KEY CHANGES")
    print(f"{'─'*70}\n")
    
    if changelog and changelog.get('changes'):
        latest = changelog['changes'][-1]
        modifications = latest.get('modifications', [])
        
        if not modifications:
            print("No changes detected\n")
        else:
            for mod in modifications:
                action = mod['action'].upper()
                field = mod['field']
                
                if action == "ADDED":
                    print(f"✅ {action}: {field}")
                    print(f"   New Value: {format_value(mod['new_value'], 1)}")
                elif action == "UPDATED":
                    print(f"🔄 {action}: {field}")
                    print(f"   Old: {format_value(mod['old_value'], 1)}")
                    print(f"   New: {format_value(mod['new_value'], 1)}")
                elif action == "REMOVED":
                    print(f"❌ {action}: {field}")
                    print(f"   Was: {format_value(mod['old_value'], 1)}")
                
                print()
    
    # Detailed comparison
    if detailed:
        print(f"{'─'*70}")
        print("DETAILED FIELD-BY-FIELD COMPARISON")
        print(f"{'─'*70}\n")
        
        # Compare key fields
        fields_to_compare = [
            'company_name',
            'business_type',
            'business_hours',
            'services_supported',
            'emergency_definition',
            'emergency_routing_rules',
            'integration_constraints',
            'questions_or_unknowns'
        ]
        
        for field in fields_to_compare:
            v1_val = v1_memo.get(field)
            v2_val = v2_memo.get(field)
            
            print(f"📌 {field}:")
            print(f"   v1: {format_value(v1_val, 1)}")
            print(f"   v2: {format_value(v2_val, 1)}")
            
            if v1_val != v2_val:
                print("   ⚠️  CHANGED")
            else:
                print("   (unchanged)")
            print()
    
    # Output files comparison
    print(f"{'─'*70}")
    print("OUTPUT FILES")
    print(f"{'─'*70}\n")
    
    print("v1:")
    print(f"  Memo: {account_dir}/v1/account_memo.json")
    print(f"  Agent Spec: {account_dir}/v1/agent_spec.json")
    
    print("\nv2:")
    print(f"  Memo: {account_dir}/v2/account_memo.json")
    print(f"  Agent Spec: {account_dir}/v2/agent_spec.json")
    
    print("\nChangelog:")
    print(f"  {account_dir}/changelog.json")
    
    print(f"\n{'='*70}\n")


def main():
    parser = argparse.ArgumentParser(
        description='Compare v1 and v2 account memos'
    )
    parser.add_argument(
        '--account-id',
        required=True,
        help='Account ID to compare'
    )
    parser.add_argument(
        '--detailed',
        action='store_true',
        help='Show detailed field-by-field comparison'
    )
    
    args = parser.parse_args()
    
    load_dotenv()
    
    try:
        compare_versions(args.account_id, args.detailed)
    except Exception as e:
        print(f"❌ Comparison failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
