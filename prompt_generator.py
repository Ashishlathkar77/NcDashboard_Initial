def generate_prompt(metadata):
    if 'error' in metadata:
        return f"Error processing file: {metadata['error']}"
    
    variables = ', '.join(metadata['variables'])
    dimensions = ', '.join(metadata['dimensions'])
    attributes = json.dumps(metadata['attributes'], indent=2)
    
    prompt = (
        "## Metadata Information\n"
        "### Variables:\n"
        f"{variables}\n\n"
        "### Dimensions:\n"
        f"{dimensions}\n\n"
        "### Attributes:\n"
        f"{attributes}\n"
    )
    return prompt
