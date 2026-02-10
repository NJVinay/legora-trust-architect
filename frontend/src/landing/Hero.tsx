import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';

const fadeUp = {
    hidden: { opacity: 0, y: 30 },
    visible: (i: number) => ({
        opacity: 1,
        y: 0,
        transition: { delay: 0.15 * i, duration: 0.8, ease: [0.16, 1, 0.3, 1] as any },
    }),
};

export default function Hero() {
    const navigate = useNavigate();

    return (
        <section className="landing-hero">
            <div className="landing-container" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <motion.div
                    className="landing-hero__badge"
                    variants={fadeUp}
                    initial="hidden"
                    animate="visible"
                    custom={0}
                >
                    <span>✦</span> Trust-First Legal AI
                </motion.div>

                <motion.h1
                    className="landing-hero__title"
                    variants={fadeUp}
                    initial="hidden"
                    animate="visible"
                    custom={1}
                >
                    Legal work,
                    <br />
                    without <em>limits.</em>
                </motion.h1>

                <motion.p
                    className="landing-hero__subtitle"
                    variants={fadeUp}
                    initial="hidden"
                    animate="visible"
                    custom={2}
                >
                    Collaborative AI built for lawyers. Draft, review, and validate
                    legal documents with confidence — powered by neuro-symbolic
                    validation that ensures every clause meets your standards.
                </motion.p>

                <motion.div
                    className="landing-hero__actions"
                    variants={fadeUp}
                    initial="hidden"
                    animate="visible"
                    custom={3}
                >
                    <button
                        className="landing-btn landing-btn--primary"
                        onClick={() => navigate('/app')}
                    >
                        Launch App →
                    </button>
                    <button
                        className="landing-btn landing-btn--ghost"
                        onClick={() =>
                            document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' })
                        }
                    >
                        See how it works
                    </button>
                </motion.div>
            </div>
        </section>
    );
}
