/**
 * InterviewAI – Main JavaScript
 * Handles landing page animations and shared utilities
 */

// ── Smooth scroll for anchor links ──
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function(e) {
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});

// ── Intersection Observer for fade-in animations ──
const observerOptions = { threshold: 0.1, rootMargin: '0px 0px -40px 0px' };
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.style.opacity = '1';
      entry.target.style.transform = 'translateY(0)';
      observer.unobserve(entry.target);
    }
  });
}, observerOptions);

// Apply to feature cards and steps
document.querySelectorAll('.feature-card, .step, .analytics-card').forEach(el => {
  el.style.opacity = '0';
  el.style.transform = 'translateY(20px)';
  el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
  observer.observe(el);
});

// ── Nav scroll effect ──
const nav = document.querySelector('.nav');
if (nav) {
  window.addEventListener('scroll', () => {
    if (window.scrollY > 20) {
      nav.style.background = 'rgba(10,14,26,0.95)';
    } else {
      nav.style.background = 'rgba(10,14,26,0.8)';
    }
  });
}

// ── Utility: Show toast notification ──
window.showToast = function(message, type = 'info') {
  const existing = document.querySelector('.toast');
  if (existing) existing.remove();

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  toast.style.cssText = `
    position: fixed; bottom: 24px; right: 24px; z-index: 9999;
    padding: 14px 20px; border-radius: 10px; font-size: 0.875rem;
    font-family: 'DM Sans', sans-serif; font-weight: 500;
    animation: slideIn 0.3s ease; max-width: 300px;
    background: ${type === 'success' ? 'rgba(16,185,129,0.15)' : type === 'error' ? 'rgba(239,68,68,0.15)' : 'rgba(99,102,241,0.15)'};
    border: 1px solid ${type === 'success' ? 'rgba(16,185,129,0.3)' : type === 'error' ? 'rgba(239,68,68,0.3)' : 'rgba(99,102,241,0.3)'};
    color: ${type === 'success' ? '#6ee7b7' : type === 'error' ? '#fca5a5' : '#a5b4fc'};
  `;

  const style = document.createElement('style');
  style.textContent = `@keyframes slideIn { from { transform: translateX(100px); opacity:0; } to { transform: translateX(0); opacity:1; } }`;
  document.head.appendChild(style);
  document.body.appendChild(toast);
  setTimeout(() => { toast.style.opacity = '0'; toast.style.transition = 'opacity 0.3s'; setTimeout(() => toast.remove(), 300); }, 3000);
};

// ── Auth guard helper ──
window.requireAuth = function() {
  if (!localStorage.getItem('interviewai_user')) {
    window.location.href = '/login';
    return false;
  }
  return true;
};

// ── Format date ──
window.formatDate = function(dateString) {
  return new Date(dateString).toLocaleDateString('en-IN', {
    day: 'numeric', month: 'short', year: 'numeric'
  });
};
