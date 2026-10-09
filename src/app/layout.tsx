import Script from "next/script";
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "PhenoFusion3D | RGB-D Plant Reconstruction and 3D Traits",
  description:
    "PhenoFusion3D captures RGB-D plant data, reconstructs coloured 3D point clouds, cleans plant models, and extracts 3D traits for APPN phenotyping workflows.",
  keywords: [
    "plant phenomics",
    "RGB-D",
    "3D reconstruction",
    "point cloud",
    "ICP",
    "Open3D",
    "RealSense L515",
    "3D trait extraction",
    "convex hull",
    "APPN",
    "ANU",
  ],
  openGraph: {
    title: "PhenoFusion3D",
    description: "RGB-D reconstruction, point-cloud cleanup, and 3D trait extraction for plant phenotyping",
    type: "website",
  },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className="scroll-smooth">
      <head><Script src="/research-assets.js" strategy="beforeInteractive" /></head>
      <body className={`${inter.className} bg-[#050a0a] text-[#f0fdf4] antialiased`}>{children}</body>
    </html>
  );
}
