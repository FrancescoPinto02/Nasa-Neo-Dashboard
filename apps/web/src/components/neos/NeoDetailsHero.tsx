import {
    AlertTriangle,
    ExternalLink,
    Orbit,
    ShieldAlert,
    ShieldCheck,
} from "lucide-react";

import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import {
    formatMeters,
} from "@/lib/formatters";
import type { NeoDetailsResponse } from "@/types/neo";

interface NeoDetailsHeroProps {
    neo: NeoDetailsResponse;
}

export function NeoDetailsHero({ neo }: NeoDetailsHeroProps) {
    return (
        <Card className="relative overflow-hidden border-white/10 bg-white/[0.08] text-white backdrop-blur">
            <div className="absolute right-0 top-0 h-64 w-64 rounded-full bg-cyan-500/20 blur-3xl" />

            <div className="relative">
                <div className="mb-5 flex flex-wrap items-center gap-2">
                    {neo.is_potentially_hazardous ? (
                        <Badge variant="danger">
                            <ShieldAlert className="h-3.5 w-3.5" />
                            Potenzialmente pericoloso
                        </Badge>
                    ) : (
                        <Badge variant="success">
                            <ShieldCheck className="h-3.5 w-3.5" />
                            Non pericoloso
                        </Badge>
                    )}

                    {neo.is_sentry_object ? (
                        <Badge variant="warning">
                            <AlertTriangle className="h-3.5 w-3.5" />
                            Sentry object
                        </Badge>
                    ) : null}
                </div>

                <p className="text-sm font-bold uppercase tracking-[0.25em] text-cyan-200">
                    Near Earth Object
                </p>

                <h1 className="mt-3 text-4xl font-black tracking-tight sm:text-5xl">
                    {neo.name}
                </h1>

                <p className="mt-3 max-w-2xl text-slate-300">
                    Analisi dettagliata dell’oggetto vicino alla Terra con dati orbitali,
                    velocità relative e informazioni NASA/JPL.
                </p>

                <div className="mt-8 flex flex-wrap gap-4">
                    <InfoPill
                        label="Diametro medio"
                        value={formatMeters(neo.diameter_avg_m)}
                        icon={<Orbit className="h-4 w-4" />}
                    />

                    <InfoPill
                        label="Magnitudine assoluta"
                        value={
                            neo.absolute_magnitude_h
                                ? String(neo.absolute_magnitude_h)
                                : "N/D"
                        }
                        icon={<Orbit className="h-4 w-4" />}
                    />
                </div>

                {neo.nasa_jpl_url ? (
                    <div className="mt-8">
                        <a
                            href={neo.nasa_jpl_url}
                            target="_blank"
                            rel="noreferrer"
                        >
                            <Button className="gap-2">
                                Apri pagina NASA/JPL
                                <ExternalLink className="h-4 w-4" />
                            </Button>
                        </a>
                    </div>
                ) : null}
            </div>
        </Card>
    );
}

interface InfoPillProps {
    label: string;
    value: string;
    icon: React.ReactNode;
}

function InfoPill({ label, value, icon }: InfoPillProps) {
    return (
        <div className="flex items-center gap-3 rounded-2xl border border-white/10 bg-white/10 px-4 py-3">
            <div className="rounded-xl bg-white/10 p-2 text-cyan-200">
                {icon}
            </div>

            <div>
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                    {label}
                </p>

                <p className="text-sm font-bold text-white">
                    {value}
                </p>
            </div>
        </div>
    );
}