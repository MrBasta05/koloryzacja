"use client";

import { useState } from "react";
import { UploadZone } from "./colorizer/upload-zone";
import { ImageViewer } from "./colorizer/image-viewer";
import { Sidebar } from "./colorizer/sidebar";
import { Adjustments, DEFAULT_ADJUSTMENTS } from "./colorizer/types";

export default function Colorizer() {
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [processedUrl, setProcessedUrl] = useState<string | null>(null);
  const [adjustments, setAdjustments] =
    useState<Adjustments>(DEFAULT_ADJUSTMENTS);
  const [isUploading, setIsUploading] = useState(false);

  // ... (Tutaj Twoje funkcje handleFileSelect i uploadToBackend bez zmian) ...
  const handleFileSelect = (selectedFile: File) => {
    setFile(selectedFile);
    const objectUrl = URL.createObjectURL(selectedFile);
    setPreviewUrl(objectUrl);
    uploadToBackend(selectedFile);
  };

  const uploadToBackend = async (fileToUpload: File) => {
    setIsUploading(true);
    const formData = new FormData();
    formData.append("file", fileToUpload);

    try {
      const res = await fetch("http://localhost:8000/colorize", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error("Błąd API");

      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      setProcessedUrl(url);
    } catch (error) {
      console.error("Błąd uploadu:", error);
    } finally {
      setIsUploading(false);
    }
  };

  // --- NOWA FUNKCJA POBIERANIA ---
  const handleDownload = () => {
    if (!processedUrl) return;

    // 1. Tworzymy obrazek w pamięci
    const img = new Image();
    img.crossOrigin = "anonymous"; // Ważne dla CORS
    img.src = processedUrl;

    img.onload = () => {
      // 2. Tworzymy canvas o wymiarach zdjęcia
      const canvas = document.createElement("canvas");
      canvas.width = img.width;
      canvas.height = img.height;

      const ctx = canvas.getContext("2d");
      if (!ctx) return;

      // 3. Aplikujemy filtry (identyczne jak w CSS)
      // Uwaga: kolejność i składnia muszą być poprawne dla Canvas Filter API
      ctx.filter = `
        hue-rotate(${adjustments.hue}deg) 
        sepia(${adjustments.sepia}%) 
        saturate(${adjustments.saturation}%) 
        brightness(${adjustments.brightness}%) 
        contrast(${adjustments.contrast}%)
      `;

      // 4. Rysujemy zdjęcie z filtrami na canvasie
      ctx.drawImage(img, 0, 0, img.width, img.height);

      // 5. Pobieramy wynik
      const link = document.createElement("a");
      link.download = `colorized-${file?.name || "image"}.png`;
      link.href = canvas.toDataURL("image/png");
      link.click();
    };
  };

  const handleReset = () => {
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    if (processedUrl) URL.revokeObjectURL(processedUrl);
    setFile(null);
    setPreviewUrl(null);
    setProcessedUrl(null);
    setAdjustments(DEFAULT_ADJUSTMENTS);
  };

  return (
    <div className="w-full max-w-6xl mx-auto p-4 md:p-8">
      {!file ? (
        <UploadZone onFileSelect={handleFileSelect} />
      ) : (
        <div className="flex flex-col lg:flex-row gap-6 h-auto lg:h-[600px]">
          <ImageViewer
            originalUrl={previewUrl}
            processedUrl={processedUrl}
            adjustments={adjustments}
            isUploading={isUploading}
            onClose={handleReset}
          />

          <Sidebar
            adjustments={adjustments}
            setAdjustments={setAdjustments}
            onReset={() => setAdjustments(DEFAULT_ADJUSTMENTS)}
            onDownload={handleDownload} // <--- Przekazujemy funkcję
            isProcessed={!!processedUrl} // <--- Przekazujemy czy przycisk ma być aktywny
          />
        </div>
      )}
    </div>
  );
}
