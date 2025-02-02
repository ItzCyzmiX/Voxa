from jam import JammableAutomation
from fastapi import FastAPI, File, UploadFile, BackgroundTasks
from fastapi.responses import FileResponse
import shutil
import os
import time

from selenium.common.exceptions import TimeoutException
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

UPLOAD_DIR = "./uploads/"
CONVERTED_DIR = "./converted/"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CONVERTED_DIR, exist_ok=True)  # Directory for converted files


@app.post("/convert/")
async def create_conversion(background_tasks: BackgroundTasks, file: UploadFile = File(...), voice: str = "Carti"):
    if voice != "Carti":
        return {"error": "Voice not supported"}

    file_location = os.path.join(UPLOAD_DIR, file.filename)

    # Save the uploaded file
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Define converted file name
    converted_filename = file.filename.replace(".wav", "_Cartied.wav")
    converted_file_path = os.path.join(CONVERTED_DIR, converted_filename)

    # Run conversion in the background
    background_tasks.add_task(convert, file_location, converted_file_path, voice)

    return {"status": "processing", "converted_file": f"/download/{converted_filename}"}


@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = os.path.join(CONVERTED_DIR, filename)
    if not os.path.exists(file_path):
        return {"error": "File not found or still processing"}
    return FileResponse(file_path, media_type="audio/wav", filename=filename)


def convert(file_path, converted_file_path, voice="Carti"):
    """Main execution function"""
    automation = None
    try:
        automation = JammableAutomation()
        email, password, _ = automation.create_account()
        automation.process_audio(file_path)

        # Simulate processing delay
        time.sleep(5)

        # Rename the processed file
        if os.path.exists(file_path.replace(".wav", "_Cartied.wav")):
            os.rename(file_path.replace(".wav", "_Cartied.wav"), converted_file_path)
            os.remove(file_path)  # Delete original file after conversion

    except TimeoutException as e:
        logger.error(f"Operation timed out: {e}")
    except Exception as e:
        logger.error(f"Fatal error occurred: {e}")
    finally:
        if automation:
            automation.cleanup()
