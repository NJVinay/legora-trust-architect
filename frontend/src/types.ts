/**
 * TypeScript types matching the backend Pydantic models.
 */

// --- Agent States ---
export type AgentState =
    | "initializing"
    | "retrieving"
    | "drafting"
    | "validating"
    | "violation_found"
    | "correcting"
    | "finalizing"
    | "complete"
    | "error";

// --- Agent Events (from SSE) ---
export interface AgentEvent {
    state: AgentState;
    message: string;
    data?: Record<string, unknown>;
    timestamp: number;
}

// --- Generated Output ---
export interface GeneratedCitation {
    source_id: string;
    relevance: string;
}

export interface GeneratedClause {
    title: string;
    text: string;
    citations: GeneratedCitation[];
    risk_level: "low" | "medium" | "high" | "critical";
    reasoning: string;
}

export interface AgentOutput {
    clauses: GeneratedClause[];
    summary: string;
    governing_jurisdiction: string;
    confidence_score: number;
}

// --- Validation ---
export interface ValidationViolation {
    field: string;
    message: string;
    severity: "low" | "medium" | "high" | "critical";
    suggestion: string;
}

export interface ValidationResult {
    is_valid: boolean;
    violations: ValidationViolation[];
    attempt_number: number;
}

// --- API Request/Response ---
export interface GenerateRequest {
    prompt: string;
    contract_type: string;
    jurisdiction: string;
    preset?: string;
}

export interface GenerateResponse {
    success: boolean;
    total_attempts: number;
    output?: AgentOutput;
    validation?: ValidationResult;
    error?: string;
}

// --- Citation Index ---
export interface CitationEntry {
    source_id: string;
    text: string;
    document_name: string;
    section_heading: string;
}

// --- Document Metadata ---
export interface DocumentMetadata {
    filename: string;
    title: string;
    total_citations: number;
    sections: string[];
}

// --- Constraint Presets ---
export interface PresetInfo {
    contract_type: string;
    jurisdiction: string;
    forbidden_clauses_count: number;
    required_citations_count: number;
}
