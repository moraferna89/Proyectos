'use client'

import { useState, useEffect } from 'react'
import { usePathname } from 'next/navigation'
import Link from 'next/link'
import { motion } from 'framer-motion'

const anchorLinks = [
  { href: '#catalogo',   label: 'Catálogo' },
  { href: '#historia',   label: 'Historia' },
  { href: '#proceso',    label: 'Proceso' },
  { href: '#beneficios', label: 'Beneficios' },
  { href: '#contacto',   label: 'Contacto' },
]

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false)
  const pathname = usePathname()
  const isHome = pathname === '/'

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 60)
    window.addEventListener('scroll', onScroll, { passive: true })
    onScroll()
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  const linkClass =
    'relative py-[6px] font-medium text-ink transition-colors duration-200 hover:text-wine ' +
    'after:absolute after:left-0 after:bottom-0 after:h-px after:w-0 after:bg-wine ' +
    'after:transition-all after:duration-300 hover:after:w-full'

  const activeClass = 'text-wine after:!w-full'

  return (
    <motion.nav
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: 'easeOut' }}
      className={`fixed top-0 left-0 right-0 z-50 flex items-center justify-between transition-all duration-300
        ${scrolled
          ? 'bg-cream/92 backdrop-blur-md shadow-[0_1px_0_rgba(43,38,32,0.12)] py-[14px] px-10'
          : 'bg-transparent backdrop-blur-none py-[22px] px-10'
        }`}
    >
      {/* Logo */}
      <Link
        href="/"
        className="font-serif text-[22px] font-medium tracking-[0.18em] flex items-center gap-[10px] text-ink"
      >
        JABONES <span className="text-wine text-[14px]">♥</span> ARTESANALES
      </Link>

      {/* Links */}
      <div className="hidden md:flex gap-[38px] text-[13px] tracking-[0.12em] uppercase">
        {/* Anchor links — prefix with / when not on home */}
        {anchorLinks.map(({ href, label }) => (
          <a
            key={href}
            href={isHome ? href : `/${href}`}
            className={linkClass}
          >
            {label}
          </a>
        ))}

        {/* Route link */}
        <Link
          href="/productos"
          className={`${linkClass} ${!isHome ? activeClass : ''}`}
        >
          Productos
        </Link>
      </div>

      {/* CTA */}
      <a
        href={isHome ? '#contacto' : '/#contacto'}
        className="inline-flex items-center gap-2 px-[22px] py-[11px] border border-ink rounded-pill
          text-[12px] tracking-[0.14em] uppercase transition-all duration-200
          hover:bg-ink hover:text-cream"
      >
        Pedir ahora
      </a>
    </motion.nav>
  )
}
