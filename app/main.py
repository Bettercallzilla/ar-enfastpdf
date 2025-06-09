FastAPI app with Arabic+English OCR

from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
import requests
import io
import os

app = FastAPI()

class FileUrl(BaseModel):
    url: str

UPLOAD_FOLDER = "app/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    try:
        images = convert_from_bytes(pdf_bytes)
        full_text = ""
        for image in images:
            text = pytesseract.image_to_string(image, lang="ara+eng")
            full_text += text + "\n"
        return full_text.strip()
    except Exception as e:
        raise RuntimeError(f"OCR processing failed: {e}")

@app.post("/ocr/file")
async def ocr_from_file(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        text = extract_text_from_pdf_bytes(contents)
        return { "text": text }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ocr/url")
async def ocr_from_url(file_url: FileUrl):
    try:
        response = requests.get(file_url.url)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to download file.")
        text = extract_text_from_pdf_bytes(response.content)
        return { "text": text }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
