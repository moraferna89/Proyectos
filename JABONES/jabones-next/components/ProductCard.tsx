'use client'

import Image from 'next/image'
import { motion } from 'framer-motion'
import type { Product } from '@/lib/types'
import { buildWhatsAppUrl } from '@/lib/utils'

interface ProductCardProps {
  product: Product
  delay?: number
}

export default function ProductCard({ product, delay = 0 }: ProductCardProps) {
  const waUrl = buildWhatsAppUrl(
    product.nameItalicFirst
      ? `${product.nameItalic} ${product.name}`
      : `${product.name} ${product.nameItalic ?? ''}`
  )

  return (
    <motion.article
      initial={{ opacity: 0, y: 36 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-60px' }}
      transition={{ duration: 1, delay, ease: [0.2, 0.7, 0.2, 1] }}
      className="cursor-pointer group"
    >
      {/* Image */}
      <div className="relative aspect-[3/4] overflow-hidden bg-cream-deep rounded-[2px] mb-[22px]">
        <Image
          src={product.image}
          alt={product.imageAlt}
          fill
          className="object-cover transition-transform duration-[900ms] cubic-bezier(0.2,0.7,0.2,1) group-hover:scale-[1.06]"
          sizes="(max-width: 640px) 100vw, (max-width: 980px) 50vw, 33vw"
        />

        {product.tag && (
          <span className="absolute top-[18px] left-[18px] bg-cream-light text-wine
            text-[10px] tracking-[0.22em] uppercase px-3 py-[6px] rounded-pill font-medium z-10">
            {product.tag}
          </span>
        )}

        <a
          href={waUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="absolute bottom-[18px] left-[18px] right-[18px]
            bg-ink text-cream text-center py-[13px] px-5 rounded-pill
            text-[11px] tracking-[0.2em] uppercase
            flex justify-center items-center gap-2 z-10
            opacity-0 translate-y-2 transition-all duration-300
            group-hover:opacity-100 group-hover:translate-y-0"
          onClick={(e) => e.stopPropagation()}
        >
          Pedir por WhatsApp →
        </a>
      </div>

      {/* Meta */}
      <div className="flex items-baseline justify-between gap-[18px]">
        <h3 className="font-serif text-[26px] font-normal leading-[1.15]">
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
        </h3>
        <span className="font-serif text-[22px] text-ink whitespace-nowrap">{product.price}</span>
      </div>

      <p className="mt-2 text-[13px] text-ink-soft leading-[1.5]">{product.description}</p>

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
}
