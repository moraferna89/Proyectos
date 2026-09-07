"use client";

import { motion } from "framer-motion";
import { MapPin, Phone, Mail, Clock, Car, Instagram } from "lucide-react";
import { Button } from "@/components/ui/button";
import { SectionHeader } from "@/components/ui/section-header";
import { SITE_CONFIG, SCHEDULE } from "@/lib/constants";
import { slideInLeft, slideInRight } from "@/lib/animations";

const contactDetails = [
  {
    icon: MapPin,
    label: "Dirección",
    value: SITE_CONFIG.address,
    sub: SITE_CONFIG.addressDetail,
    href: SITE_CONFIG.mapLink,
  },
  {
    icon: Phone,
    label: "Teléfono",
    value: SITE_CONFIG.phone,
    href: SITE_CONFIG.phoneHref,
  },
  {
    icon: Mail,
    label: "Email",
    value: SITE_CONFIG.email,
    href: `mailto:${SITE_CONFIG.email}`,
  },
  {
    icon: Car,
    label: "Estacionamiento",
    value: "Amplio estacionamiento disponible",
  },
];

export function Location() {
  return (
    <section id="ubicacion" className="py-20 md:py-28 bg-slate-950 overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <SectionHeader
          badge="Cómo Llegar"
          title="Encuéntranos en"
          titleHighlight="Concepción"
          description="Visítanos en nuestras instalaciones. Contamos con estacionamiento y estamos ubicados en un lugar de fácil acceso."
          dark
        />

        <div className="grid lg:grid-cols-2 gap-10 items-start">
          {/* Map */}
          <motion.div
            variants={slideInLeft}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.3 }}
            className="rounded-3xl overflow-hidden shadow-2xl shadow-blue-500/10 aspect-[4/3]"
          >
            <iframe
              title="Ubicación Clínica Veterinaria Huellas"
              src="https://maps.google.com/maps?q=Paicaví+976,+Concepción,+Chile&t=&z=17&ie=UTF8&iwloc=&output=embed"
              width="100%"
              height="100%"
              style={{ border: 0 }}
              allowFullScreen
              loading="lazy"
              referrerPolicy="no-referrer-when-downgrade"
              className="w-full h-full grayscale contrast-125"
            />
          </motion.div>

          {/* Info */}
          <motion.div
            variants={slideInRight}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.3 }}
            className="space-y-6"
          >
            {/* Contact details */}
            <div className="space-y-4">
              {contactDetails.map(({ icon: Icon, label, value, sub, href }) => (
                <div
                  key={label}
                  className="flex items-start gap-4 p-4 rounded-2xl bg-white/5 border border-white/8 hover:bg-white/8 transition-colors"
                >
                  <div className="w-10 h-10 rounded-xl bg-blue-600/20 flex items-center justify-center shrink-0">
                    <Icon className="w-5 h-5 text-blue-400" />
                  </div>
                  <div>
                    <div className="text-slate-400 text-xs font-medium uppercase tracking-wide mb-1">
                      {label}
                    </div>
                    {href ? (
                      <a
                        href={href}
                        target={href.startsWith("http") ? "_blank" : undefined}
                        rel="noopener noreferrer"
                        className="text-white font-medium hover:text-blue-400 transition-colors"
                      >
                        {value}
                      </a>
                    ) : (
                      <span className="text-white font-medium">{value}</span>
                    )}
                    {sub && (
                      <p className="text-slate-400 text-xs mt-0.5">{sub}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {/* Schedule */}
            <div className="p-5 rounded-2xl bg-white/5 border border-white/8">
              <div className="flex items-center gap-2 mb-4">
                <Clock className="w-5 h-5 text-blue-400" />
                <h4 className="text-white font-semibold font-heading">
                  Horario de Atención
                </h4>
              </div>
              <div className="space-y-2">
                {SCHEDULE.map((item) => (
                  <div key={item.day} className="flex justify-between items-center py-1.5 border-b border-white/5 last:border-0">
                    <span className="text-slate-300 text-sm">{item.day}</span>
                    <span
                      className={`text-sm font-semibold ${
                        item.hours === "Cerrado"
                          ? "text-red-400"
                          : "text-blue-400"
                      }`}
                    >
                      {item.hours}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* CTA buttons */}
            <div className="flex flex-col sm:flex-row gap-3">
              <Button
                asChild
                variant="gradient"
                size="lg"
                className="flex-1"
              >
                <a
                  href={SITE_CONFIG.mapLink}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <MapPin className="w-4 h-4" />
                  Cómo llegar
                </a>
              </Button>
              <Button
                asChild
                variant="outlineWhite"
                size="lg"
                className="flex-1"
              >
                <a
                  href={SITE_CONFIG.instagram}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <Instagram className="w-4 h-4" />
                  Síguenos en IG
                </a>
              </Button>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
