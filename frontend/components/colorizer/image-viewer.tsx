"use client";

import {
  ReactCompareSlider,
  ReactCompareSliderImage,
} from "react-compare-slider";
import { Loader2, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Adjustments } from "./types";

interface ImageViewerProps {
  originalUrl: string | null;
  processedUrl: string | null;
  adjustments: Adjustments;
  isUploading: boolean;
  onClose: () => void;
}

export function ImageViewer({
  originalUrl,
  processedUrl,
  adjustments,
  isUploading,
  onClose,
}: ImageViewerProps) {
  const filterStyle = {
    filter: `hue-rotate(${adjustments.hue}deg) sepia(${adjustments.sepia}%) saturate(${adjustments.saturation}%) brightness(${adjustments.brightness}%) contrast(${adjustments.contrast}%)`,
  };

  return (
    <div className="flex-grow bg-black/90 rounded-xl overflow-hidden border border-zinc-800 relative flex items-center justify-center min-h-[400px]">
      {isUploading && (
        <div className="absolute inset-0 z-50 bg-black/80 flex items-center justify-center flex-col">
          <Loader2 className="w-10 h-10 animate-spin text-blue-500 mb-2" />
          <p className="text-zinc-400">Przetwarzanie...</p>
        </div>
      )}

      <Button
        variant="ghost"
        size="icon"
        className="absolute top-4 left-4 z-40 text-white hover:bg-white/20"
        onClick={onClose}
      >
        <X className="w-5 h-5" />
      </Button>

      {originalUrl && processedUrl && (
        <ReactCompareSlider
          className="w-full h-full"
          // 1. LEWA STRONA (Oryginał)
          itemOne={
            <ReactCompareSliderImage
              src={originalUrl}
              alt="Oryginał"
              // Ważne: object-contain
              style={{ objectFit: "contain", width: "100%", height: "100%" }}
            />
          }
          // 2. PRAWA STRONA (Wynik + Filtry)
          itemTwo={
            <div className="w-full h-full relative overflow-hidden flex justify-center items-center">
              {/* Ten div pośredni zapewnia centrowanie */}
              <img
                src={processedUrl}
                alt="Kolor"
                style={{
                  ...filterStyle, // Tu wchodzą Twoje suwaki
                  objectFit: "contain", // TO NAPRAWIA PROBLEM ROZCIĄGANIA
                  width: "100%",
                  height: "100%",
                }}
              />
            </div>
          }
          style={{ width: "100%", height: "100%" }}
        />
      )}
    </div>
  );
}
