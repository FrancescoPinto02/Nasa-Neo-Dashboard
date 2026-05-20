import type { PropsWithChildren } from "react";

import { cn } from "@/lib/utils";

interface BadgeProps extends PropsWithChildren {
    variant?: "default" | "success" | "danger" | "muted" | "warning";
}

const variantClasses = {
    default: "bg-sky-100 text-sky-800 ring-sky-200",
    success: "bg-emerald-100 text-emerald-800 ring-emerald-200",
    danger: "bg-rose-100 text-rose-800 ring-rose-200",
    warning: "bg-amber-100 text-amber-800 ring-amber-200",
    muted: "bg-slate-100 text-slate-700 ring-slate-200",
};

export function Badge({ children, variant = "default" }: BadgeProps) {
    return (
        <span
            className={cn(
                "inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ring-inset",
                variantClasses[variant],
            )}
        >
      {children}
    </span>
    );
}