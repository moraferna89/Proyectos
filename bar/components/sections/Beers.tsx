"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Droplets, Flame, Percent } from "lucide-react";
import { SectionTitle } from "@/components/shared/SectionTitle";
import { AnimatedCard } from "@/components/shared/AnimatedCard";
import { Badge } from "@/components/shared/Badge";
import { BEERS } from "@/lib/constants";

const IBU_LEVELS = [
  { max: 20, label: "Suave", color: "text-green-400" },
  { max: 40, label: "Equilibrada", color: "text-amber-400" },
  { max: 60, label: "Amarga", color: "text-orange-400" },
  { max: 100, label: "Muy Amarga", color: "text-red-400" },
];

function getIbuLabel(ibu: number) {
  return IBU_LEVELS.find((l) => ibu <= l.max) ?? IBU_LEVELS[IBU_LEVELS.length - 1];
}

const BEER_COLORS: Record<string, string> = {
  Dorado: "from-yellow-400/20 to-amber-600/20",
  Ámbar: "from-amber-500/20 to-orange-700/20",
  Negro: "from-zinc-800/40 to-zinc-950/40",
  Cobre: "from-orange-500/20 to-red-700/20",
  Pálido: "from-yellow-200/20 to-yellow-400/20",
  Marrón: "from-yellow-800/20 to-amber-900/20",
  Turbia: "from-amber-300/20 to-orange-500/20",
};

export function Beers() {
  const [hovered, setHovered] = useState<number | null>(null);

  return (
    <section id="cervezas" className="relative overflow-hidden bg-[#080808]">
      {/* Decorative glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-amber-500/5 rounded-full blur-[160px] pointer-events-none" />
      <div className="absolute inset-x-0 top-0 h-px glow-line" />

      <div className="container-wide section-padding">
        <div className="flex flex-col items-center mb-16">
          <SectionTitle
            eyebrow="Carta de Cervezas"
            title="18 variedades"
            titleHighlight="artesanales."
            description="Cada cerveza es una historia. Descubre nuestra selección cuidadosamente curada de cervezas nacionales e importadas, con algo para cada paladar."
            align="center"
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {BEERS.map((beer, i) => {
            const ibuInfo = getIbuLabel(beer.ibu);
            const colorGradient = BEER_COLORS[beer.color] || BEER_COLORS.Dorado;

            return (
              <AnimatedCard
                key={beer.name}
                delay={i * 0.05}
                className="p-5"
                hover
              >
                <div
                  onMouseEnter={() => setHovered(i)}
                  onMouseLeave={() => setHovered(null)}
                >
                  {/* Beer visual */}
                  <div
                    className={`relative h-32 rounded-xl mb-4 bg-gradient-to-br ${colorGradient} border border-white/[0.06] flex items-center justify-center overflow-hidden`}
                  >
                    <motion.span
                      animate={hovered === i ? { scale: 1.2, rotate: -5 } : { scale: 1, rotate: 0 }}
                      transition={{ duration: 0.3 }}
                      className="text-5xl"
                    >
                      {beer.icon}
                    </motion.span>
                    <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent" />

                    {/* ABV pill */}
                    <div className="absolute top-3 right-3 flex items-center gap-1 bg-black/50 backdrop-blur-sm px-2 py-1 rounded-full">
                      <Percent className="w-2.5 h-2.5 text-amber-400" />
                      <span className="text-xs font-bold text-amber-400">{beer.abv}</span>
                    </div>
                  </div>

                  {/* Info */}
                  <div className="space-y-2">
                    <div className="flex items-start justify-between gap-2">
                      <h3 className="font-bold text-white text-base leading-tight">{beer.name}</h3>
                    </div>
                    <Badge variant="dark">{beer.style}</Badge>
                    <p className="text-xs text-white/50 leading-relaxed pt-1">{beer.description}</p>

                    {/* IBU bar */}
                    <div className="pt-2 space-y-1">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-1 text-xs text-white/40">
                          <Droplets className="w-3 h-3" />
                          <span>IBU {beer.ibu}</span>
                        </div>
                        <div className={`flex items-center gap-1 text-xs font-medium ${ibuInfo.color}`}>
                          <Flame className="w-3 h-3" />
                          <span>{ibuInfo.label}</span>
                        </div>
                      </div>
                      <div className="h-1 bg-white/[0.06] rounded-full overflow-hidden">
                        <motion.div
                          initial={{ width: 0 }}
                          whileInView={{ width: `${Math.min((beer.ibu / 80) * 100, 100)}%` }}
                          viewport={{ once: true }}
                          transition={{ duration: 0.8, delay: i * 0.05 + 0.3 }}
                          className="h-full bg-gradient-to-r from-amber-500 to-amber-400 rounded-full"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </AnimatedCard>
            );
          })}
        </div>

        {/* CTA */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="mt-12 text-center"
        >
          <p className="text-white/40 text-sm mb-4">
            ¿No sabes qué elegir? Nuestros bartenders te recomendarán la perfecta.
          </p>
          <a
            href={`tel:${"+56229742722"}`}
            className="inline-flex items-center gap-2 px-6 py-3 rounded-xl border border-amber-500/30 text-amber-400 text-sm font-medium hover:bg-amber-500/10 hover:border-amber-500/50 transition-all"
          >
            Consultar carta completa
          </a>
        </motion.div>
      </div>
    </section>
  );
}
