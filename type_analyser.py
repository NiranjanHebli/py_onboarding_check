def analyze_value(value):
    """
    Analyzes a Python value to determine its type, truthiness, and length.
    
    Args:
        value: Any Python object.
        
    Returns:
        str: A formatted summary of the value's attributes.
    """
    # 1. Extract the name of the type (e.g., 'int' instead of <class 'int'>)
    val_type = type(value).__name__
    
    # 2. Determine the Truthiness (bool evaluation)
    truthy = bool(value)
    
    # 3. Handle length calculation safely
    try:
        length = len(value)
    except TypeError:
        # This executes if the value type has no len() method
        length = "N/A"
        
    return f"Value: {value} | Type: {val_type} | Truthy: {truthy} | Length: {length}"

# --- Testing the Function ---
print(analyze_value(42))        # Integer: No length
print(analyze_value(""))        # Empty string: Falsy, Length 0
print(analyze_value([1, 2, 3])) # List: Truthy, Length 3
print(analyze_value(None))      # NoneType: Falsy, No length