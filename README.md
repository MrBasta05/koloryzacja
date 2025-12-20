# Koloryzacja — projekt zaliczeniowy (Inżynieria Oprogramowania)

Aplikacja składa się z backendu (FastAPI / TensorFlow / OpenCV) i frontendu (Next.js + React).

## Zawartość repozytorium

- Backend/ — serwis API i skrypty koloryzujące
  - [Backend/api.py](Backend/api.py) — endpointy FastAPI, funkcje: [`colorize_image_from_bytes`](Backend/api.py), [`colorize_image`](Backend/api.py)
- frontend/ — aplikacja Next.js z UI do uploadu, podglądu i pobierania
  - [frontend/components/Colorizer.tsx](frontend/components/Colorizer.tsx) — główny komponent aplikacji
  - [frontend/components/colorizer/image-viewer.tsx](frontend/components/colorizer/image-viewer.tsx) — porównanie przed/po
  - [frontend/components/colorizer/sidebar.tsx](frontend/components/colorizer/sidebar.tsx) — suwaki do korekcji (hue/saturation/...)
  - [frontend/app/globals.css](frontend/app/globals.css) — zmienne kolorów i styl globalny
  - [frontend/app/layout.tsx](frontend/app/layout.tsx), [frontend/components/ThemeProviderClient.tsx](frontend/components/ThemeProviderClient.tsx)

<!-- ## Uruchomienie — Backend
1. Stwórz środowisko wirtualne i zainstaluj zależności:
```bash
python -m venv .venv
.venv\Scripts\activate  # lub source .venv/bin/activate na Linux
pip install -r requirements.txt`
```
2. Uruchom serwer:
```bash
cd backend
uvicorn .api:app --reload
```
## Uruchomienie — Frontend
```bash
cd frontend
npm install
npm run dev
``` -->

## Jak korzystać

1. Na stronie głównej wrzuć czarno-białe zdjęcie (drag & drop lub wybór pliku).
2. Aplikacja wyśle plik do backendu, otrzymasz kolorowany obraz.
3. Użyj suwaków w bocznym panelu (frontend/components/colorizer/sidebar.tsx) aby dopracować efekt.
4. Pobierz wynik przy użyciu przycisku „Pobierz”.

> Aplikacja dostępna pod [http://localhost:3000](http://localhost:3000)
