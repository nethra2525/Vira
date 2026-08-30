import type { Metadata } from "next";
import "./globals.css";
import SiteHeader from "@/components/ui/SiteHeader";

export const metadata: Metadata = {
  title: "VIRA — Skills Over Background. Opportunities for Everyone.",
  description:
    "VIRA is an AI-assisted recruitment platform that matches candidates to roles by demonstrated skill, explains every recommendation, and gives every candidate a growth path forward.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-contour bg-ink min-h-screen">
        <SiteHeader />
        <main>{children}</main>
      </body>
    </html>
  );
}
