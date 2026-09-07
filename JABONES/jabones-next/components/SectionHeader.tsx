import Reveal from './Reveal'
import { cn } from '@/lib/utils'

interface SectionHeaderProps {
  eyebrow: string
  title: React.ReactNode
  subtitle?: string
  light?: boolean
  className?: string
}

export default function SectionHeader({
  eyebrow,
  title,
  subtitle,
  light = false,
  className,
}: SectionHeaderProps) {
  return (
    <Reveal className={cn('text-center mx-auto mb-[70px] max-w-[720px]', className)}>
      <span className={cn('eyebrow inline-block mb-[18px]', light && 'text-earth-light')}>
        {eyebrow}
      </span>
      <h2
        className={cn(
          'text-heading font-serif font-light mb-[18px]',
          light && 'text-cream-light'
        )}
      >
        {title}
      </h2>
      {subtitle && (
        <p
          className={cn(
            'font-serif italic text-[20px] font-light',
            light ? 'text-cream/70' : 'text-ink-soft'
          )}
        >
          {subtitle}
        </p>
      )}
    </Reveal>
  )
}
