export function init() {
    // tab swithcing logic
    document.querySelectorAll('.tab-btn').forEach(button => {
        button.addEventListener('click', () => {
            console.log('Clicked:', button);
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');
            document.querySelectorAll('.tab-panel').forEach(panel => {
                panel.classList.remove('active');
                console.log('Hiding panel:', panel.id);
            });
        const tabPanelId = button.getAttribute('data-tab');
        const tabPanel = document.getElementById(tabPanelId);
        if (tabPanel) {
            tabPanel.classList.add('active');
            console.log('Showing panel:', tabPanelId);
        } else {
            console.error(`Tab panel with id "${tabPanelId}" not found.`);
        }
        });
    });
}