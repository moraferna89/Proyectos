import type { Metadata } from 'next'
import Link from 'next/link'
import { ChevronRight } from 'lucide-react'
import Navbar from '@/components/Navbar'
import Footer from '@/components/Footer'
import FloatingWhatsApp from '@/components/FloatingWhatsApp'
import ProductsFilter from '@/components/ProductsFilter'
import LeafSVG from '@/components/LeafSVG'

export const metadata: Metadata = {
  title: 'Productos — Jabones Artesanales',
  description:
    'Explora nuestra colección completa de jabones artesanales. Hidratantes, relajantes, purificantes y más. Elaborados a mano en Chillán, Chile.',
}

export default function ProductosPage() {
  return (
    <>
      <Navbar />
      <main>
        {/* ── Page header ── */}
        <section className="relative overflow-hidden bg-cream-deep pt-[140px] pb-[90px]">
          <LeafSVG
            color="#5C5A3F"
            className="absolute top-0 right-[-60px] w-[360px] opacity-[0.09] pointer-events-none"
          />
          <LeafSVG
            color="#8B6F4E"
            className="absolute bottom-[-80px] left-[-60px] w-[280px] opacity-[0.07] rotate-[160deg] pointer-events-none"
          />

          <div className="wrap relative z-10">
            {/* Breadcrumb */}
            <nav
              aria-label="Breadcrumb"
              className="flex items-center gap-2 text-[11px] tracking-[0.2em] uppercase text-ink-soft mb-8"
            >
              <Link href="/" className="hover:text-wine transition-colors duration-200">
                Inicio
              </Link>
              <ChevronRight size={12} className="opacity-40" />
              <span className="text-wine">Productos</span>
            </nav>

            <div className="max-w-[720px]">
              <span className="eyebrow inline-block mb-5">Nuestra tienda</span>
              <h1 className="font-serif font-light text-[clamp(52px,7vw,110px)] leading-[0.95] tracking-[-0.01em]">
                La colección{' '}
                <span className="italic text-wine">completa</span>.
              </h1>
              <p className="font-serif italic font-light text-[clamp(18px,1.6vw,24px)] text-ink-soft mt-6 max-w-[520px]">
                Seis barras elaboradas a mano, cada una para una necesidad distinta
                de tu piel.
              </p>
            </div>

            {/* Stats row */}
            <div className="flex flex-wrap gap-x-10 gap-y-4 mt-12 pt-10 border-t border-[rgba(43,38,32,0.12)]">
              {[
                { num: '6', label: 'Variedades' },
                { num: '+4 sem.', label: 'De curado' },
                { num: '100%', label: 'Natural' },
                { num: '0', label: 'Plástico' },
              ].map(({ num, label }) => (
                <div key={label}>
                  <span className="font-serif text-[36px] leading-none text-wine">{num}</span>
                  <p className="text-[10px] tracking-[0.24em] uppercase text-ink-soft mt-1">
                    {label}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ── Filter + Grid ── */}
        <ProductsFilter />
      </main>
      <Footer />
      <FloatingWhatsApp />
    </>
  )
}
