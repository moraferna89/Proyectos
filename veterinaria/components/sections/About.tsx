"use client";

import { motion } from "framer-motion";
import Image from "next/image";
import { CheckCircle2, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { slideInLeft, slideInRight, staggerContainer, fadeInUp } from "@/lib/animations";

const differentiators = [
  "Atención personalizada para cada paciente",
  "Seguimiento continuo del historial de tu mascota",
  "Plan de vacunación y revisiones preventivas",
  "Equipo con formación y actualización constante",
  "Ambiente cálido y libre de estrés para tus mascotas",
  "Farmacia con productos de primera línea",
];

export function About() {
  return (
    <section id="nosotros" className="py-20 md:py-28 bg-slate-950 overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          {/* Left: Image */}
          <motion.div
            variants={slideInLeft}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.3 }}
            className="relative"
          >
            {/* Main image */}
            <div className="relative rounded-3xl overflow-hidden aspect-square shadow-2xl shadow-blue-500/10">
              <Image
                src="https://images.unsplash.com/photo-1628009368231-7bb7cfcb0def?w=700&h=700&fit=crop&q=80"
                alt="Veterinario con mascota"
                fill
                className="object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-slate-950/40 to-transparent" />
            </div>

            {/* Floating stats card */}
            <motion.div
              animate={{ y: [0, -8, 0] }}
              transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
              className="absolute -bottom-6 -right-6 bg-white rounded-2xl p-5 shadow-2xl max-w-[200px]"
            >
              <div className="text-4xl font-bold text-slate-900 font-heading gradient-text">
                15+
              </div>
              <p className="text-slate-500 text-sm mt-1">
                Años cuidando mascotas en Concepción
              </p>
            </motion.div>

            {/* Decoration dot */}
            <div className="absolute -top-4 -left-4 w-24 h-24 rounded-full bg-blue-500/15 blur-xl" />
          </motion.div>

          {/* Right: Content */}
          <motion.div
            variants={staggerContainer}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.3 }}
          >
            <motion.div variants={fadeInUp} className="mb-6">
              <Badge variant="white">Sobre Nosotros</Badge>
            </motion.div>

            <motion.h2
              variants={fadeInUp}
              className="text-3xl md:text-4xl lg:text-5xl font-bold text-white leading-tight tracking-tight mb-6 font-heading"
            >
              Tu veterinario de{" "}
              <span className="gradient-text-light">cabecera</span>{" "}
              en Concepción
            </motion.h2>

            <motion.p
              variants={fadeInUp}
              className="text-slate-300 text-lg leading-relaxed mb-4"
            >
              En Clínica Veterinaria Huellas creemos que cada mascota merece un
              médico que la conozca, que recuerde su historial y que esté
              presente en cada etapa de su vida.
            </motion.p>

            <motion.p
              variants={fadeInUp}
              className="text-slate-400 leading-relaxed mb-8"
            >
              Desde cachorros hasta adultos mayores, acompañamos a las familias
              de Concepción con revisiones preventivas, vacunas al día y
              tratamientos oportunos para que tu compañero crezca fuerte y sano.
            </motion.p>

            {/* Differentiators list */}
            <motion.ul variants={staggerContainer} className="space-y-3 mb-8">
              {differentiators.map((item) => (
                <motion.li
                  key={item}
                  variants={fadeInUp}
                  className="flex items-start gap-3"
                >
                  <CheckCircle2 className="w-5 h-5 text-blue-500 mt-0.5 shrink-0" />
                  <span className="text-slate-300 text-sm">{item}</span>
                </motion.li>
              ))}
            </motion.ul>

            <motion.div variants={fadeInUp}>
              <Button
                onClick={() =>
                  document
                    .querySelector("#contacto")
                    ?.scrollIntoView({ behavior: "smooth" })
                }
                variant="gradient"
                size="lg"
                className="group"
              >
                Conoce nuestro equipo
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Button>
            </motion.div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
