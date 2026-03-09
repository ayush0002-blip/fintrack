/**
 * main.js – FinTrack core scripts
 * Handles: theme toggle, flash message dismissal
 */

(function () {
    'use strict';

    /* ─────────────────────────────────────
       THEME MANAGEMENT
    ───────────────────────────────────── */

    const THEME_KEY = 'fintrack-theme';
    const html = document.documentElement;
    const toggleBtn = document.getElementById('theme-toggle');

    /**
     * Apply a theme ('light' | 'dark') to <html data-theme="...">
     * and persist the choice in localStorage.
     */
    function applyTheme(theme) {
        html.setAttribute('data-theme', theme);
        localStorage.setItem(THEME_KEY, theme);
    }

    /** Read saved theme, fall back to OS preference, then 'light'. */
    function loadTheme() {
        const saved = localStorage.getItem(THEME_KEY);
        if (saved === 'dark' || saved === 'light') return saved;
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            return 'dark';
        }
        return 'light';
    }

    // Apply on initial load (before first paint via inline <html data-theme> attr from server is fine too)
    applyTheme(loadTheme());

    // Toggle on button click
    if (toggleBtn) {
        toggleBtn.addEventListener('click', function () {
            const current = html.getAttribute('data-theme');
            applyTheme(current === 'dark' ? 'light' : 'dark');
        });
    }

    /* ─────────────────────────────────────
       FLASH MESSAGE AUTO-DISMISS
    ───────────────────────────────────── */

    const flashes = document.querySelectorAll('.flash');
    flashes.forEach(function (el) {
        setTimeout(function () {
            el.style.opacity = '0';
            el.style.transform = 'translateY(-8px)';
            setTimeout(function () { el.remove(); }, 350);
        }, 4500);
    });

    /* ─────────────────────────────────────
       MOBILE SIDEBAR TOGGLE (optional future use)
    ───────────────────────────────────── */

    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.querySelector('.sidebar');
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function () {
            sidebar.classList.toggle('sidebar--open');
        });
    }

})();
