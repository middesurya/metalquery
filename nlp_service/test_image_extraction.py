"""
Test script for multi-modal BRD image extraction.
Run this to verify images are being extracted from PDFs.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pathlib import Path

print("=" * 60)
print("Multi-Modal BRD Image Extraction Test")
print("=" * 60)

# Test 1: Check if PyMuPDF is available
print("\n[1] Checking PyMuPDF...")
try:
    import fitz
    print(f"   OK - PyMuPDF version: {fitz.version}")
except ImportError:
    print("   FAIL - PyMuPDF not installed. Run: pip install pymupdf")
    sys.exit(1)

# Test 2: Check BRD folder
BRD_FOLDER = Path(__file__).parent / "brd"
BRD_IMAGES_FOLDER = Path(__file__).parent / "brd_images"

print(f"\n[2] Checking BRD folder: {BRD_FOLDER}")
if BRD_FOLDER.exists():
    pdf_files = list(BRD_FOLDER.glob("*.pdf"))
    print(f"   OK - Found {len(pdf_files)} PDF files")
else:
    print("   FAIL - BRD folder not found")
    sys.exit(1)

# Test 3: Extract images from first PDF
print("\n[3] Testing image extraction from first PDF...")
if pdf_files:
    test_pdf = pdf_files[0]
    print(f"   Testing: {test_pdf.name}")
    
    doc = fitz.open(test_pdf)
    total_images = 0
    
    for page_num in range(min(5, len(doc))):  # Check first 5 pages
        page = doc[page_num]
        images = page.get_images(full=True)
        total_images += len(images)
        if images:
            print(f"   Page {page_num}: {len(images)} images found")
    
    doc.close()
    print(f"   OK - Total images in first 5 pages: {total_images}")

# Test 4: Create images folder
print(f"\n[4] Creating images folder: {BRD_IMAGES_FOLDER}")
BRD_IMAGES_FOLDER.mkdir(exist_ok=True)
print(f"   OK - Folder ready")

# Test 5: Test BRD loader
print("\n[5] Testing BRD Loader...")
try:
    from brd_loader import brd_loader
    
    # Load images
    print("   Loading images from all PDFs...")
    images = brd_loader.load_images()
    print(f"   OK - Extracted {len(images)} images total")
    
    if images:
        print(f"\n   Sample images:")
        for img in images[:5]:
            print(f"   - {img.filename} (from {img.metadata['source']})")
    
except Exception as e:
    print(f"   ERROR: {e}")

print("\n" + "=" * 60)
print("Test complete! Run the NLP service to use the multi-modal RAG.")
print("=" * 60)
