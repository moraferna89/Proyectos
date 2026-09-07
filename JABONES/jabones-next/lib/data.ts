import type { Product, ProcessStep, Benefit, InfoRow, Category } from './types'

export const WHATSAPP_PHONE = '56912345678'

export const categories: Category[] = [
  { id: 'todos',       label: 'Todos',       description: 'Toda la colección' },
  { id: 'hidratante',  label: 'Hidratante',  description: 'Nutre e hidrata la piel' },
  { id: 'relajante',   label: 'Relajante',   description: 'Para desconectarse' },
  { id: 'purificante', label: 'Purificante', description: 'Limpieza profunda' },
  { id: 'exfoliante',  label: 'Exfoliante',  description: 'Renueva la piel' },
  { id: 'regenerador', label: 'Regenerador', description: 'Repara y rejuvenece' },
]

export const products: Product[] = [
  {
    id: 'miel-avena',
    name: 'Miel',
    nameItalic: '& Avena',
    price: '$4.900',
    description: 'Calmante y nutritivo. Para pieles sensibles que buscan un abrazo suave.',
    image: 'https://images.unsplash.com/photo-1600857544200-b2f666a9a2ec?w=700&q=80',
    imageAlt: 'Jabón artesanal de miel y avena sobre tabla de madera',
    tag: 'Bestseller',
    notes: ['Miel', 'Avena', 'Aceite oliva'],
    category: 'hidratante',
  },
  {
    id: 'lavanda',
    name: 'Lavanda',
    nameItalic: 'Relajante',
    nameItalicFirst: true,
    price: '$5.200',
    description: 'Aroma floral y herbal. Para terminar el día como se merece.',
    image: 'https://images.unsplash.com/photo-1599305445671-ac291c95aaa9?w=700&q=80',
    imageAlt: 'Jabón artesanal de lavanda',
    notes: ['Lavanda', 'Sales', 'Coco'],
    category: 'relajante',
  },
  {
    id: 'carbon-activado',
    name: 'Carbón',
    nameItalic: 'Activado',
    price: '$5.500',
    description: 'Purificante profundo. Ideal para pieles mixtas y rostros con brillo.',
    image: 'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=700&q=80',
    imageAlt: 'Jabón artesanal de carbón activado',
    tag: 'Nuevo',
    notes: ['Carbón', 'Té verde', 'Menta'],
    category: 'purificante',
  },
  {
    id: 'cafe-exfoliante',
    name: 'Café',
    nameItalic: 'Exfoliante',
    price: '$5.200',
    description: 'Granos molidos para una exfoliación suave que despierta los sentidos.',
    image: 'https://images.unsplash.com/photo-1612817288484-6f916006741a?w=700&q=80',
    imageAlt: 'Jabón artesanal de café exfoliante',
    notes: ['Café', 'Cacao', 'Vainilla'],
    category: 'exfoliante',
  },
  {
    id: 'rosa-mosqueta',
    name: 'Rosa',
    nameItalic: 'Mosqueta',
    price: '$6.200',
    description: 'Regenerador para piel madura. Vitamina E y aceite prensado en frío.',
    image: 'https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?w=700&q=80',
    imageAlt: 'Jabón artesanal de rosa mosqueta',
    notes: ['Mosqueta', 'Karité', 'Vit. E'],
    category: 'regenerador',
  },
  {
    id: 'calendula',
    name: 'Caléndula',
    nameItalic: 'Suave',
    nameItalicFirst: true,
    price: '$5.800',
    description: 'Para piel reactiva y bebés. Pétalos macerados durante 40 días.',
    image: 'https://images.unsplash.com/photo-1606471191009-63994c53433b?w=700&q=80',
    imageAlt: 'Jabón artesanal de caléndula',
    tag: 'Edición ltda.',
    notes: ['Caléndula', 'Almendras', 'Sin esencia'],
    category: 'hidratante',
  },
]

export const processSteps: ProcessStep[] = [
  {
    number: '01',
    title: 'Elegimos los',
    titleItalic: 'ingredientes',
    description:
      'Aceites de oliva y coco, mantecas de karité y cacao. Botánicos secados al sol y esencias puras. Nada que no podamos pronunciar.',
    image: 'https://images.unsplash.com/photo-1602928298849-325cec8771c0?w=900&q=80',
    imageAlt: 'Ingredientes naturales para jabón artesanal',
  },
  {
    number: '02',
    title: 'Mezclamos en',
    titleItalic: 'frío',
    description:
      'Saponificación en frío, sin alterar las propiedades de los aceites. Cada tanda son entre 12 y 20 barras, contadas con los dedos.',
    image: 'https://images.unsplash.com/photo-1556228852-80b6e5eeff06?w=900&q=80',
    imageAlt: 'Proceso de mezcla del jabón en frío',
    reversed: true,
  },
  {
    number: '03',
    title: 'Cortamos y',
    titleItalic: 'curamos',
    description:
      'La pasta reposa en moldes de madera por 48 horas. Luego cortamos a mano y dejamos curar al menos 4 semanas para que cada barra dure y espume como debe.',
    image: 'https://images.unsplash.com/photo-1601612628452-9e99ced43524?w=900&q=80',
    imageAlt: 'Jabones artesanales en proceso de curado',
  },
  {
    number: '04',
    title: 'Envolvemos con',
    titleItalic: 'cariño',
    description:
      'Papel kraft, sello a mano y un mensaje en cada caja. Empaque 100% biodegradable que puedes compostar sin culpa.',
    image: 'https://images.unsplash.com/photo-1600857544200-b2f666a9a2ec?w=900&q=80&sat=-20',
    imageAlt: 'Empaque biodegradable de jabón artesanal',
    reversed: true,
  },
]

export const benefits: Benefit[] = [
  {
    numeral: 'i.',
    title: 'Glicerina',
    titleItalic: 'natural',
    description:
      'El jabón industrial extrae la glicerina para venderla aparte. Nosotros la dejamos donde corresponde: en la barra, hidratando tu piel.',
  },
  {
    numeral: 'ii.',
    title: 'Sin',
    titleItalic: 'químicos agresivos',
    description:
      'No usamos parabenos, SLS, EDTA ni colorantes sintéticos. Si no le servirías de comer a tu piel, no la pongas sobre ella.',
  },
  {
    numeral: 'iii.',
    title: 'Curado',
    titleItalic: 'de verdad',
    description:
      'Cuatro semanas mínimo. El agua se evapora, la barra endurece, dura el doble y respeta tu pH.',
  },
  {
    numeral: 'iv.',
    title: 'Trazabilidad',
    titleItalic: 'completa',
    description:
      'Conocemos a quien nos vende la miel, el aceite y los pétalos. Cada barra tiene número de tanda y fecha de elaboración.',
  },
  {
    numeral: 'v.',
    title: 'Cero',
    titleItalic: 'plástico',
    description:
      'Empaque en papel kraft, hilo natural y caja reciclada. Una barra de jabón reemplaza tres botellas de gel de ducha.',
  },
  {
    numeral: 'vi.',
    title: 'Pequeñas',
    titleItalic: 'tandas',
    description:
      'No hacemos stock para meses. Cada lote sale fresco del taller, con la concentración de aceites en su punto justo.',
  },
]

export const infoRows: InfoRow[] = [
  {
    key: 'WhatsApp',
    value: '+56 9 1234 5678',
    subValue: 'Lun a Sáb, 10:00 – 19:00',
  },
  {
    key: 'Despachos',
    value: 'A todo Chile',
    subValue: 'Starken · Chilexpress · Retiro en Chillán',
  },
  {
    key: 'Taller',
    value: 'Chillán, Ñuble',
    subValue: 'Visitas con cita previa',
  },
  {
    key: 'Pagos',
    value: 'Transferencia · Mercado Pago',
    subValue: 'Pedido mínimo: 3 barras',
  },
]

export const marqueeItems1 = [
  'Aceite de oliva',
  'Miel pura',
  'Lavanda del valle',
  'Carbón activado',
  'Café de altura',
  'Avena molida',
  'Rosa mosqueta',
  'Caléndula',
]

export const marqueeItems2 = [
  'Despachos a todo Chile',
  'Pequeñas tandas',
  'Vegan friendly',
  'Curado 4 semanas mínimo',
  'Empaque biodegradable',
]
