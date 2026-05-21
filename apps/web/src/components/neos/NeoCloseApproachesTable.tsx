import { Card } from "@/components/ui/Card";
import {
    formatDate,
    formatKm,
    formatKmh,
} from "@/lib/formatters";
import type { NeoCloseApproach } from "@/types/neo";

interface NeoCloseApproachesTableProps {
    approaches: NeoCloseApproach[];
}

export function NeoCloseApproachesTable({
                                            approaches,
                                        }: NeoCloseApproachesTableProps) {
    return (
        <Card className="overflow-hidden p-0">
            <div className="border-b border-slate-200 px-5 py-5">
                <h2 className="text-xl font-black text-slate-950">
                    Close approaches
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                    Storico degli avvicinamenti registrati.
                </p>
            </div>

            <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-slate-200">
                    <thead className="bg-slate-950">
                    <tr>
                        <TableHeader>Data</TableHeader>
                        <TableHeader>Distanza</TableHeader>
                        <TableHeader>Velocità</TableHeader>
                        <TableHeader>Corpo orbitato</TableHeader>
                    </tr>
                    </thead>

                    <tbody className="divide-y divide-slate-100 bg-white">
                    {approaches.map((approach, index) => (
                        <tr
                            key={`${approach.close_approach_date ?? "unknown"}-${index}`}
                            className="transition hover:bg-slate-50"
                        >
                            <TableCell>
                                {formatDate(approach.close_approach_date)}
                            </TableCell>

                            <TableCell>
                                {formatKm(approach.miss_distance_km)}
                            </TableCell>

                            <TableCell>
                                {formatKmh(approach.relative_velocity_kmh)}
                            </TableCell>

                            <TableCell>
                                {approach.orbiting_body ?? "N/D"}
                            </TableCell>
                        </tr>
                    ))}
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