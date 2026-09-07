import Reveal from './Reveal'

export default function QuoteBand() {
  return (
    <section className="relative overflow-hidden bg-wine py-[140px] text-center">
      {/* Decorative quote marks */}
      <span
        className="absolute top-[30px] left-10 font-serif text-[320px] leading-none
          opacity-[0.08] text-cream-light select-none pointer-events-none"
        aria-hidden="true"
      >
        &ldquo;
      </span>
      <span
        className="absolute bottom-[-80px] right-10 font-serif text-[320px] leading-none
          opacity-[0.08] text-cream-light select-none pointer-events-none"
        aria-hidden="true"
      >
        &rdquo;
      </span>

      <div className="wrap relative z-10">
        <Reveal>
          <blockquote
            className="font-serif italic font-light text-cream-light relative z-10
              text-[clamp(28px,3.6vw,52px)] leading-[1.25] max-w-[900px] mx-auto"
          >
            &ldquo;Llevo tres meses usando el de miel &amp; avena y mi dermatitis simplemente desapareció.
            No es magia, es un jabón hecho como debe ser.&rdquo;
          </blockquote>
        </Reveal>
        <Reveal delay={0.12}>
          <p className="mt-9 text-[11px] tracking-[0.3em] uppercase text-cream/70">
            — Paulina M., clienta desde 2024
          </p>
        </Reveal>
      </div>
    </section>
  )
}
