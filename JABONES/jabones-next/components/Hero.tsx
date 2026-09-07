'use client'

import { useRef } from 'react'
import Image from 'next/image'
import { motion, useScroll, useTransform } from 'framer-motion'
import { ArrowRight } from 'lucide-react'
import Link from 'next/link'
import LeafSVG from './LeafSVG'

export default function Hero() {
  const ref = useRef<HTMLElement>(null)
  const { scrollYProgress } = useScroll({ target: ref, offset: ['start start', 'end start'] })
  const productY = useTransform(scrollYProgress, [0, 1], [0, 80])
  const leaf1Y = useTransform(scrollYProgress, [0, 1], [0, -120])
  const leaf2Y = useTransform(scrollYProgress, [0, 1], [0, -60])

  const containerVariants = {
    hidden: {},
    visible: { transition: { staggerChildren: 0.14 } },
  }
  const itemVariants = {
    hidden: { opacity: 0, y: 40 },
    visible: { opacity: 1, y: 0, transition: { duration: 1, ease: [0.2, 0.7, 0.2, 1] } },
  }

  return (
    <section
      ref={ref}
      id="top"
      className="relative min-h-screen overflow-hidden flex items-center pt-[140px] pb-[80px]
        bg-gradient-to-b from-cream-light to-cream"
    >
      {/* Decorative leaves */}
      <motion.div
        style={{ y: leaf1Y }}
        className="absolute top-[10%] right-[-60px] w-[480px] opacity-[0.18] pointer-events-none z-10"
      >
        <LeafSVG color="#2B2620" className="w-full h-auto" />
      </motion.div>
      <motion.div
        style={{ y: leaf2Y }}
        className="absolute bottom-[-80px] left-[-80px] w-[380px] opacity-[0.12] pointer-events-none z-10 rotate-[160deg]"
      >
        <LeafSVG color="#5C5A3F" className="w-full h-auto" />
      </motion.div>

      {/* Content */}
      <div className="wrap relative z-20 w-full">
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="max-w-[780px]"
        >
          <motion.span variants={itemVariants} className="eyebrow">
            Natural · Hecho a mano · Con amor
          </motion.span>

          <motion.h1
            variants={itemVariants}
            className="text-display font-serif font-light mt-6 mb-7"
          >
            Jabones que
            <br />
            <span className="italic text-wine font-normal">cuidan tu piel</span>
            <br />
            como la naturaleza.
          </motion.h1>

          <motion.p
            variants={itemVariants}
            className="text-lead text-ink-soft italic max-w-[540px] mb-[44px]"
          >
            Pequeñas tandas, ingredientes nobles y la paciencia de lo hecho a mano.
            Cada barra es una pausa para ti.
          </motion.p>

          <motion.div variants={itemVariants} className="flex gap-[18px] items-center flex-wrap">
            <Link
              href="/productos"
              className="inline-flex items-center gap-3 px-[34px] py-[18px] bg-wine text-cream
                rounded-pill text-[13px] tracking-[0.18em] uppercase font-medium
                shadow-[0_4px_14px_rgba(107,45,45,0.18)]
                transition-all duration-200
                hover:-translate-y-[2px] hover:bg-[#5a2424] hover:shadow-[0_8px_24px_rgba(107,45,45,0.28)]
                group"
            >
              Ver el catálogo
              <ArrowRight
                size={16}
                className="transition-transform duration-300 group-hover:translate-x-1"
              />
            </Link>
            <a
              href="#historia"
              className="inline-flex items-center gap-[10px] px-[28px] py-[16px]
                text-[13px] tracking-[0.16em] uppercase text-ink
                border-b border-ink
                transition-all duration-200 hover:text-wine hover:border-wine hover:gap-[14px]"
            >
              Nuestra historia
            </a>
          </motion.div>
        </motion.div>
      </div>

      {/* Product image */}
      <motion.div
        style={{ y: productY }}
        className="absolute right-10 top-1/2 -translate-y-1/2
          w-[38vw] max-w-[560px] h-[70vh] max-h-[720px] z-20
          rounded-[280px_280px_12px_12px] overflow-hidden
          shadow-[0_40px_80px_-30px_rgba(43,38,32,0.35)]
          max-[980px]:relative max-[980px]:right-auto max-[980px]:top-auto
          max-[980px]:translate-y-0 max-[980px]:w-[88%] max-[980px]:max-w-[420px]
          max-[980px]:h-[460px] max-[980px]:mx-auto max-[980px]:mt-14"
      >
        <Image
          src="https://images.unsplash.com/photo-1600857544200-b2f666a9a2ec?w=900&q=80"
          alt="Jabón artesanal sobre tabla de madera"
          fill
          className="object-cover"
          priority
          sizes="(max-width: 980px) 88vw, 38vw"
        />
      </motion.div>

      {/* Bottom marks */}
      <div className="absolute bottom-[50px] left-10 z-30 hidden md:flex items-center gap-6
        text-[10px] tracking-[0.28em] uppercase text-ink-soft">
        <span>EST. 2021</span>
        <span className="w-1 h-1 rounded-full bg-wine" />
        <span>Chillán · Chile</span>
        <span className="w-1 h-1 rounded-full bg-wine" />
        <span>100% Natural</span>
      </div>

      {/* Scroll cue */}
      <div className="absolute bottom-[38px] left-1/2 -translate-x-1/2 z-30
        flex flex-col items-center gap-[14px]
        text-[10px] tracking-[0.4em] uppercase text-ink-soft">
        <span>scroll</span>
        <span className="w-px h-12 bg-gradient-to-b from-transparent to-ink-soft animate-scroll-line" />
      </div>
    </section>
  )
}
