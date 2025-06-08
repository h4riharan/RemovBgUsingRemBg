from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
from io import BytesIO
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for local testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/remove-bg/")
async def remove_bg(file: UploadFile = File(...)):
    from rembg import remove  # Lazy import

    input_image = await file.read()
    output_image = remove(input_image)
    return StreamingResponse(BytesIO(output_image), media_type="image/png")

@app.get("/warmup")
def warmup():
    try:
        from rembg import remove
        # Create a dummy 1x1 white image
        dummy_image = Image.new("RGB", (1, 1), (255, 255, 255))
        buffer = io.BytesIO()
        dummy_image.save(buffer, format="PNG")
        buffer.seek(0)
        remove(buffer.read())  # Pre-loads model
        return {"status": "Model warmed up ✅"}
    except Exception as e:
        return {"status": "Warmup failed ❌", "error": str(e)}

@app.get("/")
def read_root():
    return {"message": "Background Remover API. Use /docs to try it out."}

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("src.main:app", host="0.0.0.0", port=port)
