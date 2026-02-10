import { useState, useCallback, useRef } from "react";
import type { AgentEvent, AgentOutput, ValidationResult } from "./types";
import { generateStream } from "./api";
import AgentStateVisualizer from "./components/AgentStateVisualizer";
import ResultRenderer from "./components/ResultRenderer";
import "./App.css";

const PRESETS = [
  { value: "dpa", label: "Data Processing Agreement (DPA)", icon: "🔒" },
  { value: "msa", label: "Master Services Agreement (MSA)", icon: "📋" },
  { value: "privacy", label: "Privacy Policy Review", icon: "🛡️" },
];

const EXAMPLE_PROMPTS: Record<string, string> = {
  dpa: "Review this Data Processing Agreement for GDPR compliance. Check liability caps, breach notification timelines, sub-processor approval requirements, and data deletion obligations.",
  msa: "Analyze this Master Services Agreement. Verify liability limits, check for non-compete clauses, review termination terms, and ensure proper governing law is set.",
  privacy: "Review this Privacy Policy for completeness. Check data collection practices, legal bases for processing, data retention periods, and user rights provisions.",
};

export default function App() {
  const [prompt, setPrompt] = useState("");
  const [preset, setPreset] = useState("dpa");
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const [output, setOutput] = useState<AgentOutput | null>(null);
  const [validation, setValidation] = useState<ValidationResult | null>(null);
  const [totalAttempts, setTotalAttempts] = useState(0);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const controllerRef = useRef<AbortController | null>(null);

  const handleSubmit = useCallback(() => {
    if (!prompt.trim() || isRunning) return;

    // Reset state
    setEvents([]);
    setOutput(null);
    setValidation(null);
    setTotalAttempts(0);
    setError(null);
    setIsRunning(true);

    controllerRef.current = generateStream(
      {
        prompt: prompt.trim(),
        contract_type: "Data Processing Agreement",
        jurisdiction: "European Union",
        preset,
      },
      // onEvent
      (event) => {
        setEvents((prev) => [...prev, event]);

        // Capture final output from the "complete" event
        if (event.state === "complete" && event.data?.output) {
          setOutput(event.data.output as unknown as AgentOutput);
          setValidation(
            event.data.validation as unknown as ValidationResult
          );
          setTotalAttempts(
            (event.data.total_attempts as number) || 1
          );
        }
      },
      // onError
      (err) => {
        setError(err.message);
        setIsRunning(false);
      },
      // onComplete
      () => {
        setIsRunning(false);
      }
    );
  }, [prompt, preset, isRunning]);

  const handleStop = useCallback(() => {
    controllerRef.current?.abort();
    setIsRunning(false);
  }, []);

  const handleExamplePrompt = useCallback(() => {
    setPrompt(EXAMPLE_PROMPTS[preset] || EXAMPLE_PROMPTS.dpa);
  }, [preset]);

  return (
    <div className="min-h-screen bg-cream-100 font-body text-surface-900 selection:bg-primary-100 selection:text-primary-900">
      {/* Top Bar */}
      <header className="border-b border-surface-200 bg-cream-100/90 backdrop-blur-xl sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 rounded-xl bg-primary-600 flex items-center justify-center text-white shadow-md shadow-primary-600/20">
              <span className="font-display font-bold text-lg">L</span>
            </div>
            <div>
              <h1 className="text-xl font-display text-surface-900 tracking-tight">
                Legora <span className="text-surface-500 font-body text-sm font-normal tracking-wide ml-1">Trust-Architect</span>
              </h1>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full bg-white border border-surface-200 shadow-sm">
              <span className="w-2 h-2 rounded-full bg-accent-500 animate-pulse"></span>
              <span className="text-xs text-surface-600 font-medium uppercase tracking-wider">System Online</span>
            </div>
            <span className="text-xs text-surface-400 font-mono">
              v0.1.0
            </span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-10">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Left Column: Controls */}
          <div className="lg:col-span-4 space-y-6">
            {/* Preset Selector */}
            <div className="rounded-3xl border border-surface-200 bg-white p-6 shadow-sm">
              <h3 className="text-xs font-bold text-surface-400 uppercase tracking-widest mb-4 ml-1">
                Constraint Profile
              </h3>
              <div className="space-y-2">
                {PRESETS.map((p) => (
                  <button
                    key={p.value}
                    className={`w-full flex items-center gap-4 px-4 py-4 rounded-2xl text-sm text-left transition-all duration-300 border
                      ${preset === p.value
                        ? "bg-primary-50 text-primary-700 border-primary-200 shadow-sm"
                        : "bg-surface-50 text-surface-600 border-transparent hover:bg-surface-100 hover:text-surface-900"
                      }`}
                    onClick={() => setPreset(p.value)}
                    disabled={isRunning}
                  >
                    <span className="text-xl">{p.icon}</span>
                    <span className="font-medium">{p.label}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Agent Brain */}
            {/* Note: AgentStateVisualizer might need internal updates for light mode, 
                but for now we wrap it or assume it handles its own styles. 
                If it's transparent, it needs to look good on white. */}
            <div className="bg-white rounded-3xl border border-surface-200 p-6 shadow-sm overflow-hidden">
              <AgentStateVisualizer events={events} isRunning={isRunning} />
            </div>
          </div>

          {/* Right Column: Prompt + Results */}
          <div className="lg:col-span-8 space-y-6">
            {/* Prompt Input */}
            <div className="rounded-3xl border border-surface-200 bg-white p-6 shadow-sm relative overflow-hidden">
              <div className="flex items-center justify-between mb-4 relative z-10">
                <h3 className="text-xs font-bold text-surface-400 uppercase tracking-widest ml-1">
                  Legal Analysis Prompt
                </h3>
                <button
                  onClick={handleExamplePrompt}
                  className="text-xs text-primary-600 hover:text-primary-700 transition-colors flex items-center gap-1 group font-medium"
                  disabled={isRunning}
                >
                  load example <span className="group-hover:translate-x-0.5 transition-transform">→</span>
                </button>
              </div>

              <div className="relative group z-10">
                <div className="absolute -inset-0.5 bg-gradient-to-r from-primary-200 to-accent-200 rounded-2xl opacity-0 group-focus-within:opacity-100 transition duration-500 blur"></div>
                <textarea
                  className="relative w-full bg-surface-50 text-surface-900 rounded-xl border border-surface-200
                    px-5 py-4 text-base leading-relaxed resize-none focus:outline-none focus:border-primary-400/0 focus:bg-white
                     transition-all placeholder-surface-400 shadow-inner min-h-[140px]"
                  placeholder="Describe your legal requirements. Example: Review this DPA for strict GDPR compliance..."
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  disabled={isRunning}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
                      handleSubmit();
                    }
                  }}
                />
              </div>
              <div className="flex items-center justify-between mt-4 pl-1 relative z-10">
                <span className="text-xs text-surface-400 font-medium">
                  <span className="px-1.5 py-0.5 rounded bg-surface-100 border border-surface-200 text-surface-500 mr-2">⌘ + ↵</span>
                  to submit
                </span>
                <div className="flex gap-3">
                  {isRunning ? (
                    <button
                      onClick={handleStop}
                      className="px-6 py-2.5 rounded-full text-sm font-semibold
                        bg-danger-50 text-danger-600 border border-danger-100
                        hover:bg-danger-100 transition-all cursor-pointer shadow-sm"
                    >
                      Stop Generation
                    </button>
                  ) : (
                    <button
                      onClick={handleSubmit}
                      disabled={!prompt.trim()}
                      className="px-8 py-2.5 rounded-full text-sm font-semibold
                        bg-surface-900 text-white
                        hover:bg-black hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100
                        transition-all shadow-lg shadow-surface-900/20"
                    >
                      Analyze Contract
                    </button>
                  )}
                </div>
              </div>
            </div>

            {/* Error Display */}
            {error && (
              <div className="rounded-2xl border border-danger-200 bg-danger-50 p-5 animate-in fade-in slide-in-from-bottom-2">
                <div className="flex gap-3">
                  <span className="text-xl">⚠️</span>
                  <div>
                    <h4 className="text-sm font-bold text-danger-700 mb-1">Analysis Interrupted</h4>
                    <p className="text-sm text-danger-600/80">{error}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Results */}
            {/* ResultRenderer needs to support light mode or we wrap it in a container. 
                Assuming ResultRenderer is reasonably styled or we might need to adjust it later. */}
            <ResultRenderer
              output={output}
              validation={validation}
              totalAttempts={totalAttempts}
            />

            {/* Empty State */}
            {!output && !isRunning && !error && (
              <div className="rounded-3xl border border-dashed border-surface-200 bg-surface-50/50 p-12 text-center h-[400px] flex flex-col items-center justify-center">
                <div className="w-16 h-16 rounded-2xl bg-white flex items-center justify-center mb-6 text-3xl shadow-sm border border-surface-100">
                  ⚖️
                </div>
                <h3 className="text-2xl font-display text-surface-800 mb-3">
                  Ready to Architect
                </h3>
                <p className="text-surface-500 max-w-md mx-auto leading-relaxed">
                  Select a constraint profile, enter your legal analysis prompt,
                  and watch the neuro-symbolic agent draft and validate in real-time.
                </p>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-surface-200 mt-12 bg-white/50 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-6 py-8 flex md:items-center justify-between flex-col md:flex-row gap-4">
          <div>
            <p className="text-sm text-surface-600 font-medium">
              Legora Trust-Architect
            </p>
            <p className="text-xs text-surface-400 mt-1">
              Neuro-Symbolic Legal AI Prototype
            </p>
          </div>
          <div className="text-right">
            <p className="text-xs text-surface-400">
              Powered by <span className="text-surface-600">FastAPI</span> + <span className="text-surface-600">React</span> + <span className="text-surface-600">Azure OpenAI</span>
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
