import os
import io
import numpy as np
import tensorflow as tf
from skimage.io import imread, imsave
from skimage.color import rgb2lab, lab2rgb, gray2rgb
from skimage.transform import resize
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

app = FastAPI(title="Image Colorization API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = 'model_unet_landscape_cifar.h5'
IMAGE_SIZE = 128

# Load model at startup
model = None


@app.on_event("startup")
async def startup_event():
    global model
    model = load_model(MODEL_PATH)


def load_model(model_path):
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found: {model_path}")
    return tf.keras.models.load_model(model_path, compile=False)


def load_image(path):
    image = imread(path)
    if len(image.shape) == 3 and image.shape[2] == 4:
        image = image[:, :, :3]
    return image


def prepare_image_for_model(image, size):
    resized_image = resize(image, (size, size))
    
    if len(resized_image.shape) == 2:
        resized_image = gray2rgb(resized_image)
    
    lab = rgb2lab(resized_image)
    l_channel = lab[:, :, 0] / 100.0
    l_channel = l_channel.reshape(1, size, size, 1)
    
    return l_channel


def predict_colors(model, l_channel):
    predicted_ab = model.predict(l_channel, verbose=0)
    return predicted_ab[0]


def rescale_colors(predicted_ab, target_size):
    predicted_ab_upscaled = resize(predicted_ab, target_size)
    predicted_ab_upscaled = predicted_ab_upscaled * 128.0
    return predicted_ab_upscaled


def get_l_channel_from_original(image):
    if len(image.shape) == 2:
        image = gray2rgb(image)
    lab = rgb2lab(image)
    return lab[:, :, 0]


def merge_lab_channels(l_channel, ab_channels):
    height, width = l_channel.shape
    final_lab = np.zeros((height, width, 3))
    final_lab[:, :, 0] = l_channel
    final_lab[:, :, 1:] = ab_channels
    return final_lab


def convert_lab_to_rgb(lab_image):
    return lab2rgb(lab_image)


def save_image(rgb_image, output_path):
    imsave(output_path, (rgb_image * 255).astype(np.uint8))


def colorize_image_from_bytes(image_bytes):
    image = np.array(Image.open(io.BytesIO(image_bytes)))
    
    if len(image.shape) == 3 and image.shape[2] == 4:
        image = image[:, :, :3]
    
    original_height, original_width = image.shape[:2]
    
    l_input = prepare_image_for_model(image, IMAGE_SIZE)
    predicted_ab = predict_colors(model, l_input)
    predicted_ab_upscaled = rescale_colors(
        predicted_ab, 
        (original_height, original_width)
    )
    
    original_l = get_l_channel_from_original(image)
    final_lab = merge_lab_channels(original_l, predicted_ab_upscaled)
    final_rgb = convert_lab_to_rgb(final_lab)
    
    return final_rgb


@app.get("/")
async def root():
    return {"message": "Image Colorization API", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy", "model_loaded": model is not None}


@app.post("/colorize")
async def colorize_image(file: UploadFile = File(...)):
    if not model:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        image_bytes = await file.read()
        
        colorized_rgb = colorize_image_from_bytes(image_bytes)
        
        colorized_image = Image.fromarray((colorized_rgb * 255).astype(np.uint8))
        
        img_byte_arr = io.BytesIO()
        colorized_image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        return StreamingResponse(img_byte_arr, media_type="image/png")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")
