// Kart animasyonları
document.addEventListener('DOMContentLoaded', function() {
    // Kart animasyonları
    const cards = document.querySelectorAll('.catalog-card');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    });
    
    cards.forEach(card => observer.observe(card));
});

// Matrix Code Rain Effect (Ana arka plan)
document.addEventListener('DOMContentLoaded', function() {
    const canvas = document.getElementById('matrix-bg');
    const ctx = canvas.getContext('2d');
    
    // Canvas boyutunu ayarla
    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);
    
    // Matrix karakterleri
    const matrix = "ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789@#$%^&*()_+-=[]{}|;:,.<>?";
    const matrixArray = matrix.split("");
    
    const fontSize = 14;
    const columns = canvas.width / fontSize;
    
    // Her sütun için y pozisyonu
    const drops = [];
    for (let x = 0; x < columns; x++) {
        drops[x] = 1;
    }
    
    // Matrix efekti çiz
    function drawMatrix() {
        // Yarı saydam siyah arka plan (trail efekti için)
        ctx.fillStyle = 'rgba(0, 0, 0, 0.04)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Yeşil renk
        ctx.fillStyle = '#0F0';
        ctx.font = fontSize + 'px monospace';
        
        // Her sütun için karakterleri çiz
        for (let i = 0; i < drops.length; i++) {
            // Rastgele karakter seç
            const text = matrixArray[Math.floor(Math.random() * matrixArray.length)];
            
            // Karakteri çiz
            ctx.fillText(text, i * fontSize, drops[i] * fontSize);
            
            // Eğer karakter canvas'ın altına ulaştıysa veya rastgele olarak sıfırla
            if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
                drops[i] = 0;
            }
            
            drops[i]++;
        }
    }
    
    // Animasyon döngüsü - Optimized
    let lastTime = 0;
    const frameRate = 50; // Reduced from 35ms to 50ms
    
    function animate(currentTime) {
        if (currentTime - lastTime < frameRate) {
            requestAnimationFrame(animate);
            return;
        }
        lastTime = currentTime;
        drawMatrix();
        requestAnimationFrame(animate);
    }
    
    requestAnimationFrame(animate);
});

// Mouse takip eden parçacık efekti
document.addEventListener('DOMContentLoaded', function() {
    const canvas = document.createElement('canvas');
    canvas.style.position = 'fixed';
    canvas.style.top = '0';
    canvas.style.left = '0';
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    canvas.style.pointerEvents = 'none';
    canvas.style.zIndex = '9999';
    document.body.appendChild(canvas);
    
    const ctx = canvas.getContext('2d');
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    
    const particles = [];
    let mouseX = 0;
    let mouseY = 0;
    
    class Particle {
        constructor(x, y) {
            this.x = x;
            this.y = y;
            this.vx = (Math.random() - 0.5) * 1.5; // Reduced velocity
            this.vy = (Math.random() - 0.5) * 1.5;
            this.life = 1;
            this.decay = 0.03; // Faster decay
        }
        
        update() {
            this.x += this.vx;
            this.y += this.vy;
            this.life -= this.decay;
        }
        
        draw() {
            ctx.save();
            ctx.globalAlpha = this.life;
            ctx.fillStyle = '#00ff00';
            ctx.beginPath();
            ctx.arc(this.x, this.y, 2, 0, Math.PI * 2);
            ctx.fill();
            ctx.restore();
        }
    }
    
    let lastParticleTime = 0;
    const particleRate = 100; // Reduced particle creation rate
    
    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
        
        const currentTime = Date.now();
        if (currentTime - lastParticleTime > particleRate && Math.random() < 0.3) {
            particles.push(new Particle(mouseX, mouseY));
            lastParticleTime = currentTime;
        }
    });
    
    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        for (let i = particles.length - 1; i >= 0; i--) {
            particles[i].update();
            particles[i].draw();
            
            if (particles[i].life <= 0) {
                particles.splice(i, 1);
            }
        }
        
        requestAnimationFrame(animate);
    }
    
    animate();
    
    window.addEventListener('resize', () => {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    });
});

// Scroll animasyonları
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateX(0)';
        }
    });
}, observerOptions);

document.addEventListener('DOMContentLoaded', function() {
    const cards = document.querySelectorAll('.catalog-card');
    cards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateX(-50px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });
});

// Form submit efekti
document.addEventListener('DOMContentLoaded', function() {
    const submitBtn = document.querySelector('.submit-btn');
    if (submitBtn) {
        submitBtn.addEventListener('click', (e) => {
            // Particle efekti
            createParticleExplosion(e.target);
        });
    }
});

// Particle explosion efekti
function createParticleExplosion(element) {
    const rect = element.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    
    for (let i = 0; i < 20; i++) {
        const particle = document.createElement('div');
        particle.style.position = 'fixed';
        particle.style.left = centerX + 'px';
        particle.style.top = centerY + 'px';
        particle.style.width = '4px';
        particle.style.height = '4px';
        particle.style.background = '#00ff00';
        particle.style.borderRadius = '50%';
        particle.style.pointerEvents = 'none';
        particle.style.zIndex = '10000';
        
        document.body.appendChild(particle);
        
        const angle = (Math.PI * 2 * i) / 20;
        const velocity = 100 + Math.random() * 50;
        const vx = Math.cos(angle) * velocity;
        const vy = Math.sin(angle) * velocity;
        
        let opacity = 1;
        let x = centerX;
        let y = centerY;
        
        function animateParticle() {
            x += vx * 0.016;
            y += vy * 0.016;
            opacity -= 0.02;
            
            particle.style.left = x + 'px';
            particle.style.top = y + 'px';
            particle.style.opacity = opacity;
            
            if (opacity > 0) {
                requestAnimationFrame(animateParticle);
            } else {
                document.body.removeChild(particle);
            }
        }
        
        requestAnimationFrame(animateParticle);
    }
}

// Enhanced particle system
class ParticleSystem {
    constructor() {
        this.particles = [];
        this.canvas = document.createElement('canvas');
        this.canvas.style.position = 'fixed';
        this.canvas.style.top = '0';
        this.canvas.style.left = '0';
        this.canvas.style.width = '100%';
        this.canvas.style.height = '100%';
        this.canvas.style.pointerEvents = 'none';
        this.canvas.style.zIndex = '9998';
        document.body.appendChild(this.canvas);
        
        this.ctx = this.canvas.getContext('2d');
        this.resize();
        this.animate();
        
        window.addEventListener('resize', () => this.resize());
    }
    
    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }
    
    addParticle(x, y) {
        this.particles.push({
            x: x,
            y: y,
            vx: (Math.random() - 0.5) * 4,
            vy: (Math.random() - 0.5) * 4,
            life: 1,
            decay: 0.02,
            size: Math.random() * 3 + 1
        });
    }
    
    animate() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        for (let i = this.particles.length - 1; i >= 0; i--) {
            const p = this.particles[i];
            
            p.x += p.vx;
            p.y += p.vy;
            p.life -= p.decay;
            
            this.ctx.save();
            this.ctx.globalAlpha = p.life;
            this.ctx.fillStyle = '#00ff00';
            this.ctx.beginPath();
            this.ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            this.ctx.fill();
            this.ctx.restore();
            
            if (p.life <= 0) {
                this.particles.splice(i, 1);
            }
        }
        
        requestAnimationFrame(() => this.animate());
    }
}

// Initialize enhanced particle system
document.addEventListener('DOMContentLoaded', function() {
    const particleSystem = new ParticleSystem();
    
    document.addEventListener('mousemove', (e) => {
        if (Math.random() < 0.3) {
            particleSystem.addParticle(e.clientX, e.clientY);
        }
    });
});

// Interactive Terminal Commands
document.addEventListener('DOMContentLoaded', function() {
    const terminal = document.querySelector('.terminal-content');
    if (terminal) {
        const commands = [
            { cmd: 'whoami', output: 'selami_mert_ileri' },
            { cmd: 'ls -la', output: 'drwxr-xr-x projects/\ndrwxr-xr-x skills/\ndrwxr-xr-x contact/' },
            { cmd: 'cat about.txt', output: 'Python Developer | Web Technologies | Cybersecurity Enthusiast' },
            { cmd: 'python --version', output: 'Python 3.9.0' },
            { cmd: 'git status', output: 'On branch main\nYour branch is up to date with origin/main.' }
        ];
        
        let commandIndex = 0;
        const commandInterval = setInterval(() => {
            if (commandIndex < commands.length) {
                const command = commands[commandIndex];
                const line = document.createElement('div');
                line.className = 'terminal-line';
                line.textContent = `$ ${command.cmd}`;
                terminal.appendChild(line);
                
                setTimeout(() => {
                    const output = document.createElement('div');
                    output.className = 'terminal-output';
                    output.textContent = command.output;
                    terminal.appendChild(output);
                }, 500);
                
                commandIndex++;
            } else {
                clearInterval(commandInterval);
            }
        }, 1000);
    }
});



 