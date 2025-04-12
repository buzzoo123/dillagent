import json
import re
from .BaseIntermediateParser import BaseIntermediateParser

class PlanningJsonParser(BaseIntermediateParser):
    """
    A parser specifically designed for the planning agent workflow.
    It attempts to extract JSON objects from LLM responses, with special handling
    for the planning agent's expected format.
    """
    
    def __init__(self):
        super().__init__()
    
    def parse_values(self, text):
        """
        Parse the LLM response text to extract a JSON object.
        
        This parser looks for JSON objects in the text and extracts them.
        It has special handling for common LLM output formats.
        
        Returns:
            dict: The parsed JSON object
        """
        # Try to find a complete JSON object in the text
        json_pattern = r'({[^{}]*(?:{[^{}]*})*[^{}]*})'
        
        # First, check if the entire text is valid JSON
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # Look for JSON blocks in code blocks (```json ... ```)
        code_block_match = re.search(r'```(?:json)?\s*(.*?)\s*```', text, re.DOTALL)
        if code_block_match:
            try:
                return json.loads(code_block_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Try to extract JSON using regex
        json_matches = re.findall(json_pattern, text)
        for json_str in json_matches:
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                continue
        
        # If we still don't have valid JSON, try to find the most promising candidate
        # and fix common issues
        
        # Look for the largest {...} block
        brace_pattern = r'({[\s\S]*?})'
        brace_matches = re.findall(brace_pattern, text, re.DOTALL)
        
        if brace_matches:
            # Sort by length to find the longest match (likely the most complete JSON)
            brace_matches.sort(key=len, reverse=True)
            
            for json_candidate in brace_matches:
                # Fix common JSON formatting issues
                # 1. Fix single quotes to double quotes
                fixed_json = json_candidate.replace("'", '"')
                
                # 2. Fix unquoted keys
                fixed_json = re.sub(r'([{,])\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', fixed_json)
                
                # 3. Remove trailing commas
                fixed_json = re.sub(r',\s*}', '}', fixed_json)
                fixed_json = re.sub(r',\s*]', ']', fixed_json)
                
                try:
                    return json.loads(fixed_json)
                except json.JSONDecodeError:
                    continue
        
        # If all parsing attempts fail, create a structured representation from the text
        # For the planning agent, we need at least a minimal structure
        if "terminate" in text.lower():
            return {"terminate": True, "reason": "Parsing failed, but 'terminate' keyword found"}
        
        # Extract any agent names mentioned
        agent_names = re.findall(r'([A-Z][a-z]*Agent)', text)
        next_agents = list(set(agent_names))  # Remove duplicates
        
        # Build a minimal plan dict
        return {
            "raw_output": text,
            "next_agents": next_agents if next_agents else [],
            "terminate": False
        }