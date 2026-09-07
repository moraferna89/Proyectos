const footerLinks = {
  Tienda: [
    { href: '#catalogo', label: 'Catálogo' },
    { href: '#contacto', label: 'Cómo pedir' },
    { href: '#contacto', label: 'Despachos' },
  ],
  Marca: [
    { href: '#historia', label: 'Historia' },
    { href: '#proceso', label: 'Proceso' },
    { href: '#beneficios', label: 'Beneficios' },
  ],
  Redes: [
    { href: '#', label: 'Instagram' },
    { href: '#', label: 'TikTok' },
    { href: '#', label: 'Pinterest' },
  ],
}

export default function Footer() {
  return (
    <footer className="bg-ink text-cream pt-20 pb-9">
      <div className="wrap">
        <div className="grid grid-cols-2 sm:grid-cols-[1.6fr_1fr_1fr_1fr] gap-10 md:gap-[60px] mb-[60px]">
          <div className="col-span-2 sm:col-span-1">
            <h3 className="font-serif text-[32px] text-cream-light mb-[14px] tracking-[0.08em]">
              JABONES <span className="text-wine text-[16px]">♥</span> ARTESANALES
            </h3>
            <p className="text-cream/60 font-serif italic text-[18px] max-w-[320px]">
              Natural · Hecho a mano · Con amor. Desde un taller pequeño en el sur de Chile.
            </p>
          </div>

          {Object.entries(footerLinks).map(([title, links]) => (
            <div key={title}>
              <h4 className="text-[11px] tracking-[0.24em] uppercase text-earth-light mb-[22px] font-medium">
                {title}
              </h4>
              <nav>
                {links.map(({ href, label }) => (
                  <a
                    key={label}
                    href={href}
                    className="block py-[7px] text-[14px] text-cream/75
                      transition-colors duration-200 hover:text-cream-light"
                  >
                    {label}
                  </a>
                ))}
              </nav>
            </div>
          ))}
        </div>

        <div className="border-t border-cream/[0.12] pt-[30px] flex flex-col sm:flex-row
          justify-between items-center gap-3 text-[12px] text-cream/50 tracking-[0.1em]">
          <span>© 2026 Jabones Artesanales · Chillán, Chile</span>
          <span>Hecho con cariño · 100% Natural</span>
        </div>
      </div>
    </footer>
  )
}
