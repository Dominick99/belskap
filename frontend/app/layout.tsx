import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Belskap - AI Avatar Studio",
  description: "Create expressive AI avatars powered by intelligent agents.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
