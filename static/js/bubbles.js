/* ==========================================================================
           2. ИНТЕРАКТИВНАЯ HERO-АНИМАЦИЯ (Dream Bubbles на Canvas)
           ========================================================================== */
        const canvas = document.getElementById('hero-canvas');
        const ctx = canvas.getContext('2d');

        let particles = [];
        let mouse = { x: null, y: null, radius: 180 };

        function resizeCanvas() {
            canvas.width = canvas.parentElement.offsetWidth;
            canvas.height = canvas.parentElement.offsetHeight;
        }
        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);

        window.addEventListener('mousemove', function(e) {
            const rect = canvas.getBoundingClientRect();
            mouse.x = e.clientX - rect.left;
            mouse.y = e.clientY - rect.top;
        });

        window.addEventListener('mouseleave', function() {
            mouse.x = null;
            mouse.y = null;
        });

        class DreamBubble {
            constructor() {
                this.x = Math.random() * canvas.width;
                this.y = canvas.height + Math.random() * 100;
                this.size = Math.random() * 25 + 10;
                this.speedX = Math.random() * 0.8 - 0.4;
                this.speedY = -(Math.random() * 0.6 + 0.3);
                this.color = Math.random() > 0.5 ? '#06B6D4' : '#7C3AED';
                this.opacity = Math.random() * 0.3 + 0.15;
                this.pulseDirection = Math.random() > 0.5 ? 1 : -1;
            }

            update() {
                this.x += this.speedX;
                this.y += this.speedY;

                if (this.y < -50) {
                    this.y = canvas.height + 50;
                    this.x = Math.random() * canvas.width;
                }

                this.opacity += 0.005 * this.pulseDirection;
                if (this.opacity > 0.5 || this.opacity < 0.15) {
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
                        this.x -= directionX * force * 3;
                        this.y -= directionY * force * 3;
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
                grad.addColorStop(0, 'rgba(255, 255, 255, 0.45)');
                grad.addColorStop(0.4, this.color);
                grad.addColorStop(1, 'rgba(0,0,0,0)');

                ctx.fillStyle = grad;
                ctx.globalAlpha = this.opacity;
                ctx.shadowBlur = 10;
                ctx.shadowColor = this.color;
                ctx.fill();
                
                ctx.beginPath();
                ctx.arc(this.x - this.size * 0.3, this.y - this.size * 0.3, this.size * 0.15, 0, Math.PI * 2);
                ctx.fillStyle = '#FFFFFF';
                ctx.globalAlpha = this.opacity * 1.5;
                ctx.fill();
                ctx.restore();
            }
        }

        function initBubbles() {
            particles = [];
            let count = Math.min(window.innerWidth / 20, 60);
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