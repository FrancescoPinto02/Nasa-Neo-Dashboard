export type NeoSortBy = "date" | "distance" | "velocity" | "diameter";

export type SortOrder = "asc" | "desc";

export interface NeoSummary {
    id: string;
    name: string;

    nasa_jpl_url: string | null;
    absolute_magnitude_h: number | null;

    is_potentially_hazardous: boolean;

    close_approach_date: string;

    miss_distance_km: number | null;
    relative_velocity_kmh: number | null;

    diameter_min_m: number | null;
    diameter_max_m: number | null;
    diameter_avg_m: number | null;
}

export interface NeoFeedResponse {
    start_date: string;
    end_date: string;
    count: number;
    results: NeoSummary[];
}

export interface NeoDailyCount {
    date: string;
    count: number;
}

export interface NeoHazardousDistributionItem {
    label: string;
    value: number;
}

export interface NeoStatsResponse {
    start_date: string;
    end_date: string;

    total_count: number;
    hazardous_count: number;
    non_hazardous_count: number;

    average_diameter_m: number | null;
    min_miss_distance_km: number | null;
    max_relative_velocity_kmh: number | null;

    closest_neo: NeoSummary | null;
    fastest_neo: NeoSummary | null;
    largest_neo: NeoSummary | null;

    daily_counts: NeoDailyCount[];
    hazardous_distribution: NeoHazardousDistributionItem[];
}

export interface NeoOrbitalData {
    orbit_id: string | null;
    orbit_determination_date: string | null;

    first_observation_date: string | null;
    last_observation_date: string | null;

    data_arc_in_days: number | null;
    observations_used: number | null;

    orbit_class_type: string | null;
    orbit_class_description: string | null;
    orbit_class_range: string | null;
}

export interface NeoCloseApproach {
    close_approach_date: string | null;
    close_approach_date_full: string | null;
    epoch_date_close_approach: number | null;

    relative_velocity_kmh: number | null;
    miss_distance_km: number | null;

    orbiting_body: string | null;
}

export interface NeoDetailsResponse {
    id: string;
    name: string;
    designation: string | null;

    nasa_jpl_url: string | null;
    absolute_magnitude_h: number | null;

    is_potentially_hazardous: boolean;
    is_sentry_object: boolean;

    diameter_min_m: number | null;
    diameter_max_m: number | null;
    diameter_avg_m: number | null;

    orbital_data: NeoOrbitalData | null;
    close_approaches: NeoCloseApproach[];
}
export interface NeoFeedQuery {
    startDate: string;
    endDate: string;
    hazardous?: boolean | null;
    sortBy?: NeoSortBy;
    sortOrder?: SortOrder;
}

export interface NeoStatsQuery {
    startDate: string;
    endDate: string;
}