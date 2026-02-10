export default function Footer() {
    const currentYear = new Date().getFullYear();

    return (
        <footer className="landing-footer">
            <div className="landing-container">
                <div className="landing-footer__grid">
                    {/* Brand */}
                    <div className="landing-footer__brand">
                        <div className="landing-footer__logo">
                            <span className="landing-nav__logo-icon" style={{ width: 28, height: 28, fontSize: '0.75rem', borderRadius: 7 }}>
                                L
                            </span>
                            Legora
                        </div>
                        <p className="landing-footer__tagline">
                            Trust-first legal AI. Generate, validate, and verify
                            legal documents with neuro-symbolic precision.
                        </p>
                    </div>

                    {/* Product */}
                    <div>
                        <h4 className="landing-footer__col-title">Product</h4>
                        <ul className="landing-footer__links">
                            <li><a className="landing-footer__link" href="#features">Features</a></li>
                            <li><a className="landing-footer__link" href="#product">How it works</a></li>
                            <li><a className="landing-footer__link" href="#trust">Security</a></li>
                            <li><a className="landing-footer__link" href="#">Pricing</a></li>
                        </ul>
                    </div>

                    {/* Company */}
                    <div>
                        <h4 className="landing-footer__col-title">Company</h4>
                        <ul className="landing-footer__links">
                            <li><a className="landing-footer__link" href="#">About</a></li>
                            <li><a className="landing-footer__link" href="#">Careers</a></li>
                            <li><a className="landing-footer__link" href="#">Blog</a></li>
                            <li><a className="landing-footer__link" href="#contact">Contact</a></li>
                        </ul>
                    </div>

                    {/* Legal */}
                    <div>
                        <h4 className="landing-footer__col-title">Legal</h4>
                        <ul className="landing-footer__links">
                            <li><a className="landing-footer__link" href="#">Privacy Policy</a></li>
                            <li><a className="landing-footer__link" href="#">Terms of Service</a></li>
                            <li><a className="landing-footer__link" href="#">Cookie Policy</a></li>
                            <li><a className="landing-footer__link" href="#">DPA</a></li>
                        </ul>
                    </div>
                </div>

                {/* Bottom */}
                <div className="landing-footer__bottom">
                    <span className="landing-footer__copy">
                        © {currentYear} Legora. All rights reserved.
                    </span>
                    <div className="landing-footer__bottom-links">
                        <a className="landing-footer__bottom-link" href="#">LinkedIn</a>
                        <a className="landing-footer__bottom-link" href="#">Twitter</a>
                        <a className="landing-footer__bottom-link" href="https://github.com" target="_blank" rel="noopener noreferrer">GitHub</a>
                    </div>
                </div>
            </div>
        </footer>
    );
}
