import os
import logging
from typing import Dict

logger = logging.getLogger(__name__)

# Mappings of extensions (with dot, lowercase) to categories
EXTENSION_MAP: Dict[str, str] = {
    # Media
    ".png": "Media", ".jpg": "Media", ".jpeg": "Media", ".gif": "Media", ".bmp": "Media",
    ".mp3": "Media", ".wav": "Media", ".mp4": "Media", ".mkv": "Media", ".avi": "Media",
    ".mov": "Media", ".flac": "Media", ".ogg": "Media", ".webm": "Media", ".svg": "Media",
    ".ico": "Media", ".tiff": "Media", ".webp": "Media",
    
    # Documents
    ".pdf": "Documents", ".docx": "Documents", ".doc": "Documents", ".xlsx": "Documents",
    ".xls": "Documents", ".pptx": "Documents", ".ppt": "Documents", ".txt": "Documents",
    ".rtf": "Documents", ".odt": "Documents", ".csv": "Documents", ".md": "Documents",
    
    # Code
    ".py": "Code", ".js": "Code", ".ts": "Code", ".html": "Code", ".css": "Code",
    ".json": "Code", ".java": "Code", ".c": "Code", ".cpp": "Code", ".h": "Code",
    ".cs": "Code", ".go": "Code", ".rs": "Code", ".php": "Code", ".rb": "Code",
    ".sh": "Code", ".bat": "Code", ".ps1": "Code", ".xml": "Code", ".yaml": "Code",
    ".yml": "Code", ".sql": "Code",
    
    # Archives
    ".zip": "Archives", ".tar": "Archives", ".gz": "Archives", ".rar": "Archives",
    ".7z": "Archives", ".bz2": "Archives", ".tgz": "Archives",
    
    # Temp
    ".tmp": "Temp", ".temp": "Temp", ".bak": "Temp", ".log": "Temp", ".cache": "Temp"
}

# Magic bytes signature mapping
MAGIC_BYTES_MAP: Dict[bytes, str] = {
    b"\xff\xd8\xff": "Media",        # JPEG
    b"\x89PNG\r\n": "Media",        # PNG
    b"GIF8": "Media",               # GIF
    b"%PDF": "Documents",           # PDF
    b"PK\x03\x04": "Archives"       # ZIP container (docx/xlsx will be checked by extension in fallback)
}

def determine_category(file_path: str, extension: str) -> str:
    """Determine the logical category of a file based on suffix or magic bytes file structure.
    
    Categories: Media, Documents, Code, Archives, Temp, Other
    """
    ext_lower = (extension or "").strip().lower()
    
    # 1. Primary check: Extension-based mapping (fast in-memory check)
    if ext_lower in EXTENSION_MAP:
        return EXTENSION_MAP[ext_lower]
        
    # 2. Secondary fallback: Check file structure/signatures if extension is unknown or empty
    if file_path and os.path.exists(file_path):
        try:
            with open(file_path, "rb") as f:
                header = f.read(8)
                for signature, category in MAGIC_BYTES_MAP.items():
                    if header.startswith(signature):
                        # Special handling for ZIP container: DOCX/XLSX/PPTX are technically ZIP containers
                        if signature == b"PK\x03\x04":
                            if ext_lower in [".docx", ".xlsx", ".pptx"]:
                                return "Documents"
                            return "Archives"
                        return category
        except Exception as e:
            # Silently log and ignore read errors (permission denied, locked file, etc.)
            logger.debug("Failed to read header of %s: %s", file_path, str(e))
            
    return "Other"
