import { ExternalLink, ShieldAlert, ShieldCheck } from "lucide-react";

import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import {
    formatDate,
    formatKm,
    formatKmh,
    formatMeters,
} from "@/lib/formatters";
import type { NeoSummary } from "@/types/neo";
import Link from "next/link";

interface NeoTableProps {
    neos: NeoSummary[];
}

export function NeoTable({ neos }: NeoTableProps) {
    return (
        <Card className="overflow-hidden p-0">
            <div className="flex flex-col gap-2 border-b border-slate-200 px-5 py-5 sm:flex-row sm:items-center sm:justify-between">
                <div>
                    <h2 className="text-lg font-black text-slate-950">
                        Avvicinamenti NEO
                    </h2>
                    <p className="mt-1 text-sm text-slate-500">
                        Oggetti vicini alla Terra nel range selezionato.
                    </p>
                </div>

                <Badge variant="muted">{neos.length} risultati</Badge>
            </div>

            <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-slate-200">
                    <thead className="bg-slate-950">
                    <tr>
                        <TableHeader>Nome</TableHeader>
                        <TableHeader>Data</TableHeader>
                        <TableHeader>Distanza</TableHeader>
                        <TableHeader>Velocità</TableHeader>
                        <TableHeader>Diametro medio</TableHeader>
                        <TableHeader>Rischio</TableHeader>
                        <TableHeader>NASA/JPL</TableHeader>
                    </tr>
                    </thead>

                    <tbody className="divide-y divide-slate-100 bg-white">
                    {neos.length === 0 ? (
                        <tr>
                            <td
                                colSpan={7}
                                className="px-5 py-10 text-center text-sm text-slate-500"
                            >
                                Nessun NEO trovato per i filtri selezionati.
                            </td>
                        </tr>
                    ) : (
                        neos.map((neo) => (
                            <tr
                                key={`${neo.id}-${neo.close_approach_date}`}
                                className="transition hover:bg-slate-50"
                            >
                                <TableCell>
                                    <div>
                                        <Link
                                            href={`/neos/${neo.id}`}
                                            className="font-bold text-slate-950 transition hover:text-blue-700"
                                        >
                                            {neo.name}
                                        </Link>
                                        <p className="text-xs text-slate-500">ID {neo.id}</p>
                                    </div>
                                </TableCell>

                                <TableCell>{formatDate(neo.close_approach_date)}</TableCell>
                                <TableCell>{formatKm(neo.miss_distance_km)}</TableCell>
                                <TableCell>{formatKmh(neo.relative_velocity_kmh)}</TableCell>
                                <TableCell>{formatMeters(neo.diameter_avg_m)}</TableCell>

                                <TableCell>
                                    {neo.is_potentially_hazardous ? (
                                        <Badge variant="danger">
                                            <ShieldAlert className="h-3.5 w-3.5" />
                                            Pericoloso
                                        </Badge>
                                    ) : (
                                        <Badge variant="success">
                                            <ShieldCheck className="h-3.5 w-3.5" />
                                            Sicuro
                                        </Badge>
                                    )}
                                </TableCell>

                                <TableCell>
                                    {neo.nasa_jpl_url ? (
                                        <a
                                            href={neo.nasa_jpl_url}
                                            target="_blank"
                                            rel="noreferrer"
                                            className="inline-flex items-center gap-1 text-sm font-semibold text-blue-700 hover:text-blue-900"
                                        >
                                            Apri
                                            <ExternalLink className="h-3.5 w-3.5" />
                                        </a>
                                    ) : (
                                        <span className="text-slate-400">N/D</span>
                                    )}
                                </TableCell>
                            </tr>
                        ))
                    )}
                    </tbody>
                </table>
            </div>
        </Card>
    );
}

interface TableTextProps {
    children: React.ReactNode;
}

function TableHeader({ children }: TableTextProps) {
    return (
        <th className="whitespace-nowrap px-5 py-3 text-left text-xs font-bold uppercase tracking-wide text-slate-300">
            {children}
        </th>
    );
}

function TableCell({ children }: TableTextProps) {
    return (
        <td className="whitespace-nowrap px-5 py-4 text-sm text-slate-700">
            {children}
        </td>
    );
}