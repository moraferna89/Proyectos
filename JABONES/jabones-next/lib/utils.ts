import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'
import { WHATSAPP_PHONE } from './data'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function buildWhatsAppUrl(product?: string): string {
  const msg = product
    ? `¡Hola! Me interesa el jabón de *${product}*. ¿Tienen disponibilidad?`
    : '¡Hola! Quiero hacer un pedido de jabones artesanales 🌿'
  return `https://wa.me/${WHATSAPP_PHONE}?text=${encodeURIComponent(msg)}`
}
