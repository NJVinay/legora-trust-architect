import { useState, useCallback } from "react";
import type { AgentOutput, ValidationResult, CitationEntry } from "../types";
import { fetchCitation } from "../api";
import CitationBadge from "./CitationBadge";

interface Props {
    output: AgentOutput | null;
    validation: ValidationResult | null;
    totalAttempts: number;
}

export default function ResultRenderer({
    output,
    validation,
    totalAttempts,
}: Props) {
    const [citationCache, setCitationCache] = useState<
        Record<string, CitationEntry>
    >({});

    const handleCitationLookup = useCallback(async (sourceId: string) => {
        if (citationCache[sourceId]) return;
        try {
            const citation = await fetchCitation(sourceId);
            setCitationCache((prev) => ({ ...prev, [sourceId]: citation }));
        } catch {
            // Silently fail — citation not found
        }
    }, [citationCache]);

    if (!output) return null;

    const riskColors = {
        low: "text-accent-700 bg-accent-50 border-accent-200",
        medium: "text-warning-700 bg-warning-50 border-warning-200",
        high: "text-danger-700 bg-danger-50 border-danger-200",
        critical: "text-danger-800 bg-danger-100 border-danger-300",
    };

    return (
        <div className="space-y-6">
            {/* Summary Header */}
            <div className="rounded-2xl border border-surface-200 bg-white p-6 shadow-sm">
                <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-surface-900">
                        Analysis Result
                    </h3>
                    <div className="flex items-center gap-3">
                        {/* Confidence Score */}
                        <div className="flex items-center gap-2">
                            <div className="h-2 w-24 rounded-full bg-surface-100 overflow-hidden">
                                <div
                                    className={`h-full rounded-full transition-all duration-1000 ${output.confidence_score >= 0.8
                                        ? "bg-accent-500"
                                        : output.confidence_score >= 0.6
                                            ? "bg-warning-500"
                                            : "bg-danger-500"
                                        }`}
                                    style={{ width: `${output.confidence_score * 100}%` }}
                                />
                            </div>
                            <span className="text-xs text-surface-500 font-mono">
                                {(output.confidence_score * 100).toFixed(0)}%
                            </span>
                        </div>

                        {/* Validation badge */}
                        <span
                            className={`text-xs px-3 py-1 rounded-full font-medium border ${validation?.is_valid
                                ? "text-accent-700 bg-accent-50 border-accent-200"
                                : "text-danger-700 bg-danger-50 border-danger-200"
                                }`}
                        >
                            {validation?.is_valid ? "✅ Verified" : "⚠️ Issues Found"}
                        </span>

                        {/* Attempts */}
                        <span className="text-xs text-surface-400">
                            {totalAttempts} attempt{totalAttempts !== 1 ? "s" : ""}
                        </span>
                    </div>
                </div>

                <p className="text-sm text-surface-600 leading-relaxed">{output.summary}</p>
                <p className="text-xs text-surface-400 mt-2">
                    Jurisdiction: {output.governing_jurisdiction}
                </p>
            </div>

            {/* Clauses */}
            {output.clauses.map((clause, idx) => (
                <div
                    key={idx}
                    className="rounded-2xl border border-surface-200 bg-white overflow-hidden shadow-sm transition-all hover:shadow-md"
                >
                    {/* Clause Header */}
                    <div className="flex items-center justify-between px-6 py-4 border-b border-surface-100 bg-surface-50/50">
                        <h4 className="text-sm font-semibold text-surface-800">
                            {clause.title}
                        </h4>
                        <span
                            className={`text-xs px-2.5 py-1 rounded-full font-medium border ${riskColors[clause.risk_level]
                                }`}
                        >
                            {clause.risk_level.toUpperCase()}
                        </span>
                    </div>

                    {/* Clause Body */}
                    <div className="px-6 py-4">
                        <p className="text-sm text-surface-700 leading-relaxed whitespace-pre-wrap font-serif">
                            {clause.text}
                        </p>

                        {/* Citations */}
                        {clause.citations.length > 0 && (
                            <div className="mt-4 pt-3 border-t border-surface-100">
                                <p className="text-xs text-surface-400 mb-2 uppercase tracking-wider font-medium">
                                    Sources
                                </p>
                                <div className="flex flex-wrap gap-2">
                                    {clause.citations.map((cit, ci) => (
                                        <CitationBadge
                                            key={ci}
                                            sourceId={cit.source_id}
                                            citation={citationCache[cit.source_id]}
                                            onLookup={handleCitationLookup}
                                        />
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Reasoning */}
                        {clause.reasoning && (
                            <div className="mt-3 pt-3 border-t border-surface-100">
                                <p className="text-xs text-surface-500 italic flex gap-2">
                                    <span>💡</span>
                                    <span>{clause.reasoning}</span>
                                </p>
                            </div>
                        )}
                    </div>
                </div>
            ))}

            {/* Validation Violations (if any) */}
            {validation && !validation.is_valid && validation.violations.length > 0 && (
                <div className="rounded-2xl border border-danger-200 bg-danger-50 p-6">
                    <h4 className="text-sm font-bold text-danger-700 mb-3">
                        ⚠️ Remaining Violations
                    </h4>
                    <div className="space-y-2">
                        {validation.violations.map((v, vi) => (
                            <div
                                key={vi}
                                className="flex items-start gap-3 text-xs bg-white/50 border border-danger-100 rounded-lg p-3"
                            >
                                <span
                                    className={`font-bold uppercase shrink-0 ${v.severity === "critical"
                                        ? "text-danger-600"
                                        : v.severity === "high"
                                            ? "text-danger-500"
                                            : "text-warning-600"
                                        }`}
                                >
                                    {v.severity}
                                </span>
                                <div>
                                    <p className="text-surface-700">{v.message}</p>
                                    {v.suggestion && (
                                        <p className="text-surface-500 mt-1 italic">
                                            Fix: {v.suggestion}
                                        </p>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
