from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import io
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader

app = FastAPI()
templates = Jinja2Templates(directory="templates")
@app.get("/", response_class=HTMLResponse)
async def read_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

@app.post("/fill")
async def fill_pdf(request: Request,
                   owner_name: str = Form(...),
                   nationality: str = Form(...),
                   passport_id: str = Form(...),
                   operator_name: str = Form(...),
                   license_number: str = Form(...),
                   unit_number: str = Form(...),
                   area: str = Form(...),
                   building_name: str = Form(...),
                   dewa_number: str = Form(...),
                   phone: str = Form(...),
                   email: str = Form(...),
                   signature: UploadFile = File(...)):

    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)

    # Draw text on specific estimated positions
    can.drawString(150, 660, owner_name)
    can.drawString(150, 640, nationality)
    can.drawString(150, 620, passport_id)
    can.drawString(150, 600, operator_name)
    can.drawString(400, 600, license_number)
    can.drawString(150, 580, unit_number)
    can.drawString(300, 580, area)
    can.drawString(150, 560, dewa_number)
    can.drawString(150, 540, f"{building_name} - {phone}")
    can.drawString(150, 500, owner_name)
    can.drawString(300, 500, phone)
    can.drawString(150, 480, email)

    # Draw signature image near the owner name
    sig_data = await signature.read()
    sig_image = ImageReader(io.BytesIO(sig_data))
    can.drawImage(sig_image, 400, 655, width=100, height=30, mask='auto')

    can.save()
    packet.seek(0)

    new_pdf = PdfReader(packet)
    existing_pdf = PdfReader("pdfs/pm temp.pdf")
    output = PdfWriter()

    page = existing_pdf.pages[0]
    page.merge_page(new_pdf.pages[0])
    output.add_page(page)

    with open("output/filled.pdf", "wb") as f:
        output.write(f)

    return FileResponse("output/filled.pdf", media_type='application/pdf', filename="filled.pdf")
