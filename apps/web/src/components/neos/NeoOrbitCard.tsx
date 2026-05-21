import { Card } from "@/components/ui/Card";
import { formatInteger } from "@/lib/formatters";
import type { NeoOrbitalData } from "@/types/neo";

interface NeoOrbitCardProps {
    orbitalData: NeoOrbitalData | null;
}

export function NeoOrbitCard({ orbitalData }: NeoOrbitCardProps) {
    if (!orbitalData) {
        return (
            <Card>
                <div>
                    <h2 className="text-xl font-black text-slate-950">
                        Parametri orbitali
                    </h2>

                    <p className="mt-2 text-sm text-slate-500">
                        I dati orbitali non sono disponibili per questo oggetto.
                    </p>
                </div>
            </Card>
        );
    }

    const items = [
        {
            label: "Orbit ID",
            value: orbitalData.orbit_id,
        },
        {
            label: "Data determinazione orbita",
            value: orbitalData.orbit_determination_date,
        },
        {
            label: "Prima osservazione",
            value: orbitalData.first_observation_date,
        },
        {
            label: "Ultima osservazione",
            value: orbitalData.last_observation_date,
        },
        {
            label: "Arco dati",
            value:
                orbitalData.data_arc_in_days !== null
                    ? `${formatInteger(orbitalData.data_arc_in_days)} giorni`
                    : "N/D",
        },
        {
            label: "Osservazioni usate",
            value:
                orbitalData.observations_used !== null
                    ? formatInteger(orbitalData.observations_used)
                    : "N/D",
        },
        {
            label: "Classe orbitale",
            value: orbitalData.orbit_class_type,
        },
        {
            label: "Range classe",
            value: orbitalData.orbit_class_range,
        },
    ];

    return (
        <Card>
            <div className="mb-6">
                <h2 className="text-xl font-black text-slate-950">
                    Parametri orbitali
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                    Informazioni sulla classificazione orbitale e sulla qualità delle
                    osservazioni disponibili.
                </p>
            </div>

            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                {items.map((item) => (
                    <div
                        key={item.label}
                        className="rounded-2xl border border-slate-200 bg-slate-50 p-4"
                    >
                        <p className="text-xs font-bold uppercase tracking-wide text-slate-500">
                            {item.label}
                        </p>

                        <p className="mt-2 text-base font-bold text-slate-950">
                            {item.value ?? "N/D"}
                        </p>
                    </div>
                ))}
            </div>

            {orbitalData.orbit_class_description ? (
                <div className="mt-4 rounded-2xl border border-blue-100 bg-blue-50 p-4">
                    <p className="text-xs font-bold uppercase tracking-wide text-blue-700">
                        Descrizione classe orbitale
                    </p>

                    <p className="mt-2 text-sm leading-6 text-blue-950">
                        {orbitalData.orbit_class_description}
                    </p>
                </div>
            ) : null}
        </Card>
    );
}