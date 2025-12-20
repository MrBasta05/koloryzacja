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

MODELS_DIR = "models"
os.makedirs(MODELS_DIR, exist_ok=True)

# --- LISTA PEWNYCH LINKÓW (Mirrory) ---
LINKS = {
    "prototxt": [
        "https://raw.githubusercontent.com/richzhang/colorization/caffe/models/colorization_deploy_v2.prototxt",
        "https://raw.githubusercontent.com/opencv/opencv/master/samples/data/dnn/colorization_deploy_v2.prototxt",
        "https://cdn.jsdelivr.net/gh/richzhang/colorization@caffe/models/colorization_deploy_v2.prototxt"
    ],
    "points": [
        "https://raw.githubusercontent.com/richzhang/colorization/caffe/resources/pts_in_hull.npy",
        "https://github.com/richzhang/colorization/raw/caffe/resources/pts_in_hull.npy",
        "https://cdn.jsdelivr.net/gh/richzhang/colorization@caffe/resources/pts_in_hull.npy"
    ],
    "caffemodel": [
        # To jest nowy, działający link do modelu (129MB):
        "https://people.eecs.berkeley.edu/~rich.zhang/projects/2016_colorization/files/demo_v2/colorization_release_v2.caffemodel",
        "https://www.dropbox.com/s/dx0qvhhp5hbcx7z/colorization_release_v2.caffemodel?dl=1",
        "https://github.com/AhmetHamzaEmra/Colorizing-Black-and-White-Images/raw/master/models/colorization_release_v2.caffemodel"
    ]
}

PATHS = {
    "prototxt": os.path.join(MODELS_DIR, "colorization_deploy_v2.prototxt"),
    "points": os.path.join(MODELS_DIR, "pts_in_hull.npy"),
    "caffemodel": os.path.join(MODELS_DIR, "colorization_release_v2.caffemodel")
}

def download_file_smart(urls, target_path):
    if os.path.exists(target_path):
        # Sprawdzamy czy plik nie jest uszkodzonym HTMLem (małym plikiem)
        if os.path.getsize(target_path) < 10000 and "caffemodel" in target_path:
            print(f"⚠️ Wykryto uszkodzony plik {target_path}. Usuwam i pobieram ponownie...")
            os.remove(target_path)
        else:
            return # Plik już jest ok

    print(f"⏳ Pobieram: {os.path.basename(target_path)}...")
    
    for url in urls:
        try:
            print(f"   Próba: {url}")
            r = requests.get(url, stream=True, timeout=30)
            if r.status_code == 200:
                with open(target_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"   ✅ Sukces!")
                return
            else:
                print(f"   ❌ Błąd HTTP: {r.status_code}")
        except Exception as e:
            print(f"   ❌ Błąd połączenia: {e}")
    
    raise Exception(f"Nie udało się pobrać {os.path.basename(target_path)} z żadnego źródła!")

@app.on_event("startup")
async def startup_event():
    print("--- START SYSTEMU KOLORYZACJI ---")
    try:
        # Pobieramy wszystko automatycznie
        download_file_smart(LINKS["prototxt"], PATHS["prototxt"])
        download_file_smart(LINKS["points"], PATHS["points"])
        download_file_smart(LINKS["caffemodel"], PATHS["caffemodel"])
        print("--- WSZYSTKIE PLIKI GOTOWE ---")
    except Exception as e:
        print(f"KRYTYCZNY BŁĄD: {e}")

def colorize_opencv(image_bytes):
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None: raise Exception("Błąd odczytu obrazu")

    # Wczytanie sieci
    net = cv2.dnn.readNetFromCaffe(PATHS["prototxt"], PATHS["caffemodel"])
    pts = np.load(PATHS["points"])

    # Konfiguracja warstw
    class8 = net.getLayerId("class8_ab")
    conv8 = net.getLayerId("conv8_313_rh")
    pts = pts.transpose().reshape(2, 313, 1, 1)
    net.getLayer(class8).blobs = [pts.astype("float32")]
    net.getLayer(conv8).blobs = [np.full([1, 313], 2.606, dtype="float32")]

    # Przetwarzanie
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
        content = await file.read()
        result_image = colorize_opencv(content)
        _, encoded_img = cv2.imencode('.jpg', result_image)
        return StreamingResponse(io.BytesIO(encoded_img.tobytes()), media_type="image/jpeg")
    except Exception as e:
        print(f"BŁĄD: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)