import { Instagram, Phone, Mail, MapPin, Clock, Heart } from "lucide-react";
import { SITE_CONFIG, NAV_LINKS, SCHEDULE } from "@/lib/constants";

export function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className="bg-slate-950 text-white">
      {/* Main footer */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-10">
          {/* Brand column */}
          <div className="lg:col-span-1">
            <div className="flex items-center gap-2.5 mb-5">
              <div className="rainbow-ring-sm">
                <div className="w-10 h-10 rounded-xl bg-slate-950 flex items-center justify-center">
                  <PawIcon className="w-6 h-6 text-blue-400" />
                </div>
              </div>
              <div>
                <div className="font-bold text-lg tracking-tight font-heading">Huellas</div>
                <div className="text-[10px] text-slate-400 uppercase tracking-widest">
                  Clínica Veterinaria
                </div>
              </div>
            </div>
            <p className="text-slate-400 text-sm leading-relaxed mb-6">
              Tu veterinario de cabecera en Concepción. Cuidamos a tu mascota
              con profesionalismo, amor y dedicación.
            </p>
            <a
              href={SITE_CONFIG.instagram}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 text-white text-sm font-medium hover:opacity-90 transition-opacity"
            >
              <Instagram className="w-4 h-4" />
              @veterinariahuellas
            </a>
          </div>

          {/* Quick links */}
          <div>
            <h3 className="font-semibold text-white mb-5 font-heading">Navegación</h3>
            <ul className="space-y-3">
              {NAV_LINKS.map((link) => (
                <li key={link.href}>
                  <a
                    href={link.href}
                    className="text-slate-400 hover:text-blue-400 text-sm transition-colors"
                  >
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Horarios */}
          <div>
            <h3 className="font-semibold text-white mb-5 font-heading">Horarios</h3>
            <ul className="space-y-3">
              {SCHEDULE.map((item) => (
                <li key={item.day} className="flex items-start gap-2">
                  <Clock className="w-4 h-4 text-blue-500 mt-0.5 shrink-0" />
                  <div>
                    <div className="text-slate-300 text-sm font-medium">{item.day}</div>
                    <div className="text-slate-500 text-xs">{item.hours}</div>
                  </div>
                </li>
              ))}
            </ul>
            <div className="mt-4 inline-flex items-center gap-1.5 bg-blue-950/50 border border-blue-900/50 rounded-lg px-3 py-1.5">
              <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
              <span className="text-blue-400 text-xs font-medium">Abierto ahora</span>
            </div>
          </div>

          {/* Contacto */}
          <div>
            <h3 className="font-semibold text-white mb-5 font-heading">Contacto</h3>
            <ul className="space-y-4">
              <li>
                <a
                  href={SITE_CONFIG.phoneHref}
                  className="flex items-start gap-3 text-slate-400 hover:text-blue-400 transition-colors group"
                >
                  <div className="w-8 h-8 rounded-lg bg-blue-950/50 flex items-center justify-center shrink-0 group-hover:bg-blue-900/50 transition-colors">
                    <Phone className="w-4 h-4 text-blue-500" />
                  </div>
                  <div>
                    <div className="text-xs text-slate-500 mb-0.5">Teléfono</div>
                    <span className="text-sm">{SITE_CONFIG.phone}</span>
                  </div>
                </a>
              </li>
              <li>
                <a
                  href={`mailto:${SITE_CONFIG.email}`}
                  className="flex items-start gap-3 text-slate-400 hover:text-blue-400 transition-colors group"
                >
                  <div className="w-8 h-8 rounded-lg bg-blue-950/50 flex items-center justify-center shrink-0 group-hover:bg-blue-900/50 transition-colors">
                    <Mail className="w-4 h-4 text-blue-500" />
                  </div>
                  <div>
                    <div className="text-xs text-slate-500 mb-0.5">Email</div>
                    <span className="text-sm break-all">{SITE_CONFIG.email}</span>
                  </div>
                </a>
              </li>
              <li>
                <a
                  href={SITE_CONFIG.mapLink}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-start gap-3 text-slate-400 hover:text-blue-400 transition-colors group"
                >
                  <div className="w-8 h-8 rounded-lg bg-blue-950/50 flex items-center justify-center shrink-0 group-hover:bg-blue-900/50 transition-colors">
                    <MapPin className="w-4 h-4 text-blue-500" />
                  </div>
                  <div>
                    <div className="text-xs text-slate-500 mb-0.5">Dirección</div>
                    <span className="text-sm">{SITE_CONFIG.address}</span>
                  </div>
                </a>
              </li>
            </ul>
          </div>
        </div>
      </div>

      {/* Bottom bar */}
      <div className="border-t border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-slate-500 text-sm">
            © {year} Clínica Veterinaria Huellas. Todos los derechos reservados.
          </p>
          <p className="text-slate-600 text-xs flex items-center gap-1">
            Hecho con <Heart className="w-3 h-3 text-blue-500 fill-blue-500" /> en Concepción, Chile
          </p>
        </div>
      </div>
    </footer>
  );
}

function PawIcon({ className }: { className?: string }) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="currentColor"
      className={className}
    >
      <ellipse cx="6.5" cy="9.5" rx="1.8" ry="2.5"/>
      <ellipse cx="10.5" cy="7" rx="1.5" ry="2.2"/>
      <ellipse cx="14.5" cy="7" rx="1.5" ry="2.2"/>
      <ellipse cx="17.5" cy="9.5" rx="1.8" ry="2.5"/>
      <path d="M12 11.5c-2.33 0-4.5 1.5-5.5 3.5-.5 1 0 2.5 1.5 3s4 .5 4 .5 2.5.5 4-.5 2-2 1.5-3c-1-2-3.17-3.5-5.5-3.5z"/>
    </svg>
  );
}
