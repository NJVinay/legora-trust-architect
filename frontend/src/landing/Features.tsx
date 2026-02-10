import { motion } from 'framer-motion';
import { useInView } from 'framer-motion';
import { useRef } from 'react';

const features = [
    {
        icon: '⚡',
        title: 'Review faster',
        desc: 'AI-powered document review that surfaces risks, missing clauses, and compliance gaps in seconds — not hours.',
    },
    {
        icon: '✍',
        title: 'Draft smarter',
        desc: 'Intelligent drafting assistance that generates legally precise clauses with built-in citation tracking and constraint validation.',
    },
    {
        icon: '🔍',
        title: 'Research deeper',
        desc: 'Enhanced legal research across your entire document corpus with semantic search and source-linked citations you can trust.',
    },
];

const cardVariants = {
    hidden: { opacity: 0, y: 30 },
    visible: (i: number) => ({
        opacity: 1,
        y: 0,
        transition: {
            delay: 0.15 * i,
            duration: 0.7,
            ease: [0.16, 1, 0.3, 1] as any,
        },
    }),
};

export default function Features() {
    const ref = useRef(null);
    const isInView = useInView(ref, { once: true, margin: '-80px' });

    return (
        <section className="landing-features" id="features">
            <div className="landing-container" ref={ref}>
                <motion.div
                    className="landing-features__header"
                    initial={{ opacity: 0, y: 20 }}
                    animate={isInView ? { opacity: 1, y: 0 } : {}}
                    transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] as any }}
                >
                    <p className="landing-features__label">Capabilities</p>
                    <h2 className="landing-features__heading">
                        Built for how lawyers
                        <br />
                        actually work
                    </h2>
                </motion.div>

                <div className="landing-features__grid">
                    {features.map((f, i) => (
                        <motion.div
                            key={f.title}
                            className="landing-feature-card"
                            variants={cardVariants}
                            initial="hidden"
                            animate={isInView ? 'visible' : 'hidden'}
                            custom={i}
                        >
                            <div className="landing-feature-card__icon">{f.icon}</div>
                            <h3 className="landing-feature-card__title">{f.title}</h3>
                            <p className="landing-feature-card__desc">{f.desc}</p>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
}
