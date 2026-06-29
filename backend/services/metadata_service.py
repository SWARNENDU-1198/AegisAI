import os
import logging
import struct
import datetime
import zipfile
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional

try:
    from services.security_service import analyze_file_security
except ImportError:
    try:
        from .security_service import analyze_file_security
    except ImportError:
        analyze_file_security = None

logger = logging.getLogger(__name__)


# Try to import optional dependencies
try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None
    logger.warning("pypdf package is not installed; PDF metadata extraction will be disabled.")

try:
    from tinytag import TinyTag
except ImportError:
    TinyTag = None
    logger.warning("tinytag package is not installed; Audio metadata extraction will be disabled.")


def extract_image_dimensions(file_path: str) -> tuple[Optional[int], Optional[int]]:
    """Determine image dimensions (width, height) natively from PNG, JPEG, or GIF headers."""
    try:
        with open(file_path, "rb") as f:
            header = f.read(24)
            
            # 1. PNG Check
            if header.startswith(b"\x89PNG\r\n\x1a\n") and header[12:16] == b"IHDR":
                w, h = struct.unpack(">II", header[16:24])
                return w, h
                
            # 2. GIF Check
            if header.startswith(b"GIF87a") or header.startswith(b"GIF89a"):
                w, h = struct.unpack("<HH", header[6:10])
                return w, h
                
            # 3. JPEG Check
            if header.startswith(b"\xff\xd8"):
                f.seek(2)
                while True:
                    marker = f.read(2)
                    if not marker or marker[0] != 0xff:
                        break
                    marker_type = marker[1]
                    if marker_type in [0xd9, 0xda]:  # EOI (End of Image) or SOS (Start of Scan)
                        break
                    # Read segment length
                    length_bytes = f.read(2)
                    if len(length_bytes) < 2:
                        break
                    length = struct.unpack(">H", length_bytes)[0]
                    # Check for SOF markers (Start of Frame)
                    if marker_type in [0xc0, 0xc1, 0xc2, 0xc3, 0xc5, 0xc6, 0xc7, 0xc9, 0xca, 0xcb, 0xcd, 0xce, 0xcf]:
                        # Skip precision byte
                        f.seek(1, 1)
                        h, w = struct.unpack(">HH", f.read(4))
                        return w, h
                    else:
                        # Skip marker content
                        f.seek(length - 2, 1)
    except Exception as e:
        logger.debug("Failed to extract image dimensions for %s: %s", file_path, str(e))
    return None, None


def extract_image_metadata(file_path: str) -> Dict[str, Any]:
    """Extract width, height, and creation date for images."""
    meta = {}
    try:
        w, h = extract_image_dimensions(file_path)
        if w is not None and h is not None:
            meta["width"] = w
            meta["height"] = h
            
        if os.path.exists(file_path):
            timestamp = os.path.getctime(file_path)
            dt = datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc)
            meta["creation_date"] = dt.isoformat()
    except Exception as e:
        logger.debug("Failed to extract image metadata for %s: %s", file_path, str(e))
    return meta


def extract_audio_metadata(file_path: str) -> Dict[str, Any]:
    """Extract artist and duration (seconds) for audio files using tinytag."""
    meta = {}
    if TinyTag is None:
        return meta
    try:
        tag = TinyTag.get(file_path)
        if tag.artist:
            meta["artist"] = tag.artist
        if tag.duration is not None:
            meta["duration"] = int(tag.duration)
    except Exception as e:
        logger.debug("Failed to extract audio metadata for %s: %s", file_path, str(e))
    return meta


def extract_pdf_metadata(file_path: str) -> Dict[str, Any]:
    """Extract author and pages count for PDF documents using pypdf."""
    meta = {}
    if PdfReader is None:
        return meta
    try:
        reader = PdfReader(file_path)
        meta_info = reader.metadata
        if meta_info and meta_info.author:
            meta["author"] = meta_info.author
        meta["pages"] = len(reader.pages)
    except Exception as e:
        logger.debug("Failed to extract PDF metadata for %s: %s", file_path, str(e))
    return meta


def extract_office_metadata(file_path: str) -> Dict[str, Any]:
    """Extract author and page/slide count for Microsoft Office (docx, xlsx, pptx) files natively."""
    meta = {}
    try:
        with zipfile.ZipFile(file_path) as z:
            # 1. Parse core properties (Author/Creator)
            try:
                with z.open("docProps/core.xml") as f:
                    tree = ET.parse(f)
                    root = tree.getroot()
                    namespaces = {
                        'cp': 'http://schemas.openxmlformats.org/package/2006/metadata/core-properties',
                        'dc': 'http://purl.org/dc/elements/1.1/'
                    }
                    creator = root.find(".//dc:creator", namespaces)
                    if creator is not None and creator.text:
                        meta["author"] = creator.text
            except Exception:
                pass

            # 2. Parse app properties (Pages/Slides count)
            try:
                with z.open("docProps/app.xml") as f:
                    tree = ET.parse(f)
                    root = tree.getroot()
                    namespaces = {
                        'ep': 'http://schemas.openxmlformats.org/officeDocument/2006/extended-properties'
                    }
                    pages = root.find(".//ep:Pages", namespaces)
                    if pages is not None and pages.text:
                        meta["pages"] = int(pages.text)
                    else:
                        slides = root.find(".//ep:Slides", namespaces)
                        if slides is not None and slides.text:
                            meta["pages"] = int(slides.text)
            except Exception:
                pass
    except Exception as e:
        logger.debug("Failed to extract Office XML metadata for %s: %s", file_path, str(e))
    return meta


def extract_metadata(file_path: str, category: str, extension: str) -> Dict[str, Any]:
    """Dispatcher to extract metadata depending on category and extension."""
    if not file_path or not os.path.exists(file_path):
        return {}

    ext_lower = (extension or "").strip().lower()
    
    meta = {}

    # Dispatch by extension or category
    if ext_lower in [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"]:
        meta = extract_image_metadata(file_path)
    elif ext_lower in [".mp3", ".wav", ".flac", ".ogg", ".webm"] or category == "Media":
        # If it's categorized as media and is an audio file (or has media category)
        # Note: Image extensions check above prevents images from falling into this block
        if ext_lower in [".mp3", ".wav", ".flac", ".ogg", ".webm"]:
            meta = extract_audio_metadata(file_path)
        else:
            # Fallback check for magic bytes to see if it is audio vs image
            try:
                with open(file_path, "rb") as f:
                    header = f.read(4)
                if header.startswith(b"ID3") or header.startswith(b"\xff\xfb") or header.startswith(b"RIFF"):
                    meta = extract_audio_metadata(file_path)
                elif header.startswith(b"\x89PNG") or header.startswith(b"\xff\xd8") or header.startswith(b"GIF8"):
                    meta = extract_image_metadata(file_path)
            except Exception:
                pass

    elif ext_lower == ".pdf":
        meta = extract_pdf_metadata(file_path)
    elif ext_lower in [".docx", ".xlsx", ".pptx"]:
        meta = extract_office_metadata(file_path)

    # Documents category fallback if not matched
    elif category == "Documents" and ext_lower == ".pdf":
        meta = extract_pdf_metadata(file_path)

    # Run security scans on all checked files
    if analyze_file_security:
        alerts = analyze_file_security(file_path, extension)
        if alerts:
            meta["security_alerts"] = alerts

    return meta

