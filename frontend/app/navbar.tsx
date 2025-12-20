"use client";

import { ThemeToggle } from "@/components/theme-toogle";
import Link from "next/link";
import { TbPhotoAi } from "react-icons/tb";

export default function Navbar() {
  return (
    <nav className="w-full h-18 flex items-center justify-between px-4">
      <Link href="/" className="flex items-center">
      <TbPhotoAi className="w-10 h-10" />
      </Link>
      <ThemeToggle />
    </nav>
  );
}
