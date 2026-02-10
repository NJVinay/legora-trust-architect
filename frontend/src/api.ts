/**
 * API client for the Legora Trust-Architect backend.
 * 
 * Security:
 *   - All requests include X-API-Key header (Req #5)
 *   - Error messages are user-friendly, no internal details (Req #4)
 *   - Handles SSE streaming with proper error boundaries
 */

import type {
    AgentEvent,
    GenerateRequest,
    GenerateResponse,
    CitationEntry,
    DocumentMetadata,
    PresetInfo,
} from "./types";

const API_BASE = (import.meta.env.VITE_API_URL || "") + "/api";

/**
 * Get the API key from environment or config.
 * In dev, Vite injects VITE_API_KEY from .env.
 * In prod, this should be set at build time or via a login flow.
 */
function getApiKey(): string {
    return import.meta.env.VITE_API_KEY || "";
}

/**
 * Build standard headers for all API requests.
 */
function getHeaders(extra: Record<string, string> = {}): Record<string, string> {
    const headers: Record<string, string> = { ...extra };
    const apiKey = getApiKey();
    if (apiKey) {
        headers["X-API-Key"] = apiKey;
    }
    return headers;
}

/**
 * Handle fetch errors with user-friendly messages.
 * Never expose raw server error details to the UI.
 */
function handleFetchError(res: Response, context: string): never {
    if (res.status === 403) {
        throw new Error("Access denied. Please check your API key.");
    }
    if (res.status === 429) {
        throw new Error("Rate limit exceeded. Please wait a moment and try again.");
    }
    if (res.status === 401) {
        throw new Error("Authentication required. Please log in.");
    }
    throw new Error(`${context}. Please try again.`);
}

// --- REST Endpoints ---

export async function fetchCitations(): Promise<Record<string, CitationEntry>> {
    const res = await fetch(`${API_BASE}/citations`, {
        headers: getHeaders(),
    });
    if (!res.ok) handleFetchError(res, "Failed to load citations");
    const data = await res.json();
    return data.citations;
}

export async function fetchCitation(sourceId: string): Promise<CitationEntry> {
    const res = await fetch(`${API_BASE}/citations/${encodeURIComponent(sourceId)}`, {
        headers: getHeaders(),
    });
    if (!res.ok) handleFetchError(res, "Citation not found");
    return res.json();
}

export async function fetchDocuments(): Promise<DocumentMetadata[]> {
    const res = await fetch(`${API_BASE}/documents`, {
        headers: getHeaders(),
    });
    if (!res.ok) handleFetchError(res, "Failed to load documents");
    const data = await res.json();
    return data.documents;
}

export async function fetchPresets(): Promise<Record<string, PresetInfo>> {
    const res = await fetch(`${API_BASE}/constraints/presets`, {
        headers: getHeaders(),
    });
    if (!res.ok) handleFetchError(res, "Failed to load presets");
    const data = await res.json();
    return data.presets;
}

export async function generate(request: GenerateRequest): Promise<GenerateResponse> {
    const res = await fetch(`${API_BASE}/generate`, {
        method: "POST",
        headers: getHeaders({ "Content-Type": "application/json" }),
        body: JSON.stringify(request),
    });
    if (!res.ok) handleFetchError(res, "Generation failed");
    return res.json();
}

// --- SSE Streaming ---

export function generateStream(
    request: GenerateRequest,
    onEvent: (event: AgentEvent) => void,
    onError: (error: Error) => void,
    onComplete: () => void,
): AbortController {
    const controller = new AbortController();

    (async () => {
        try {
            const res = await fetch(`${API_BASE}/generate/stream`, {
                method: "POST",
                headers: getHeaders({ "Content-Type": "application/json" }),
                body: JSON.stringify(request),
                signal: controller.signal,
            });

            if (!res.ok) {
                handleFetchError(res, "Stream failed");
            }

            const reader = res.body?.getReader();
            if (!reader) throw new Error("Connection lost. Please try again.");

            const decoder = new TextDecoder();
            let buffer = "";

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split("\n");
                buffer = lines.pop() || "";

                for (const line of lines) {
                    if (line.startsWith("data: ")) {
                        try {
                            const eventData = JSON.parse(line.slice(6));
                            onEvent(eventData as AgentEvent);
                        } catch {
                            // Skip malformed SSE frames
                        }
                    }
                }
            }

            onComplete();
        } catch (err) {
            if (err instanceof DOMException && err.name === "AbortError") return;
            onError(err instanceof Error ? err : new Error("An unexpected error occurred."));
        }
    })();

    return controller;
}
