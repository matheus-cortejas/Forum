document.addEventListener('DOMContentLoaded', function() {
    const themeToggle = document.getElementById('theme-toggle');
    const languageToggle = document.getElementById('language-toggle');

    // Theme Toggle
    themeToggle.addEventListener('click', function() {
        document.body.classList.toggle('dark-theme');
        const isDark = document.body.classList.contains('dark-theme');
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
        themeToggle.textContent = isDark ? '☀️ Light' : '🌙 Dark';
    });

    // Language Toggle
    languageToggle.addEventListener('click', function() {
        const currentLang = languageToggle.textContent.includes('EN') ? 'pt' : 'en';
        localStorage.setItem('language', currentLang);
        languageToggle.textContent = currentLang === 'en' ? '🌐 EN' : '🌐 PT';
    });

    // Initialize from localStorage
    const savedTheme = localStorage.getItem('theme') || 'light';
    const savedLang = localStorage.getItem('language') || 'en';

    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
        themeToggle.textContent = '☀️ Light';
    }

    languageToggle.textContent = savedLang === 'en' ? '🌐 EN' : '🌐 PT';
});
