'use client'

import { motion, type Variants } from 'framer-motion'
import { type ReactNode } from 'react'

interface RevealProps {
  children: ReactNode
  delay?: number
  className?: string
  y?: number
}

const variants: Variants = {
  hidden: { opacity: 0, y: 36 },
  visible: (delay: number) => ({
    opacity: 1,
    y: 0,
    transition: {
      duration: 1,
      delay,
      ease: [0.2, 0.7, 0.2, 1],
    },
  }),
}

export default function Reveal({ children, delay = 0, className, y = 36 }: RevealProps) {
  return (
    <motion.div
      className={className}
      initial={{ opacity: 0, y }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-60px' }}
      transition={{ duration: 1, delay, ease: [0.2, 0.7, 0.2, 1] }}
    >
      {children}
    </motion.div>
  )
}
