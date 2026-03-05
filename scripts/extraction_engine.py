#!/usr/bin/env python3
"""
Clara Answers - Extraction Engine
Extracts structured data from demo/onboarding call transcripts using Claude API
"""

import os
import json
import anthropic
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


class ExtractionEngine:
    """Handles structured data extraction from call transcripts"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")
        self.client = anthropic.Anthropic(api_key=self.api_key)
        
    def extract_demo_data(self, transcript: str, account_id: str) -> Dict[str, Any]:
        """
        Extract preliminary account data from demo call transcript
        
        Args:
            transcript: Full text of demo call
            account_id: Unique account identifier
            
        Returns:
            Structured account memo (v1) as dictionary
        """
        
        prompt = f"""You are analyzing a demo call transcript for Clara Answers, an AI voice agent service for trade businesses (fire protection, sprinklers, alarms, HVAC, electrical).

CRITICAL RULES:
1. Extract ONLY explicitly stated information
2. Do NOT invent or assume missing details
3. If information is missing, leave field blank or add to "questions_or_unknowns"
4. This is a DEMO call - expect incomplete information
5. Focus on directional understanding, not final specifications

TRANSCRIPT:
{transcript}

Extract the following information and respond ONLY with valid JSON (no markdown, no preamble):

{{
  "account_id": "{account_id}",
  "version": "v1",
  "company_name": "",
  "business_type": "",
  "business_hours": {{
    "timezone": "",
    "schedule": []
  }},
  "office_address": {{
    "street": "",
    "city": "",
    "state": "",
    "zip": ""
  }},
  "services_supported": [],
  "emergency_definition": [],
  "emergency_routing_rules": {{
    "primary": {{}},
    "fallback": {{}}
  }},
  "non_emergency_routing_rules": {{}},
  "call_transfer_rules": {{
    "timeout_seconds": null,
    "max_retries": null,
    "failure_message": ""
  }},
  "integration_constraints": [],
  "pain_points_mentioned": [],
  "after_hours_flow_summary": "",
  "office_hours_flow_summary": "",
  "questions_or_unknowns": [],
  "notes": "",
  "created_at": "{datetime.utcnow().isoformat()}Z",
  "updated_at": "{datetime.utcnow().isoformat()}Z"
}}

EXTRACTION GUIDELINES:

**company_name**: Exact name mentioned
**business_type**: One of: fire_protection, sprinkler_contractor, alarm_contractor, electrical, hvac, facility_maintenance, other
**business_hours**: Only if explicitly stated. Format schedule as [{{"day": "Monday", "open": "HH:MM", "close": "HH:MM"}}]
**services_supported**: List services mentioned (e.g., ["sprinkler_repair", "fire_alarm_installation", "inspection"])
**emergency_definition**: What constitutes an emergency for this business (e.g., ["sprinkler_leak", "fire_alarm_triggered", "no_water_flow"])
**emergency_routing_rules**: Who gets emergency calls, in what order
**pain_points_mentioned**: Current problems they're trying to solve
**questions_or_unknowns**: List anything critical that wasn't mentioned
**notes**: Brief summary of key takeaways (2-3 sentences max)

Remember: This is a demo call. Missing information is EXPECTED and NORMAL."""

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                temperature=0.0,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Extract JSON from response
            response_text = message.content[0].text
            
            # Try to parse JSON directly
            try:
                extracted_data = json.loads(response_text)
            except json.JSONDecodeError:
                # If response has markdown formatting, strip it
                if "```json" in response_text:
                    json_str = response_text.split("```json")[1].split("```")[0].strip()
                    extracted_data = json.loads(json_str)
                elif "```" in response_text:
                    json_str = response_text.split("```")[1].split("```")[0].strip()
                    extracted_data = json.loads(json_str)
                else:
                    raise ValueError("Could not extract valid JSON from response")
            
            # Add extraction metadata
            extracted_data['_extraction_metadata'] = {
                'model': 'claude-sonnet-4-20250514',
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'transcript_length': len(transcript),
                'extraction_type': 'demo_call'
            }
            
            return extracted_data
            
        except Exception as e:
            raise RuntimeError(f"Extraction failed: {str(e)}")
    
    def extract_onboarding_data(self, transcript: str, account_id: str, 
                               existing_memo: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract onboarding updates and merge with existing account data
        
        Args:
            transcript: Full text of onboarding call or form
            account_id: Unique account identifier
            existing_memo: The v1 account memo to update
            
        Returns:
            Updated account memo (v2) as dictionary
        """
        
        prompt = f"""You are analyzing an onboarding call/form for Clara Answers. This is a CONFIGURATION-FOCUSED session that provides operational precision.

EXISTING ACCOUNT DATA (v1 from demo call):
{json.dumps(existing_memo, indent=2)}

NEW ONBOARDING TRANSCRIPT/FORM DATA:
{transcript}

CRITICAL RULES:
1. This onboarding data OVERRIDES or REFINES the demo assumptions
2. Extract ONLY explicitly stated new information
3. PRESERVE existing data unless explicitly contradicted or refined
4. Mark what changed and why
5. Do NOT invent missing details
6. Focus on: exact hours, timezone, emergency definitions, routing logic, integration rules, special constraints

Extract updates and respond ONLY with valid JSON (no markdown):

{{
  "account_id": "{account_id}",
  "version": "v2",
  "company_name": "",
  "business_type": "",
  "business_hours": {{
    "timezone": "",
    "schedule": []
  }},
  "office_address": {{
    "street": "",
    "city": "",
    "state": "",
    "zip": ""
  }},
  "services_supported": [],
  "emergency_definition": [],
  "emergency_routing_rules": {{
    "primary": {{}},
    "secondary": {{}},
    "fallback": {{}}
  }},
  "non_emergency_routing_rules": {{}},
  "call_transfer_rules": {{
    "timeout_seconds": null,
    "max_retries": null,
    "failure_message": "",
    "dispatch_notification": ""
  }},
  "integration_constraints": [],
  "special_rules": [],
  "after_hours_flow_summary": "",
  "office_hours_flow_summary": "",
  "questions_or_unknowns": [],
  "notes": "",
  "created_at": "{existing_memo.get('created_at', '')}",
  "updated_at": "{datetime.utcnow().isoformat()}Z"
}}

ONBOARDING-SPECIFIC EXTRACTIONS:

**business_hours**: Exact confirmed hours. Look for timezone mentions.
**emergency_definition**: Precise emergency triggers
**routing_rules**: Exact phone numbers, names, escalation paths
**call_transfer_rules.timeout_seconds**: Exact timeout if mentioned (e.g., "60 seconds", "1 minute" → 60)
**special_rules**: Constraints like "never create sprinkler jobs in ServiceTrade", "all emergencies go to phone tree", "don't book on Wednesdays"
**integration_constraints**: ServiceTrade rules, CRM limitations, etc.

MERGE LOGIC:
- If onboarding provides MORE detail, use it
- If onboarding CONTRADICTS demo, use onboarding (it's authoritative)
- If onboarding DOESN'T mention something, keep demo data
- Clear "questions_or_unknowns" if they're now answered"""

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                temperature=0.0,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text
            
            # Parse JSON
            try:
                updated_data = json.loads(response_text)
            except json.JSONDecodeError:
                if "```json" in response_text:
                    json_str = response_text.split("```json")[1].split("```")[0].strip()
                    updated_data = json.loads(json_str)
                elif "```" in response_text:
                    json_str = response_text.split("```")[1].split("```")[0].strip()
                    updated_data = json.loads(json_str)
                else:
                    raise ValueError("Could not extract valid JSON from response")
            
            # Add extraction metadata
            updated_data['_extraction_metadata'] = {
                'model': 'claude-sonnet-4-20250514',
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'transcript_length': len(transcript),
                'extraction_type': 'onboarding_update',
                'previous_version': 'v1'
            }
            
            return updated_data
            
        except Exception as e:
            raise RuntimeError(f"Onboarding extraction failed: {str(e)}")
    
    def generate_changelog(self, v1_memo: Dict[str, Any], v2_memo: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate detailed changelog between v1 and v2
        
        Args:
            v1_memo: Original demo-derived account memo
            v2_memo: Updated onboarding-refined account memo
            
        Returns:
            Changelog dictionary
        """
        
        def compare_values(path: str, old_val: Any, new_val: Any) -> Optional[Dict[str, Any]]:
            """Compare two values and generate change record if different"""
            # Skip metadata fields
            if path.startswith('_') or path in ['created_at', 'updated_at', 'version']:
                return None
            
            if old_val == new_val:
                return None
            
            # Determine change type
            if old_val is None or old_val == "" or old_val == []:
                action = "added"
                reason = "New information provided during onboarding"
            elif new_val is None or new_val == "" or new_val == []:
                action = "removed"
                reason = "Clarified as not applicable"
            else:
                action = "updated"
                reason = "Refined during onboarding"
            
            return {
                "field": path,
                "action": action,
                "old_value": old_val,
                "new_value": new_val,
                "reason": reason
            }
        
        def deep_compare(obj1: Any, obj2: Any, path: str = "") -> list:
            """Recursively compare nested dictionaries"""
            changes = []
            
            if isinstance(obj1, dict) and isinstance(obj2, dict):
                all_keys = set(obj1.keys()) | set(obj2.keys())
                for key in all_keys:
                    new_path = f"{path}.{key}" if path else key
                    val1 = obj1.get(key)
                    val2 = obj2.get(key)
                    
                    if isinstance(val1, dict) and isinstance(val2, dict):
                        changes.extend(deep_compare(val1, val2, new_path))
                    elif isinstance(val1, list) and isinstance(val2, list):
                        if val1 != val2:
                            change = compare_values(new_path, val1, val2)
                            if change:
                                changes.append(change)
                    else:
                        change = compare_values(new_path, val1, val2)
                        if change:
                            changes.append(change)
            
            return changes
        
        modifications = deep_compare(v1_memo, v2_memo)
        
        # Generate summary
        summary_parts = []
        if any(m['action'] == 'added' for m in modifications):
            added_count = sum(1 for m in modifications if m['action'] == 'added')
            summary_parts.append(f"Added {added_count} new field(s)")
        if any(m['action'] == 'updated' for m in modifications):
            updated_count = sum(1 for m in modifications if m['action'] == 'updated')
            summary_parts.append(f"Updated {updated_count} field(s)")
        if any(m['action'] == 'removed' for m in modifications):
            removed_count = sum(1 for m in modifications if m['action'] == 'removed')
            summary_parts.append(f"Removed {removed_count} field(s)")
        
        summary = "; ".join(summary_parts) if summary_parts else "No changes detected"
        
        changelog = {
            "account_id": v2_memo.get('account_id'),
            "changes": [
                {
                    "timestamp": datetime.utcnow().isoformat() + 'Z',
                    "from_version": "v1",
                    "to_version": "v2",
                    "change_type": "onboarding_update",
                    "modifications": modifications,
                    "summary": summary
                }
            ]
        }
        
        return changelog


if __name__ == "__main__":
    # Quick test
    print("Extraction Engine loaded successfully")
    print("Use pipeline_a_demo.py or pipeline_b_onboarding.py to run extractions")
