import Image from 'next/image'
import Reveal from './Reveal'
import SectionHeader from './SectionHeader'
import { processSteps } from '@/lib/data'

export default function Process() {
  return (
    <section id="proceso" className="relative overflow-hidden bg-cream section-pad">
      <div className="wrap">
        <SectionHeader
          eyebrow="El proceso"
          title={
            <>
              Cuatro pasos,{' '}
              <span className="italic text-wine">cuarenta días</span>.
            </>
          }
          subtitle="Desde que pesamos el aceite hasta que la barra llega a tus manos."
        />

        <div className="flex flex-col gap-[120px]">
          {processSteps.map((step, i) => (
            <div
              key={step.number}
              className={`grid grid-cols-1 md:grid-cols-2 gap-10 md:gap-[90px] items-center
                ${step.reversed ? 'md:[direction:rtl]' : ''}`}
            >
              <Reveal
                delay={0}
                className="md:[direction:ltr]"
              >
                <div className="font-serif italic text-[72px] leading-none text-earth-light mb-6">
                  {step.number}
                </div>
                <h3 className="font-serif text-[clamp(32px,3vw,48px)] font-light leading-[1.1] mb-5">
                  {step.title}{' '}
                  <span className="italic text-wine">{step.titleItalic}</span>.
                </h3>
                <p className="text-ink-soft max-w-[460px] leading-[1.7]">{step.description}</p>
              </Reveal>

              <Reveal
                delay={0.12}
                className="md:[direction:ltr]"
              >
                <div className="aspect-[4/5] overflow-hidden rounded-[4px]
                  shadow-[0_30px_60px_-30px_rgba(43,38,32,0.35)]">
                  <Image
                    src={step.image}
                    alt={step.imageAlt}
                    width={900}
                    height={1125}
                    className="w-full h-full object-cover"
                    sizes="(max-width: 768px) 100vw, 50vw"
                  />
                </div>
              </Reveal>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
