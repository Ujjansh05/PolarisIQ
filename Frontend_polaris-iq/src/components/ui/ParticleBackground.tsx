import { useEffect, useRef } from 'react';

const ParticleBackground = () => {
    const canvasRef = useRef<HTMLCanvasElement>(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        let particles: Particle[] = [];
        let animationFrameId: number;

        const resize = () => {
            if (!canvasRef.current) return;
            canvasRef.current.width = window.innerWidth;
            canvasRef.current.height = window.innerHeight;
            initParticles();
        };

        class Particle {
            x: number;
            y: number;
            size: number;
            speedX: number;
            speedY: number;
            color: string;
            glowBase: number;

            constructor() {
                this.x = Math.random() * (canvasRef.current?.width || window.innerWidth);
                this.y = Math.random() * (canvasRef.current?.height || window.innerHeight);
                this.size = Math.random() * 2 + 0.5;
                this.speedX = (Math.random() - 0.5) * 0.5;
                this.speedY = (Math.random() - 0.5) * 0.5;

                // Randomly choose between primary and secondary neon colors
                const colors = ['rgba(99, 102, 241,', 'rgba(168, 85, 247,'];
                this.color = colors[Math.floor(Math.random() * colors.length)];
                this.glowBase = Math.random() * 0.5 + 0.1;
            }

            update() {
                if (!canvasRef.current) return;
                const canvasW = canvasRef.current.width;
                const canvasH = canvasRef.current.height;

                this.x += this.speedX;
                this.y += this.speedY;

                if (this.x > canvasW) this.x = 0;
                else if (this.x < 0) this.x = canvasW;

                if (this.y > canvasH) this.y = 0;
                else if (this.y < 0) this.y = canvasH;
            }

            draw() {
                if (!ctx) return;

                // Pulsating alpha
                const alpha = this.glowBase + Math.sin(Date.now() * 0.001 * this.speedX * 10) * 0.2;

                ctx.fillStyle = `${this.color}${Math.max(0.1, alpha)})`;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);

                // Add glow
                ctx.shadowBlur = 10;
                ctx.shadowColor = `${this.color}0.8)`;
                ctx.fill();
                ctx.shadowBlur = 0; // reset
            }
        }

        const initParticles = () => {
            particles = [];
            const particleCount = Math.floor((window.innerWidth * window.innerHeight) / 15000);
            for (let i = 0; i < particleCount; i++) {
                particles.push(new Particle());
            }
        };

        const animate = () => {
            if (!ctx || !canvasRef.current) return;
            ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);

            // Draw subtle connecting lines
            for (let i = 0; i < particles.length; i++) {
                particles[i].update();
                particles[i].draw();

                for (let j = i; j < particles.length; j++) {
                    const dx = particles[i].x - particles[j].x;
                    const dy = particles[i].y - particles[j].y;
                    const distance = Math.sqrt(dx * dx + dy * dy);

                    if (distance < 100) {
                        ctx.beginPath();
                        ctx.strokeStyle = `rgba(99, 102, 241, ${0.1 * (1 - distance / 100)})`;
                        ctx.lineWidth = 0.5;
                        ctx.moveTo(particles[i].x, particles[i].y);
                        ctx.lineTo(particles[j].x, particles[j].y);
                        ctx.stroke();
                    }
                }
            }

            animationFrameId = requestAnimationFrame(animate);
        };

        window.addEventListener('resize', resize);
        resize();
        animate();

        return () => {
            window.removeEventListener('resize', resize);
            cancelAnimationFrame(animationFrameId);
        };
    }, []);

    return (
        <canvas
            ref={canvasRef}
            className="fixed inset-0 pointer-events-none z-[-1] opacity-60"
        />
    );
};

export default ParticleBackground;
