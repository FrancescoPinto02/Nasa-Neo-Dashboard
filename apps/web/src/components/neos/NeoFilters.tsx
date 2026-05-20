import type { FormEvent } from "react";

import { Button } from "@/components/ui/Button";
import type { NeoSortBy, SortOrder } from "@/types/neo";

interface NeoFiltersProps {
    startDate: string;
    endDate: string;
    hazardous: string;
    sortBy: NeoSortBy;
    sortOrder: SortOrder;
    isLoading: boolean;

    onStartDateChange: (value: string) => void;
    onEndDateChange: (value: string) => void;
    onHazardousChange: (value: string) => void;
    onSortByChange: (value: NeoSortBy) => void;
    onSortOrderChange: (value: SortOrder) => void;
    onSubmit: () => void;
}

export function NeoFilters({
                               startDate,
                               endDate,
                               hazardous,
                               sortBy,
                               sortOrder,
                               isLoading,
                               onStartDateChange,
                               onEndDateChange,
                               onHazardousChange,
                               onSortByChange,
                               onSortOrderChange,
                               onSubmit,
                           }: NeoFiltersProps) {
    function handleSubmit(event: FormEvent<HTMLFormElement>) {
        event.preventDefault();
        onSubmit();
    }

    return (
        <form
            onSubmit={handleSubmit}
            className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm"
        >
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-6">
                <label className="space-y-1.5">
                    <span className="text-sm font-medium text-slate-700">Da</span>
                    <input
                        type="date"
                        value={startDate}
                        onChange={(event) => onStartDateChange(event.target.value)}
                        className="h-10 w-full rounded-xl border border-slate-300 px-3 text-sm outline-none focus:border-slate-900"
                        required
                    />
                </label>

                <label className="space-y-1.5">
                    <span className="text-sm font-medium text-slate-700">A</span>
                    <input
                        type="date"
                        value={endDate}
                        onChange={(event) => onEndDateChange(event.target.value)}
                        className="h-10 w-full rounded-xl border border-slate-300 px-3 text-sm outline-none focus:border-slate-900"
                        required
                    />
                </label>

                <label className="space-y-1.5">
                    <span className="text-sm font-medium text-slate-700">Rischio</span>
                    <select
                        value={hazardous}
                        onChange={(event) => onHazardousChange(event.target.value)}
                        className="h-10 w-full rounded-xl border border-slate-300 px-3 text-sm outline-none focus:border-slate-900"
                    >
                        <option value="all">Tutti</option>
                        <option value="true">Potenzialmente pericolosi</option>
                        <option value="false">Non pericolosi</option>
                    </select>
                </label>

                <label className="space-y-1.5">
                    <span className="text-sm font-medium text-slate-700">Ordina per</span>
                    <select
                        value={sortBy}
                        onChange={(event) => onSortByChange(event.target.value as NeoSortBy)}
                        className="h-10 w-full rounded-xl border border-slate-300 px-3 text-sm outline-none focus:border-slate-900"
                    >
                        <option value="date">Data</option>
                        <option value="distance">Distanza</option>
                        <option value="velocity">Velocità</option>
                        <option value="diameter">Diametro</option>
                    </select>
                </label>

                <label className="space-y-1.5">
                    <span className="text-sm font-medium text-slate-700">Direzione</span>
                    <select
                        value={sortOrder}
                        onChange={(event) =>
                            onSortOrderChange(event.target.value as SortOrder)
                        }
                        className="h-10 w-full rounded-xl border border-slate-300 px-3 text-sm outline-none focus:border-slate-900"
                    >
                        <option value="asc">Crescente</option>
                        <option value="desc">Decrescente</option>
                    </select>
                </label>

                <div className="flex items-end">
                    <Button type="submit" className="w-full" disabled={isLoading}>
                        {isLoading ? "Carico..." : "Aggiorna"}
                    </Button>
                </div>
            </div>
        </form>
    );
}