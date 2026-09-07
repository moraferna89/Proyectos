import SectionHeader from './SectionHeader'
import ProductCard from './ProductCard'
import LeafSVG from './LeafSVG'
import { products } from '@/lib/data'

export default function Catalog() {
  return (
    <section id="catalogo" className="relative overflow-hidden bg-cream section-pad">
      <LeafSVG
        color="#5C5A3F"
        className="absolute top-[60px] left-[-80px] w-[320px] opacity-10 pointer-events-none"
      />

      <div className="wrap relative z-10">
        <SectionHeader
          eyebrow="Nuestro catálogo"
          title={
            <>
              Seis barras,{' '}
              <em className="italic text-wine not-italic">
                <span className="italic">infinitas pausas</span>
              </em>
              .
            </>
          }
          subtitle="Cada jabón es elaborado en pequeñas tandas con curado mínimo de 4 semanas."
        />

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-x-10 gap-y-14">
          {products.map((product, i) => (
            <ProductCard
              key={product.id}
              product={product}
              delay={(i % 3) * 0.12}
            />
          ))}
        </div>
      </div>
    </section>
  )
}
