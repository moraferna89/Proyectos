import { cn } from '@/lib/utils'

interface LeafSVGProps {
  color?: string
  className?: string
}

export default function LeafSVG({ color = '#2B2620', className }: LeafSVGProps) {
  return (
    <svg
      className={cn('pointer-events-none', className)}
      viewBox="0 0 200 400"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
    >
      <path
        d="M100 20 C 60 60, 50 120, 70 180 C 90 240, 110 300, 100 380"
        stroke={color}
        strokeWidth="1.5"
        fill="none"
      />
      <path d="M100 60 C 70 65, 50 78, 38 92 C 56 96, 78 90, 100 78 Z" fill={color} />
      <path d="M100 95 C 130 100, 150 113, 162 128 C 144 130, 122 124, 100 112 Z" fill={color} />
      <path d="M100 140 C 70 145, 50 158, 38 172 C 56 176, 78 170, 100 158 Z" fill={color} />
      <path d="M100 180 C 130 185, 150 198, 162 213 C 144 215, 122 209, 100 197 Z" fill={color} />
      <path d="M100 225 C 70 230, 50 243, 38 257 C 56 261, 78 255, 100 243 Z" fill={color} />
      <path d="M100 268 C 130 273, 150 286, 162 301 C 144 303, 122 297, 100 285 Z" fill={color} />
      <path d="M100 310 C 70 315, 50 328, 38 342 C 56 346, 78 340, 100 328 Z" fill={color} />
    </svg>
  )
}
