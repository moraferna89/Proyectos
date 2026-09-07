"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface AnimatedCardProps {
  children: React.ReactNode;
  className?: string;
  delay?: number;
  hover?: boolean;
}

export function AnimatedCard({
  children,
  className,
  delay = 0,
  hover = true,
}: AnimatedCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-50px" }}
      transition={{ duration: 0.5, delay, ease: "easeOut" }}
      whileHover={hover ? { y: -4, transition: { duration: 0.2 } } : undefined}
      className={cn(
        "relative rounded-2xl border border-white/[0.06] bg-white/[0.03]",
        "backdrop-blur-sm overflow-hidden",
        hover && "cursor-pointer group",
        className
      )}
    >
      <div
        className={cn(
          "absolute inset-0 opacity-0 transition-opacity duration-300",
          "bg-gradient-to-br from-amber-500/[0.06] to-transparent",
          hover && "group-hover:opacity-100"
        )}
      />
      <div className="relative z-10">{children}</div>
    </motion.div>
  );
}
