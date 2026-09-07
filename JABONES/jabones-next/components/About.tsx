'use client'

import Image from 'next/image'
import { motion } from 'framer-motion'
import Reveal from './Reveal'

export default function About() {
  return (
    <section id="historia" className="relative overflow-hidden bg-cream-deep section-pad">
      <div className="wrap">
        <div className="grid grid-cols-1 lg:grid-cols-[1.1fr_1fr] gap-[60px] lg:gap-[100px] items-center">

          {/* Text */}
          <Reveal className="order-2 lg:order-1">
            <span className="eyebrow inline-block mb-6">Nuestra historia</span>
            <h2 className="text-heading font-serif font-light mb-8">
              Empezamos en la cocina,{' '}
              <span className="italic text-wine">terminamos en tu ducha</span>.
            </h2>
            <p className="text-[16px] text-ink-soft mb-5 max-w-[520px] leading-relaxed">
              Todo comenzó un invierno del 2021, buscando un jabón que no irritara la piel de mi hija.
              Cuatro recetas y muchas tandas después, los vecinos empezaron a pedirme barras.
            </p>
            <p className="text-[16px] text-ink-soft mb-5 max-w-[520px] leading-relaxed">
              Hoy somos un pequeño taller en Chillán que sigue haciendo cada jabón a mano,
              con aceites prensados en frío, miel de apicultores locales y la misma paciencia del primer día.
            </p>
            <p className="text-[16px] text-ink-soft max-w-[520px] leading-relaxed">
              No hacemos miles. Hacemos los que podemos hacer bien.
            </p>
            <div className="mt-9">
              <p className="font-serif italic text-[26px] text-ink">— Camila Reyes</p>
              <p className="text-[11px] tracking-[0.24em] uppercase text-ink-soft mt-1">
                Fundadora y jabonera
              </p>
            </div>
          </Reveal>

          {/* Images */}
          <Reveal delay={0.12} className="relative h-[480px] md:h-[600px] order-1 lg:order-2">
            {/* Main image */}
            <motion.div
              className="absolute top-0 left-0 w-[64%] h-[70%] overflow-hidden rounded-[4px]
                shadow-[0_20px_50px_-20px_rgba(43,38,32,0.3)]"
              whileInView={{ y: [0, -8, 0] }}
              transition={{ duration: 6, repeat: Infinity, ease: 'easeInOut' }}
            >
              <Image
                src="https://images.unsplash.com/photo-1556228720-195a672e8a03?w=700&q=80"
                alt="Manos elaborando jabón artesanal"
                fill
                className="object-cover"
                sizes="(max-width: 980px) 64vw, 32vw"
              />
            </motion.div>

            {/* Secondary image */}
            <motion.div
              className="absolute bottom-0 right-0 w-[56%] h-[56%] overflow-hidden
                rounded-[200px_200px_4px_4px]
                shadow-[0_20px_50px_-20px_rgba(43,38,32,0.3)]"
              whileInView={{ y: [0, 6, 0] }}
              transition={{ duration: 7, repeat: Infinity, ease: 'easeInOut', delay: 0.5 }}
            >
              <Image
                src="https://images.unsplash.com/photo-1583512603805-3cc6b41f3edb?w=700&q=80"
                alt="Ingredientes naturales para jabones artesanales"
                fill
                className="object-cover"
                sizes="(max-width: 980px) 56vw, 28vw"
              />
            </motion.div>

            {/* Stat card */}
            <Reveal
              delay={0.24}
              className="absolute bottom-[36%] left-[-10%] bg-cream-light
                px-7 py-6 rounded-[4px] shadow-[0_16px_40px_-16px_rgba(43,38,32,0.2)] z-30"
            >
              <div className="font-serif text-[56px] leading-none text-wine">+2.400</div>
              <div className="text-[10px] tracking-[0.22em] uppercase text-ink-soft mt-2">
                Barras curadas a mano
              </div>
            </Reveal>
          </Reveal>

        </div>
      </div>
    </section>
  )
}
