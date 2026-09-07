export type ProductCategory =
  | 'todos'
  | 'hidratante'
  | 'relajante'
  | 'purificante'
  | 'exfoliante'
  | 'regenerador'

export interface Category {
  id: ProductCategory
  label: string
  description: string
}

export interface Product {
  id: string
  name: string
  nameItalic?: string
  nameItalicFirst?: boolean
  price: string
  description: string
  image: string
  imageAlt: string
  tag?: string
  notes: string[]
  category: Exclude<ProductCategory, 'todos'>
}

export interface ProcessStep {
  number: string
  title: string
  titleItalic: string
  description: string
  image: string
  imageAlt: string
  reversed?: boolean
}

export interface Benefit {
  numeral: string
  title: string
  titleItalic: string
  description: string
}

export interface InfoRow {
  key: string
  value: string
  subValue?: string
}
