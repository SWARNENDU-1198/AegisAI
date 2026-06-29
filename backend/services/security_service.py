import os
import re
import logging
from typing import List

logger = logging.getLogger(__name__)

# Compile regex patterns
API_KEY_PATTERN = re.compile(r'(?i)(api[-_]?key|secret[-_]?key|private[-_]?key|token|auth[-_]?key)["\'\s]*[:=]\s*[\'"]([a-zA-Z0-9_\-]{16,})[\'"]')
PASSWORD_PATTERN = re.compile(r'(?i)(password|passwd)["\'\s]*[:=]\s*[\'"]([a-zA-Z0-9_\-]{8,})[\'"]')

SSN_PATTERN = re.compile(r'\b\d{3}-\d{2}-\d{4}\b')
CC_PATTERN = re.compile(r'\b(?:\d{4}[ -]?){3}\d{4}\b')

DANGEROUS_EXTENSIONS = {".exe", ".bat", ".ps1", ".vbs", ".sh", ".cmd", ".msi"}

TEXT_EXTENSIONS = {
    ".txt", ".md", ".json", ".yaml", ".yml", ".xml", ".py", ".js", 
    ".ts", ".html", ".css", ".sh", ".bat", ".ps1", ".ini", ".env", ".csv"
}

def analyze_file_security(file_path: str, extension: str) -> List[str]:
    """Scans file for plain-text keys, passwords, PII, and identifies dangerous executables.
    
    Args:
        file_path: Path to the target file.
        extension: The file's extension.
        
    Returns:
        List of alert string keywords.
    """
    alerts = []
    ext_lower = (extension or "").strip().lower()
    
    # 1. Check for dangerous executables/scripts
    if ext_lower in DANGEROUS_EXTENSIONS:
        alerts.append("unverified_executable")
        
    # 2. Check for secrets/PII in text files
    if ext_lower in TEXT_EXTENSIONS and os.path.exists(file_path):
        try:
            # Skip files larger than 1MB to prevent memory/performance issues
            if os.path.getsize(file_path) < 1024 * 1024:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    
                if API_KEY_PATTERN.search(content):
                    alerts.append("contains_api_key")
                if PASSWORD_PATTERN.search(content):
                    alerts.append("contains_password")
                if SSN_PATTERN.search(content):
                    alerts.append("contains_pii_ssn")
                if CC_PATTERN.search(content):
                    alerts.append("contains_pii_credit_card")
        except Exception as e:
            logger.debug("Failed to read file %s for security scan: %s", file_path, str(e))
            
    return alerts
