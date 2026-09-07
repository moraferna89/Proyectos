import Reveal from './Reveal'
import SectionHeader from './SectionHeader'
import LeafSVG from './LeafSVG'
import { benefits } from '@/lib/data'

export default function Benefits() {
  return (
    <section id="beneficios" className="relative overflow-hidden bg-olive section-pad">
      <LeafSVG
        color="#F4EDE0"
        className="absolute top-[10%] right-[-10%] w-[600px] opacity-[0.08] pointer-events-none"
      />

      <div className="wrap relative z-10">
        <SectionHeader
          eyebrow="¿Por qué artesanal?"
          title={
            <>
              Razones que tu piel{' '}
              <span className="italic text-earth-light">va a agradecer</span>.
            </>
          }
          light
        />

        <div
          className="grid grid-cols-1 md:grid-cols-3
            border border-cream/[0.16] bg-cream/[0.16]
            divide-y md:divide-y-0 divide-cream/[0.16]"
          style={{ gap: '2px' }}
        >
          {benefits.map((benefit, i) => (
            <Reveal
              key={benefit.numeral}
              delay={(i % 3) * 0.12}
            >
              <div
                className="bg-olive px-11 py-14 transition-colors duration-300
                  hover:bg-[#525038] h-full"
              >
                <div className="font-serif italic text-[18px] text-earth-light mb-7">
                  {benefit.numeral}
                </div>
                <h3 className="font-serif text-subheading font-light text-cream-light mb-[14px]">
                  {benefit.title}{' '}
                  <span className="italic text-earth-light">{benefit.titleItalic}</span>
                </h3>
                <p className="text-cream/[0.72] text-[14px] leading-[1.65]">
                  {benefit.description}
                </p>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  )
}
