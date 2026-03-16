// results.js — semi-circular gauge chart for result.html

(function () {
    const canvas = document.getElementById('gc');
    if (!canvas) return;

    const riskPct = parseFloat(canvas.dataset.riskPct) || 0;
    const ctx     = canvas.getContext('2d');
    const W       = canvas.width;
    const H       = canvas.height;
    const cx      = W / 2;
    const cy      = H - 30;
    const radius  = Math.min(W, H * 2) / 2 - 20;

    // Color stops: green → yellow → orange → red
    function riskColor(pct) {
        if (pct < 25)  return '#22c55e';   // green
        if (pct < 50)  return '#facc15';   // yellow
        if (pct < 75)  return '#f97316';   // orange
        return '#ef4444';                   // red
    }

    function drawGauge(pct) {
        ctx.clearRect(0, 0, W, H);

        const startAngle = Math.PI;           // 180°
        const endAngle   = 2 * Math.PI;       // 360°
        const fillAngle  = startAngle + (pct / 100) * Math.PI;

        // Background track
        ctx.beginPath();
        ctx.arc(cx, cy, radius, startAngle, endAngle);
        ctx.lineWidth   = 28;
        ctx.strokeStyle = '#2a2d3a';
        ctx.lineCap     = 'round';
        ctx.stroke();

        // Coloured fill arc
        ctx.beginPath();
        ctx.arc(cx, cy, radius, startAngle, fillAngle);
        ctx.lineWidth   = 28;
        ctx.strokeStyle = riskColor(pct);
        ctx.lineCap     = 'round';
        ctx.stroke();

        // Percentage text in centre
        ctx.fillStyle  = '#ffffff';
        ctx.font       = 'bold 2.6rem Segoe UI, sans-serif';
        ctx.textAlign  = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(pct + '%', cx, cy - radius * 0.18);

        // "Risk Score" label
        ctx.fillStyle  = '#9a9a9a';
        ctx.font       = '0.9rem Segoe UI, sans-serif';
        ctx.fillText('Risk Score', cx, cy - radius * 0.18 + 40);

        // Left label (0%)
        ctx.fillStyle  = '#777';
        ctx.font       = '0.8rem Segoe UI, sans-serif';
        ctx.textAlign  = 'left';
        ctx.fillText('0%', cx - radius - 14, cy + 18);

        // Right label (100%)
        ctx.textAlign  = 'right';
        ctx.fillText('100%', cx + radius + 14, cy + 18);
    }

    // Animate from 0 to riskPct
    let current = 0;
    const step  = riskPct / 60;   // ~60 frames

    function animate() {
        current += step;
        if (current >= riskPct) {
            drawGauge(riskPct);
            return;
        }
        drawGauge(Math.round(current * 10) / 10);
        requestAnimationFrame(animate);
    }

    animate();
})();

