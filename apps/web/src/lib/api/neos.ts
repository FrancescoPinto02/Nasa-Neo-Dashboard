import { apiFetch } from "@/lib/api/client";
import type {
    NeoFeedQuery,
    NeoFeedResponse,
    NeoStatsQuery,
    NeoStatsResponse,
} from "@/types/neo";

export function getNeoFeed(query: NeoFeedQuery): Promise<NeoFeedResponse> {
    const searchParams = buildSearchParams({
        start_date: query.startDate,
        end_date: query.endDate,
        hazardous: query.hazardous,
        sort_by: query.sortBy ?? "date",
        sort_order: query.sortOrder ?? "asc",
    });

    return apiFetch<NeoFeedResponse>(`/neos?${searchParams.toString()}`);
}

export function getNeoStats(query: NeoStatsQuery): Promise<NeoStatsResponse> {
    const searchParams = buildSearchParams({
        start_date: query.startDate,
        end_date: query.endDate,
    });

    return apiFetch<NeoStatsResponse>(`/neos/stats?${searchParams.toString()}`);
}

function buildSearchParams(
    params: Record<string, string | number | boolean | null | undefined>,
): URLSearchParams {
    const searchParams = new URLSearchParams();

    Object.entries(params).forEach(([key, value]) => {
        if (value === null || value === undefined || value === "") {
            return;
        }

        searchParams.set(key, String(value));
    });

    return searchParams;
}