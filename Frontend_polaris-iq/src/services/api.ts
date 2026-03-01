import type { QueryRequest, QueryResponse } from '../types/api';

const API_BASE_URL = '/api';

export async function sendQuery(query: string, table: string): Promise<QueryResponse> {
    const body: QueryRequest = { query, table };

    const res = await fetch(`${API_BASE_URL}/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
    });

    if (!res.ok) {
        const errorText = await res.text().catch(() => 'Unknown error');
        throw new Error(`Backend error (${res.status}): ${errorText}`);
    }

    return res.json() as Promise<QueryResponse>;
}
