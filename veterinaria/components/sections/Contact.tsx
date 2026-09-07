"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Send, CheckCircle2, Phone, Mail, MapPin } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { SectionHeader } from "@/components/ui/section-header";
import { SITE_CONFIG, PET_TYPES } from "@/lib/constants";
import { slideInLeft, slideInRight, staggerContainer, fadeInUp } from "@/lib/animations";

interface FormState {
  name: string;
  email: string;
  phone: string;
  petType: string;
  message: string;
}

const initialForm: FormState = {
  name: "",
  email: "",
  phone: "",
  petType: "",
  message: "",
};

const quickContacts = [
  {
    icon: Phone,
    label: "Llámanos",
    value: SITE_CONFIG.phone,
    href: SITE_CONFIG.phoneHref,
  },
  {
    icon: Mail,
    label: "Escríbenos",
    value: SITE_CONFIG.email,
    href: `mailto:${SITE_CONFIG.email}`,
  },
  {
    icon: MapPin,
    label: "Visítanos",
    value: SITE_CONFIG.address,
    href: SITE_CONFIG.mapLink,
  },
];

export function Contact() {
  const [form, setForm] = useState<FormState>(initialForm);
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    await new Promise((r) => setTimeout(r, 1200));
    setLoading(false);
    setSubmitted(true);
  };

  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >
  ) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  return (
    <section id="contacto" className="py-20 md:py-28 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <SectionHeader
          badge="Contáctanos"
          title="Agenda tu consulta"
          titleHighlight="hoy"
          description="Completa el formulario y nos pondremos en contacto contigo a la brevedad. ¡Tu mascota lo merece!"
        />

        <div className="grid lg:grid-cols-5 gap-12">
          {/* Form */}
          <motion.div
            variants={slideInLeft}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.2 }}
            className="lg:col-span-3"
          >
            {submitted ? (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="flex flex-col items-center justify-center text-center h-full min-h-[400px] bg-blue-50 rounded-3xl p-12 border border-blue-100"
              >
                <div className="w-20 h-20 rounded-full bg-blue-100 flex items-center justify-center mb-6">
                  <CheckCircle2 className="w-10 h-10 text-blue-600" />
                </div>
                <h3 className="text-2xl font-bold text-slate-900 mb-3 font-heading">
                  ¡Mensaje enviado!
                </h3>
                <p className="text-slate-500 max-w-sm leading-relaxed">
                  Gracias por contactarnos. Nos comunicaremos contigo dentro de
                  las próximas horas para confirmar tu consulta.
                </p>
                <Button
                  onClick={() => {
                    setSubmitted(false);
                    setForm(initialForm);
                  }}
                  variant="outline"
                  className="mt-6"
                >
                  Enviar otro mensaje
                </Button>
              </motion.div>
            ) : (
              <form
                onSubmit={handleSubmit}
                className="bg-slate-50 rounded-3xl p-8 border border-slate-100"
              >
                <div className="grid sm:grid-cols-2 gap-5 mb-5">
                  <div className="space-y-2">
                    <Label htmlFor="name">Nombre completo *</Label>
                    <Input
                      id="name"
                      name="name"
                      value={form.name}
                      onChange={handleChange}
                      placeholder="Tu nombre"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="email">Email *</Label>
                    <Input
                      id="email"
                      name="email"
                      type="email"
                      value={form.email}
                      onChange={handleChange}
                      placeholder="tu@email.cl"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="phone">Teléfono</Label>
                    <Input
                      id="phone"
                      name="phone"
                      type="tel"
                      value={form.phone}
                      onChange={handleChange}
                      placeholder="+56 9 XXXX XXXX"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="petType">Tipo de mascota</Label>
                    <select
                      id="petType"
                      name="petType"
                      value={form.petType}
                      onChange={handleChange}
                      className="flex h-11 w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
                    >
                      <option value="">Seleccionar</option>
                      {PET_TYPES.map((type) => (
                        <option key={type} value={type}>
                          {type}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="space-y-2 mb-6">
                  <Label htmlFor="message">Mensaje *</Label>
                  <Textarea
                    id="message"
                    name="message"
                    value={form.message}
                    onChange={handleChange}
                    placeholder="Cuéntanos qué necesitas para tu mascota..."
                    required
                    className="min-h-[140px]"
                  />
                </div>

                <Button
                  type="submit"
                  variant="gradient"
                  size="lg"
                  className="w-full group"
                  disabled={loading}
                >
                  {loading ? (
                    <span className="flex items-center gap-2">
                      <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                      </svg>
                      Enviando...
                    </span>
                  ) : (
                    <>
                      Enviar mensaje
                      <Send className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                    </>
                  )}
                </Button>

                <p className="text-slate-400 text-xs text-center mt-4">
                  Respondemos dentro de las próximas 24 horas hábiles.
                </p>
              </form>
            )}
          </motion.div>

          {/* Sidebar */}
          <motion.div
            variants={staggerContainer}
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.2 }}
            className="lg:col-span-2 space-y-5"
          >
            {/* Quick contact cards */}
            {quickContacts.map(({ icon: Icon, label, value, href }) => (
              <motion.div key={label} variants={fadeInUp}>
                <a
                  href={href}
                  target={href?.startsWith("http") ? "_blank" : undefined}
                  rel="noopener noreferrer"
                  className="flex items-start gap-4 p-5 rounded-2xl bg-slate-50 border border-slate-100 hover:border-blue-200 hover:bg-blue-50/50 hover:shadow-md transition-all duration-300 group"
                >
                  <div className="w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center shrink-0 group-hover:bg-blue-600 transition-colors">
                    <Icon className="w-6 h-6 text-blue-600 group-hover:text-white transition-colors" />
                  </div>
                  <div>
                    <div className="text-xs text-slate-400 font-medium uppercase tracking-wide mb-1">
                      {label}
                    </div>
                    <div className="text-slate-800 font-semibold text-sm group-hover:text-blue-700 transition-colors">
                      {value}
                    </div>
                  </div>
                </a>
              </motion.div>
            ))}

            {/* Info banner */}
            <motion.div
              variants={fadeInUp}
              className="p-5 rounded-2xl bg-gradient-to-br from-blue-600 to-sky-600 text-white shadow-lg shadow-blue-600/25"
            >
              <div className="text-2xl mb-3">🐾</div>
              <h4 className="font-bold font-heading text-lg mb-2">
                Primera consulta
              </h4>
              <p className="text-blue-100 text-sm leading-relaxed">
                En tu primera visita, realizamos una evaluación completa del
                estado de salud de tu mascota sin costo adicional por el chequeo
                preventivo.
              </p>
            </motion.div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
