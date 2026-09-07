import { cn } from "@/lib/utils";
import { Badge } from "./badge";

interface SectionHeaderProps {
  badge?: string;
  title: string;
  titleHighlight?: string;
  description?: string;
  centered?: boolean;
  dark?: boolean;
  className?: string;
}

export function SectionHeader({
  badge,
  title,
  titleHighlight,
  description,
  centered = true,
  dark = false,
  className,
}: SectionHeaderProps) {
  return (
    <div
      className={cn(
        "mb-12 md:mb-16",
        centered && "text-center",
        className
      )}
    >
      {badge && (
        <div className={cn("mb-4", centered && "flex justify-center")}>
          <Badge variant={dark ? "white" : "default"}>{badge}</Badge>
        </div>
      )}
      <h2
        className={cn(
          "text-3xl md:text-4xl lg:text-5xl font-bold leading-tight tracking-tight",
          dark ? "text-white" : "text-slate-900"
        )}
      >
        {title}{" "}
        {titleHighlight && (
          <span className="gradient-text">{titleHighlight}</span>
        )}
      </h2>
      {description && (
        <p
          className={cn(
            "mt-4 text-lg leading-relaxed max-w-2xl",
            centered && "mx-auto",
            dark ? "text-slate-300" : "text-slate-500"
          )}
        >
          {description}
        </p>
      )}
    </div>
  );
}
