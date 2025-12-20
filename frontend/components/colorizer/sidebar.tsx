"use client";

import { Slider } from "@/components/ui/slider";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Download } from "lucide-react";
import { Adjustments } from "./types";

interface SidebarProps {
  adjustments: Adjustments;
  setAdjustments: React.Dispatch<React.SetStateAction<Adjustments>>;
  onReset: () => void;
  onDownload: () => void;
  isProcessed: boolean;
}

export function Sidebar({
  adjustments,
  setAdjustments,
  onReset,
  onDownload,
  isProcessed,
}: SidebarProps) {
  const SLIDERS_CONFIG = [
    { label: "Barwa", key: "hue", min: 0, max: 360 },
    { label: "Sepia", key: "sepia", min: 0, max: 100 },
    { label: "Nasycenie", key: "saturation", min: 0, max: 200 },
    { label: "Jasność", key: "brightness", min: 50, max: 150 },
    { label: "Kontrast", key: "contrast", min: 50, max: 150 },
  ] as const;

  const handleValueChange = (key: keyof Adjustments, value: number[]) => {
    setAdjustments((prev) => ({ ...prev, [key]: value[0] }));
  };

  return (
    <Card className="w-full lg:w-80 p-6 flex flex-col shrink-0 h-full">
      <div className="flex justify-between items-center mb-6">
        <h3 className="font-semibold text-lg">Parametry</h3>
        <Button variant="ghost" size="sm" onClick={onReset}>
          Reset
        </Button>
      </div>

      <div className="space-y-6 overflow-y-auto flex-grow pr-2">
        {SLIDERS_CONFIG.map((item) => (
          <div key={item.key} className="space-y-3">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">{item.label}</span>
              <span>{adjustments[item.key]}</span>
            </div>
            <Slider
              min={item.min}
              max={item.max}
              step={1}
              value={[adjustments[item.key]]}
              onValueChange={(val) => handleValueChange(item.key, val)}
            />
          </div>
        ))}
      </div>
      <Button
        className="w-full mt-6 bg-cyan-600"
        // variant="outline"
        onClick={onDownload}
        disabled={!isProcessed}
      >
        <Download className="mr-2 h-4 w-4" /> Pobierz
      </Button>
    </Card>
  );
}
