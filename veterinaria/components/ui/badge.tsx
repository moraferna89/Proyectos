import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center gap-1.5 rounded-full text-xs font-semibold transition-colors",
  {
    variants: {
      variant: {
        default: "bg-blue-100 text-blue-700 px-3 py-1",
        solid: "bg-blue-600 text-white px-3 py-1",
        outline: "border border-blue-600 text-blue-600 px-3 py-1",
        subtle: "bg-slate-100 text-slate-600 px-3 py-1",
        white: "bg-white/15 text-white border border-white/20 px-3 py-1 backdrop-blur-sm",
        category: "bg-blue-50 text-blue-700 px-2.5 py-0.5 uppercase tracking-wide text-[10px]",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  );
}

export { Badge, badgeVariants };
