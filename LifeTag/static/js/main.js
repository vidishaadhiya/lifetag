// ---------------- Reveal on scroll ----------------
const revealEls = Array.from(document.querySelectorAll(".reveal"));

const io = new IntersectionObserver(
  (entries) => {
    entries.forEach((e) => {
      if (e.isIntersecting) e.target.classList.add("is-in");
    });
  },
  { threshold: 0.12 }
);

// ✅ observe all reveal elements
revealEls.forEach((el) => io.observe(el));


// ---------------- Parallax blob ----------------
function onScrollParallax() {
  const blob = document.querySelector(".blob");
  if (!blob) return;
  const y = window.scrollY || 0;
  blob.style.transform = `translateY(${y * 0.08}px)`;
}
document.addEventListener("scroll", onScrollParallax, { passive: true });
onScrollParallax();


// ---------------- 3D tilt cards/panels ----------------
const tiltEls = Array.from(document.querySelectorAll("[data-tilt]"));

tiltEls.forEach((el) => {
  let rect = null;

  function enter() {
    rect = el.getBoundingClientRect();
    el.style.transition = "transform 80ms ease";
  }

  function leave() {
    el.style.transition = "transform 240ms ease";
    el.style.transform = "rotateX(0deg) rotateY(0deg)";
    rect = null;
  }

  function move(ev) {
    if (!rect) rect = el.getBoundingClientRect();

    const x = ev.clientX - rect.left;
    const y = ev.clientY - rect.top;

    const rx = ((y / rect.height) - 0.5) * -8;
    const ry = ((x / rect.width) - 0.5) * 10;

    el.style.setProperty("--mx", `${(x / rect.width) * 100}%`);
    el.style.setProperty("--my", `${(y / rect.height) * 100}%`);
    el.style.transform = `rotateX(${rx}deg) rotateY(${ry}deg) translateY(-1px)`;
  }

  el.addEventListener("mouseenter", enter);
  el.addEventListener("mouseleave", leave);
  el.addEventListener("mousemove", move);
});
