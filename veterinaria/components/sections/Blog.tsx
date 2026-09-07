"use client";

import { motion } from "framer-motion";
import Image from "next/image";
import { ArrowRight, Clock, BookOpen } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { SectionHeader } from "@/components/ui/section-header";
import { BLOG_POSTS } from "@/lib/constants";
import { staggerContainer, fadeInUp } from "@/lib/animations";

export function Blog() {
  return (
    <section id="blog" className="py-20 md:py-28 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4 mb-12 md:mb-16">
          <SectionHeader
            badge="Blog Veterinario"
            title="Consejos para cuidar"
            titleHighlight="a tu mascota"
            description="Artículos educativos escritos por nuestro equipo para ayudarte a mantener a tu compañero feliz y saludable."
            centered={false}
            className="mb-0"
          />
          <button
            onClick={() =>
              document
                .querySelector("#contacto")
                ?.scrollIntoView({ behavior: "smooth" })
            }
            className="hidden md:flex items-center gap-2 text-blue-600 font-semibold hover:gap-3 transition-all shrink-0"
          >
            Ver todos los artículos <ArrowRight className="w-5 h-5" />
          </button>
        </div>

        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.1 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
        >
          {BLOG_POSTS.map((post, index) => (
            <motion.article
              key={post.id}
              variants={fadeInUp}
              whileHover={{ y: -4, transition: { duration: 0.2 } }}
              className={`group bg-white rounded-2xl border border-slate-100 overflow-hidden shadow-sm hover:shadow-xl hover:shadow-slate-200/60 transition-all duration-300 ${
                index === 0 ? "md:col-span-2 lg:col-span-1" : ""
              }`}
            >
              {/* Image */}
              <div className="relative aspect-[16/9] overflow-hidden">
                <Image
                  src={post.image}
                  alt={post.title}
                  fill
                  className="object-cover transition-transform duration-500 group-hover:scale-105"
                />
                <div className="absolute top-4 left-4">
                  <Badge variant="category" className="bg-blue-600 text-white">
                    {post.category}
                  </Badge>
                </div>
              </div>

              {/* Content */}
              <div className="p-6">
                <div className="flex items-center gap-4 text-slate-400 text-xs mb-3">
                  <span className="flex items-center gap-1">
                    <BookOpen className="w-3.5 h-3.5" />
                    {post.date}
                  </span>
                  <span className="flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5" />
                    {post.readTime} lectura
                  </span>
                </div>

                <h3 className="font-bold text-slate-900 text-lg leading-snug mb-3 group-hover:text-blue-600 transition-colors font-heading">
                  {post.title}
                </h3>

                <p className="text-slate-500 text-sm leading-relaxed mb-5 line-clamp-3">
                  {post.excerpt}
                </p>

                <div className="flex items-center gap-2 text-blue-600 text-sm font-semibold group-hover:gap-3 transition-all">
                  <span>Leer artículo</span>
                  <ArrowRight className="w-4 h-4" />
                </div>
              </div>
            </motion.article>
          ))}
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.3 }}
          className="text-center mt-10 md:hidden"
        >
          <button className="flex items-center gap-2 text-blue-600 font-semibold mx-auto">
            Ver todos los artículos <ArrowRight className="w-5 h-5" />
          </button>
        </motion.div>
      </div>
    </section>
  );
}
