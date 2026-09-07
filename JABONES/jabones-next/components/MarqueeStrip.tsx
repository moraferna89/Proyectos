import { cn } from '@/lib/utils'

interface MarqueeStripProps {
  items: string[]
  reverse?: boolean
  bgColor?: string
  textColor?: string
}

export default function MarqueeStrip({
  items,
  reverse = false,
  bgColor = 'bg-ink',
  textColor = 'text-cream',
}: MarqueeStripProps) {
  const doubled = [...items, ...items]

  return (
    <div
      className={cn('overflow-hidden whitespace-nowrap py-[22px]', bgColor)}
      aria-hidden="true"
    >
      <div
        className={cn(
          'inline-flex gap-[60px] font-serif italic text-[22px] tracking-[0.04em]',
          textColor,
          reverse ? 'animate-marquee-reverse' : 'animate-marquee'
        )}
      >
        {doubled.map((item, i) => (
          <span key={i} className="inline-flex items-center gap-[60px]">
            {item}
            <span className="text-wine not-italic text-[12px]">✦</span>
          </span>
        ))}
      </div>
    </div>
  )
}
