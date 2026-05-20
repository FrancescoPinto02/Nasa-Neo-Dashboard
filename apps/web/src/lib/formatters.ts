const integerFormatter = new Intl.NumberFormat("it-IT", {
    maximumFractionDigits: 0,
});

const decimalFormatter = new Intl.NumberFormat("it-IT", {
    maximumFractionDigits: 2,
});

const dateFormatter = new Intl.DateTimeFormat("it-IT", {
    day: "2-digit",
    month: "short",
    year: "numeric",
});

export function formatInteger(value: number | null | undefined): string {
    if (value === null || value === undefined) {
        return "N/D";
    }

    return integerFormatter.format(value);
}

export function formatDecimal(value: number | null | undefined): string {
    if (value === null || value === undefined) {
        return "N/D";
    }

    return decimalFormatter.format(value);
}

export function formatKm(value: number | null | undefined): string {
    if (value === null || value === undefined) {
        return "N/D";
    }

    return `${integerFormatter.format(value)} km`;
}

export function formatKmh(value: number | null | undefined): string {
    if (value === null || value === undefined) {
        return "N/D";
    }

    return `${integerFormatter.format(value)} km/h`;
}

export function formatMeters(value: number | null | undefined): string {
    if (value === null || value === undefined) {
        return "N/D";
    }

    return `${decimalFormatter.format(value)} m`;
}

export function formatDate(value: string | null | undefined): string {
    if (!value) {
        return "N/D";
    }

    const date = new Date(`${value}T00:00:00`);

    if (Number.isNaN(date.getTime())) {
        return value;
    }

    return dateFormatter.format(date);
}