"use client";

import { motion } from "framer-motion";
import { Phone, Mail } from "lucide-react";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Button } from "@/components/ui/button";
import { SectionHeader } from "@/components/ui/section-header";
import { FAQ_ITEMS, SITE_CONFIG } from "@/lib/constants";
import { staggerContainer, fadeInUp, slideInRight } from "@/lib/animations";

export function FAQ() {
  return (
    <section id="faq" className="py-20 md:py-28 bg-slate-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <SectionHeader
          badge="Preguntas Frecuentes"
          title="Resolvemos tus"
          titleHighlight="dudas"
          description="Todo lo que necesitas saber sobre nuestros servicios y el cuidado de tu mascota."
        />

        <div className="grid lg:grid-cols-3 gap-12 items-start">
          {/* FAQ accordion */}
          <motion.div
            variants={staggerContainer}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.1 }}
            className="lg:col-span-2 space-y-3"
          >
            <Accordion type="single" collapsible>
              {FAQ_ITEMS.map((item, index) => (
                <motion.div key={index} variants={fadeInUp}>
                  <AccordionItem value={`item-${index}`} className="mb-3">
                    <AccordionTrigger>{item.question}</AccordionTrigger>
                    <AccordionContent>{item.answer}</AccordionContent>
                  </AccordionItem>
                </motion.div>
              ))}
            </Accordion>
          </motion.div>

          {/* Sidebar */}
          <motion.div
            variants={slideInRight}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.3 }}
            className="space-y-5"
          >
            {/* Contact card */}
            <div className="bg-gradient-to-br from-blue-600 to-sky-600 rounded-2xl p-6 shadow-lg shadow-blue-600/25 text-white">
              <div className="text-3xl mb-3">🐾</div>
              <h3 className="font-bold text-xl mb-2 font-heading">
                ¿No encontraste tu respuesta?
              </h3>
              <p className="text-blue-100 text-sm leading-relaxed mb-5">
                Nuestro equipo está disponible para responder todas tus preguntas
                de forma personalizada.
              </p>
              <div className="space-y-3">
                <a href={SITE_CONFIG.phoneHref}>
                  <Button variant="white" className="w-full justify-start gap-3">
                    <Phone className="w-4 h-4 text-blue-600" />
                    {SITE_CONFIG.phone}
                  </Button>
                </a>
                <a href={`mailto:${SITE_CONFIG.email}`}>
                  <Button
                    variant="outlineWhite"
                    className="w-full justify-start gap-3 mt-2"
                  >
                    <Mail className="w-4 h-4" />
                    Enviar email
                  </Button>
                </a>
              </div>
            </div>

            {/* Hours card */}
            <div className="bg-white rounded-2xl p-6 border border-slate-100 shadow-sm">
              <h4 className="font-bold text-slate-900 mb-4 font-heading">
                Horario de Atención
              </h4>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-slate-600 text-sm">Lunes – Viernes</span>
                  <span className="font-semibold text-slate-900 text-sm">
                    10:30 – 18:30
                  </span>
                </div>
                <div className="h-px bg-slate-100" />
                <div className="flex items-center justify-between">
                  <span className="text-slate-600 text-sm">Sábado</span>
                  <span className="text-red-500 text-sm font-medium">Cerrado</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-600 text-sm">Domingo / Festivos</span>
                  <span className="text-red-500 text-sm font-medium">Cerrado</span>
                </div>
              </div>
              <div className="mt-4 flex items-center gap-2 bg-blue-50 rounded-xl p-3">
                <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
                <span className="text-blue-700 text-sm font-medium">
                  Atendemos con o sin cita previa
                </span>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
