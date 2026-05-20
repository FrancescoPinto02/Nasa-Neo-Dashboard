import { config } from "@/lib/config";

interface BackendErrorEnvelope {
    error?: {
        code?: string;
        message?: string;
        details?: unknown;
    };
}

export class ApiClientError extends Error {
    readonly status: number;
    readonly code: string;
    readonly details: unknown;

    constructor({
                    status,
                    code,
                    message,
                    details,
                }: {
        status: number;
        code: string;
        message: string;
        details?: unknown;
    }) {
        super(message);
        this.name = "ApiClientError";
        this.status = status;
        this.code = code;
        this.details = details;
    }
}

export async function apiFetch<T>(
    path: string,
    init?: RequestInit,
): Promise<T> {
    const response = await fetch(`${config.apiBaseUrl}${path}`, {
        ...init,
        headers: {
            Accept: "application/json",
            ...init?.headers,
        },
    });

    if (!response.ok) {
        throw await buildApiError(response);
    }

    return response.json() as Promise<T>;
}

async function buildApiError(response: Response): Promise<ApiClientError> {
    let payload: BackendErrorEnvelope | null = null;

    try {
        payload = (await response.json()) as BackendErrorEnvelope;
    } catch {
        payload = null;
    }

    return new ApiClientError({
        status: response.status,
        code: payload?.error?.code ?? "http_error",
        message:
            payload?.error?.message ??
            `Request failed with status ${response.status}.`,
        details: payload?.error?.details,
    });
}