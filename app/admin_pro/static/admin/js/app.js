/**
 * Flask Admin Pro - Main App JavaScript
 */
const ThemeManager = {
    currentTheme: 'blue',
    isDarkMode: false,
    init() {
        const savedTheme = localStorage.getItem('admin-theme');
        if (savedTheme) this.currentTheme = savedTheme;
        this.applyTheme();
    },
    setTheme(theme) {
        if (theme === 'dark') {
            this.isDarkMode = !this.isDarkMode;
            localStorage.setItem('admin-dark-mode', this.isDarkMode);
        } else {
            this.currentTheme = theme;
            localStorage.setItem('admin-theme', theme);
        }
        this.applyTheme();
    },
    applyTheme() {
        document.body.classList.remove('theme-blue', 'theme-purple', 'theme-green', 'theme-orange', 'theme-red', 'dark-mode');
        if (this.isDarkMode) document.body.classList.add('dark-mode');
        else document.body.classList.add(`theme-${this.currentTheme}`);
    }
};
document.addEventListener('DOMContentLoaded', () => ThemeManager.init());
window.ThemeManager = ThemeManager;
