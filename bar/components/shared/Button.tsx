"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { forwardRef } from "react";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost" | "outline";
  size?: "sm" | "md" | "lg";
  asChild?: boolean;
  href?: string;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ children, variant = "primary", size = "md", className, href, ...props }, ref) => {
    const base =
      "inline-flex items-center justify-center gap-2 font-semibold rounded-xl transition-all duration-200 whitespace-nowrap";

    const variants = {
      primary:
        "bg-amber-500 text-black hover:bg-amber-400 shadow-glow-amber hover:shadow-glow-amber-lg active:scale-[0.97]",
      secondary:
        "bg-white/[0.08] text-white border border-white/10 hover:bg-white/[0.12] hover:border-white/20 active:scale-[0.97]",
      ghost: "text-white/70 hover:text-white hover:bg-white/[0.06] active:scale-[0.97]",
      outline:
        "border border-amber-500/40 text-amber-400 hover:bg-amber-500/10 hover:border-amber-500/60 active:scale-[0.97]",
    };

    const sizes = {
      sm: "text-sm px-4 py-2",
      md: "text-sm px-6 py-3",
      lg: "text-base px-8 py-4",
    };

    const classes = cn(base, variants[variant], sizes[size], className);

    if (href) {
      return (
        <a href={href} className={classes}>
          {children}
        </a>
      );
    }

    return (
      <button ref={ref} className={classes} {...props}>
        {children}
      </button>
    );
  }
);

Button.displayName = "Button";
