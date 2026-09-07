import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";
import { Hero } from "@/components/sections/Hero";
import { About } from "@/components/sections/About";
import { Beers } from "@/components/sections/Beers";
import { Food } from "@/components/sections/Food";
import { Atmosphere } from "@/components/sections/Atmosphere";
import { Testimonials } from "@/components/sections/Testimonials";
import { Contact } from "@/components/sections/Contact";

export default function Home() {
  return (
    <main className="relative overflow-x-hidden">
      <Navbar />
      <Hero />
      <About />
      <Beers />
      <Food />
      <Atmosphere />
      <Testimonials />
      <Contact />
      <Footer />
    </main>
  );
}
