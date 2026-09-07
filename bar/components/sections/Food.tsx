"use client";

import { motion } from "framer-motion";
import Image from "next/image";
import { Sparkles } from "lucide-react";
import { SectionTitle } from "@/components/shared/SectionTitle";
import { AnimatedCard } from "@/components/shared/AnimatedCard";
import { Badge } from "@/components/shared/Badge";
import { FOOD_ITEMS } from "@/lib/constants";

const FOOD_IMAGES = [
  "https://images.unsplash.com/photo-1606755962773-d324e0a13086?q=80&w=800",
  "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?q=80&w=800",
  "https://images.unsplash.com/photo-1513104890138-7c749659a591?q=80&w=800",
];

export function Food() {
  return (
    <section id="carta" className="relative overflow-hidden">
      {/* Ambient */}
      <div className="absolute bottom-0 left-0 w-[500px] h-[500px] bg-amber-600/5 rounded-full blur-[140px] pointer-events-none" />

      <div className="container-wide section-padding">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 lg:gap-24 items-start">
          {/* Left – Menu */}
          <div className="space-y-10">
            <SectionTitle
              eyebrow="Carta de Alimentos"
              title="Comida que"
              titleHighlight="enamora."
              description="Pensada para maridar con nuestra cerveza. Cada plato es una experiencia que complementa tu bebida favorita."
              align="left"
            />

            <div className="space-y-8">
              {FOOD_ITEMS.map((category, ci) => (
                <motion.div
                  key={category.category}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: ci * 0.1 }}
                >
                  <div className="flex items-center gap-3 mb-4">
                    <span className="text-xs font-bold text-amber-400 uppercase tracking-[0.15em]">
                      {category.category}
                    </span>
                    <span className="flex-1 h-px bg-white/[0.06]" />
                  </div>

                  <div className="space-y-3">
                    {category.items.map((item, ii) => (
                      <AnimatedCard
                        key={item.name}
                        delay={ci * 0.1 + ii * 0.05}
                        className="p-4"
                        hover
                      >
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1.5">
                              <h3 className="font-semibold text-white text-sm">{item.name}</h3>
                              {item.badge && (
                                <Badge
                                  variant={
                                    item.badge === "Favorita"
                                      ? "amber"
                                      : item.badge === "Nuevo"
                                      ? "amber"
                                      : "dark"
                                  }
                                >
                                  {item.badge === "Favorita" && (
                                    <Sparkles className="w-3 h-3 mr-1" />
                                  )}
                                  {item.badge}
                                </Badge>
                              )}
                            </div>
                            <p className="text-xs text-white/45 leading-relaxed">
                              {item.description}
                            </p>
                          </div>
                          <div className="flex-shrink-0 text-sm font-bold text-amber-400">
                            {item.price}
                          </div>
                        </div>
                      </AnimatedCard>
                    ))}
                  </div>
                </motion.div>
              ))}
            </div>

            <motion.p
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              className="text-xs text-white/30 italic"
            >
              * Precios en pesos chilenos. IVA incluido. Carta sujeta a cambios estacionales.
            </motion.p>
          </div>

          {/* Right – Images */}
          <div className="hidden lg:block sticky top-28 space-y-4">
            {FOOD_IMAGES.map((src, i) => (
              <motion.div
                key={src}
                initial={{ opacity: 0, x: 30 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: i * 0.15 }}
                className={`relative overflow-hidden rounded-2xl border border-white/[0.06] ${
                  i === 1 ? "h-48 ml-8" : "h-56"
                }`}
              >
                <Image
                  src={src}
                  alt={`Plato ${i + 1}`}
                  fill
                  className="object-cover hover:scale-105 transition-transform duration-700"
                  sizes="(max-width: 1024px) 0vw, 40vw"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/40 to-transparent" />
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
