# Phase 3: Rich Metadata Engine - Research

## Requirements & Libraries

We will install the following packages:
- `pypdf`: To parse page counts and authors from PDF files.
- `tinytag`: To parse duration and artist from MP3/audio files.

```bash
pip install pypdf tinytag
```

## Native Extraction Strategies

### 1. Image Size & Creation Date
PNG, JPEG, and GIF sizes can be parsed from headers natively to avoid any OS package dependencies:
- **PNG**: Parse big-endian integers at offset 16 (width) and 20 (height).
- **GIF**: Parse little-endian integers at offset 6 (width) and 8 (height).
- **JPEG**: Scan SOF markers `0xFFC0`-`0xFFCF` (excluding `0xFFC4`, `0xFFC8`, `0xFFCC`) and read height and width.

Creation date can be read using `os.path.getctime()` and converted to ISO format.

### 2. Office Document Parsing (.docx, .xlsx, .pptx)
Office documents are ZIP files containing XML structures:
- **Author**: Found in `docProps/core.xml` under `<dc:creator>`.
- **Pages count**: Found in `docProps/app.xml` under `<Pages>`. (Excel sheets don't have pages, but slides/documents do).

Snippet for Office properties extraction:
```python
import zipfile
import xml.etree.ElementTree as ET

def extract_office_metadata(file_path):
    metadata = {}
    try:
        with zipfile.ZipFile(file_path) as z:
            # Parse core properties
            try:
                with z.open("docProps/core.xml") as f:
                    tree = ET.parse(f)
                    root = tree.getroot()
                    # Namespaces are usually present
                    namespaces = {
                        'cp': 'http://schemas.openxmlformats.org/package/2006/metadata/core-properties',
                        'dc': 'http://purl.org/dc/elements/1.1/'
                    }
                    creator = root.find(".//dc:creator", namespaces)
                    if creator is not None and creator.text:
                        metadata["author"] = creator.text
            except Exception:
                pass

            # Parse app properties
            try:
                with z.open("docProps/app.xml") as f:
                    tree = ET.parse(f)
                    root = tree.getroot()
                    namespaces = {
                        'ep': 'http://schemas.openxmlformats.org/officeDocument/2006/extended-properties'
                    }
                    pages = root.find(".//ep:Pages", namespaces)
                    if pages is not None and pages.text:
                        metadata["pages"] = int(pages.text)
                    else:
                        slides = root.find(".//ep:Slides", namespaces)
                        if slides is not None and slides.text:
                            metadata["pages"] = int(slides.text)
            except Exception:
                pass
    except Exception:
        pass
    return metadata
```

### 3. PDF Parsing
Using `pypdf`:
```python
from pypdf import PdfReader

def extract_pdf_metadata(file_path):
    try:
        reader = PdfReader(file_path)
        meta = reader.metadata
        return {
            "author": meta.author if meta and meta.author else None,
            "pages": len(reader.pages)
        }
    except Exception:
        return {}
```

### 4. Audio Parsing
Using `tinytag`:
```python
from tinytag import TinyTag

def extract_audio_metadata(file_path):
    try:
        tag = TinyTag.get(file_path)
        return {
            "artist": tag.artist,
            "duration": int(tag.duration) if tag.duration else None
        }
    except Exception:
        return {}
```
