import { useState } from "react";
import type { CitationEntry } from "../types";

interface Props {
    sourceId: string;
    citation?: CitationEntry;
    onLookup?: (sourceId: string) => void;
}

export default function CitationBadge({ sourceId, citation, onLookup }: Props) {
    const [showPopover, setShowPopover] = useState(false);

    return (
        <span className="relative inline-flex">
            <button
                className="inline-flex items-center gap-1 text-xs font-mono px-2 py-0.5 rounded-full
          bg-primary-900/40 text-primary-300 border border-primary-700/50
          hover:bg-primary-800/60 hover:text-primary-200 transition-all
          cursor-pointer"
                onMouseEnter={() => {
                    setShowPopover(true);
                    if (!citation && onLookup) onLookup(sourceId);
                }}
                onMouseLeave={() => setShowPopover(false)}
                onClick={() => setShowPopover(!showPopover)}
            >
                <svg
                    className="w-3 h-3 opacity-60"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                >
                    <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"
                    />
                </svg>
                {sourceId}
            </button>

            {/* Popover */}
            {showPopover && citation && (
                <div
                    className="absolute z-50 bottom-full left-0 mb-2 w-80
            bg-surface-800 border border-surface-600 rounded-xl shadow-2xl
            p-4 text-sm animate-in fade-in slide-in-from-bottom-2 duration-200"
                >
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-xs font-mono text-primary-400 bg-primary-900/30 px-2 py-0.5 rounded">
                            {citation.source_id}
                        </span>
                        <span className="text-xs text-surface-400">{citation.document_name}</span>
                    </div>
                    <p className="text-xs text-surface-300 mb-2 font-medium">
                        § {citation.section_heading}
                    </p>
                    <p className="text-xs text-surface-200 leading-relaxed line-clamp-4">
                        {citation.text}
                    </p>
                    <div className="absolute -bottom-1.5 left-6 w-3 h-3 bg-surface-800 border-r border-b border-surface-600 rotate-45" />
                </div>
            )}
        </span>
    );
}
