/* ==========================================================================
   2. ГЛОБАЛЬНАЯ АНИМАЦИЯ СНОВ (Dream Bubbles на весь экран)
   ========================================================================== */
const canvas = document.getElementById('hero-canvas');
const ctx = canvas.getContext('2d');

let particles = [];
let mouse = { x: null, y: null, radius: 190 };

function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}
resizeCanvas();
window.addEventListener('resize', () => {
    resizeCanvas();
    initBubbles();
});

window.addEventListener('mousemove', function(e) {
    mouse.x = e.clientX;
    mouse.y = e.clientY;
});

window.addEventListener('mouseleave', function() {
    mouse.x = null;
    mouse.y = null;
});

class DreamBubble {
    constructor() {
        this.reset(true);
    }

    reset(initial = false) {
        this.x = Math.random() * canvas.width;
        this.y = initial ? Math.random() * canvas.height : canvas.height + Math.random() * 80;
        this.size = Math.random() * 26 + 8;
        this.speedX = Math.random() * 0.6 - 0.3;
        this.speedY = -(Math.random() * 0.5 + 0.25);
        this.color = Math.random() > 0.5 ? '#06B6D4' : '#7C3AED';
        this.opacity = Math.random() * 0.25 + 0.12;
        this.pulseDirection = Math.random() > 0.5 ? 1 : -1;
    }

    update() {
        this.x += this.speedX;
        this.y += this.speedY;

        if (this.y < -60) {
            this.reset(false);
        }

        this.opacity += 0.003 * this.pulseDirection;
        if (this.opacity > 0.45 || this.opacity < 0.12) {
            this.pulseDirection *= -1;
        }

        if (mouse.x !== null && mouse.y !== null) {
            let dx = mouse.x - this.x;
            let dy = mouse.y - this.y;
            let distance = Math.sqrt(dx * dx + dy * dy);
            if (distance < mouse.radius) {
                let force = (mouse.radius - distance) / mouse.radius;
                let directionX = dx / distance;
                let directionY = dy / distance;
                this.x -= directionX * force * 3.5;
                this.y -= directionY * force * 3.5;
            }
        }
    }

    draw() {
        ctx.save();
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        
        let grad = ctx.createRadialGradient(
            this.x - this.size * 0.3, this.y - this.size * 0.3, this.size * 0.1,
            this.x, this.y, this.size
        );
        grad.addColorStop(0, 'rgba(255, 255, 255, 0.5)');
        grad.addColorStop(0.4, this.color);
        grad.addColorStop(1, 'rgba(0,0,0,0)');

        ctx.fillStyle = grad;
        ctx.globalAlpha = Math.max(0.05, Math.min(0.6, this.opacity));
        ctx.shadowBlur = 12;
        ctx.shadowColor = this.color;
        ctx.fill();
        
        ctx.beginPath();
        ctx.arc(this.x - this.size * 0.3, this.y - this.size * 0.3, this.size * 0.15, 0, Math.PI * 2);
        ctx.fillStyle = '#FFFFFF';
        ctx.globalAlpha = Math.max(0.1, Math.min(0.8, this.opacity * 1.5));
        ctx.fill();
        ctx.restore();
    }
}

function initBubbles() {
    particles = [];
    let count = Math.min(Math.floor(window.innerWidth / 25), 70);
    for (let i = 0; i < count; i++) {
        particles.push(new DreamBubble());
    }
}
initBubbles();

function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (let i = 0; i < particles.length; i++) {
        particles[i].update();
        particles[i].draw();
    }
    requestAnimationFrame(animate);
}
animate();