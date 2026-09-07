import Reveal from './Reveal'
import LeafSVG from './LeafSVG'
import { infoRows } from '@/lib/data'
import { buildWhatsAppUrl } from '@/lib/utils'

const WA_ICON = (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="white" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
    <path d="M.057 24l1.687-6.163a11.867 11.867 0 01-1.587-5.946C.16 5.335 5.495 0 12.05 0a11.817 11.817 0 018.413 3.488 11.824 11.824 0 013.48 8.414c-.003 6.557-5.338 11.892-11.893 11.892a11.9 11.9 0 01-5.688-1.448L.057 24zm6.597-3.807c1.676.995 3.276 1.591 5.392 1.592 5.448 0 9.886-4.434 9.889-9.885.002-5.462-4.415-9.89-9.881-9.892-5.452 0-9.887 4.434-9.889 9.884a9.86 9.86 0 001.51 5.26l.601.955-1.002 3.648 3.748-.984.632.422zm11.387-5.464c-.074-.124-.272-.198-.57-.347-.297-.149-1.758-.868-2.031-.967-.272-.099-.47-.149-.669.149-.198.297-.768.967-.941 1.165-.173.198-.347.223-.644.074-.297-.149-1.255-.462-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.297-.347.446-.521.151-.172.2-.296.3-.494.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51l-.57-.01c-.198 0-.52.074-.792.372s-1.04 1.016-1.04 2.479 1.065 2.876 1.213 3.074c.149.198 2.095 3.2 5.076 4.487.71.306 1.263.489 1.694.626.712.226 1.36.194 1.872.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413z" />
  </svg>
)

export default function Contact() {
  return (
    <section id="contacto" className="relative overflow-hidden bg-cream-deep section-pad">
      <LeafSVG
        color="#5C5A3F"
        className="absolute bottom-[-120px] left-[-120px] w-[500px] opacity-10
          rotate-45 pointer-events-none"
      />

      <div className="wrap relative z-10">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-[50px] md:gap-[80px] items-center">

          {/* Card */}
          <Reveal>
            <div className="bg-cream-light px-12 py-14 rounded-[6px]
              shadow-[0_30px_60px_-30px_rgba(43,38,32,0.2)]">
              <span className="eyebrow block mb-[18px]">Hacer un pedido</span>
              <h2 className="font-serif text-[clamp(34px,4vw,56px)] font-light mb-[18px]">
                Pidamos por{' '}
                <span className="italic text-wine">WhatsApp</span>.
              </h2>
              <p className="text-ink-soft mb-9 max-w-[420px]">
                Cuéntanos qué jabones te interesan y a qué comuna despachamos.
                Respondemos de lunes a sábado, antes de que se enfríe el café.
              </p>
              <a
                href={buildWhatsAppUrl()}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-[14px] px-8 py-5
                  bg-[#25D366] text-white rounded-pill
                  text-[13px] tracking-[0.16em] uppercase font-medium
                  shadow-[0_6px_20px_rgba(37,211,102,0.3)]
                  transition-all duration-200
                  hover:-translate-y-[2px] hover:shadow-[0_10px_28px_rgba(37,211,102,0.4)]"
              >
                {WA_ICON}
                Escribir por WhatsApp
              </a>
            </div>
          </Reveal>

          {/* Info rows */}
          <div className="pl-0 md:pl-5">
            <Reveal delay={0.12}>
              <h3 className="font-serif italic text-[28px] text-wine mb-9">El taller</h3>
            </Reveal>
            {infoRows.map((row, i) => (
              <Reveal key={row.key} delay={0.12 + i * 0.08}>
                <div
                  className="py-[22px] border-t border-[rgba(43,38,32,0.12)]
                    grid grid-cols-[130px_1fr] gap-5 last:border-b last:border-[rgba(43,38,32,0.12)]"
                >
                  <div className="text-[10px] tracking-[0.24em] uppercase text-ink-soft pt-1">
                    {row.key}
                  </div>
                  <div className="font-serif text-[20px] text-ink">
                    {row.value}
                    {row.subValue && (
                      <small className="block font-sans text-[13px] text-ink-soft mt-1">
                        {row.subValue}
                      </small>
                    )}
                  </div>
                </div>
              </Reveal>
            ))}
          </div>

        </div>
      </div>
    </section>
  )
}
