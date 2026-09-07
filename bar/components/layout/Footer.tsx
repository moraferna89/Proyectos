import { Beer, Instagram, MapPin, Phone, Mail, Clock } from "lucide-react";
import { SITE_CONFIG, NAV_LINKS } from "@/lib/constants";

export function Footer() {
  return (
    <footer className="relative bg-[#080808] border-t border-white/[0.06]">
      <div className="absolute inset-x-0 top-0 h-px glow-line" />

      <div className="container-wide section-padding">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12">
          {/* Brand */}
          <div className="lg:col-span-2 space-y-5">
            <div className="flex items-center gap-2.5">
              <div className="w-10 h-10 rounded-xl bg-amber-500/15 border border-amber-500/30 flex items-center justify-center">
                <Beer className="w-5 h-5 text-amber-400" />
              </div>
              <span className="font-bold text-xl">
                <span className="text-white">Fuente</span>
                <span className="text-amber-400"> Divka</span>
              </span>
            </div>
            <p className="text-white/50 text-sm leading-relaxed max-w-sm">
              Bar Cervecero con 12 años de historia en el corazón de Apoquindo.
              18 variedades de cerveza artesanal, gastronomía gourmet y el mejor
              ambiente de Santiago.
            </p>
            <div className="flex items-center gap-3">
              <a
                href={SITE_CONFIG.instagram}
                target="_blank"
                rel="noopener noreferrer"
                className="w-10 h-10 rounded-xl bg-white/[0.04] border border-white/[0.08] flex items-center justify-center text-white/50 hover:text-white hover:bg-white/[0.08] hover:border-white/20 transition-all"
                aria-label="Instagram"
              >
                <Instagram className="w-4 h-4" />
              </a>
              <a
                href={SITE_CONFIG.tiktok}
                target="_blank"
                rel="noopener noreferrer"
                className="w-10 h-10 rounded-xl bg-white/[0.04] border border-white/[0.08] flex items-center justify-center text-white/50 hover:text-white hover:bg-white/[0.08] hover:border-white/20 transition-all"
                aria-label="TikTok"
              >
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M19.59 6.69a4.83 4.83 0 01-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 01-2.88 2.5 2.89 2.89 0 01-2.89-2.89 2.89 2.89 0 012.89-2.89c.28 0 .54.04.79.1V9.01a6.34 6.34 0 00-.79-.05 6.34 6.34 0 00-6.34 6.34 6.34 6.34 0 006.34 6.34 6.34 6.34 0 006.33-6.34V8.67a8.18 8.18 0 004.78 1.52V6.74a4.85 4.85 0 01-1.01-.05z" />
                </svg>
              </a>
            </div>
          </div>

          {/* Nav Links */}
          <div className="space-y-4">
            <h4 className="text-sm font-semibold text-white/80 uppercase tracking-wider">Menú</h4>
            <ul className="space-y-2.5">
              {NAV_LINKS.map((link) => (
                <li key={link.href}>
                  <a
                    href={link.href}
                    className="text-sm text-white/50 hover:text-amber-400 transition-colors"
                  >
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Contact Info */}
          <div className="space-y-4">
            <h4 className="text-sm font-semibold text-white/80 uppercase tracking-wider">
              Contacto
            </h4>
            <ul className="space-y-3">
              <li className="flex items-start gap-3 text-sm text-white/50">
                <MapPin className="w-4 h-4 text-amber-400/70 mt-0.5 flex-shrink-0" />
                <span>{SITE_CONFIG.address}</span>
              </li>
              <li className="flex items-center gap-3 text-sm text-white/50">
                <Phone className="w-4 h-4 text-amber-400/70 flex-shrink-0" />
                <a href={`tel:${SITE_CONFIG.phone}`} className="hover:text-white transition-colors">
                  {SITE_CONFIG.phone}
                </a>
              </li>
              <li className="flex items-center gap-3 text-sm text-white/50">
                <Mail className="w-4 h-4 text-amber-400/70 flex-shrink-0" />
                <a href={`mailto:${SITE_CONFIG.email}`} className="hover:text-white transition-colors">
                  {SITE_CONFIG.email}
                </a>
              </li>
              <li className="flex items-start gap-3 text-sm text-white/50">
                <Clock className="w-4 h-4 text-amber-400/70 mt-0.5 flex-shrink-0" />
                <div className="space-y-1">
                  <p>{SITE_CONFIG.hours.weekdays}</p>
                  <p>{SITE_CONFIG.hours.friday}</p>
                  <p>{SITE_CONFIG.hours.weekend}</p>
                </div>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="mt-16 pt-8 border-t border-white/[0.06] flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-xs text-white/30">
            © {new Date().getFullYear()} Fuente Divka. Todos los derechos reservados.
          </p>
          <p className="text-xs text-white/20">
            Beber con responsabilidad. Prohibida la venta de alcohol a menores.
          </p>
        </div>
      </div>
    </footer>
  );
}
