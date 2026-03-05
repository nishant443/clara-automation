#!/usr/bin/env python3
"""
Clara Answers - Agent Prompt Generator
Generates production-ready Retell agent system prompts from account memos
"""

import json
from typing import Dict, Any, List
from datetime import datetime


class PromptGenerator:
    """Generates Retell agent system prompts with proper conversation hygiene"""
    
    def __init__(self):
        self.version = "1.0.0"
    
    def generate_agent_spec(self, account_memo: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate complete Retell agent specification from account memo
        
        Args:
            account_memo: Structured account data
            
        Returns:
            Complete agent specification including system prompt
        """
        
        system_prompt = self._build_system_prompt(account_memo)
        
        agent_spec = {
            "agent_name": f"Clara - {account_memo.get('company_name', 'Untitled')}",
            "version": account_memo.get('version', 'v1'),
            "voice_config": {
                "provider": "eleven_labs",
                "voice_id": "professional_female",
                "speed": 1.0,
                "stability": 0.8,
                "clarity": 0.75
            },
            "system_prompt": system_prompt,
            "variables": self._extract_variables(account_memo),
            "conversation_config": {
                "max_duration_minutes": 10,
                "interruption_sensitivity": "medium",
                "end_call_phrases": ["goodbye", "that's all", "nothing else", "no thank you"],
                "silence_timeout_seconds": 10
            },
            "tool_placeholders": {
                "transfer_call": {
                    "enabled": True,
                    "timeout": account_memo.get('call_transfer_rules', {}).get('timeout_seconds', 60),
                    "max_retries": account_memo.get('call_transfer_rules', {}).get('max_retries', 2)
                },
                "create_ticket": {
                    "enabled": False,
                    "note": "Reserved for future ServiceTrade integration"
                }
            },
            "transfer_protocol": self._build_transfer_protocol(account_memo),
            "fallback_protocol": self._build_fallback_protocol(account_memo),
            "created_at": datetime.utcnow().isoformat() + 'Z',
            "updated_at": datetime.utcnow().isoformat() + 'Z'
        }
        
        return agent_spec
    
    def _build_system_prompt(self, memo: Dict[str, Any]) -> str:
        """Build the core system prompt with business and after-hours flows"""
        
        company_name = memo.get('company_name', 'the company')
        services = memo.get('services_supported', [])
        emergency_defs = memo.get('emergency_definition', [])
        business_hours = memo.get('business_hours', {})
        integration_constraints = memo.get('integration_constraints', [])
        special_rules = memo.get('special_rules', [])
        
        # Format business hours
        hours_text = self._format_business_hours(business_hours)
        
        # Format emergency definitions
        emergency_text = self._format_emergency_definitions(emergency_defs)
        
        # Build the prompt
        prompt = f"""You are Clara, the AI receptionist for {company_name}. You handle inbound calls professionally, efficiently, and empathetically.

## YOUR ROLE
You answer calls, identify the caller's needs, collect necessary information, and route calls appropriately. You represent {company_name} with professionalism and care.

## SERVICES WE PROVIDE
{self._format_list(services) if services else "- Multiple service offerings"}

## BUSINESS HOURS
{hours_text}

## EMERGENCY VS NON-EMERGENCY

### What Counts as an Emergency:
{emergency_text}

### What is NOT an Emergency:
- Routine service requests
- Inspection scheduling
- General questions
- Billing inquiries

---

## CONVERSATION FLOW

### DURING BUSINESS HOURS ({hours_text})

1. **Greeting**
   - "Thank you for calling {company_name}, this is Clara. How can I help you today?"

2. **Identify Purpose**
   - Listen to caller's reason
   - Determine if emergency or non-emergency

3. **Collect Information**
   - Get caller's name: "May I have your name please?"
   - Get callback number: "And what's the best number to reach you?"
   - For emergencies: Also get location/address

4. **Route the Call**
   - "Let me connect you with someone who can help right away."
   - Initiate transfer (use internal transfer function - do not mention this to caller)
   - Stay on line during transfer

5. **Transfer Fallback** (if no answer after timeout)
   - "I apologize, I'm having trouble reaching someone at the moment."
   - "I have your name as [name] and your callback number as [number]."
   - "Someone from our team will call you back within 30 minutes."
   - For emergencies: "Given this is urgent, let me also make sure dispatch is notified immediately."

6. **Wrap Up**
   - "Is there anything else I can help you with today?"
   - If yes: handle additional request
   - If no: "Thank you for calling {company_name}. Have a great day!"

### AFTER BUSINESS HOURS

1. **Greeting**
   - "Thank you for calling {company_name}, this is Clara. Our office is currently closed, but I'm here to help."
   - State hours: "We're open {hours_text}."

2. **Identify Purpose**
   - "What can I help you with?"

3. **Determine Urgency**
   - "Is this an emergency situation?"
   - Confirm based on emergency definitions

4. **If EMERGENCY:**
   - "I understand this is urgent. Let me get your information quickly."
   - Collect in this order:
     * Name
     * Phone number
     * Exact location/address
     * Brief description of the emergency
   - "I'm going to connect you with our on-call technician right away."
   - Attempt transfer to emergency contact
   - **If transfer fails:**
     * "I apologize for the delay. I have all your information."
     * "Our on-call technician will receive this immediately and call you back within 15 minutes."
     * "For your records, you called about [brief emergency description] at [location]."

5. **If NON-EMERGENCY:**
   - "I understand. Since this isn't an emergency, let me take down your information."
   - Collect:
     * Name
     * Phone number
     * Brief description of what you need
   - "Thank you. Someone from our team will call you back when we open at [opening time]."

6. **Wrap Up**
   - "Is there anything else I can help you with?"
   - If no: "Thank you for calling {company_name}. We'll be in touch soon."

---

## IMPORTANT RULES

### Conversation Hygiene:
- Be warm but professional
- Keep questions concise - only collect what you need
- Don't ask the same question twice
- Repeat critical information back to confirm (phone numbers, addresses)
- Use natural transitions, not robotic scripts

### Transfer Handling:
- NEVER say "I'm using a function" or mention "API calls" or "tools"
- Simply say "Let me connect you" or "I'm transferring you now"
- If transfer is taking time: "Please hold while I connect you"
- Monitor transfer timeout internally

### Information Collection:
- Get name and callback number for ALL calls
- Get address ONLY for emergencies
- Don't ask for information you don't need
- Be respectful of caller's time

### Special Constraints:
{self._format_constraints(integration_constraints, special_rules)}

### Emergency Protocols:
- Treat all emergency calls with urgency
- Never delay an emergency caller with unnecessary questions
- Prioritize immediate human connection for emergencies
- If on-call doesn't answer emergency: escalate internally and assure caller

---

## TONE & STYLE

- **Empathetic**: Show you understand their situation
- **Efficient**: Don't waste their time
- **Professional**: You represent {company_name}
- **Clear**: Use simple language
- **Calm**: Especially during emergencies

---

## EDGE CASES

**Angry or frustrated caller:**
- Stay calm and empathetic
- "I understand your frustration. Let me make sure we get this handled."
- Don't argue or get defensive

**Caller asks if you're AI:**
- "I'm Clara, the AI assistant for {company_name}. I'm here to help get you connected with the right person."
- Don't pretend to be human if asked directly

**Unclear request:**
- "Just to make sure I understand correctly, you need help with [restate]?"
- Seek clarification politely

**Multiple issues in one call:**
- Handle them one at a time
- "Let me help you with [first issue] first, then we'll address [second issue]."

**Language barrier:**
- Speak slowly and clearly
- Use simple words
- Confirm understanding: "Did I understand correctly that..."

---

## WHAT NOT TO DO

❌ Don't mention "transferring to function" or technical operations
❌ Don't ask unnecessary questions
❌ Don't make promises about response times you can't control (unless specified)
❌ Don't handle billing, technical troubleshooting, or complex questions - transfer or take message
❌ Don't stay on a call longer than necessary
❌ Don't be overly chatty or casual with emergency callers

---

Remember: You are the first point of contact for {company_name}. Every interaction shapes their impression of the company. Be professional, efficient, and genuinely helpful."""

        return prompt
    
    def _format_business_hours(self, hours: Dict[str, Any]) -> str:
        """Format business hours into readable text"""
        if not hours or not hours.get('schedule'):
            return "Business hours not yet confirmed"
        
        schedule = hours.get('schedule', [])
        timezone = hours.get('timezone', '')
        
        if not schedule:
            return "Business hours not yet confirmed"
        
        # Group consecutive days with same hours
        grouped = []
        current_group = None
        
        for day_info in schedule:
            day = day_info.get('day', '')
            open_time = day_info.get('open', '')
            close_time = day_info.get('close', '')
            hours_str = f"{open_time}-{close_time}"
            
            if current_group and current_group['hours'] == hours_str:
                current_group['days'].append(day)
            else:
                if current_group:
                    grouped.append(current_group)
                current_group = {'days': [day], 'hours': hours_str}
        
        if current_group:
            grouped.append(current_group)
        
        # Format output
        lines = []
        for group in grouped:
            days = group['days']
            if len(days) == 1:
                day_str = days[0]
            elif len(days) == 2:
                day_str = f"{days[0]} and {days[1]}"
            else:
                day_str = f"{days[0]}-{days[-1]}"
            lines.append(f"{day_str}: {group['hours']}")
        
        result = "\n".join(lines)
        if timezone:
            result += f"\nTimezone: {timezone}"
        
        return result
    
    def _format_emergency_definitions(self, emergencies: List[str]) -> str:
        """Format emergency definitions into bullet points"""
        if not emergencies:
            return "- Emergency situations will be determined case-by-case"
        
        formatted = []
        for item in emergencies:
            # Convert snake_case to readable text
            readable = item.replace('_', ' ').title()
            formatted.append(f"- {readable}")
        
        return "\n".join(formatted)
    
    def _format_list(self, items: List[str]) -> str:
        """Format a list into bullet points"""
        if not items:
            return "- (To be determined)"
        
        formatted = []
        for item in items:
            readable = item.replace('_', ' ').title()
            formatted.append(f"- {readable}")
        
        return "\n".join(formatted)
    
    def _format_constraints(self, integration: List[str], special: List[str]) -> str:
        """Format constraints and special rules"""
        all_constraints = integration + special
        if not all_constraints:
            return "- No special constraints at this time"
        
        formatted = []
        for constraint in all_constraints:
            formatted.append(f"- {constraint}")
        
        return "\n".join(formatted)
    
    def _extract_variables(self, memo: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key variables for easy reference"""
        
        hours = memo.get('business_hours', {})
        schedule = hours.get('schedule', [])
        
        # Simplified hours string
        if schedule:
            first_day = schedule[0]
            hours_str = f"{first_day.get('open', '')}-{first_day.get('close', '')}"
        else:
            hours_str = "Hours TBD"
        
        emergency_rules = memo.get('emergency_routing_rules', {})
        primary_contact = emergency_rules.get('primary', {})
        
        return {
            "company_name": memo.get('company_name', ''),
            "timezone": hours.get('timezone', 'America/New_York'),
            "business_hours_simple": hours_str,
            "emergency_phone": primary_contact.get('phone', ''),
            "emergency_contact_name": primary_contact.get('name', 'on-call technician'),
            "office_address": self._format_address(memo.get('office_address', {}))
        }
    
    def _format_address(self, address: Dict[str, str]) -> str:
        """Format address into single line"""
        parts = [
            address.get('street', ''),
            address.get('city', ''),
            address.get('state', ''),
            address.get('zip', '')
        ]
        return ", ".join([p for p in parts if p])
    
    def _build_transfer_protocol(self, memo: Dict[str, Any]) -> str:
        """Build transfer protocol description"""
        transfer_rules = memo.get('call_transfer_rules', {})
        timeout = transfer_rules.get('timeout_seconds', 60)
        retries = transfer_rules.get('max_retries', 2)
        
        return f"Attempt transfer with {timeout}s timeout. Retry up to {retries} times if initial attempt fails. Monitor connection status internally without mentioning to caller."
    
    def _build_fallback_protocol(self, memo: Dict[str, Any]) -> str:
        """Build fallback protocol description"""
        transfer_rules = memo.get('call_transfer_rules', {})
        failure_msg = transfer_rules.get('failure_message', '')
        
        if failure_msg:
            return failure_msg
        
        return "If transfer fails after all retries: apologize professionally, confirm you have their information (name, number, and issue details), assure them someone will call back within 30 minutes, and offer to help with anything else."


if __name__ == "__main__":
    print("Prompt Generator loaded successfully")
    print("Use pipeline_a_demo.py or pipeline_b_onboarding.py to generate prompts")
