import { motion } from 'framer-motion';
import { useInView } from 'framer-motion';
import { useRef } from 'react';

import { useNavigate } from 'react-router-dom';

export default function CtaSection() {
    const navigate = useNavigate();
    const ref = useRef(null);
    const isInView = useInView(ref, { once: true, margin: '-80px' });

    return (
        <section className="landing-cta" id="contact" ref={ref}>
            <div className="landing-container">
                <motion.h2
                    className="landing-cta__title"
                    initial={{ opacity: 0, y: 30 }}
                    animate={isInView ? { opacity: 1, y: 0 } : {}}
                    transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] as any }}
                >
                    Ready to work
                    <br />
                    <em>without limits?</em>
                </motion.h2>

                <motion.p
                    className="landing-cta__subtitle"
                    initial={{ opacity: 0, y: 20 }}
                    animate={isInView ? { opacity: 1, y: 0 } : {}}
                    transition={{ duration: 0.7, delay: 0.15, ease: [0.16, 1, 0.3, 1] as any }}
                >
                    Join forward-thinking law firms already using Legora to
                    deliver faster, more accurate legal work.
                </motion.p>

                <motion.div
                    className="landing-hero__actions"
                    initial={{ opacity: 0, y: 20 }}
                    animate={isInView ? { opacity: 1, y: 0 } : {}}
                    transition={{ duration: 0.7, delay: 0.3, ease: [0.16, 1, 0.3, 1] as any }}
                >
                    <button
                        className="landing-btn landing-btn--primary"
                        onClick={() => navigate('/app')}
                    >
                        Launch App →
                    </button>
                    <button className="landing-btn landing-btn--ghost">
                        Talk to sales
                    </button>
                </motion.div>
            </div>
        </section>
    );
}
