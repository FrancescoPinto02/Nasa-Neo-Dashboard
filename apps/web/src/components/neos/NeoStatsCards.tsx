import type { ReactNode } from "react";
import { Activity, AlertTriangle, Gauge, Ruler } from "lucide-react";

import { Card } from "@/components/ui/Card";
import {
    formatInteger,
    formatKm,
    formatKmh,
    formatMeters,
} from "@/lib/formatters";
import { cn } from "@/lib/utils";
import type { NeoStatsResponse } from "@/types/neo";

interface NeoStatsCardsProps {
    stats: NeoStatsResponse;
}

export function NeoStatsCards({ stats }: NeoStatsCardsProps) {
    return (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <MetricCard
                title="NEO totali"
                value={formatInteger(stats.total_count)}
                description={`${formatInteger(stats.hazardous_count)} potenzialmente pericolosi`}
                icon={<Activity className="h-5 w-5" />}
                accent="from-sky-500 to-cyan-400"
            />

            <MetricCard
                title="Distanza minima"
                value={formatKm(stats.min_miss_distance_km)}
                description={stats.closest_neo?.name ?? "N/D"}
                icon={<AlertTriangle className="h-5 w-5" />}
                accent="from-rose-500 to-orange-400"
            />

            <MetricCard
                title="Velocità massima"
                value={formatKmh(stats.max_relative_velocity_kmh)}
                description={stats.fastest_neo?.name ?? "N/D"}
                icon={<Gauge className="h-5 w-5" />}
                accent="from-violet-500 to-fuchsia-400"
            />

            <MetricCard
                title="Diametro medio"
                value={formatMeters(stats.average_diameter_m)}
                description={
                    stats.largest_neo ? `Più grande: ${stats.largest_neo.name}` : "N/D"
                }
                icon={<Ruler className="h-5 w-5" />}
                accent="from-emerald-500 to-teal-400"
            />
        </div>
    );
}

interface MetricCardProps {
    title: string;
    value: string;
    description: string;
    icon: ReactNode;
    accent: string;
}

function MetricCard({ title, value, description, icon, accent }: MetricCardProps) {
    return (
        <Card className="relative overflow-hidden">
            <div
                className={cn(
                    "absolute -right-8 -top-8 h-28 w-28 rounded-full bg-gradient-to-br opacity-20 blur-2xl",
                    accent,
                )}
            />

            <div className="relative flex items-start justify-between gap-4">
                <div>
                    <p className="text-sm font-semibold text-slate-500">{title}</p>

                    <p className="mt-2 text-2xl font-black tracking-tight text-slate-950">
                        {value}
                    </p>

                    <p className="mt-1 truncate text-sm text-slate-500">{description}</p>
                </div>

                <div
                    className={cn(
                        "rounded-2xl bg-gradient-to-br p-3 text-white shadow-lg",
                        accent,
                    )}
                >
                    {icon}
                </div>
            </div>
        </Card>
    );
}