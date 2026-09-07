"use client";

import { motion } from "framer-motion";
import Image from "next/image";
import { Award, Users, Zap, Heart } from "lucide-react";
import { SectionTitle } from "@/components/shared/SectionTitle";

const VALUES = [
  {
    icon: Award,
    title: "12 Años de Trayectoria",
    description:
      "Desde 2012 siendo la picada favorita de Apoquindo. Historia, sabor y tradición en cada copa.",
  },
  {
    icon: Zap,
    title: "Cerveza Artesanal",
    description:
      "18 variedades cuidadosamente seleccionadas. Desde lagers suaves hasta IPAs explosivas.",
  },
  {
    icon: Heart,
    title: "Gastronomía Gourmet",
    description:
      "Tablas, picadas y platos diseñados para maridar perfecto con cada cerveza.",
  },
  {
    icon: Users,
    title: "El Mejor Ambiente",
    description:
      "Un espacio auténtico donde la gente se reúne. Pool, música y buena onda garantizados.",
  },
];

export function About() {
  return (
    <section id="nosotros" className="relative overflow-hidden">
      {/* Ambient glow */}
      <div className="absolute top-1/2 right-0 w-[600px] h-[600px] bg-amber-500/5 rounded-full blur-[160px] pointer-events-none -translate-y-1/2" />

      <div className="container-wide section-padding">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 lg:gap-24 items-center">
          {/* Left – Image */}
          <motion.div
            initial={{ opacity: 0, x: -40 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7, ease: "easeOut" }}
            className="relative"
          >
            <div className="relative aspect-[4/5] rounded-3xl overflow-hidden border border-white/[0.06]">
              <Image
                src="https://images.unsplash.com/photo-1559526324-4b87b5e36e44?q=80&w=1171"
                alt="Interior Fuente Divka"
                fill
                className="object-cover"
                sizes="(max-width: 1024px) 100vw, 50vw"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-[#0A0A0A]/60 to-transparent" />
            </div>

            {/* Floating Badge */}
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: 0.4 }}
              className="absolute -bottom-6 -right-6 bg-amber-500 text-black rounded-2xl p-5 shadow-glow-amber"
            >
              <div className="text-4xl font-extrabold leading-none">12+</div>
              <div className="text-xs font-semibold mt-1 opacity-80">Años en Santiago</div>
            </motion.div>

            {/* Second Image */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="absolute -top-8 -right-8 w-40 h-40 rounded-2xl overflow-hidden border-2 border-[#0A0A0A] shadow-2xl hidden lg:block"
            >
              <Image
                src="https://images.unsplash.com/photo-1571613316887-6f8d5cbf7ef7?q=80&w=500"
                alt="Cervezas artesanales"
                fill
                className="object-cover"
              />
            </motion.div>
          </motion.div>

          {/* Right – Content */}
          <div className="space-y-10">
            <SectionTitle
              eyebrow="Nuestra Historia"
              title="Más que un bar,"
              titleHighlight="una experiencia."
              description="Fuente Divka nació con la convicción de que una buena cerveza merece el mejor entorno. Hoy somos el punto de encuentro favorito de Las Condes: auténtico, apasionado y sin pretensiones."
              align="left"
            />

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
              {VALUES.map((item, i) => (
                <motion.div
                  key={item.title}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.4, delay: i * 0.1 }}
                  className="flex gap-4 p-4 rounded-xl bg-white/[0.03] border border-white/[0.06] hover:border-amber-500/20 hover:bg-amber-500/[0.03] transition-all duration-300 group"
                >
                  <div className="w-9 h-9 rounded-lg bg-amber-500/10 flex items-center justify-center flex-shrink-0 group-hover:bg-amber-500/20 transition-colors">
                    <item.icon className="w-4 h-4 text-amber-400" />
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-white mb-1">{item.title}</h3>
                    <p className="text-xs text-white/50 leading-relaxed">{item.description}</p>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
