/* ==========================================================================
   GitHub Easy Push - Ultra-Smooth & Slow Cosmic Falling Star Engine
   Author: Prakhar Yadav (@blazecodeprakhar)
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  // Launch Cosmic Falling Star Particle System (Ultra-Smooth Slow Mode)
  initSpaceFallingStarEngine();

  // Mobile Navigation Toggle
  const navToggle = document.getElementById('nav-toggle');
  const navMenu = document.getElementById('nav-menu');

  if (navToggle && navMenu) {
    navToggle.addEventListener('click', () => {
      navMenu.classList.toggle('active');
    });

    navMenu.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        navMenu.classList.remove('active');
      });
    });
  }

  // 3D Card Tilt Effect on Hover
  document.querySelectorAll('.tilt-card, .hero-card').forEach(card => {
    card.addEventListener('mousemove', e => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left - rect.width / 2;
      const y = e.clientY - rect.top - rect.height / 2;

      const tiltX = (y / (rect.height / 2)) * -6;
      const tiltY = (x / (rect.width / 2)) * 6;

      card.style.transform = `perspective(1000px) rotateX(${tiltX}deg) rotateY(${tiltY}deg) translateY(-4px)`;
    });

    card.addEventListener('mouseleave', () => {
      card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) translateY(0px)';
    });
  });

  // Smooth Navigation Scroll Offset
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      const targetId = this.getAttribute('href');
      if (targetId === '#') return;

      const targetElem = document.querySelector(targetId);
      if (targetElem) {
        e.preventDefault();
        const navHeight = 84;
        const targetPos = targetElem.getBoundingClientRect().top + window.pageYOffset - navHeight;
        window.scrollTo({
          top: targetPos,
          behavior: 'smooth'
        });
      }
    });
  });
});

/**
 * Ultra-Smooth, Slow Cosmic Falling Star Engine with Cursor Sparkle Trails
 */
function initSpaceFallingStarEngine() {
  const canvas = document.getElementById('space-canvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  let width = canvas.width = window.innerWidth;
  let height = canvas.height = window.innerHeight;

  window.addEventListener('resize', () => {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  });

  // Color Palette for Cosmic Stars
  const colors = ['#22D3EE', '#38BDF8', '#34D399', '#C084FC', '#FFFFFF', '#FBBF24'];

  // 1. Falling Stars Array (Slower, smoother speeds)
  const starCount = Math.floor((width * height) / 7000);
  const stars = [];

  for (let i = 0; i < starCount; i++) {
    stars.push({
      x: Math.random() * width,
      y: Math.random() * height,
      length: Math.random() * 30 + 12,
      speedY: Math.random() * 0.7 + 0.3, // Ultra-slow falling speed
      speedX: (Math.random() - 0.5) * 0.25, // Soft ambient horizontal drift
      opacity: Math.random() * 0.75 + 0.25,
      size: Math.random() * 2.0 + 0.8,
      color: colors[Math.floor(Math.random() * colors.length)]
    });
  }

  // 2. Interactive Cursor Sparkles Array
  const sparkles = [];
  window.addEventListener('mousemove', e => {
    for (let i = 0; i < 2; i++) {
      sparkles.push({
        x: e.clientX + (Math.random() - 0.5) * 12,
        y: e.clientY + (Math.random() - 0.5) * 12,
        vx: (Math.random() - 0.5) * 1.2,
        vy: (Math.random() - 0.5) * 1.2 - 0.3,
        size: Math.random() * 2.4 + 1.0,
        opacity: 1,
        color: colors[Math.floor(Math.random() * colors.length)]
      });
    }
  });

  // Animation Loop
  function render() {
    ctx.clearRect(0, 0, width, height);

    // Draw Subtle Cyber Mesh Background Gradient
    const bgGradient = ctx.createRadialGradient(width / 2, height / 3, 10, width / 2, height / 3, width);
    bgGradient.addColorStop(0, '#0c162d');
    bgGradient.addColorStop(0.6, '#070a12');
    bgGradient.addColorStop(1, '#05060a');
    ctx.fillStyle = bgGradient;
    ctx.fillRect(0, 0, width, height);

    // Draw & Update Falling Stars
    for (let i = 0; i < stars.length; i++) {
      const s = stars[i];

      // Draw Glowing Speed Tail
      const tailGrad = ctx.createLinearGradient(s.x, s.y, s.x - s.speedX * 10, s.y - s.length);
      tailGrad.addColorStop(0, s.color);
      tailGrad.addColorStop(1, 'transparent');

      ctx.beginPath();
      ctx.moveTo(s.x, s.y);
      ctx.lineTo(s.x - s.speedX * 10, s.y - s.length);
      ctx.strokeStyle = tailGrad;
      ctx.lineWidth = s.size;
      ctx.globalAlpha = s.opacity;
      ctx.stroke();

      // Draw Glowing Particle Head
      ctx.beginPath();
      ctx.arc(s.x, s.y, s.size * 1.1, 0, Math.PI * 2);
      ctx.fillStyle = s.color;
      ctx.globalAlpha = s.opacity;
      ctx.shadowBlur = 8;
      ctx.shadowColor = s.color;
      ctx.fill();
      ctx.shadowBlur = 0;

      // Update Motion (Slow vertical fall & soft horizontal drift)
      s.y += s.speedY;
      s.x += s.speedX;

      // Reset Star when falling off-screen
      if (s.y > height + s.length) {
        s.y = -s.length;
        s.x = Math.random() * width;
        s.speedY = Math.random() * 0.7 + 0.3;
        s.speedX = (Math.random() - 0.5) * 0.25;
        s.opacity = Math.random() * 0.75 + 0.25;
      }
    }

    // Render & Update Interactive Cursor Sparkles
    for (let i = sparkles.length - 1; i >= 0; i--) {
      const sp = sparkles[i];
      ctx.beginPath();
      ctx.arc(sp.x, sp.y, sp.size, 0, Math.PI * 2);
      ctx.fillStyle = sp.color;
      ctx.globalAlpha = sp.opacity;
      ctx.shadowBlur = 8;
      ctx.shadowColor = sp.color;
      ctx.fill();
      ctx.shadowBlur = 0;

      sp.x += sp.vx;
      sp.y += sp.vy;
      sp.opacity -= 0.02;
      sp.size *= 0.96;

      if (sp.opacity <= 0 || sp.size <= 0.2) {
        sparkles.splice(i, 1);
      }
    }

    requestAnimationFrame(render);
  }

  render();
}

/**
 * Copy terminal command to clipboard with UI feedback
 */
function copyCode(textToCopy, btnElement) {
  if (navigator.clipboard && window.isSecureContext) {
    navigator.clipboard.writeText(textToCopy).then(() => {
      showCopySuccess(btnElement);
    }).catch(() => {
      fallbackCopyText(textToCopy, btnElement);
    });
  } else {
    fallbackCopyText(textToCopy, btnElement);
  }
}

function fallbackCopyText(text, btnElement) {
  const textArea = document.createElement('textarea');
  textArea.value = text;
  textArea.style.position = 'fixed';
  textArea.style.left = '-999999px';
  document.body.appendChild(textArea);
  textArea.focus();
  textArea.select();
  try {
    document.execCommand('copy');
    showCopySuccess(btnElement);
  } catch (err) {
    console.error('Copy fallback failed', err);
  }
  document.body.removeChild(textArea);
}

function showCopySuccess(btnElement) {
  if (!btnElement) return;
  const originalText = btnElement.innerHTML;
  btnElement.innerHTML = '<i class="fa-solid fa-check"></i> Copied!';
  btnElement.style.background = '#22D3EE';
  btnElement.style.color = '#07090E';

  setTimeout(() => {
    btnElement.innerHTML = originalText;
    btnElement.style.background = '';
    btnElement.style.color = '';
  }, 2000);
}
