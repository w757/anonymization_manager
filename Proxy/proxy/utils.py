import uuid

def validate_uuid(value):
    try:
        uuid.UUID(str(value))
        return True
    except ValueError:
        return False
