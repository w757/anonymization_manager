from faker import Faker
import re
from typing import Dict, Optional
from datetime import datetime

fake = Faker()

def identify_data_type(value: str) -> Dict[str, str]:
    """
    Identify data type based on example value.
    Returns dictionary with type, category and suggested anonymization method.
    """
    # Default result for unknown types
    default_result = {
        "type": "unknown",
        "category": "other",
        "suggested_method": None
    }
    
    if not value or not isinstance(value, str):
        return default_result
    
    try:
        # Check for email
        if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
            return {
                "type": "email",
                "category": "personal_data",
                "suggested_method": "masking"
            }
        
        # Check for phone number (international format)
        if re.match(r'^\+?[\d\s-]{9,}$', value.replace(" ", "")):
            return {
                "type": "phone_number",
                "category": "personal_data",
                "suggested_method": "encryption"
            }
        
        # Check for date (YYYY-MM-DD)
        try:
            datetime.strptime(value, '%Y-%m-%d')
            return {
                "type": "date",
                "category": "personal_data",
                "suggested_method": "partial_masking"
            }
        except ValueError:
            pass
        
        # Check for password (basic complexity check)
        if len(value) >= 8 and any(c.isupper() for c in value) and any(c.isdigit() for c in value):
            return {
                "type": "password",
                "category": "sensitive_data",
                "suggested_method": "hashing"
            }
        
        # Check for names using Faker
        name_parts = value.split()
        if name_parts and (name_parts[0] in fake.first_names() or (len(name_parts) > 1 and name_parts[-1] in fake.last_names())):
            return {
                "type": "person_name",
                "category": "personal_data",
                "suggested_method": "pseudonymization"
            }
        
        # Check for addresses
        if any(part in value.lower() for part in ['ul.', 'street', 'avenue', 'al.', 'aleja', 'st.']):
            return {
                "type": "address",
                "category": "personal_data",
                "suggested_method": "generalization"
            }
        
        # Check for numeric IDs
        if value.isdigit() and len(value) > 3:
            return {
                "type": "numeric_id",
                "category": "identifier",
                "suggested_method": "tokenization"
            }
        
        # Fallback to Faker's detection
        try:
            if fake.validate_email(value):
                return {
                    "type": "email",
                    "category": "personal_data",
                    "suggested_method": "masking"
                }
        except:
            pass
        
        # If value looks like random string (UUID, token etc.)
        if len(value) > 20 and '-' in value:
            return {
                "type": "token",
                "category": "identifier",
                "suggested_method": "tokenization"
            }
        
    except Exception as e:
        print(f"Error during data type identification: {e}")
    
    return default_result

def analyze_field(field_name: str, example_value: Optional[str]) -> Dict[str, str]:
    """
    Analyze field based on both field name and example value.
    Returns consistent dictionary structure even when identification fails.
    """
    # Default result structure
    result = {
        "name": field_name,
        "type": "unknown",
        "category": "other",
        "suggested_method": None,
        "confidence": "low"
    }
    
    if not field_name or not isinstance(field_name, str):
        return result
    
    try:
        field_name_lower = field_name.lower()
        
        # First try to identify by field name patterns
        if "email" in field_name_lower:
            return {
                **result,
                "type": "email",
                "category": "personal_data",
                "suggested_method": "masking",
                "confidence": "high"
            }
        elif "phone" in field_name_lower or "tel" in field_name_lower:
            return {
                **result,
                "type": "phone_number",
                "category": "personal_data",
                "suggested_method": "encryption",
                "confidence": "high"
            }
        elif "password" in field_name_lower or "pass" in field_name_lower:
            return {
                **result,
                "type": "password",
                "category": "sensitive_data",
                "suggested_method": "hashing",
                "confidence": "high"
            }
        elif "date" in field_name_lower or "dob" in field_name_lower:
            return {
                **result,
                "type": "date",
                "category": "personal_data",
                "suggested_method": "partial_masking",
                "confidence": "high"
            }
        elif "name" in field_name_lower:
            return {
                **result,
                "type": "person_name",
                "category": "personal_data",
                "suggested_method": "pseudonymization",
                "confidence": "high"
            }
        elif "address" in field_name_lower or "addr" in field_name_lower:
            return {
                **result,
                "type": "address",
                "category": "personal_data",
                "suggested_method": "generalization",
                "confidence": "high"
            }
        elif "id" in field_name_lower:
            return {
                **result,
                "type": "identifier",
                "category": "identifier",
                "suggested_method": "tokenization",
                "confidence": "medium"
            }
        
        # If not identified by name, try by value
        if example_value and isinstance(example_value, str):
            value_analysis = identify_data_type(example_value)
            return {
                **result,
                **value_analysis,
                "confidence": "medium" if value_analysis["type"] != "unknown" else "low"
            }
            
    except Exception as e:
        print(f"Error during field analysis: {e}")
    
    return result

# # Example usage
# if __name__ == "__main__":
#     test_cases = [
#         ("email", "user@example.com"),
#         ("phone_number", "+48 123 456 789"),
#         ("password", "SecurePass123!"),
#         ("birth_date", "1990-01-15"),
#         ("full_name", "John Doe"),
#         ("home_address", "ul. Example 123, Warsaw"),
#         ("user_id", "12345"),
#         ("unknown_field", "some random value")
#     ]
    
#     for field_name, example_value in test_cases:
#         analysis = analyze_field(field_name, example_value)
#         print(f"Field: {field_name}, Value: {example_value}")
#         print(f"Analysis: {analysis}\n")