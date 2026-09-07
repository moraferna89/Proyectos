import Navbar from '@/components/Navbar'
import Hero from '@/components/Hero'
import MarqueeStrip from '@/components/MarqueeStrip'
import Catalog from '@/components/Catalog'
import About from '@/components/About'
import Process from '@/components/Process'
import Benefits from '@/components/Benefits'
import QuoteBand from '@/components/QuoteBand'
import Contact from '@/components/Contact'
import Footer from '@/components/Footer'
import FloatingWhatsApp from '@/components/FloatingWhatsApp'
import { marqueeItems1, marqueeItems2 } from '@/lib/data'

export default function HomePage() {
  return (
    <>
      <Navbar />
      <main>
        <Hero />
        <MarqueeStrip items={marqueeItems1} />
        <Catalog />
        <MarqueeStrip items={marqueeItems2} reverse bgColor="bg-wine" textColor="text-cream-light" />
        <About />
        <Process />
        <Benefits />
        <QuoteBand />
        <Contact />
      </main>
      <Footer />
      <FloatingWhatsApp />
    </>
  )
}
