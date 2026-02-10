import { useState, useEffect, useRef } from "react";
import type { AgentEvent, AgentState } from "../types";

interface Props {
    events: AgentEvent[];
    isRunning: boolean;
}

const STATE_CONFIG: Record<
    AgentState,
    { icon: string; color: string; bg: string; label: string }
> = {
    initializing: {
        icon: "⚙️",
        color: "text-surface-500",
        bg: "bg-surface-100",
        label: "Initializing",
    },
    retrieving: {
        icon: "🔍",
        color: "text-primary-600",
        bg: "bg-primary-50",
        label: "Retrieving Sources",
    },
    drafting: {
        icon: "✍️",
        color: "text-primary-700",
        bg: "bg-primary-50",
        label: "Drafting",
    },
    validating: {
        icon: "🔎",
        color: "text-warning-600",
        bg: "bg-warning-50",
        label: "Validating",
    },
    violation_found: {
        icon: "❌",
        color: "text-danger-600",
        bg: "bg-danger-50",
        label: "Violation Found",
    },
    correcting: {
        icon: "🔄",
        color: "text-warning-600",
        bg: "bg-warning-50",
        label: "Auto-Correcting",
    },
    finalizing: {
        icon: "✅",
        color: "text-accent-600",
        bg: "bg-accent-50",
        label: "Finalizing",
    },
    complete: {
        icon: "🎯",
        color: "text-accent-700",
        bg: "bg-accent-50",
        label: "Complete",
    },
    error: {
        icon: "⚠️",
        color: "text-danger-600",
        bg: "bg-danger-50",
        label: "Error",
    },
};

export default function AgentStateVisualizer({ events, isRunning }: Props) {
    const scrollRef = useRef<HTMLDivElement>(null);
    const [expandedIdx, setExpandedIdx] = useState<number | null>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [events]);

    const currentState = events.length > 0 ? events[events.length - 1].state : null;

    return (
        <div className="rounded-2xl border border-surface-200 bg-white overflow-hidden h-full flex flex-col">
            {/* Header */}
            <div className="flex items-center gap-3 px-5 py-4 border-b border-surface-200">
                <div className="relative flex h-3 w-3">
                    {isRunning && (
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent-400 opacity-75" />
                    )}
                    <span
                        className={`relative inline-flex rounded-full h-3 w-3 ${isRunning ? "bg-accent-500" : currentState === "error" ? "bg-danger-500" : "bg-surface-300"
                            }`}
                    />
                </div>
                <h3 className="text-sm font-semibold text-surface-700 tracking-wide uppercase">
                    Agent Brain
                </h3>
                {currentState && (
                    <span
                        className={`ml-auto text-xs px-3 py-1 rounded-full font-medium ${STATE_CONFIG[currentState].bg
                            } ${STATE_CONFIG[currentState].color}`}
                    >
                        {STATE_CONFIG[currentState].label}
                    </span>
                )}
            </div>

            {/* Event Timeline */}
            <div
                ref={scrollRef}
                className="max-h-80 overflow-y-auto p-4 space-y-2 scrollbar-thin flex-1"
            >
                {events.length === 0 && !isRunning && (
                    <p className="text-surface-400 text-sm text-center py-8">
                        Submit a prompt to see the agent's thought process...
                    </p>
                )}

                {events.map((event, idx) => {
                    const config = STATE_CONFIG[event.state];
                    const hasData = event.data && Object.keys(event.data).length > 0;

                    const renderExpandedData = (): React.ReactNode => {
                        if (!hasData || expandedIdx !== idx) return null;
                        return (
                            <pre className="mt-2 text-xs text-surface-600 bg-surface-50 rounded-lg p-3 overflow-x-auto border border-surface-100">
                                {JSON.stringify(event.data, null, 2)}
                            </pre>
                        );
                    };

                    const renderViolations = (): React.ReactNode => {
                        if (event.state !== "violation_found") return null;
                        if (!event.data?.violations || !Array.isArray(event.data.violations)) return null;
                        const violations = event.data.violations as Array<{ severity: string; message: string }>;
                        return (
                            <div className="mt-2 space-y-1">
                                {violations.map((v, vi) => (
                                    <div
                                        key={vi}
                                        className="flex items-center gap-2 text-xs text-danger-700 bg-danger-50 px-2 py-1 rounded border border-danger-100"
                                    >
                                        <span
                                            className={`font-bold uppercase ${v.severity === "critical"
                                                ? "text-danger-600"
                                                : "text-warning-600"
                                                }`}
                                        >
                                            {v.severity}
                                        </span>
                                        <span className="text-surface-600">{v.message}</span>
                                    </div>
                                ))}
                            </div>
                        );
                    };

                    return (
                        <div
                            key={idx}
                            className={`flex items-start gap-3 px-3 py-2 rounded-lg transition-all
                ${idx === events.length - 1 && isRunning ? config.bg : "hover:bg-surface-50"}
                cursor-pointer`}
                            onClick={() => hasData && setExpandedIdx(expandedIdx === idx ? null : idx)}
                        >
                            {/* Timeline dot */}
                            <div className="flex flex-col items-center pt-1">
                                <span className="text-base">{config.icon}</span>
                                {idx < events.length - 1 && (
                                    <div className="w-px h-4 bg-surface-200 mt-1" />
                                )}
                            </div>

                            {/* Content */}
                            <div className="flex-1 min-w-0">
                                <p className={`text-sm ${config.color} font-medium`}>{event.message}</p>
                                {renderExpandedData()}
                                {renderViolations()}
                            </div>

                            {/* Timestamp */}
                            <span className="text-[10px] text-surface-400 shrink-0 pt-1">
                                {new Date(event.timestamp * 1000).toLocaleTimeString()}
                            </span>
                        </div>
                    );
                })}

                {/* Pulsing cursor when running */}
                {isRunning && (
                    <div className="flex items-center gap-3 px-3 py-2">
                        <div className="flex gap-1">
                            <span className="animate-bounce h-1.5 w-1.5 rounded-full bg-primary-400 [animation-delay:-0.3s]" />
                            <span className="animate-bounce h-1.5 w-1.5 rounded-full bg-primary-400 [animation-delay:-0.15s]" />
                            <span className="animate-bounce h-1.5 w-1.5 rounded-full bg-primary-400" />
                        </div>
                        <span className="text-xs text-surface-400">Processing...</span>
                    </div>
                )}
            </div>
        </div>
    );
}
