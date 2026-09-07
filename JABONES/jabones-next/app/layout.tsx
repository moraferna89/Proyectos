import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Jabones Artesanales — Natural, hecho a mano, con amor',
  description:
    'Jabones artesanales elaborados en pequeñas tandas con ingredientes naturales. Aceite de oliva, miel, lavanda y más. Desde Chillán, Chile, a todo el país.',
  keywords: [
    'jabones artesanales',
    'jabón natural',
    'jabón hecho a mano',
    'jabón orgánico',
    'Chillán',
    'Chile',
    'cuidado de la piel',
  ],
  openGraph: {
    title: 'Jabones Artesanales — Natural, hecho a mano, con amor',
    description:
      'Pequeñas tandas, ingredientes nobles y la paciencia de lo hecho a mano. Cada barra es una pausa para ti.',
    type: 'website',
    locale: 'es_CL',
  },
  robots: {
    index: true,
    follow: true,
  },
  authors: [{ name: 'Jabones Artesanales' }],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  )
}
