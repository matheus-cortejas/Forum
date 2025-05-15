import { initNavbar } from './navbar.js';
import { initPageTransitions } from './page-transitions.js';
import { initFooter } from './footer.js';
import { initMobileNavbar } from './mobile-nav.js';

export function initAll() {
    initNavbar();
    initPageTransitions();
    initFooter();
    initMobileNavbar();
}

document.addEventListener('DOMContentLoaded', initAll);
