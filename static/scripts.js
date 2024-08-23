document.addEventListener('DOMContentLoaded', () => {
    const themeToggleButton = document.getElementById('theme-toggle');

    // Load the saved theme from localStorage
    const currentTheme = localStorage.getItem('theme');
    if (currentTheme) {
        document.body.classList.add(currentTheme);
    }

    // Toggle the theme and save the choice in localStorage
    themeToggleButton.addEventListener('click', () => {
        if (document.body.classList.contains('dark-theme')) {
            document.body.classList.remove('dark-theme');
            localStorage.setItem('theme', '');
        } else {
            document.body.classList.add('dark-theme');
            localStorage.setItem('theme', 'dark-theme');
        }
    });
});
