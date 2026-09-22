import sys

packages = ["easyocr", "pytesseract", "PIL", "cv2", "torch", "transformers", "numpy"]
for p in packages:
    try:
        __import__(p)
        print(f"  OK  {p}")
    except ImportError as e:
        print(f"  --  {p}  (missing)")
