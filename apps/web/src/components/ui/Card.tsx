import type { PropsWithChildren } from "react";

import { cn } from "@/lib/utils";

interface CardProps extends PropsWithChildren {
    className?: string;
}

export function Card({ children, className }: CardProps) {
    return (
        <section
            className={cn(
                "rounded-3xl border border-white/70 bg-white/90 p-5 shadow-xl shadow-slate-950/5 backdrop-blur",
                className,
            )}
        >
            {children}
        </section>
    );
}