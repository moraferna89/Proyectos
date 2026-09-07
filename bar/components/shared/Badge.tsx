import { cn } from "@/lib/utils";

interface BadgeProps {
  children: React.ReactNode;
  variant?: "amber" | "dark" | "outline";
  className?: string;
}

export function Badge({ children, variant = "dark", className }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium",
        {
          "bg-amber-500/20 text-amber-400 border border-amber-500/30": variant === "amber",
          "bg-white/[0.06] text-white/70 border border-white/10": variant === "dark",
          "border border-white/20 text-white/60 bg-transparent": variant === "outline",
        },
        className
      )}
    >
      {children}
    </span>
  );
}
