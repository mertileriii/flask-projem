// Fareyi takip eden turuncu arka plan efekti
const circle = document.querySelector('#mouse-bg .circle');
document.addEventListener('mousemove', function(e) {
    circle.style.left = e.clientX + 'px';
    circle.style.top = e.clientY + 'px';
});

// Kartlar scroll ile süpürülerek gelsin ve her seferinde tekrar animasyon olsun
function revealOnScroll() {
    const cards = document.querySelectorAll('.catalog-card');
    const windowHeight = window.innerHeight;
    cards.forEach(card => {
        const rect = card.getBoundingClientRect();
        if (rect.top < windowHeight - 80 && rect.bottom > 80) {
            card.classList.add('visible');
        } else {
            card.classList.remove('visible');
        }
    });
}
window.addEventListener('scroll', revealOnScroll);
window.addEventListener('load', revealOnScroll); 