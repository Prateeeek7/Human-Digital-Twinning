"""
OCR and Text Extraction from Images and PDFs.
"""

import io
from typing import Optional, Dict, Any
from pathlib import Path
import numpy as np

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    import pdf2image
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False


class DocumentOCR:
    """Extract text from prescription images and lab reports."""
    
    def __init__(self, use_easyocr: bool = False):
        """
        Initialize OCR engine.
        
        Args:
            use_easyocr: Use EasyOCR instead of Tesseract (more accurate but slower)
        """
        if not PIL_AVAILABLE:
            raise RuntimeError("Pillow not installed. Install with: pip install Pillow")
        
        self.use_easyocr = use_easyocr and EASYOCR_AVAILABLE
        
        if self.use_easyocr:
            print("Initializing EasyOCR...")
            self.reader = easyocr.Reader(['en'])
            print("✓ EasyOCR initialized")
        elif TESSERACT_AVAILABLE:
            # Check if tesseract is available
            try:
                pytesseract.get_tesseract_version()
            except Exception:
                raise RuntimeError(
                    "Tesseract OCR not found. Install with: "
                    "brew install tesseract (macOS) or apt-get install tesseract-ocr (Linux)"
                )
        else:
            raise RuntimeError(
                "No OCR library available. Install with: "
                "pip install pytesseract pdf2image (for Tesseract) or "
                "pip install easyocr (for EasyOCR)"
            )
    
    def extract_text_from_image(self, image_path: str) -> str:
        """
        Extract text from image file.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Extracted text
        """
        image = Image.open(image_path)
        return self.extract_text_from_pil_image(image)
    
    def extract_text_from_pil_image(self, image) -> str:
        """
        Extract text from PIL Image.
        
        Args:
            image: PIL Image object
            
        Returns:
            Extracted text
        """
        if self.use_easyocr:
            # Convert PIL to numpy array
            img_array = np.array(image)
            results = self.reader.readtext(img_array)
            text = "\n".join([result[1] for result in results])
        elif TESSERACT_AVAILABLE:
            # Use Tesseract
            text = pytesseract.image_to_string(image)
        else:
            raise RuntimeError("No OCR library available")
        
        return text.strip()
    
    def extract_text_from_pdf(self, pdf_path: str, dpi: int = 200) -> str:
        """
        Extract text from PDF file.
        
        Args:
            pdf_path: Path to PDF file
            dpi: DPI for PDF to image conversion
            
        Returns:
            Extracted text from all pages
        """
        if not PDF2IMAGE_AVAILABLE:
            raise RuntimeError("pdf2image not installed. Install with: pip install pdf2image")
        
        try:
            # Convert PDF to images
            images = pdf2image.convert_from_path(pdf_path, dpi=dpi)
            
            # Extract text from each page
            all_text = []
            for i, image in enumerate(images):
                page_text = self.extract_text_from_pil_image(image)
                all_text.append(f"--- Page {i+1} ---\n{page_text}")
            
            return "\n\n".join(all_text)
        except Exception as e:
            raise RuntimeError(f"Error extracting text from PDF: {str(e)}")
    
    def extract_text_from_bytes(
        self,
        file_bytes: bytes,
        file_type: str = "image"
    ) -> str:
        """
        Extract text from file bytes.
        
        Args:
            file_bytes: File content as bytes
            file_type: "image" or "pdf"
            
        Returns:
            Extracted text
        """
        if file_type.lower() == "pdf":
            # Save to temporary file and process
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp.write(file_bytes)
                tmp_path = tmp.name
            
            try:
                text = self.extract_text_from_pdf(tmp_path)
            finally:
                Path(tmp_path).unlink()
            
            return text
        else:
            # Treat as image
            if not PIL_AVAILABLE:
                raise RuntimeError("Pillow not installed")
            image = Image.open(io.BytesIO(file_bytes))
            return self.extract_text_from_pil_image(image)
    
    def extract_text(self, file_path: Optional[str] = None, 
                    file_bytes: Optional[bytes] = None,
                    file_type: Optional[str] = None) -> str:
        """
        Extract text from file (auto-detect type).
        
        Args:
            file_path: Path to file
            file_bytes: File content as bytes
            file_type: Optional file type hint
            
        Returns:
            Extracted text
        """
        if file_path:
            path = Path(file_path)
            if path.suffix.lower() == '.pdf':
                return self.extract_text_from_pdf(str(path))
            else:
                return self.extract_text_from_image(str(path))
        elif file_bytes:
            if file_type:
                return self.extract_text_from_bytes(file_bytes, file_type)
            else:
                # Try as image first
                try:
                    return self.extract_text_from_bytes(file_bytes, "image")
                except:
                    # Try as PDF
                    return self.extract_text_from_bytes(file_bytes, "pdf")
        else:
            raise ValueError("Either file_path or file_bytes must be provided")

