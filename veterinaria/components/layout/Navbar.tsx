"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Menu, X, Phone } from "lucide-react";
import { Button } from "@/components/ui/button";
import { NAV_LINKS, SITE_CONFIG } from "@/lib/constants";
import { cn } from "@/lib/utils";

export function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => {
    if (mobileOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
    };
  }, [mobileOpen]);

  const handleNavClick = (href: string) => {
    setMobileOpen(false);
    const el = document.querySelector(href);
    if (el) {
      el.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <>
      <motion.header
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, ease: [0.25, 0.46, 0.45, 0.94] }}
        className={cn(
          "fixed top-0 left-0 right-0 z-50 transition-all duration-300",
          scrolled
            ? "bg-white/95 backdrop-blur-md shadow-sm border-b border-slate-100"
            : "bg-transparent"
        )}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-18 py-3">
            {/* Logo */}
            <button
              onClick={() => handleNavClick("#inicio")}
              className="flex items-center gap-2.5 group"
            >
              <div className="rainbow-ring-sm group-hover:scale-105 transition-transform duration-200">
                <div className="w-10 h-10 rounded-xl bg-slate-950 flex items-center justify-center">
                  <PawIcon className="w-6 h-6 text-blue-400" />
                </div>
              </div>
              <div className="flex flex-col leading-none">
                <span
                  className={cn(
                    "font-bold text-lg tracking-tight font-heading transition-colors",
                    scrolled ? "text-slate-900" : "text-white"
                  )}
                >
                  Huellas
                </span>
                <span
                  className={cn(
                    "text-[10px] font-medium tracking-widest uppercase transition-colors",
                    scrolled ? "text-slate-400" : "text-white/60"
                  )}
                >
                  Clínica Veterinaria
                </span>
              </div>
            </button>

            {/* Desktop Nav */}
            <nav className="hidden lg:flex items-center gap-1">
              {NAV_LINKS.map((link) => (
                <button
                  key={link.href}
                  onClick={() => handleNavClick(link.href)}
                  className={cn(
                    "px-4 py-2 rounded-lg text-sm font-medium transition-colors",
                    scrolled
                      ? "text-slate-600 hover:text-blue-600 hover:bg-blue-50"
                      : "text-white/80 hover:text-white hover:bg-white/10"
                  )}
                >
                  {link.label}
                </button>
              ))}
            </nav>

            {/* Right: Phone + CTA */}
            <div className="hidden md:flex items-center gap-3">
              <a
                href={SITE_CONFIG.phoneHref}
                className={cn(
                  "flex items-center gap-2 text-sm font-medium transition-colors",
                  scrolled ? "text-slate-600 hover:text-blue-600" : "text-white/80 hover:text-white"
                )}
              >
                <Phone className="w-4 h-4" />
                {SITE_CONFIG.phone}
              </a>
              <Button
                onClick={() => handleNavClick("#contacto")}
                variant={scrolled ? "gradient" : "white"}
                size="sm"
              >
                Agendar Hora
              </Button>
            </div>

            {/* Mobile hamburger */}
            <button
              onClick={() => setMobileOpen(!mobileOpen)}
              className={cn(
                "lg:hidden p-2 rounded-lg transition-colors",
                scrolled
                  ? "text-slate-700 hover:bg-slate-100"
                  : "text-white hover:bg-white/10"
              )}
            >
              {mobileOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </motion.header>

      {/* Mobile Menu Overlay */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 z-40 bg-black/50 backdrop-blur-sm lg:hidden"
            onClick={() => setMobileOpen(false)}
          />
        )}
      </AnimatePresence>

      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", damping: 30, stiffness: 300 }}
            className="fixed top-0 right-0 bottom-0 z-50 w-80 bg-white shadow-2xl lg:hidden flex flex-col"
          >
            <div className="flex items-center justify-between p-6 border-b border-slate-100">
              <div className="flex items-center gap-2.5">
                <div className="rainbow-ring-sm">
                  <div className="w-9 h-9 rounded-xl bg-white flex items-center justify-center">
                    <PawIcon className="w-5 h-5 text-blue-600" />
                  </div>
                </div>
                <span className="font-bold text-slate-900 font-heading">Huellas</span>
              </div>
              <button
                onClick={() => setMobileOpen(false)}
                className="p-2 rounded-lg text-slate-500 hover:bg-slate-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <nav className="flex-1 overflow-y-auto p-6 space-y-1">
              {NAV_LINKS.map((link, i) => (
                <motion.button
                  key={link.href}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.05 }}
                  onClick={() => handleNavClick(link.href)}
                  className="w-full text-left px-4 py-3 rounded-xl text-slate-700 hover:text-blue-600 hover:bg-blue-50 font-medium transition-colors"
                >
                  {link.label}
                </motion.button>
              ))}
            </nav>

            <div className="p-6 border-t border-slate-100 space-y-3">
              <a
                href={SITE_CONFIG.phoneHref}
                className="flex items-center gap-2 text-slate-600 hover:text-blue-600 font-medium"
              >
                <Phone className="w-4 h-4" />
                {SITE_CONFIG.phone}
              </a>
              <Button
                onClick={() => handleNavClick("#contacto")}
                variant="gradient"
                className="w-full"
              >
                Agendar Hora
              </Button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
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
      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z" opacity="0"/>
      <ellipse cx="6.5" cy="9.5" rx="1.8" ry="2.5"/>
      <ellipse cx="10.5" cy="7" rx="1.5" ry="2.2"/>
      <ellipse cx="14.5" cy="7" rx="1.5" ry="2.2"/>
      <ellipse cx="17.5" cy="9.5" rx="1.8" ry="2.5"/>
      <path d="M12 11.5c-2.33 0-4.5 1.5-5.5 3.5-.5 1 0 2.5 1.5 3s4 .5 4 .5 2.5.5 4-.5 2-2 1.5-3c-1-2-3.17-3.5-5.5-3.5z"/>
    </svg>
  );
}
