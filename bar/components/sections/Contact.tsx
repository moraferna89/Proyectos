"use client";

import { motion } from "framer-motion";
import { MapPin, Phone, Clock, Instagram, ExternalLink, Mail } from "lucide-react";
import { SectionTitle } from "@/components/shared/SectionTitle";
import { Button } from "@/components/shared/Button";
import { SITE_CONFIG } from "@/lib/constants";

const CONTACT_CARDS = [
  {
    icon: MapPin,
    title: "Ubicación",
    lines: [SITE_CONFIG.address],
    action: {
      label: "Ver en Google Maps",
      href: `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(SITE_CONFIG.address)}`,
      external: true,
    },
  },
  {
    icon: Phone,
    title: "Teléfono",
    lines: [SITE_CONFIG.phone],
    action: {
      label: "Llamar ahora",
      href: `tel:${SITE_CONFIG.phone.replace(/\s/g, "")}`,
      external: false,
    },
  },
  {
    icon: Clock,
    title: "Horarios",
    lines: [
      SITE_CONFIG.hours.weekdays,
      SITE_CONFIG.hours.friday,
      SITE_CONFIG.hours.weekend,
    ],
    action: null,
  },
  {
    icon: Instagram,
    title: "Redes Sociales",
    lines: ["@fuente.divka", "@fuentedivka"],
    action: {
      label: "Seguir en Instagram",
      href: SITE_CONFIG.instagram,
      external: true,
    },
  },
];

export function Contact() {
  return (
    <section id="contacto" className="relative overflow-hidden bg-[#080808]">
      <div className="absolute inset-x-0 top-0 h-px glow-line" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[700px] bg-amber-500/5 rounded-full blur-[180px] pointer-events-none" />

      <div className="container-wide section-padding">
        <div className="flex flex-col items-center mb-14">
          <SectionTitle
            eyebrow="Contáctanos"
            title="Ven a"
            titleHighlight="visitarnos."
            description="Estamos en Apoquindo 7645, Las Condes. Fácil acceso en metro y con estacionamiento cercano. Te esperamos."
            align="center"
          />
        </div>

        {/* Contact Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-12">
          {CONTACT_CARDS.map((card, i) => (
            <motion.div
              key={card.title}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: i * 0.08 }}
              className="p-5 rounded-2xl border border-white/[0.06] bg-white/[0.02] hover:border-amber-500/20 hover:bg-amber-500/[0.03] transition-all duration-300 group flex flex-col gap-4"
            >
              <div className="w-10 h-10 rounded-xl bg-amber-500/10 flex items-center justify-center group-hover:bg-amber-500/20 transition-colors">
                <card.icon className="w-5 h-5 text-amber-400" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-white text-sm mb-2">{card.title}</h3>
                <div className="space-y-1">
                  {card.lines.map((line) => (
                    <p key={line} className="text-xs text-white/50 leading-relaxed">{line}</p>
                  ))}
                </div>
              </div>
              {card.action && (
                <a
                  href={card.action.href}
                  target={card.action.external ? "_blank" : undefined}
                  rel={card.action.external ? "noopener noreferrer" : undefined}
                  className="flex items-center gap-1.5 text-xs font-medium text-amber-400 hover:text-amber-300 transition-colors"
                >
                  {card.action.label}
                  {card.action.external && <ExternalLink className="w-3 h-3" />}
                </a>
              )}
            </motion.div>
          ))}
        </div>

        {/* Map Embed Placeholder */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="relative h-72 md:h-96 rounded-3xl overflow-hidden border border-white/[0.06] bg-white/[0.02]"
        >
          {/* Map placeholder — replace with <iframe> embed when ready */}
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-4">
            <div className="w-16 h-16 rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center">
              <MapPin className="w-8 h-8 text-amber-400" />
            </div>
            <div className="text-center">
              <p className="text-white font-semibold mb-1">{SITE_CONFIG.address}</p>
              <p className="text-white/40 text-sm">Las Condes, Santiago, Chile</p>
            </div>
            <Button
              href={`https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(SITE_CONFIG.address)}`}
              variant="outline"
              size="sm"
            >
              <ExternalLink className="w-4 h-4" />
              Abrir en Google Maps
            </Button>
          </div>
        </motion.div>

        {/* Bottom CTA Banner */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="mt-10 p-8 rounded-3xl border border-amber-500/20 bg-gradient-to-r from-amber-500/[0.06] to-transparent flex flex-col sm:flex-row items-center justify-between gap-6"
        >
          <div>
            <h3 className="text-xl font-bold text-white mb-1">¿Listo para una buena cerveza?</h3>
            <p className="text-white/50 text-sm">Reserva tu mesa o llámanos directamente.</p>
          </div>
          <div className="flex flex-wrap gap-3">
            <Button href={`tel:${SITE_CONFIG.phone}`} variant="primary" size="md">
              <Phone className="w-4 h-4" />
              Llamar ahora
            </Button>
            <Button href={`mailto:${SITE_CONFIG.email}`} variant="secondary" size="md">
              <Mail className="w-4 h-4" />
              Enviar email
            </Button>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
