import { motion } from 'framer-motion';
import { useInView } from 'framer-motion';
import { useRef } from 'react';

const badges = [
    { icon: '🛡️', label: 'ISO 27001\nCertified' },
    { icon: '🔒', label: 'SOC 2\nType II' },
    { icon: '🇪🇺', label: 'GDPR\nCompliant' },
    { icon: '⚖️', label: 'Legal Tech\nVerified' },
];

const logos = [
    'Baker & Sterling',
    'Lexington Partners',
    'Ashworth Legal',
    'Meridian Law',
    'Clarke & Associates',
];

const testimonials = [
    {
        quote: 'Legora has transformed how we approach contract review. What used to take our team days now takes hours — with better accuracy.',
        name: 'Sarah Chen',
        role: 'Partner, Baker & Sterling LLP',
        initials: 'SC',
        stars: 5,
    },
    {
        quote: 'The neuro-symbolic validation gives us confidence that no critical clauses are missed. It\'s like having a senior associate checking every line.',
        name: 'James Whitfield',
        role: 'Head of Legal Ops, Meridian Law',
        initials: 'JW',
        stars: 5,
    },
    {
        quote: 'Finally, an AI tool that cites its sources. The transparency in how it reasons through legal constraints is exactly what our compliance team needed.',
        name: 'Dr. Priya Nair',
        role: 'Chief Compliance Officer, FinServ Global',
        initials: 'PN',
        stars: 5,
    },
];

export default function TrustIndicators() {
    const ref = useRef(null);
    const isInView = useInView(ref, { once: true, margin: '-80px' });

    return (
        <section className="landing-trust" id="trust" ref={ref}>
            <div className="landing-container">
                <motion.div
                    className="landing-trust__header"
                    initial={{ opacity: 0, y: 20 }}
                    animate={isInView ? { opacity: 1, y: 0 } : {}}
                    transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] as any }}
                >
                    <p className="landing-trust__label">Trust & Security</p>
                    <h2 className="landing-trust__heading">
                        Enterprise-grade security,
                        <br />
                        built from day one
                    </h2>
                </motion.div>

                {/* Certification Badges */}
                <motion.div
                    className="landing-trust__badges"
                    initial={{ opacity: 0, y: 20 }}
                    animate={isInView ? { opacity: 1, y: 0 } : {}}
                    transition={{ duration: 0.7, delay: 0.15, ease: [0.16, 1, 0.3, 1] as any }}
                >
                    {badges.map((b) => (
                        <div key={b.label} className="landing-trust__badge">
                            <div className="landing-trust__badge-icon">{b.icon}</div>
                            <span className="landing-trust__badge-label">
                                {b.label.split('\n').map((line, i) => (
                                    <span key={i}>
                                        {line}
                                        {i === 0 && <br />}
                                    </span>
                                ))}
                            </span>
                        </div>
                    ))}
                </motion.div>

                {/* Client Logos */}
                <motion.div
                    className="landing-trust__logos"
                    initial={{ opacity: 0 }}
                    animate={isInView ? { opacity: 0.4 } : {}}
                    transition={{ duration: 0.8, delay: 0.3 }}
                >
                    {logos.map((name) => (
                        <span key={name} className="landing-trust__logo">
                            {name}
                        </span>
                    ))}
                </motion.div>

                {/* Testimonials */}
                <div className="landing-trust__testimonials">
                    {testimonials.map((t, i) => (
                        <motion.div
                            key={t.name}
                            className="landing-testimonial"
                            initial={{ opacity: 0, y: 20 }}
                            animate={isInView ? { opacity: 1, y: 0 } : {}}
                            transition={{
                                duration: 0.7,
                                delay: 0.4 + i * 0.12,
                                ease: [0.16, 1, 0.3, 1] as any,
                            }}
                        >
                            <div className="landing-testimonial__stars">
                                {'★'.repeat(t.stars)}
                            </div>
                            <p className="landing-testimonial__quote">"{t.quote}"</p>
                            <div className="landing-testimonial__author">
                                <div className="landing-testimonial__avatar">{t.initials}</div>
                                <div>
                                    <div className="landing-testimonial__name">{t.name}</div>
                                    <div className="landing-testimonial__role">{t.role}</div>
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </div>
            </div>
        </section>
    );
}
