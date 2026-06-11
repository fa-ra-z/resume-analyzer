"""
Universal Resume File Parser
─────────────────────────────
Accepts ANY common resume format and returns clean, AI-ready text.

Supported formats
─────────────────
✓ PDF (text-based)              .pdf
✓ PDF (scanned / image-based)   .pdf  → OCR fallback
✓ Microsoft Word (modern)       .docx
✓ Microsoft Word (legacy)       .doc
✓ Rich Text Format              .rtf
✓ Plain Text                    .txt
✓ Images (resumes as photos)    .png .jpg .jpeg .webp .bmp .tiff

Features
────────
✓ Auto file-type detection (by extension AND magic bytes)
✓ Multi-column PDF layout detection
✓ Hyperlink extraction (LinkedIn, GitHub, portfolio)
✓ Smart OCR fallback for scanned PDFs
✓ Image preprocessing for better OCR accuracy
✓ Ligature, smart-quote, and bullet normalization
✓ Page-number / header / footer stripping
✓ Optional rich metadata extraction
"""

import io
import re
import unicodedata
from typing import Union, BinaryIO

import fitz   # PyMuPDF


# ─────────────────────────────────────────────────────────────
# OPTIONAL DEPENDENCIES — loaded only when needed
# ─────────────────────────────────────────────────────────────
def _try_import(module_name: str):
    try:
        return __import__(module_name)
    except ImportError:
        return None


# ─────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────
COMMON_LIGATURES = {
    "\ufb00": "ff",  "\ufb01": "fi",  "\ufb02": "fl",
    "\ufb03": "ffi", "\ufb04": "ffl", "\ufb05": "ft",
    "\ufb06": "st",
}

BULLET_CHARS = [
    "\u2022", "\u2023", "\u25E6", "\u2043", "\u2219",
    "\u25AA", "\u25AB", "\u25CB", "\u25CF", "\u25A0",
    "\u00B7", "\u2027", "\u2218", "\u29BE", "\u29BF",
    "►", "▶", "➤", "➢", "❖", "✦", "✧", "✪", "✶", "✱",
    "◆", "◇", "◉", "○", "●", "■", "□", "▪", "▫",
]

SMART_REPLACEMENTS = {
    "\u2018": "'",  "\u2019": "'",
    "\u201C": '"',  "\u201D": '"',
    "\u2013": "-",  "\u2014": "-",
    "\u2212": "-",  "\u2010": "-",
    "\u00A0": " ",  "\u202F": " ",  "\u2009": " ",
    "\u2026": "...",
    "\u00AD": "",
}

SUPPORTED_EXTENSIONS = {
    ".pdf", ".docx", ".doc", ".rtf", ".txt",
    ".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".tif",
}

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".tif"}

# Magic bytes for file-type detection (when extension is unreliable)
MAGIC_BYTES = {
    b"%PDF":               "pdf",
    b"PK\x03\x04":         "docx",      # DOCX = zip archive
    b"\xD0\xCF\x11\xE0":   "doc",       # legacy DOC (OLE2)
    b"{\\rtf":             "rtf",
    b"\x89PNG":            "png",
    b"\xFF\xD8\xFF":       "jpg",
    b"RIFF":               "webp",
    b"GIF8":               "gif",
    b"BM":                 "bmp",
    b"II*\x00":            "tiff",
    b"MM\x00*":            "tiff",
}


# ═════════════════════════════════════════════════════════════
# PUBLIC ENTRY POINT
# ═════════════════════════════════════════════════════════════
def extract_text_from_pdf(uploaded_file, return_metadata: bool = False):
    """
    Backward-compatible alias for extract_text().
    Despite the name, this now accepts ALL supported file types.
    """
    return extract_text(uploaded_file, return_metadata=return_metadata)


def extract_text(
    uploaded_file: Union[BinaryIO, bytes],
    return_metadata: bool = False,
):
    """
    Universal text extractor for any resume file format.

    Parameters
    ----------
    uploaded_file : Streamlit UploadedFile, file-like object, or raw bytes
    return_metadata : bool
        If True, returns a dict with text + extracted metadata.
        If False (default), returns clean text string.

    Returns
    -------
    str | dict
    """
    # ── Read raw bytes ───────────────────────────────────
    if hasattr(uploaded_file, "read"):
        raw_bytes = uploaded_file.read()
        filename = getattr(uploaded_file, "name", "") or ""
    elif isinstance(uploaded_file, (bytes, bytearray)):
        raw_bytes = bytes(uploaded_file)
        filename = ""
    else:
        raise ValueError("uploaded_file must be a file-like object or bytes")

    if not raw_bytes:
        return _empty_result(return_metadata, "Empty file")

    # ── Detect file type ─────────────────────────────────
    file_type = _detect_file_type(raw_bytes, filename)

    # ── Route to correct extractor ───────────────────────
    extracted_text = ""
    links_found = set()

    try:
        if file_type == "pdf":
            extracted_text, links_found = _extract_pdf(raw_bytes)

        elif file_type == "docx":
            extracted_text, links_found = _extract_docx(raw_bytes)

        elif file_type == "doc":
            extracted_text = _extract_doc(raw_bytes)

        elif file_type == "rtf":
            extracted_text = _extract_rtf(raw_bytes)

        elif file_type == "txt":
            extracted_text = _extract_txt(raw_bytes)

        elif file_type in ("png", "jpg", "jpeg", "webp", "bmp", "tiff", "gif"):
            extracted_text = _extract_image(raw_bytes)

        else:
            return _empty_result(
                return_metadata,
                f"Unsupported file type: {file_type or 'unknown'}"
            )

    except Exception as e:
        return _empty_result(return_metadata, f"Extraction failed: {str(e)}")

    # ── Inject any links discovered but missing in text ──
    extracted_text = _inject_missing_links(extracted_text, links_found)

    # ── Apply full cleanup pipeline ──────────────────────
    clean = _clean_text(extracted_text)

    if return_metadata:
        return {
            "text":         clean,
            "file_type":    file_type,
            "word_count":   len(clean.split()),
            "char_count":   len(clean),
            "links_found":  sorted(links_found),
            "emails":       _find_emails(clean),
            "phones":       _find_phones(clean),
            "linkedin":     _find_linkedin(clean, links_found),
            "github":       _find_github(clean, links_found),
            "error":        None,
        }
    return clean


# ═════════════════════════════════════════════════════════════
# FILE TYPE DETECTION
# ═════════════════════════════════════════════════════════════
def _detect_file_type(raw_bytes: bytes, filename: str) -> str:
    """Detect file type using magic bytes first, then file extension."""
    # 1. Magic bytes
    header = raw_bytes[:8]
    for magic, ftype in MAGIC_BYTES.items():
        if header.startswith(magic):
            # Special case: WEBP is in RIFF container
            if magic == b"RIFF" and b"WEBP" in raw_bytes[:16]:
                return "webp"
            elif magic == b"RIFF":
                continue
            return ftype

    # 2. Filename extension
    if filename:
        ext = "." + filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
        if ext in SUPPORTED_EXTENSIONS:
            return ext.lstrip(".")

    # 3. Try to detect text
    try:
        raw_bytes[:1000].decode("utf-8")
        return "txt"
    except UnicodeDecodeError:
        pass

    return ""


# ═════════════════════════════════════════════════════════════
# EXTRACTORS — one per file type
# ═════════════════════════════════════════════════════════════

# ── PDF (with OCR fallback) ──────────────────────────────────
def _extract_pdf(raw_bytes: bytes) -> tuple:
    """Extract text from PDF. Auto-falls back to OCR for scanned PDFs."""
    doc = fitz.open(stream=raw_bytes, filetype="pdf")
    pages = []
    all_links = set()

    for page_num, page in enumerate(doc):
        page_text = _extract_pdf_page(page)
        page_text = _strip_header_footer(page_text)
        pages.append(page_text)

        for link in page.get_links():
            uri = link.get("uri", "")
            if uri:
                all_links.add(uri.strip())

    full_text = "\n\n".join(pages).strip()

    # If almost no text was found → it's likely a scanned PDF → use OCR
    if len(full_text) < 100:
        ocr_text = _ocr_pdf_pages(doc)
        if ocr_text and len(ocr_text) > len(full_text):
            full_text = ocr_text

    doc.close()
    return full_text, all_links


def _extract_pdf_page(page) -> str:
    """Extract one PDF page in correct reading order (multi-column aware)."""
    try:
        blocks = page.get_text("dict")["blocks"]
    except Exception:
        return page.get_text("text")

    items = []
    for block in blocks:
        if block.get("type", 0) != 0:
            continue
        for line in block.get("lines", []):
            line_text = "".join(span.get("text", "") for span in line.get("spans", []))
            line_text = line_text.strip()
            if line_text:
                items.append({
                    "x": line["bbox"][0],
                    "y": line["bbox"][1],
                    "text": line_text,
                })

    if not items:
        return page.get_text("text")

    # Detect two-column layout
    page_width = page.rect.width
    midpoint = page_width / 2
    left_count = sum(1 for it in items if it["x"] < midpoint - 20)
    right_count = sum(1 for it in items if it["x"] > midpoint + 20)
    is_two_column = (
        left_count > 5 and right_count > 5
        and abs(left_count - right_count) < max(left_count, right_count) * 0.6
    )

    if is_two_column:
        left  = sorted([it for it in items if it["x"] < midpoint],
                       key=lambda i: (round(i["y"], 1), i["x"]))
        right = sorted([it for it in items if it["x"] >= midpoint],
                       key=lambda i: (round(i["y"], 1), i["x"]))
        ordered = left + right
    else:
        ordered = sorted(items, key=lambda i: (round(i["y"], 1), i["x"]))

    lines, prev_y = [], None
    for it in ordered:
        if prev_y is not None and abs(it["y"] - prev_y) > 14:
            lines.append("")
        lines.append(it["text"])
        prev_y = it["y"]
    return "\n".join(lines)


def _ocr_pdf_pages(doc) -> str:
    """Render each PDF page as image and OCR it."""
    pytesseract = _try_import("pytesseract")
    PIL = _try_import("PIL")
    if not pytesseract or not PIL:
        return ""

    from PIL import Image
    pages_text = []
    for page in doc:
        try:
            pix = page.get_pixmap(dpi=300)   # high-res for accuracy
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            img = _preprocess_image_for_ocr(img)
            text = pytesseract.image_to_string(img, lang="eng")
            pages_text.append(text)
        except Exception:
            continue
    return "\n\n".join(pages_text)


# ── DOCX ─────────────────────────────────────────────────────
def _extract_docx(raw_bytes: bytes) -> tuple:
    """Extract text + hyperlinks from a .docx file."""
    docx = _try_import("docx")
    if not docx:
        # Fall back to docx2txt if python-docx not available
        return _extract_docx_via_docx2txt(raw_bytes), set()

    from docx import Document
    doc = Document(io.BytesIO(raw_bytes))

    parts = []
    links = set()

    # Paragraphs
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            parts.append(text)

    # Tables (skills are often in tables)
    for table in doc.tables:
        for row in table.rows:
            row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
            if row_text:
                parts.append(row_text)

    # Hyperlinks (stored in document.xml.rels)
    try:
        for rel in doc.part.rels.values():
            if "hyperlink" in rel.reltype.lower():
                target = rel.target_ref
                if target and target.startswith("http"):
                    links.add(target)
    except Exception:
        pass

    return "\n".join(parts), links


def _extract_docx_via_docx2txt(raw_bytes: bytes) -> str:
    """Secondary DOCX extractor using docx2txt."""
    docx2txt = _try_import("docx2txt")
    if not docx2txt:
        return ""
    try:
        return docx2txt.process(io.BytesIO(raw_bytes)) or ""
    except Exception:
        return ""


# ── Legacy DOC ───────────────────────────────────────────────
def _extract_doc(raw_bytes: bytes) -> str:
    """Extract text from legacy .doc (Word 97-2003) files."""
    # Try docx2txt first (handles some .doc files)
    docx2txt = _try_import("docx2txt")
    if docx2txt:
        try:
            text = docx2txt.process(io.BytesIO(raw_bytes))
            if text and len(text.strip()) > 30:
                return text
        except Exception:
            pass

    # Fall back to textract if available (more reliable for .doc)
    textract = _try_import("textract")
    if textract:
        try:
            import tempfile, os
            with tempfile.NamedTemporaryFile(suffix=".doc", delete=False) as tmp:
                tmp.write(raw_bytes)
                tmp_path = tmp.name
            text = textract.process(tmp_path).decode("utf-8", errors="ignore")
            os.unlink(tmp_path)
            return text
        except Exception:
            pass

    # Last resort: olefile manual extraction
    return _extract_doc_fallback(raw_bytes)


def _extract_doc_fallback(raw_bytes: bytes) -> str:
    """Crude .doc text extraction by stripping binary noise."""
    try:
        text = raw_bytes.decode("utf-8", errors="ignore")
        # Keep only printable ASCII and common whitespace
        text = re.sub(r"[^\x20-\x7E\n\r\t]+", " ", text)
        text = re.sub(r"\s{3,}", "\n", text)
        return text if len(text.strip()) > 50 else ""
    except Exception:
        return ""


# ── RTF ──────────────────────────────────────────────────────
def _extract_rtf(raw_bytes: bytes) -> str:
    """Extract text from .rtf files."""
    striprtf = _try_import("striprtf")
    if striprtf:
        try:
            from striprtf.striprtf import rtf_to_text
            text = raw_bytes.decode("utf-8", errors="ignore")
            return rtf_to_text(text)
        except Exception:
            pass

    # Fallback: regex-strip RTF control codes
    try:
        text = raw_bytes.decode("utf-8", errors="ignore")
        text = re.sub(r"\\[a-z]+\d* ?", "", text)   # remove control words
        text = re.sub(r"[{}]", "", text)            # remove braces
        text = re.sub(r"\\\'[0-9a-f]{2}", "", text) # remove hex escapes
        return text
    except Exception:
        return ""


# ── TXT ──────────────────────────────────────────────────────
def _extract_txt(raw_bytes: bytes) -> str:
    """Decode plain text file using best-guess encoding."""
    for encoding in ("utf-8", "utf-16", "latin-1", "cp1252"):
        try:
            return raw_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw_bytes.decode("utf-8", errors="ignore")


# ── IMAGE (OCR) ──────────────────────────────────────────────
def _extract_image(raw_bytes: bytes) -> str:
    """OCR text from an image of a resume."""
    pytesseract = _try_import("pytesseract")
    PIL = _try_import("PIL")
    if not pytesseract or not PIL:
        return ""

    from PIL import Image
    try:
        img = Image.open(io.BytesIO(raw_bytes))
        img = _preprocess_image_for_ocr(img)
        return pytesseract.image_to_string(img, lang="eng")
    except Exception:
        return ""


def _preprocess_image_for_ocr(img):
    """Enhance image quality for better OCR accuracy."""
    from PIL import Image, ImageOps, ImageFilter
    # Convert to grayscale
    img = img.convert("L")
    # Increase contrast
    img = ImageOps.autocontrast(img, cutoff=2)
    # Upscale small images
    if img.width < 1500:
        scale = 1500 / img.width
        new_size = (int(img.width * scale), int(img.height * scale))
        img = img.resize(new_size, Image.LANCZOS)
    # Slight sharpen
    img = img.filter(ImageFilter.SHARPEN)
    return img


# ═════════════════════════════════════════════════════════════
# SHARED HELPERS
# ═════════════════════════════════════════════════════════════
def _empty_result(return_metadata: bool, error_msg: str):
    if return_metadata:
        return {
            "text": "", "file_type": "", "word_count": 0,
            "char_count": 0, "links_found": [], "emails": [],
            "phones": [], "linkedin": "", "github": "",
            "error": error_msg,
        }
    return ""


def _strip_header_footer(text: str) -> str:
    """Remove page numbers and footer noise."""
    cleaned = []
    for line in text.split("\n"):
        s = line.strip()
        if re.fullmatch(r"\d{1,3}", s):                                 continue
        if re.fullmatch(r"(?i)page\s*\d+(\s*of\s*\d+)?", s):            continue
        if re.fullmatch(r"\d+\s*/\s*\d+", s):                           continue
        cleaned.append(line)
    return "\n".join(cleaned)


def _inject_missing_links(text: str, links: set) -> str:
    if not links:
        return text
    text_lower = text.lower()
    additions = []
    for link in links:
        link_lower = link.lower()
        if link_lower.startswith(("mailto:", "tel:")):
            continue
        slug = link.rstrip("/").split("/")[-1].lower()
        if link_lower not in text_lower and slug not in text_lower:
            additions.append(link)
    if additions:
        text += "\n\n" + "\n".join(additions)
    return text


def _clean_text(text: str) -> str:
    if not text:
        return ""
    text = unicodedata.normalize("NFKC", text)
    for lig, repl in COMMON_LIGATURES.items():
        text = text.replace(lig, repl)
    for smart, ascii_char in SMART_REPLACEMENTS.items():
        text = text.replace(smart, ascii_char)
    for b in BULLET_CHARS:
        text = text.replace(b, "•")
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)        # hyphenation fix
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = "\n".join(line.rstrip() for line in text.split("\n"))
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"•\s*", "• ", text)
    text = "".join(
        ch for ch in text
        if ch == "\n" or ch == "\t" or (ord(ch) >= 32 and ord(ch) != 127)
    )
    return text.strip()


# ── Metadata extractors ──────────────────────────────────────
def _find_emails(text: str) -> list:
    pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    return list(dict.fromkeys(re.findall(pattern, text)))


def _find_phones(text: str) -> list:
    pattern = r"(\+?\d{1,3}[\s-]?)?\(?\d{3,5}\)?[\s.-]?\d{3,5}[\s.-]?\d{3,5}"
    phones = []
    for m in re.finditer(pattern, text):
        raw = m.group(0).strip()
        digits = re.sub(r"\D", "", raw)
        if 10 <= len(digits) <= 15:
            phones.append(raw)
    return list(dict.fromkeys(phones))


def _find_linkedin(text: str, links: set) -> str:
    for link in links:
        if "linkedin.com" in link.lower():
            return link.strip()
    m = re.search(r"https?://(?:www\.)?linkedin\.com/[^\s)\]]+", text, re.I)
    if m: return m.group(0).rstrip(".,;")
    m = re.search(r"linkedin\.com/in/[A-Za-z0-9_-]+", text, re.I)
    if m: return "https://" + m.group(0)
    return ""


def _find_github(text: str, links: set) -> str:
    for link in links:
        if "github.com" in link.lower():
            return link.strip()
    m = re.search(r"https?://(?:www\.)?github\.com/[^\s)\]]+", text, re.I)
    if m: return m.group(0).rstrip(".,;")
    m = re.search(r"github\.com/[A-Za-z0-9_-]+", text, re.I)
    if m: return "https://" + m.group(0)
    return ""