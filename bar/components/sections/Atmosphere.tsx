"use client";

import { motion } from "framer-motion";
import Image from "next/image";
import { Music, Circle, Tv2, Users } from "lucide-react";
import { SectionTitle } from "@/components/shared/SectionTitle";

const FEATURES = [
  {
    icon: Circle,
    title: "Mesa de Pool",
    description: "Reta a tus amigos en nuestra mesa de billar mientras disfrutas tu cerveza favorita.",
  },
  {
    icon: Music,
    title: "Música en Vivo",
    description: "Noches con artistas locales y la mejor selección musical para acompañar tu noche.",
  },
  {
    icon: Tv2,
    title: "Pantallas HD",
    description: "No te pierdas ningún partido. Transmisiones deportivas en pantallas de alta definición.",
  },
  {
    icon: Users,
    title: "Eventos Privados",
    description: "Celebra con tu grupo. Reservas para empresas, cumpleaños y reuniones especiales.",
  },
];

const GALLERY_IMAGES = [
  {
    src: "https://images.unsplash.com/photo-1566417713940-fe7c737a9ef2?q=80&w=900",
    alt: "Ambiente del bar",
    className: "col-span-2 row-span-2",
  },
  {
    src: "https://images.unsplash.com/photo-1543007631-283050bb3e8c?q=80&w=600",
    alt: "Barra de cervezas",
    className: "col-span-1 row-span-1",
  },
  {
    src: "https://images.unsplash.com/photo-1575367439058-6096bb9cf5e2?q=80&w=600",
    alt: "Amigos en el bar",
    className: "col-span-1 row-span-1",
  },
  {
    src: "https://images.unsplash.com/photo-1510812431401-41d2bd2722f3?q=80&w=900",
    alt: "Cervezas servidas",
    className: "col-span-2 row-span-1",
  },
];

export function Atmosphere() {
  return (
    <section id="ambiente" className="relative overflow-hidden bg-[#080808]">
      <div className="absolute inset-x-0 top-0 h-px glow-line" />
      <div className="absolute top-1/2 right-1/4 w-[500px] h-[500px] bg-amber-500/5 rounded-full blur-[160px] pointer-events-none -translate-y-1/2" />

      <div className="container-wide section-padding">
        <div className="flex flex-col items-center mb-16">
          <SectionTitle
            eyebrow="El Ambiente"
            title="Un lugar donde"
            titleHighlight="todo fluye."
            description="No somos solo un bar. Somos el plan perfecto para cualquier ocasión: after office, cumpleaños, ver el partido o simplemente desconectar."
            align="center"
          />
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-16">
          {FEATURES.map((feat, i) => (
            <motion.div
              key={feat.title}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: i * 0.08 }}
              className="p-5 rounded-2xl border border-white/[0.06] bg-white/[0.02] hover:border-amber-500/20 hover:bg-amber-500/[0.03] transition-all duration-300 group text-center"
            >
              <div className="w-10 h-10 rounded-xl bg-amber-500/10 flex items-center justify-center mx-auto mb-3 group-hover:bg-amber-500/20 transition-colors">
                <feat.icon className="w-5 h-5 text-amber-400" />
              </div>
              <h3 className="font-semibold text-white text-sm mb-2">{feat.title}</h3>
              <p className="text-xs text-white/45 leading-relaxed">{feat.description}</p>
            </motion.div>
          ))}
        </div>

        {/* Gallery */}
        <div className="grid grid-cols-3 grid-rows-3 gap-3 h-[500px] md:h-[600px]">
          {GALLERY_IMAGES.map((img, i) => (
            <motion.div
              key={img.src}
              initial={{ opacity: 0, scale: 0.97 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: i * 0.1 }}
              className={`relative overflow-hidden rounded-2xl border border-white/[0.06] ${img.className}`}
            >
              <Image
                src={img.src}
                alt={img.alt}
                fill
                className="object-cover hover:scale-105 transition-transform duration-700"
                sizes="(max-width: 768px) 50vw, 33vw"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/30 to-transparent" />
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
