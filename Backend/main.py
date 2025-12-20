import os
import io
import cv2
import numpy as np
import requests
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- KONFIGURACJA MODELI ---
# Używamy sprawdzonych linków "raw"
MODELS_DIR = "models"
os.makedirs(MODELS_DIR, exist_ok=True)

FILES = {
    "proto": {
        "url": "https://raw.githubusercontent.com/richzhang/colorization/master/models/colorization_deploy_v2.prototxt",
        "path": os.path.join(MODELS_DIR, "colorization_deploy_v2.prototxt")
    },
    "model": {
        # Ten plik jest duży (129MB), link z Berkeley jest stabilny
        "url": "http://eecs.berkeley.edu/~rich.zhang/projects/2016_colorization/files/demo_v2/colorization_release_v2.caffemodel",
        "path": os.path.join(MODELS_DIR, "colorization_release_v2.caffemodel")
    },
    "points": {
        "url": "https://raw.githubusercontent.com/richzhang/colorization/master/resources/pts_in_hull.npy",
        "path": os.path.join(MODELS_DIR, "pts_in_hull.npy")
    }
}

def download_file(url, path):
    if not os.path.exists(path):
        print(f"--> Pobieram: {os.path.basename(path)} ...")
        try:
            r = requests.get(url, stream=True)
            if r.status_code != 200:
                raise Exception(f"Błąd HTTP {r.status_code} dla {url}")
            
            with open(path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            print("    Pobrano pomyślnie.")
        except Exception as e:
            # Jeśli pobieranie się nie uda, usuwamy pusty/błędny plik, żeby nie blokował kolejnych prób
            if os.path.exists(path):
                os.remove(path)
            raise e

@app.on_event("startup")
async def startup_event():
    print("Sprawdzanie plików modelu...")
    try:
        for key, file_info in FILES.items():
            download_file(file_info["url"], file_info["path"])
        print("SYSTEM GOTOWY DO PRACY.")
    except Exception as e:
        print(f"KRYTYCZNY BŁĄD POBIERANIA: {e}")
        print("Rozwiązanie: Spróbuj pobrać pliki ręcznie lub sprawdź połączenie.")

def colorize_opencv(image_bytes):
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        raise Exception("Nie udało się odczytać obrazu")

    # Wczytywanie sieci
    net = cv2.dnn.readNetFromCaffe(FILES["proto"]["path"], FILES["model"]["path"])
    pts = np.load(FILES["points"]["path"])

    class8 = net.getLayerId("class8_ab")
    conv8 = net.getLayerId("conv8_313_rh")
    pts = pts.transpose().reshape(2, 313, 1, 1)
    net.getLayer(class8).blobs = [pts.astype("float32")]
    net.getLayer(conv8).blobs = [np.full([1, 313], 2.606, dtype="float32")]

    normalized = img.astype("float32") / 255.0
    lab = cv2.cvtColor(normalized, cv2.COLOR_BGR2LAB)
    resized = cv2.resize(lab, (224, 224))
    L = cv2.split(resized)[0]
    L -= 50

    net.setInput(cv2.dnn.blobFromImage(L))
    ab = net.forward()[0, :, :, :].transpose((1, 2, 0))
    
    ab = cv2.resize(ab, (img.shape[1], img.shape[0]))

    L_orig = cv2.split(lab)[0]
    colorized = np.concatenate((L_orig[:, :, np.newaxis], ab), axis=2)

    colorized = cv2.cvtColor(colorized, cv2.COLOR_LAB2BGR)
    colorized = np.clip(colorized, 0, 1)
    colorized = (255 * colorized).astype("uint8")

    return colorized

@app.post("/colorize")
async def colorize_image(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        print("Otrzymano zdjęcie - przetwarzanie OpenCV...")
        result_bgr = colorize_opencv(image_bytes)
        
        is_success, buffer = cv2.imencode(".jpg", result_bgr)
        if not is_success:
            raise Exception("Błąd kodowania")
            
        return StreamingResponse(io.BytesIO(buffer.tobytes()), media_type="image/jpeg")

    except Exception as e:
        print(f"BŁĄD: {str(e)}")
        # Jeśli błąd dotyczy plików modelu, dajemy jasny komunikat
        if "ReadNetParams" in str(e) or "NetParameter" in str(e):
             raise HTTPException(status_code=500, detail="Pliki modelu są uszkodzone. Usuń folder 'models' i zrestartuj serwer.")
        
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)