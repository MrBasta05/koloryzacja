import pytest
import io
import numpy as np
from PIL import Image
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# 1. Mockujemy ładowanie modelu ZANIM zaimportujemy 'api'
# Dzięki temu test zadziała nawet jeśli nie masz pliku .h5 na dysku
with patch("tensorflow.keras.models.load_model", return_value=MagicMock()):
    with patch("os.path.exists", return_value=True):
        from api import app, prepare_image_for_model, IMAGE_SIZE

client = TestClient(app)

def test_read_root():
    """Teraz powinno zwrócić 200, bo importujemy właściwą aplikację."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Image Colorization API"

def test_health_check():
    """Sprawdza status zdrowia aplikacji."""
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()

@patch("api.model")
def test_colorize_success(mock_model):
    """Testuje endpoint /colorize z zamarkowanym modelem."""
    # Ustawiamy co ma zwrócić 'model.predict'
    mock_model.predict.return_value = np.zeros((1, IMAGE_SIZE, IMAGE_SIZE, 2))

    # Tworzymy testowy obrazek PNG w pamięci
    img = Image.new('RGB', (64, 64), color='blue')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    files = {'file': ('test.png', img_byte_arr, 'image/png')}
    
    response = client.post("/colorize", files=files)

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"

def test_prepare_image_logic():
    """Testuje samą funkcję przetwarzania obrazu."""
    # Tworzymy losową macierz udającą obraz
    test_img = np.ones((100, 100, 3), dtype=np.uint8) * 255
    processed = prepare_image_for_model(test_img, IMAGE_SIZE)
    
    # Sprawdzamy wymiary wejściowe dla sieci (1, 128, 128, 1)
    assert processed.shape == (1, 128, 128, 1)