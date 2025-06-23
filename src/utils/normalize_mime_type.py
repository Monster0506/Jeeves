def normalize_mime_type(mime_type: str) -> str:
    """
    Normalize MIME types for better AI provider compatibility.
    
    Args:
        mime_type: The MIME type to normalize
        
    Returns:
        Normalized MIME type string
    """
    if not mime_type:
        return 'application/octet-stream'
    
    # Normalize common MIME type variations
    mime_type = mime_type.lower().strip()
    
    # Check if the string is empty after stripping
    if not mime_type:
        return 'application/octet-stream'
    
    # Audio format normalizations
    if mime_type == "audio/mpeg":
        mime_type = "audio/mp3"
    elif mime_type == "application/ogg":
        mime_type = "audio/ogg"
    elif mime_type == "audio/x-m4a":
        mime_type = "audio/mp4"
    elif mime_type == "audio/x-wav":
        mime_type = "audio/wav"
    
    # Video format normalizations
    elif mime_type == "video/x-msvideo":
        mime_type = "video/avi"
    elif mime_type == "video/x-ms-wmv":
        mime_type = "video/wmv"
    elif mime_type == "video/quicktime":
        mime_type = "video/mp4"
    
    # Image format normalizations
    elif mime_type == "image/x-png":
        mime_type = "image/png"
    elif mime_type == "image/x-jpeg":
        mime_type = "image/jpeg"
    elif mime_type == "image/x-gif":
        mime_type = "image/gif"
    elif mime_type == "image/x-bmp":
        mime_type = "image/bmp"
    elif mime_type == "image/x-tiff":
        mime_type = "image/tiff"
    
    # Document format normalizations
    elif mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif mime_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif mime_type == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
        mime_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    
    return mime_type 