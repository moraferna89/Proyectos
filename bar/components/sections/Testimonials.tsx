"use client";

import { motion } from "framer-motion";
import { Star, Quote } from "lucide-react";
import { SectionTitle } from "@/components/shared/SectionTitle";
import { AnimatedCard } from "@/components/shared/AnimatedCard";
import { TESTIMONIALS } from "@/lib/constants";

export function Testimonials() {
  return (
    <section className="relative overflow-hidden">
      <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[600px] h-[300px] bg-amber-500/5 rounded-full blur-[120px] pointer-events-none" />

      <div className="container-wide section-padding">
        <div className="flex flex-col items-center mb-14">
          <SectionTitle
            eyebrow="Testimonios"
            title="Lo que dicen"
            titleHighlight="nuestros clientes."
            align="center"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {TESTIMONIALS.map((t, i) => (
            <AnimatedCard key={t.name} delay={i * 0.1} className="p-6">
              <div className="flex items-start gap-3 mb-4">
                <div className="w-10 h-10 rounded-xl bg-amber-500/20 flex items-center justify-center flex-shrink-0">
                  <span className="text-amber-400 font-bold text-sm">{t.name[0]}</span>
                </div>
                <div>
                  <p className="font-semibold text-white text-sm">{t.name}</p>
                  <div className="flex items-center gap-0.5 mt-1">
                    {Array.from({ length: t.rating }).map((_, si) => (
                      <Star key={si} className="w-3 h-3 text-amber-400 fill-amber-400" />
                    ))}
                  </div>
                </div>
                <Quote className="w-6 h-6 text-amber-500/20 ml-auto flex-shrink-0" />
              </div>
              <p className="text-sm text-white/55 leading-relaxed">{t.text}</p>
            </AnimatedCard>
          ))}
        </div>

        {/* Google Rating */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="mt-10 flex items-center justify-center gap-6"
        >
          <div className="flex items-center gap-2 px-5 py-3 rounded-xl bg-white/[0.03] border border-white/[0.06]">
            <div className="flex items-center gap-0.5">
              {Array.from({ length: 5 }).map((_, i) => (
                <Star key={i} className="w-4 h-4 text-amber-400 fill-amber-400" />
              ))}
            </div>
            <span className="text-white font-bold text-sm">5.0</span>
            <span className="text-white/40 text-xs">en Google</span>
          </div>

          <div className="h-8 w-px bg-white/[0.08]" />

          <p className="text-white/40 text-sm">
            +5,000 clientes satisfechos
          </p>
        </motion.div>
      </div>
    </section>
  );
}
