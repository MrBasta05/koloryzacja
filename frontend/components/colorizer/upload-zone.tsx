"use client";

import { useDropzone } from "react-dropzone";
import { UploadCloud } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { useCallback } from "react";

interface UploadZoneProps {
  onFileSelect: (file: File) => void;
}

export function UploadZone({ onFileSelect }: UploadZoneProps) {
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles?.[0]) {
        onFileSelect(acceptedFiles[0]);
      }
    },
    [onFileSelect]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "image/*": [] },
    maxFiles: 1,
  });

  return (
    <Card
      {...getRootProps()}
      className={`h-[500px] border-dashed border-2 flex flex-col items-center justify-center p-10 transition-colors cursor-pointer ${
        isDragActive ? "bg-muted/50 border-primary" : "hover:bg-muted/50"
      }`}
    >
      <input {...getInputProps()} />
      <div className="bg-primary/10 p-6 rounded-full mb-6">
        <UploadCloud className="w-12 h-12 text-primary" />
      </div>
      <h2 className="text-2xl font-bold mb-2 text-center">
        {isDragActive ? "Upuść plik tutaj" : "Przeciągnij zdjęcie tutaj"}
      </h2>
      <p className="text-muted-foreground mb-6 text-center">
        lub kliknij, aby wybrać z dysku
      </p>
      <Button size="lg">Wybierz plik</Button>
    </Card>
  );
}
