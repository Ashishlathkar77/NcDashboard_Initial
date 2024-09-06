def generate_prompt(user_query, metadata):
    prompt = (
        "You are an expert Python software engineer. "
        "You have an xarray dataset with the following variables and metadata:\n\n"
    )

    for var, details in metadata.items():
        prompt += (
            f"Variable: {var}, Dimensions: {details['dims']}, "
            f"Shape: {details['shape']}, Units: {details['units']}\n"
        )

    prompt += f"\nPlease {user_query} using only xarray and numpy libraries."
    return prompt