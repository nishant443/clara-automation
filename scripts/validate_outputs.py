#!/usr/bin/env python3
"""
Output Validation Script

Validates that generated account memos and agent specs conform to expected schema
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List


class OutputValidator:
    """Validates account memos and agent specs"""
    
    REQUIRED_MEMO_FIELDS = [
        'account_id',
        'version',
        'company_name',
        'business_hours',
        'services_supported',
        'emergency_definition',
        'questions_or_unknowns',
        'notes'
    ]
    
    REQUIRED_AGENT_SPEC_FIELDS = [
        'agent_name',
        'version',
        'system_prompt',
        'voice_config',
        'conversation_config'
    ]
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate_memo(self, memo: Dict[str, Any], version: str) -> bool:
        """Validate account memo structure"""
        
        valid = True
        
        # Check required fields
        for field in self.REQUIRED_MEMO_FIELDS:
            if field not in memo:
                self.errors.append(f"Missing required field: {field}")
                valid = False
        
        # Check version matches
        if memo.get('version') != version:
            self.errors.append(f"Version mismatch: expected {version}, got {memo.get('version')}")
            valid = False
        
        # Validate business_hours structure
        if 'business_hours' in memo:
            hours = memo['business_hours']
            if not isinstance(hours, dict):
                self.errors.append("business_hours must be a dictionary")
                valid = False
            elif 'schedule' in hours and not isinstance(hours['schedule'], list):
                self.errors.append("business_hours.schedule must be a list")
                valid = False
        
        # Check for hallucinated unknowns
        unknowns = memo.get('questions_or_unknowns', [])
        if len(unknowns) > 10:
            self.warnings.append(f"Unusually high number of unknowns: {len(unknowns)}")
        
        # Validate lists
        for list_field in ['services_supported', 'emergency_definition']:
            if list_field in memo and not isinstance(memo[list_field], list):
                self.errors.append(f"{list_field} must be a list")
                valid = False
        
        return valid
    
    def validate_agent_spec(self, spec: Dict[str, Any], version: str) -> bool:
        """Validate agent spec structure"""
        
        valid = True
        
        # Check required fields
        for field in self.REQUIRED_AGENT_SPEC_FIELDS:
            if field not in spec:
                self.errors.append(f"Missing required field: {field}")
                valid = False
        
        # Check version matches
        if spec.get('version') != version:
            self.errors.append(f"Version mismatch: expected {version}, got {spec.get('version')}")
            valid = False
        
        # Validate system prompt
        if 'system_prompt' in spec:
            prompt = spec['system_prompt']
            if not isinstance(prompt, str):
                self.errors.append("system_prompt must be a string")
                valid = False
            elif len(prompt) < 500:
                self.warnings.append(f"System prompt seems short: {len(prompt)} characters")
            
            # Check for prompt hygiene violations
            if 'function' in prompt.lower() or 'tool call' in prompt.lower():
                self.errors.append("System prompt mentions 'function' or 'tool call' - this violates prompt hygiene")
                valid = False
            
            # Check for required conversation flows
            if 'business hours' not in prompt.lower():
                self.warnings.append("System prompt may be missing business hours flow")
            if 'after hours' not in prompt.lower() and 'after-hours' not in prompt.lower():
                self.warnings.append("System prompt may be missing after-hours flow")
        
        return valid
    
    def validate_changelog(self, changelog: Dict[str, Any]) -> bool:
        """Validate changelog structure"""
        
        valid = True
        
        if 'changes' not in changelog:
            self.errors.append("Changelog missing 'changes' field")
            return False
        
        if not isinstance(changelog['changes'], list):
            self.errors.append("Changelog 'changes' must be a list")
            return False
        
        for i, change in enumerate(changelog['changes']):
            if 'modifications' not in change:
                self.errors.append(f"Change {i} missing 'modifications' field")
                valid = False
            
            if 'timestamp' not in change:
                self.warnings.append(f"Change {i} missing timestamp")
            
            if 'summary' not in change:
                self.warnings.append(f"Change {i} missing summary")
        
        return valid
    
    def print_results(self):
        """Print validation results"""
        
        if not self.errors and not self.warnings:
            print("✅ All validations passed!")
            return True
        
        if self.errors:
            print(f"\n❌ Errors ({len(self.errors)}):")
            for error in self.errors:
                print(f"   • {error}")
        
        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        return len(self.errors) == 0


def validate_account(account_id: str, check_v2: bool = True) -> bool:
    """Validate all outputs for an account"""
    
    print(f"\n{'='*70}")
    print(f"Validating Account: {account_id}")
    print(f"{'='*70}\n")
    
    # Find account directory
    output_base = Path(os.getenv('STORAGE_PATH', './outputs'))
    accounts_dir = output_base / 'accounts'
    
    account_dir = None
    for d in accounts_dir.iterdir():
        if d.is_dir() and d.name.startswith(account_id):
            account_dir = d
            break
    
    if not account_dir:
        print(f"❌ Account directory not found for {account_id}")
        return False
    
    print(f"📁 Account Directory: {account_dir}\n")
    
    validator = OutputValidator()
    all_valid = True
    
    # Validate v1
    print("Validating v1 outputs...")
    print("─" * 70)
    
    v1_memo_path = account_dir / 'v1' / 'account_memo.json'
    v1_spec_path = account_dir / 'v1' / 'agent_spec.json'
    
    if not v1_memo_path.exists():
        print("❌ v1 account memo not found")
        all_valid = False
    else:
        with open(v1_memo_path, 'r') as f:
            v1_memo = json.load(f)
        
        print(f"Checking {v1_memo_path}...")
        if not validator.validate_memo(v1_memo, 'v1'):
            all_valid = False
        validator.print_results()
        validator.errors = []
        validator.warnings = []
    
    if not v1_spec_path.exists():
        print("❌ v1 agent spec not found")
        all_valid = False
    else:
        with open(v1_spec_path, 'r') as f:
            v1_spec = json.load(f)
        
        print(f"\nChecking {v1_spec_path}...")
        if not validator.validate_agent_spec(v1_spec, 'v1'):
            all_valid = False
        validator.print_results()
        validator.errors = []
        validator.warnings = []
    
    # Validate v2 if requested
    if check_v2:
        v2_dir = account_dir / 'v2'
        
        if not v2_dir.exists():
            print(f"\n⚠️  v2 directory not found (may not be created yet)")
        else:
            print(f"\n\nValidating v2 outputs...")
            print("─" * 70)
            
            v2_memo_path = v2_dir / 'account_memo.json'
            v2_spec_path = v2_dir / 'agent_spec.json'
            changelog_path = account_dir / 'changelog.json'
            
            if not v2_memo_path.exists():
                print("❌ v2 account memo not found")
                all_valid = False
            else:
                with open(v2_memo_path, 'r') as f:
                    v2_memo = json.load(f)
                
                print(f"Checking {v2_memo_path}...")
                if not validator.validate_memo(v2_memo, 'v2'):
                    all_valid = False
                validator.print_results()
                validator.errors = []
                validator.warnings = []
            
            if not v2_spec_path.exists():
                print("❌ v2 agent spec not found")
                all_valid = False
            else:
                with open(v2_spec_path, 'r') as f:
                    v2_spec = json.load(f)
                
                print(f"\nChecking {v2_spec_path}...")
                if not validator.validate_agent_spec(v2_spec, 'v2'):
                    all_valid = False
                validator.print_results()
                validator.errors = []
                validator.warnings = []
            
            if not changelog_path.exists():
                print(f"\n⚠️  Changelog not found: {changelog_path}")
            else:
                with open(changelog_path, 'r') as f:
                    changelog = json.load(f)
                
                print(f"\nChecking {changelog_path}...")
                if not validator.validate_changelog(changelog):
                    all_valid = False
                validator.print_results()
    
    print(f"\n{'='*70}")
    if all_valid:
        print("✅ ALL VALIDATIONS PASSED")
    else:
        print("❌ VALIDATION FAILED - Please review errors above")
    print(f"{'='*70}\n")
    
    return all_valid


def validate_all_accounts(check_v2: bool = True) -> Dict[str, bool]:
    """Validate all accounts in outputs directory"""
    
    output_base = Path(os.getenv('STORAGE_PATH', './outputs'))
    accounts_dir = output_base / 'accounts'
    
    if not accounts_dir.exists():
        print(f"❌ No accounts directory found: {accounts_dir}")
        return {}
    
    account_dirs = [d for d in accounts_dir.iterdir() if d.is_dir()]
    
    if not account_dirs:
        print(f"❌ No accounts found in {accounts_dir}")
        return {}
    
    print(f"\n{'='*70}")
    print(f"Validating All Accounts ({len(account_dirs)} found)")
    print(f"{'='*70}\n")
    
    results = {}
    
    for account_dir in sorted(account_dirs):
        account_id = account_dir.name.split('_')[0]
        results[account_id] = validate_account(account_id, check_v2)
    
    # Summary
    print(f"\n{'='*70}")
    print("VALIDATION SUMMARY")
    print(f"{'='*70}\n")
    
    passed = sum(1 for v in results.values() if v)
    failed = len(results) - passed
    
    print(f"Total Accounts: {len(results)}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    
    if failed > 0:
        print(f"\nFailed Accounts:")
        for account_id, valid in results.items():
            if not valid:
                print(f"  • {account_id}")
    
    print(f"\n{'='*70}\n")
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description='Validate pipeline outputs'
    )
    parser.add_argument(
        '--account-id',
        help='Specific account to validate (omit to validate all)'
    )
    parser.add_argument(
        '--v1-only',
        action='store_true',
        help='Only validate v1 outputs, skip v2'
    )
    
    args = parser.parse_args()
    
    from dotenv import load_dotenv
    load_dotenv()
    
    try:
        if args.account_id:
            success = validate_account(args.account_id, check_v2=not args.v1_only)
        else:
            results = validate_all_accounts(check_v2=not args.v1_only)
            success = all(results.values())
        
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"\n❌ Validation error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
