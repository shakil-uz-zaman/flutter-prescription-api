from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import pytesseract
import io
import re
import json

app = FastAPI()

# Allow all origins for testing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Vague schedule keywords
vague_keywords = ['after meals', 'ভোজনের পর', 'ভোরে', 'রাতে', 'সকাল', 'বিকাল']

def parse_prescription(text):
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    meds = []
    for line in lines:
        parts = line.split()
        if not parts:
            continue
        name = parts[0]
        schedule = ' '.join(parts[1:]) if len(parts) > 1 else ''
        is_manual = any(v.lower() in schedule.lower() for v in vague_keywords)
        meds.append({
            'medicine': name,
            'schedule': schedule,
            'manual': is_manual
        })
    return meds

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))

    # OCR in English and Bangla
    text_eng = pytesseract.image_to_string(image, lang='eng')
    text_ben = pytesseract.image_to_string(image, lang='ben')

    full_text = f"{text_eng}\n{text_ben}"
    result = parse_prescription(full_text)
    return result
