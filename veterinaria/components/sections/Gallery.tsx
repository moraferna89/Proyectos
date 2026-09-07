"use client";

import { motion } from "framer-motion";
import Image from "next/image";
import { Heart } from "lucide-react";
import { Button } from "@/components/ui/button";
import { SectionHeader } from "@/components/ui/section-header";
import { GALLERY_IMAGES } from "@/lib/constants";
import { staggerContainer, scaleIn } from "@/lib/animations";

export function Gallery() {
  return (
    <section id="pacientes" className="py-20 md:py-28 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <SectionHeader
          badge="Nuestros Pacientes"
          title="Ellos son nuestra"
          titleHighlight="razón de ser"
          description="Cada uno de estos compañeros ha pasado por nuestras manos con amor y cuidado. ¿Ya nos traes al tuyo?"
        />

        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.1 }}
          className="grid grid-cols-2 md:grid-cols-3 gap-4 md:gap-5"
        >
          {GALLERY_IMAGES.map((img, index) => (
            <motion.div
              key={img.id}
              variants={scaleIn}
              className={`group relative overflow-hidden rounded-2xl shadow-md cursor-default ${
                index === 0 ? "md:col-span-2 md:row-span-2" : ""
              }`}
            >
              <div
                className={`relative w-full ${
                  index === 0 ? "aspect-square" : "aspect-square"
                }`}
              >
                <Image
                  src={img.src}
                  alt={img.alt}
                  fill
                  className="object-cover transition-transform duration-500 group-hover:scale-110"
                />
                {/* Hover overlay */}
                <div className="absolute inset-0 bg-gradient-to-t from-slate-900/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

                {/* Pet name on hover */}
                <div className="absolute bottom-0 left-0 right-0 p-4 translate-y-full group-hover:translate-y-0 transition-transform duration-300">
                  <div className="flex items-center gap-2">
                    <Heart className="w-4 h-4 text-blue-400 fill-blue-400" />
                    <span className="text-white font-semibold text-sm">
                      {img.name}
                    </span>
                  </div>
                </div>

                {/* Green corner accent */}
                <div className="absolute top-3 right-3 w-8 h-8 rounded-full bg-blue-500/90 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300 shadow-md">
                  <Heart className="w-4 h-4 text-white fill-white" />
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* CTA */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.3, duration: 0.6 }}
          className="text-center mt-12"
        >
          <p className="text-slate-500 mb-4">
            Únete a la familia Huellas. ¡Tu mascota merece lo mejor!
          </p>
          <Button
            onClick={() =>
              document
                .querySelector("#contacto")
                ?.scrollIntoView({ behavior: "smooth" })
            }
            variant="gradient"
            size="lg"
          >
            Agenda una consulta hoy
          </Button>
        </motion.div>
      </div>
    </section>
  );
}
