"use client";

import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";

export default function FileUploader() {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);

  // Obsługa wyboru pliku
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
    }
  };

  // Obsługa wysyłki
  const handleUpload = async () => {
    if (!file) return alert("Wybierz plik!");

    setUploading(true);

    const formData = new FormData();
    // "uploaded_file" to nazwa parametru, którą musi odebrać FastAPI
    formData.append("uploaded_file", file);

    try {
      const response = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
        // WAŻNE: Nie ustawiaj nagłówka 'Content-Type' ręcznie!
        // Przeglądarka sama ustawi go na 'multipart/form-data' z odpowiednim boundary.
      });

      if (response.ok) {
        const data = await response.json();
        alert(`Sukces: ${data.filename}`);
      } else {
        alert("Błąd przesyłania");
      }
    } catch (error) {
      console.error("Błąd sieci:", error);
      alert("Wystąpił błąd połączenia");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="grid w-full max-w-sm items-center gap-1.5 p-4 border rounded-lg">
      <Label htmlFor="file-upload">Twój plik</Label>

      {/* Komponent Input z shadcn/ui działający jako plik */}
      <Input id="file-upload" type="file" onChange={handleFileChange} />

      <Button
        onClick={handleUpload}
        disabled={uploading || !file}
        className="mt-2"
      >
        {uploading ? "Wysyłanie..." : "Wyślij do API"}
      </Button>
    </div>
  );
}
