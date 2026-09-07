"use client";

import { motion } from "framer-motion";
import Image from "next/image";
import { ArrowDown, Star, Beer } from "lucide-react";
import { Button } from "@/components/shared/Button";
import { SITE_CONFIG, STATS } from "@/lib/constants";

export function Hero() {
  const handleScroll = (href: string) => {
    const el = document.querySelector(href);
    if (el) el.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <section
      id="hero"
      className="relative min-h-screen flex flex-col justify-center overflow-hidden"
    >
      {/* Background Image */}
      <div className="absolute inset-0 z-0">
        <Image
          src="https://images.unsplash.com/photo-1514190051997-0f6f39ca5cde?q=80&w=2070"
          alt="Bar Fuente Divka"
          fill
          priority
          className="object-cover object-center"
          sizes="100vw"
        />
        {/* Gradient Overlays */}
        <div className="absolute inset-0 bg-gradient-to-r from-[#0A0A0A] via-[#0A0A0A]/85 to-[#0A0A0A]/40" />
        <div className="absolute inset-0 bg-gradient-to-t from-[#0A0A0A] via-transparent to-transparent" />
      </div>

      {/* Amber glow */}
      <div className="absolute bottom-0 left-1/4 w-96 h-96 bg-amber-500/8 rounded-full blur-[120px] pointer-events-none" />

      {/* Content */}
      <div className="relative z-10 container-wide section-padding pt-32 md:pt-40">
        <div className="max-w-2xl">
          {/* Eyebrow */}
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="flex items-center gap-3 mb-6"
          >
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-amber-500/10 border border-amber-500/20">
              <Star className="w-3.5 h-3.5 text-amber-400 fill-amber-400" />
              <span className="text-amber-400 text-xs font-medium tracking-wide">
                12 años en Apoquindo
              </span>
            </div>
          </motion.div>

          {/* Headline */}
          <motion.h1
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="text-5xl sm:text-6xl md:text-7xl font-extrabold tracking-tight leading-[1.05] mb-6"
          >
            El bar donde{" "}
            <span className="text-gradient block">la cerveza</span>
            manda.
          </motion.h1>

          {/* Description */}
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.35 }}
            className="text-white/60 text-lg sm:text-xl leading-relaxed mb-10 max-w-lg"
          >
            18 variedades de cerveza artesanal, gastronomía gourmet y el mejor
            ambiente de Santiago. La picada que buscabas.
          </motion.p>

          {/* CTAs */}
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.5 }}
            className="flex flex-wrap items-center gap-4"
          >
            <Button
              size="lg"
              variant="primary"
              onClick={() => handleScroll("#cervezas")}
            >
              <Beer className="w-5 h-5" />
              Ver Cervezas
            </Button>
            <Button
              size="lg"
              variant="secondary"
              onClick={() => handleScroll("#contacto")}
            >
              Reservar Mesa
            </Button>
          </motion.div>

          {/* Address badge */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.7 }}
            className="mt-10 flex items-center gap-2 text-white/40 text-sm"
          >
            <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
            <span>{SITE_CONFIG.address}</span>
          </motion.div>
        </div>

        {/* Stats Row */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.8 }}
          className="mt-16 md:mt-24 grid grid-cols-2 sm:grid-cols-4 gap-px bg-white/[0.06] rounded-2xl overflow-hidden max-w-2xl border border-white/[0.06]"
        >
          {STATS.map((stat) => (
            <div
              key={stat.label}
              className="bg-[#0A0A0A] px-6 py-5 flex flex-col gap-1"
            >
              <span className="text-3xl font-extrabold text-gradient">{stat.value}</span>
              <span className="text-xs text-white/45 font-medium">{stat.label}</span>
            </div>
          ))}
        </motion.div>
      </div>

      {/* Scroll indicator */}
      <motion.button
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.2 }}
        onClick={() => handleScroll("#nosotros")}
        className="absolute bottom-8 left-1/2 -translate-x-1/2 z-10 flex flex-col items-center gap-2 text-white/30 hover:text-white/60 transition-colors"
        aria-label="Scroll down"
      >
        <span className="text-xs tracking-widest uppercase">Scroll</span>
        <motion.div
          animate={{ y: [0, 6, 0] }}
          transition={{ repeat: Infinity, duration: 1.5 }}
        >
          <ArrowDown className="w-4 h-4" />
        </motion.div>
      </motion.button>
    </section>
  );
}
