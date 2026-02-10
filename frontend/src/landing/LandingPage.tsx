import './landing.css';
import Navbar from './Navbar';
import Hero from './Hero';
import Features from './Features';
import ProductShowcase from './ProductShowcase';
import TrustIndicators from './TrustIndicators';
import CtaSection from './CtaSection';
import Footer from './Footer';

export default function LandingPage() {
    return (
        <div className="landing-page">
            <Navbar />
            <Hero />
            <Features />
            <ProductShowcase />
            <TrustIndicators />
            <CtaSection />
            <Footer />
        </div>
    );
}
