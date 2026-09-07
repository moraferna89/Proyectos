"use client";

import { motion } from "framer-motion";
import Image from "next/image";
import { ArrowRight, Phone, Star, Shield, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { SITE_CONFIG } from "@/lib/constants";
import { fadeInUp, slideInRight, staggerContainer } from "@/lib/animations";

const trustItems = [
  { icon: Star, text: "15+ años de experiencia" },
  { icon: Shield, text: "Atención de calidad" },
  { icon: Clock, text: "Lun–Vie 10:30–18:30" },
];

export function Hero() {
  const scrollTo = (id: string) => {
    document.querySelector(id)?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <section
      id="inicio"
      className="relative min-h-screen flex items-center overflow-hidden bg-slate-950"
    >
      {/* Background decorations */}
      <div className="absolute inset-0 bg-dot-pattern opacity-30" />
      <div className="absolute top-0 right-0 w-[600px] h-[600px] rounded-full bg-blue-500/10 blur-[100px] -translate-y-1/2 translate-x-1/4" />
      <div className="absolute bottom-0 left-0 w-[400px] h-[400px] rounded-full bg-sky-500/8 blur-[80px] translate-y-1/3 -translate-x-1/4" />

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-20 w-full">
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
          {/* Left: Content */}
          <motion.div
            variants={staggerContainer}
            initial="hidden"
            animate="visible"
            className="flex flex-col"
          >
            {/* Badge */}
            <motion.div variants={fadeInUp} className="mb-6">
              <Badge variant="white" className="text-sm py-1.5 px-4">
                <span className="text-lg">🐾</span>
                Clínica Veterinaria en Concepción
              </Badge>
            </motion.div>

            {/* Headline */}
            <motion.h1
              variants={fadeInUp}
              className="text-4xl sm:text-5xl lg:text-6xl xl:text-7xl font-bold text-white leading-[1.1] tracking-tight mb-6 font-heading"
            >
              El bienestar de{" "}
              <span className="gradient-text-light">tu mascota,</span>
              <br />
              nuestra misión
            </motion.h1>

            {/* Description */}
            <motion.p
              variants={fadeInUp}
              className="text-lg text-slate-300 leading-relaxed mb-8 max-w-xl"
            >
              Tu veterinario de cabecera en Concepción. Cuidamos a tu compañero
              de vida con diagnóstico integral, seguimiento personalizado y
              todo el amor que merece.
            </motion.p>

            {/* CTA Buttons */}
            <motion.div
              variants={fadeInUp}
              className="flex flex-col sm:flex-row gap-4 mb-10"
            >
              <Button
                onClick={() => scrollTo("#contacto")}
                variant="gradient"
                size="lg"
                className="group"
              >
                Agendar Consulta
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Button>
              <Button
                onClick={() => scrollTo("#servicios")}
                variant="outlineWhite"
                size="lg"
              >
                Ver Servicios
              </Button>
            </motion.div>

            {/* Trust indicators */}
            <motion.div
              variants={fadeInUp}
              className="flex flex-col sm:flex-row gap-4"
            >
              {trustItems.map(({ icon: Icon, text }) => (
                <div key={text} className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-lg bg-blue-500/20 flex items-center justify-center shrink-0">
                    <Icon className="w-4 h-4 text-blue-400" />
                  </div>
                  <span className="text-slate-300 text-sm font-medium">{text}</span>
                </div>
              ))}
            </motion.div>
          </motion.div>

          {/* Right: Image + floating cards */}
          <motion.div
            variants={slideInRight}
            initial="hidden"
            animate="visible"
            className="relative flex justify-center lg:justify-end"
          >
            {/* Main image */}
            <div className="relative w-full max-w-md lg:max-w-full">
              <div className="relative rounded-3xl overflow-hidden aspect-[4/5] shadow-2xl shadow-blue-500/20">
                <Image
                  src="/images/hero.png"
                  alt="Veterinaria atendiendo mascota"
                  fill
                  className="object-cover"
                  priority
                />
                <div className="absolute inset-0 bg-gradient-to-t from-slate-950/60 via-transparent to-transparent" />
              </div>

              {/* Floating card: rating */}
              <motion.div
                animate={{ y: [0, -8, 0] }}
                transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
                className="absolute -top-4 -left-4 glass-card rounded-2xl px-4 py-3 shadow-xl"
              >
                <div className="flex items-center gap-2">
                  <div className="flex">
                    {[1, 2, 3, 4, 5].map((i) => (
                      <Star
                        key={i}
                        className="w-4 h-4 text-amber-400 fill-amber-400"
                      />
                    ))}
                  </div>
                  <span className="text-white text-sm font-semibold">5.0</span>
                </div>
                <p className="text-slate-300 text-xs mt-1">
                  +500 reseñas positivas
                </p>
              </motion.div>

              {/* Floating card: next appointment */}
              <motion.div
                animate={{ y: [0, 8, 0] }}
                transition={{
                  duration: 4,
                  repeat: Infinity,
                  ease: "easeInOut",
                  delay: 1,
                }}
                className="absolute -bottom-4 -right-4 glass-card rounded-2xl px-4 py-3 shadow-xl"
              >
                <div className="flex items-center gap-3">
                  <div className="rainbow-ring-sm shrink-0"><div className="w-10 h-10 rounded-xl bg-white flex items-center justify-center">
                    <Phone className="w-5 h-5 text-blue-600" />
                  </div></div>
                  <div>
                    <p className="text-white text-sm font-semibold">Agenda tu hora</p>
                    <p className="text-blue-400 text-xs">{SITE_CONFIG.phone}</p>
                  </div>
                </div>
              </motion.div>
            </div>
          </motion.div>
        </div>

        {/* Scroll indicator */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.5 }}
          className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2"
        >
          <span className="text-slate-500 text-xs uppercase tracking-widest">
            Scroll
          </span>
          <motion.div
            animate={{ y: [0, 8, 0] }}
            transition={{ duration: 1.5, repeat: Infinity }}
            className="w-6 h-10 rounded-full border-2 border-slate-700 flex items-start justify-center pt-1.5"
          >
            <div className="w-1.5 h-3 bg-blue-500 rounded-full" />
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
}
