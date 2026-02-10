import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

import { useNavigate } from 'react-router-dom';

export default function Navbar() {
    const navigate = useNavigate();
    const [scrolled, setScrolled] = useState(false);
    const [menuOpen, setMenuOpen] = useState(false);

    useEffect(() => {
        const handleScroll = () => setScrolled(window.scrollY > 40);
        window.addEventListener('scroll', handleScroll, { passive: true });
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const scrollTo = (id: string) => {
        document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
        setMenuOpen(false);
    };

    return (
        <motion.nav
            className={`landing-nav ${scrolled ? 'landing-nav--scrolled' : ''}`}
            initial={{ y: -20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] as any }}
        >
            <div className="landing-nav__inner">
                <a href="#" className="landing-nav__logo">
                    <span className="landing-nav__logo-icon">L</span>
                    Legora
                </a>

                <ul className={`landing-nav__links ${menuOpen ? 'landing-nav__links--open' : ''}`}>
                    <li><a className="landing-nav__link" onClick={() => scrollTo('features')}>Features</a></li>
                    <li><a className="landing-nav__link" onClick={() => scrollTo('product')}>Product</a></li>
                    <li><a className="landing-nav__link" onClick={() => scrollTo('trust')}>Trust</a></li>
                    <li><a className="landing-nav__link" onClick={() => scrollTo('contact')}>Contact</a></li>
                </ul>

                <button className="landing-nav__cta" onClick={() => navigate('/app')}>
                    Launch App
                </button>

                <button
                    className="landing-nav__toggle"
                    onClick={() => setMenuOpen(!menuOpen)}
                    aria-label="Toggle menu"
                >
                    {menuOpen ? '✕' : '☰'}
                </button>
            </div>

            <AnimatePresence>
                {menuOpen && (
                    <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        style={{ overflow: 'hidden' }}
                    />
                )}
            </AnimatePresence>
        </motion.nav>
    );
}
