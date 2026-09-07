import type { Metadata, Viewport } from "next";
import { Inter, Sora } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const sora = Sora({
  subsets: ["latin"],
  variable: "--font-sora",
  weight: ["400", "500", "600", "700", "800"],
  display: "swap",
});

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
};

export const metadata: Metadata = {
  title: "Clínica Veterinaria Huellas | Concepción",
  description:
    "Tu veterinario de cabecera en Concepción. Consultas, cirugías, farmacia, peluquería canina y más. Paicaví 976 Local 3. ¡Agenda tu hora hoy!",
  keywords: [
    "veterinaria concepción",
    "clínica veterinaria huellas",
    "veterinario concepción",
    "consulta veterinaria",
    "peluquería canina",
    "esterilización mascotas",
  ],
  openGraph: {
    title: "Clínica Veterinaria Huellas | Concepción",
    description:
      "Tu veterinario de cabecera en Concepción. Más de 15 años cuidando mascotas con amor y profesionalismo.",
    type: "website",
    locale: "es_CL",
  },
  robots: {
    index: true,
    follow: true,
  },
  icons: {
    icon: "/favicon.ico",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es" className={`${inter.variable} ${sora.variable}`}>
      <body className="min-h-screen antialiased">{children}</body>
    </html>
  );
}
