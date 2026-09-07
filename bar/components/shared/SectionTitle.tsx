"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface SectionTitleProps {
  eyebrow?: string;
  title: string;
  titleHighlight?: string;
  description?: string;
  align?: "left" | "center" | "right";
  className?: string;
}

export function SectionTitle({
  eyebrow,
  title,
  titleHighlight,
  description,
  align = "center",
  className,
}: SectionTitleProps) {
  const alignClass = {
    left: "text-left items-start",
    center: "text-center items-center",
    right: "text-right items-end",
  }[align];

  return (
    <div className={cn("flex flex-col gap-4", alignClass, className)}>
      {eyebrow && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.4 }}
          className="flex items-center gap-3"
        >
          <span className="h-px w-8 bg-amber-500/60" />
          <span className="text-amber-400 text-xs font-semibold uppercase tracking-[0.2em]">
            {eyebrow}
          </span>
          <span className="h-px w-8 bg-amber-500/60" />
        </motion.div>
      )}

      <motion.h2
        initial={{ opacity: 0, y: 16 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="text-3xl sm:text-4xl md:text-5xl font-bold tracking-tight leading-tight"
      >
        {title}{" "}
        {titleHighlight && (
          <span className="text-gradient">{titleHighlight}</span>
        )}
      </motion.h2>

      {description && (
        <motion.p
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className={cn(
            "text-white/55 text-base sm:text-lg leading-relaxed",
            align === "center" && "max-w-2xl"
          )}
        >
          {description}
        </motion.p>
      )}
    </div>
  );
}
