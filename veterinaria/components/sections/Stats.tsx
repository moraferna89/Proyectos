"use client";

import { useRef, useState, useEffect } from "react";
import { motion, useInView } from "framer-motion";
import { Award, Heart, Star, ThumbsUp } from "lucide-react";
import { STATS } from "@/lib/constants";
import { staggerContainer, fadeInUp } from "@/lib/animations";

const ICONS = { Award, Heart, Star, ThumbsUp };

function CountUp({
  target,
  suffix,
  isActive,
}: {
  target: number;
  suffix: string;
  isActive: boolean;
}) {
  const [count, setCount] = useState(0);

  useEffect(() => {
    if (!isActive) return;
    let start = 0;
    const duration = 2000;
    const steps = 60;
    const increment = target / steps;
    const timer = setInterval(() => {
      start += increment;
      if (start >= target) {
        setCount(target);
        clearInterval(timer);
      } else {
        setCount(Math.floor(start));
      }
    }, duration / steps);
    return () => clearInterval(timer);
  }, [isActive, target]);

  return (
    <span>
      {count.toLocaleString()}
      {suffix}
    </span>
  );
}

export function Stats() {
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true, amount: 0.3 });

  return (
    <section
      ref={ref}
      className="relative py-16 bg-gradient-to-r from-blue-700 via-blue-600 to-sky-600 overflow-hidden"
    >
      {/* Background pattern */}
      <div className="absolute inset-0 bg-dot-pattern opacity-20" />

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          animate={isInView ? "visible" : "hidden"}
          className="grid grid-cols-2 lg:grid-cols-4 gap-8"
        >
          {STATS.map((stat) => {
            const Icon = ICONS[stat.icon as keyof typeof ICONS];
            return (
              <motion.div
                key={stat.label}
                variants={fadeInUp}
                className="text-center"
              >
                <div className="flex justify-center mb-3">
                  <div className="w-12 h-12 rounded-2xl bg-white/15 flex items-center justify-center">
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                </div>
                <div className="text-4xl lg:text-5xl font-bold text-white font-heading mb-2">
                  <CountUp
                    target={stat.value}
                    suffix={stat.suffix}
                    isActive={isInView}
                  />
                </div>
                <p className="text-blue-100 text-sm font-medium">{stat.label}</p>
              </motion.div>
            );
          })}
        </motion.div>
      </div>
    </section>
  );
}
