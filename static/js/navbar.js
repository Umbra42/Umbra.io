export function init(navTogglerBtn, navbar) { 
  // toggle navbar small screens
  if (navTogglerBtn) {
      navTogglerBtn.addEventListener('click', () => {
        navbar.classList.toggle('active');
        });
    } else {
        console.warn('Navbar toggler button not found');
    };
    return;
}
