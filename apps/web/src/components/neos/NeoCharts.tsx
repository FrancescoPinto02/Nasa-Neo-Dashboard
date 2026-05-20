"use client";

import {
    Bar,
    BarChart,
    CartesianGrid,
    Cell,
    Line,
    LineChart,
    Pie,
    PieChart,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from "recharts";

import { Card } from "@/components/ui/Card";
import type { NeoStatsResponse } from "@/types/neo";

interface NeoChartsProps {
    stats: NeoStatsResponse;
}

const hazardousColors: Record<string, string> = {
    Hazardous: "#f43f5e",
    "Non hazardous": "#10b981",
};

export function NeoCharts({ stats }: NeoChartsProps) {
    const dailyCounts = stats.daily_counts.map((item) => ({
        date: formatChartDate(item.date),
        count: item.count,
    }));

    return (
        <div className="grid gap-4 xl:grid-cols-3">
            <Card className="xl:col-span-2">
                <div className="mb-5">
                    <h2 className="text-base font-bold text-slate-950">
                        Avvicinamenti giornalieri
                    </h2>
                    <p className="mt-1 text-sm text-slate-500">
                        Numero di oggetti vicini alla Terra per giorno.
                    </p>
                </div>

                <div className="h-72">
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={dailyCounts}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                            <XAxis
                                dataKey="date"
                                tickLine={false}
                                axisLine={false}
                                tick={{ fill: "#64748b", fontSize: 12 }}
                            />
                            <YAxis
                                allowDecimals={false}
                                tickLine={false}
                                axisLine={false}
                                tick={{ fill: "#64748b", fontSize: 12 }}
                            />
                            <Tooltip
                                contentStyle={{
                                    borderRadius: 16,
                                    border: "1px solid #e2e8f0",
                                    boxShadow: "0 20px 40px rgba(15, 23, 42, 0.12)",
                                }}
                            />
                            <Line
                                type="monotone"
                                dataKey="count"
                                name="NEO"
                                stroke="#2563eb"
                                strokeWidth={3}
                                dot={{ r: 4, fill: "#2563eb" }}
                                activeDot={{ r: 7 }}
                            />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            </Card>

            <Card>
                <div className="mb-5">
                    <h2 className="text-base font-bold text-slate-950">
                        Distribuzione rischio
                    </h2>
                    <p className="mt-1 text-sm text-slate-500">
                        Rapporto tra NEO pericolosi e non pericolosi.
                    </p>
                </div>

                <div className="h-72">
                    <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                            <Pie
                                data={stats.hazardous_distribution}
                                dataKey="value"
                                nameKey="label"
                                innerRadius={58}
                                outerRadius={90}
                                paddingAngle={4}
                            >
                                {stats.hazardous_distribution.map((item) => (
                                    <Cell
                                        key={item.label}
                                        fill={hazardousColors[item.label] ?? "#64748b"}
                                    />
                                ))}
                            </Pie>
                            <Tooltip
                                contentStyle={{
                                    borderRadius: 16,
                                    border: "1px solid #e2e8f0",
                                    boxShadow: "0 20px 40px rgba(15, 23, 42, 0.12)",
                                }}
                            />
                        </PieChart>
                    </ResponsiveContainer>
                </div>
            </Card>

            <Card className="xl:col-span-3">
                <div className="mb-5">
                    <h2 className="text-base font-bold text-slate-950">
                        Intensità giornaliera
                    </h2>
                    <p className="mt-1 text-sm text-slate-500">
                        Vista alternativa a barre, utile per confrontare rapidamente i giorni.
                    </p>
                </div>

                <div className="h-72">
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={dailyCounts}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                            <XAxis
                                dataKey="date"
                                tickLine={false}
                                axisLine={false}
                                tick={{ fill: "#64748b", fontSize: 12 }}
                            />
                            <YAxis
                                allowDecimals={false}
                                tickLine={false}
                                axisLine={false}
                                tick={{ fill: "#64748b", fontSize: 12 }}
                            />
                            <Tooltip
                                contentStyle={{
                                    borderRadius: 16,
                                    border: "1px solid #e2e8f0",
                                    boxShadow: "0 20px 40px rgba(15, 23, 42, 0.12)",
                                }}
                            />
                            <Bar
                                dataKey="count"
                                name="NEO"
                                fill="#7c3aed"
                                radius={[10, 10, 0, 0]}
                            />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </Card>
        </div>
    );
}

function formatChartDate(value: string): string {
    const date = new Date(`${value}T00:00:00`);

    if (Number.isNaN(date.getTime())) {
        return value;
    }

    return date.toLocaleDateString("it-IT", {
        day: "2-digit",
        month: "short",
    });
}