"use client";

import { motion } from "framer-motion";
import {
  Stethoscope,
  Activity,
  Pill,
  Scissors,
  ShoppingBag,
  Package,
  Smile,
  ArrowRight,
} from "lucide-react";
import { SERVICES } from "@/lib/constants";
import { SectionHeader } from "@/components/ui/section-header";
import { staggerContainer, fadeInUp } from "@/lib/animations";

const ICONS = {
  Stethoscope,
  Activity,
  Pill,
  Scissors,
  ShoppingBag,
  Package,
  Smile,
};

export function Services() {
  return (
    <section id="servicios" className="py-20 md:py-28 bg-slate-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <SectionHeader
          badge="Nuestros Servicios"
          title="Todo lo que tu mascota"
          titleHighlight="necesita"
          description="Ofrecemos atención veterinaria integral bajo un mismo techo, con profesionales comprometidos con la salud y bienestar de tu compañero de vida."
        />

        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.1 }}
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5"
        >
          {SERVICES.map((service) => {
            const Icon = ICONS[service.icon as keyof typeof ICONS];
            return (
              <motion.div
                key={service.id}
                variants={fadeInUp}
                whileHover={{ y: -6, transition: { duration: 0.25 } }}
                className="group bg-white rounded-2xl p-6 border border-slate-100 hover:border-blue-200 shadow-sm hover:shadow-xl hover:shadow-blue-500/10 transition-all duration-300 cursor-default"
              >
                {/* Icon */}
                <div
                  className={`w-12 h-12 rounded-xl ${service.lightBg} flex items-center justify-center mb-5 group-hover:scale-110 transition-transform duration-300`}
                >
                  <Icon className={`w-6 h-6 ${service.iconColor}`} />
                </div>

                {/* Title */}
                <h3 className="font-bold text-slate-900 text-lg mb-3 font-heading leading-tight">
                  {service.title}
                </h3>

                {/* Description */}
                <p className="text-slate-500 text-sm leading-relaxed mb-4">
                  {service.description}
                </p>

                {/* Learn more link */}
                <div className="flex items-center gap-1 text-blue-600 text-sm font-semibold opacity-0 group-hover:opacity-100 transition-opacity duration-200 -translate-x-2 group-hover:translate-x-0">
                  <span>Saber más</span>
                  <ArrowRight className="w-4 h-4" />
                </div>
              </motion.div>
            );
          })}

          {/* CTA card */}
          <motion.a
            variants={fadeInUp}
            href="#contacto"
            onClick={(e) => {
              e.preventDefault();
              document.querySelector("#contacto")?.scrollIntoView({ behavior: "smooth" });
            }}
            whileHover={{ y: -6, transition: { duration: 0.25 } }}
            className="group bg-gradient-to-br from-blue-600 to-sky-600 rounded-2xl p-6 shadow-lg shadow-blue-600/25 hover:shadow-xl hover:shadow-blue-600/35 transition-all duration-300 cursor-pointer flex flex-col justify-between"
          >
            <div>
              <div className="w-12 h-12 rounded-xl bg-white/20 flex items-center justify-center mb-5">
                <span className="text-2xl">🐾</span>
              </div>
              <h3 className="font-bold text-white text-lg mb-3 font-heading leading-tight">
                ¿Necesitas orientación?
              </h3>
              <p className="text-blue-100 text-sm leading-relaxed">
                Contáctanos y nuestro equipo te guiará hacia el mejor servicio para tu mascota.
              </p>
            </div>
            <div className="flex items-center gap-1 text-white text-sm font-semibold mt-5 group-hover:gap-2 transition-all">
              <span>Contactar ahora</span>
              <ArrowRight className="w-4 h-4" />
            </div>
          </motion.a>
        </motion.div>
      </div>
    </section>
  );
}
