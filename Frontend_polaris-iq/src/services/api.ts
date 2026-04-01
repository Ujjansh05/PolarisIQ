// services/api.ts

import type {
    QueryRequest, QueryResponse, ToolQueryResponse,
    HealthResponse, TablesResponse, SchemaResponse, PreviewResponse,
    IngestResponse, StatsResponse, LogsResponse,
    CorrelationsResponse, StatisticsResponse,
} from '../types/api';

const API_BASE_URL = '/api';

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
    const res = await fetch(`${API_BASE_URL}${path}`, options);

    if (!res.ok) {
        const errorText = await res.text().catch(() => 'Unknown error');
        throw new Error(`Backend error (${res.status}): ${errorText}`);
    }

    return res.json() as Promise<T>;
}

// ── Health ───────────────────────────────────────────────────────

export function fetchHealth(): Promise<HealthResponse> {
    return apiFetch('/health');
}

// ── Query ────────────────────────────────────────────────────────

export function sendQuery(query: string, table: string): Promise<QueryResponse> {
    const body: QueryRequest = { query, table };
    return apiFetch('/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
    });
}

export function sendToolQuery(query: string, table: string): Promise<ToolQueryResponse> {
    return apiFetch('/tool-query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, table }),
    });
}

// ── Tables ───────────────────────────────────────────────────────

export function fetchTables(): Promise<TablesResponse> {
    return apiFetch('/tables');
}

export function fetchSchema(tableName: string): Promise<SchemaResponse> {
    return apiFetch(`/tables/${tableName}/schema`);
}

export function fetchPreview(tableName: string, limit = 50): Promise<PreviewResponse> {
    return apiFetch(`/tables/${tableName}/preview?limit=${limit}`);
}

// ── Ingest ───────────────────────────────────────────────────────

export async function ingestFile(file: File, tableName?: string): Promise<IngestResponse> {
    const formData = new FormData();
    formData.append('file', file);
    if (tableName) {
        formData.append('table_name', tableName);
    }

    return apiFetch('/ingest', {
        method: 'POST',
        body: formData,
    });
}

// ── Stats / Logs ─────────────────────────────────────────────────

export function fetchStats(): Promise<StatsResponse> {
    return apiFetch('/stats');
}

export function fetchLogs(limit = 50): Promise<LogsResponse> {
    return apiFetch(`/logs?limit=${limit}`);
}

// ── Profiling ────────────────────────────────────────────────────

export function fetchCorrelations(tableName: string): Promise<CorrelationsResponse> {
    return apiFetch(`/correlations/${tableName}`);
}

export function fetchStatistics(tableName: string): Promise<StatisticsResponse> {
    return apiFetch(`/statistics/${tableName}`);
}
