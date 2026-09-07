'use client'

import { useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import Image from 'next/image'
import { ArrowRight } from 'lucide-react'
import type { ProductCategory } from '@/lib/types'
import { products, categories } from '@/lib/data'
import { buildWhatsAppUrl, cn } from '@/lib/utils'

export default function ProductsFilter() {
  const [active, setActive] = useState<ProductCategory>('todos')

  const filtered =
    active === 'todos'
      ? products
      : products.filter((p) => p.category === active)

  const activeCategory = categories.find((c) => c.id === active)

  return (
    <div className="bg-cream">
      {/* ── Filter bar ── */}
      <div className="sticky top-[60px] z-40 bg-cream/95 backdrop-blur-sm border-b border-[rgba(43,38,32,0.1)]">
        <div className="wrap py-6">
          <div className="flex flex-col sm:flex-row sm:items-center gap-4 sm:gap-0 justify-between">
            {/* Pills */}
            <div className="flex items-center gap-2 flex-wrap">
              {categories.map((cat) => (
                <button
                  key={cat.id}
                  onClick={() => setActive(cat.id)}
                  className={cn(
                    'relative px-5 py-[9px] rounded-pill text-[11px] tracking-[0.18em] uppercase font-medium transition-all duration-250',
                    active === cat.id
                      ? 'bg-wine text-cream shadow-[0_4px_12px_rgba(107,45,45,0.22)]'
                      : 'border border-[rgba(43,38,32,0.2)] text-ink-soft hover:border-wine hover:text-wine bg-transparent'
                  )}
                >
                  {cat.label}
                  {active === cat.id && (
                    <motion.span
                      layoutId="filter-bg"
                      className="absolute inset-0 rounded-pill bg-wine -z-10"
                      transition={{ type: 'spring', stiffness: 380, damping: 30 }}
                    />
                  )}
                </button>
              ))}
            </div>

            {/* Count */}
            <motion.p
              key={active}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-[12px] tracking-[0.2em] uppercase text-ink-soft whitespace-nowrap"
            >
              {filtered.length}{' '}
              {filtered.length === 1 ? 'jabón' : 'jabones'}
              {active !== 'todos' && (
                <span className="ml-1 text-wine">· {activeCategory?.description}</span>
              )}
            </motion.p>
          </div>
        </div>
      </div>

      {/* ── Grid ── */}
      <section className="section-pad">
        <div className="wrap">
          <AnimatePresence mode="popLayout">
            {filtered.length > 0 ? (
              <motion.div
                key={active}
                layout
                className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-x-10 gap-y-14"
              >
                {filtered.map((product, i) => {
                  const waUrl = buildWhatsAppUrl(
                    product.nameItalicFirst
                      ? `${product.nameItalic} ${product.name}`
                      : `${product.name} ${product.nameItalic ?? ''}`
                  )

                  return (
                    <motion.article
                      key={product.id}
                      layout
                      initial={{ opacity: 0, y: 24, scale: 0.97 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      exit={{ opacity: 0, y: -16, scale: 0.96 }}
                      transition={{
                        duration: 0.5,
                        delay: i * 0.06,
                        ease: [0.2, 0.7, 0.2, 1],
                      }}
                      className="cursor-pointer group"
                    >
                      {/* Image */}
                      <div className="relative aspect-[3/4] overflow-hidden bg-cream-deep rounded-[2px] mb-[22px]">
                        <Image
                          src={product.image}
                          alt={product.imageAlt}
                          fill
                          className="object-cover transition-transform duration-[900ms] ease-[cubic-bezier(0.2,0.7,0.2,1)] group-hover:scale-[1.06]"
                          sizes="(max-width: 640px) 100vw, (max-width: 980px) 50vw, 33vw"
                        />

                        {/* Category badge */}
                        <span className="absolute top-[18px] right-[18px] bg-cream/90 text-olive-soft
                          text-[9px] tracking-[0.2em] uppercase px-3 py-[5px] rounded-pill font-medium
                          backdrop-blur-sm z-10">
                          {categories.find((c) => c.id === product.category)?.label}
                        </span>

                        {product.tag && (
                          <span className="absolute top-[18px] left-[18px] bg-cream-light text-wine
                            text-[10px] tracking-[0.22em] uppercase px-3 py-[6px] rounded-pill font-medium z-10">
                            {product.tag}
                          </span>
                        )}

                        {/* WhatsApp overlay */}
                        <a
                          href={waUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="absolute bottom-[18px] left-[18px] right-[18px]
                            bg-ink text-cream text-center py-[13px] px-5 rounded-pill
                            text-[11px] tracking-[0.2em] uppercase z-10
                            flex justify-center items-center gap-2
                            opacity-0 translate-y-2 transition-all duration-300
                            group-hover:opacity-100 group-hover:translate-y-0"
                          onClick={(e) => e.stopPropagation()}
                        >
                          Pedir por WhatsApp →
                        </a>
                      </div>

                      {/* Meta */}
                      <div className="flex items-baseline justify-between gap-[18px]">
                        <h2 className="font-serif text-[26px] font-normal leading-[1.15]">
                          {product.nameItalicFirst ? (
                            <>
                              <span className="italic text-wine">{product.nameItalic}</span>{' '}
                              {product.name}
                            </>
                          ) : (
                            <>
                              {product.name}{' '}
                              {product.nameItalic && (
                                <span className="italic text-wine">{product.nameItalic}</span>
                              )}
                            </>
                          )}
                        </h2>
                        <span className="font-serif text-[22px] text-ink whitespace-nowrap">
                          {product.price}
                        </span>
                      </div>
                      <p className="mt-2 text-[13px] text-ink-soft leading-[1.5]">
                        {product.description}
                      </p>
                      <div className="mt-[14px] flex gap-2 flex-wrap">
                        {product.notes.map((note) => (
                          <span
                            key={note}
                            className="text-[10px] tracking-[0.16em] uppercase px-[10px] py-[5px]
                              border border-[rgba(43,38,32,0.12)] rounded-pill text-ink-soft"
                          >
                            {note}
                          </span>
                        ))}
                      </div>
                    </motion.article>
                  )
                })}
              </motion.div>
            ) : (
              <motion.div
                key="empty"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="text-center py-32"
              >
                <p className="font-serif italic text-[28px] text-ink-soft">
                  Sin jabones en esta categoría.
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </section>

      {/* ── CTA band ── */}
      <section className="bg-ink py-[100px] text-center relative overflow-hidden">
        <div className="absolute inset-0 pointer-events-none opacity-[0.04]"
          style={{ backgroundImage: 'radial-gradient(circle at 30% 50%, #C9B391 0%, transparent 60%), radial-gradient(circle at 70% 50%, #6B2D2D 0%, transparent 60%)' }}
        />
        <div className="wrap relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 28 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.9, ease: [0.2, 0.7, 0.2, 1] }}
          >
            <span className="eyebrow text-earth-light block mb-5">¿Necesitas ayuda?</span>
            <h2 className="font-serif text-[clamp(36px,5vw,64px)] font-light text-cream-light leading-[1.05] mb-5">
              Te ayudamos a elegir{' '}
              <span className="italic text-earth-light">el tuyo</span>.
            </h2>
            <p className="font-serif italic text-cream/60 text-[18px] mb-10 max-w-[480px] mx-auto">
              Cuéntanos tu tipo de piel y te recomendamos el jabón perfecto para ti.
            </p>
            <a
              href={buildWhatsAppUrl()}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-3 px-9 py-5 bg-wine text-cream
                rounded-pill text-[13px] tracking-[0.18em] uppercase font-medium
                shadow-[0_4px_14px_rgba(107,45,45,0.35)]
                transition-all duration-200 group
                hover:-translate-y-[2px] hover:bg-[#5a2424] hover:shadow-[0_8px_24px_rgba(107,45,45,0.45)]"
            >
              Escribir por WhatsApp
              <ArrowRight
                size={16}
                className="transition-transform duration-300 group-hover:translate-x-1"
              />
            </a>
          </motion.div>
        </div>
      </section>
    </div>
  )
}
