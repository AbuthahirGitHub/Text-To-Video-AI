def generate_script(script_text):
    """
    Simply returns the provided script text without any AI processing.
    Args:
        script_text (str): The script text provided by the user
    Returns:
        str: The same script text
    """
    if not script_text or not isinstance(script_text, str):
        raise ValueError("Please provide a valid script text")
    
    return script_text.strip() 