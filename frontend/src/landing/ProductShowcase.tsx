import { motion } from 'framer-motion';
import { useInView } from 'framer-motion';
import { useRef } from 'react';

function MockUI({ variant }: { variant: 'review' | 'draft' | 'validate' }) {
    return (
        <div className="landing-showcase__mock-ui">
            <div className="landing-showcase__mock-titlebar">
                <span className="landing-showcase__mock-dot" />
                <span className="landing-showcase__mock-dot" />
                <span className="landing-showcase__mock-dot" />
            </div>
            <div className="landing-showcase__mock-body">
                {variant === 'review' && (
                    <>
                        <div className="landing-showcase__mock-line landing-showcase__mock-line--long" />
                        <div className="landing-showcase__mock-line landing-showcase__mock-line--medium" />
                        <div className="landing-showcase__mock-line landing-showcase__mock-line--long landing-showcase__mock-line--accent" />
                        <div className="landing-showcase__mock-line landing-showcase__mock-line--short" />
                        <div className="landing-showcase__mock-line landing-showcase__mock-line--medium" />
                        <div className="landing-showcase__mock-line landing-showcase__mock-line--long" />
                        <div className="landing-showcase__mock-line landing-showcase__mock-line--medium landing-showcase__mock-line--accent" />
                        <div className="landing-showcase__mock-line landing-showcase__mock-line--short" />
                    </>
                )}
                {variant === 'draft' && (
                    <>
                        <div className="landing-showcase__mock-line landing-showcase__mock-line--short" style={{ background: '#6C8EEF', opacity: 0.3 }} />
                        <div className="landing-showcase__mock-line landing-showcase__mock-line--long" />
                        <div className="landing-showcase__mock-line landing-showcase__mock-line--long" />
                        <div className="landing-showcase__mock-line landing-showcase__mock-line--medium" />
                        <div style={{ height: 12 }} />
                        <div className="landing-showcase__mock-line landing-showcase__mock-line--short" style={{ background: '#6C8EEF', opacity: 0.3 }} />
                        <div className="landing-showcase__mock-line landing-showcase__mock-line--long" />
                        <div className="landing-showcase__mock-line landing-showcase__mock-line--medium" />
                    </>
                )}
                {variant === 'validate' && (
                    <>
                        <div style={{ display: 'flex', gap: 8, marginBottom: 4 }}>
                            <div style={{ width: 16, height: 16, borderRadius: '50%', background: '#27CA40', flexShrink: 0 }} />
                            <div className="landing-showcase__mock-line landing-showcase__mock-line--long" />
                        </div>
                        <div style={{ display: 'flex', gap: 8, marginBottom: 4 }}>
                            <div style={{ width: 16, height: 16, borderRadius: '50%', background: '#27CA40', flexShrink: 0 }} />
                            <div className="landing-showcase__mock-line landing-showcase__mock-line--medium" />
                        </div>
                        <div style={{ display: 'flex', gap: 8, marginBottom: 4 }}>
                            <div style={{ width: 16, height: 16, borderRadius: '50%', background: '#FBBF24', flexShrink: 0 }} />
                            <div className="landing-showcase__mock-line landing-showcase__mock-line--long" />
                        </div>
                        <div style={{ display: 'flex', gap: 8 }}>
                            <div style={{ width: 16, height: 16, borderRadius: '50%', background: '#27CA40', flexShrink: 0 }} />
                            <div className="landing-showcase__mock-line landing-showcase__mock-line--medium" />
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}

const blocks = [
    {
        label: 'Neuro-Symbolic Validation',
        title: 'Every clause verified against hard constraints',
        desc: 'Our dual-layer architecture combines LLM intelligence with deterministic Pydantic constraint checking. No hallucinations slip through — every output is validated against jurisdiction rules, forbidden clauses, and citation requirements.',
        variant: 'validate' as const,
        reverse: false,
    },
    {
        label: 'Intelligent Drafting',
        title: 'Context-aware drafting with citation tracking',
        desc: 'Generate legally precise contract clauses grounded in your source documents. Every generated clause includes traceable citations back to your legal corpus, so you always know the basis for every recommendation.',
        variant: 'draft' as const,
        reverse: true,
    },
    {
        label: 'Real-Time Agent Visualization',
        title: 'Watch the AI think, step by step',
        desc: 'Full transparency into the agent\'s reasoning process. See each state — retrieving, drafting, validating, correcting — streamed in real-time through our live visualization dashboard.',
        variant: 'review' as const,
        reverse: false,
    },
];

export default function ProductShowcase() {
    return (
        <section className="landing-showcase" id="product">
            <div className="landing-container">
                {blocks.map((block, idx) => (
                    <ShowcaseBlock key={idx} {...block} />
                ))}
            </div>
        </section>
    );
}

function ShowcaseBlock({
    label,
    title,
    desc,
    variant,
    reverse,
}: {
    label: string;
    title: string;
    desc: string;
    variant: 'review' | 'draft' | 'validate';
    reverse: boolean;
}) {
    const ref = useRef(null);
    const isInView = useInView(ref, { once: true, margin: '-100px' });

    return (
        <motion.div
            ref={ref}
            className={`landing-showcase__block ${reverse ? 'landing-showcase__block--reverse' : ''}`}
            initial={{ opacity: 0, y: 40 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.8, delay: 0.1, ease: [0.16, 1, 0.3, 1] as any }}
        >
            <div>
                <p className="landing-showcase__label">{label}</p>
                <h3 className="landing-showcase__title">{title}</h3>
                <p className="landing-showcase__desc">{desc}</p>
                <button className="landing-btn landing-btn--dark">
                    Learn more →
                </button>
            </div>
            <div className="landing-showcase__visual">
                <MockUI variant={variant} />
            </div>
        </motion.div>
    );
}
