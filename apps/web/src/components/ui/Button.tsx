import type { ButtonHTMLAttributes } from "react";

import { cn } from "@/lib/utils";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: "primary" | "secondary";
}

const variantClasses = {
    primary:
        "bg-slate-950 text-white hover:bg-slate-800 disabled:bg-slate-400",
    secondary:
        "bg-white text-slate-900 ring-1 ring-inset ring-slate-300 hover:bg-slate-50 disabled:text-slate-400",
};

export function Button({
                           children,
                           className,
                           variant = "primary",
                           ...props
                       }: ButtonProps) {
    return (
        <button
            className={cn(
                "inline-flex h-10 items-center justify-center rounded-xl px-4 text-sm font-semibold transition disabled:cursor-not-allowed",
                variantClasses[variant],
                className,
            )}
            {...props}
        >
            {children}
        </button>
    );
}