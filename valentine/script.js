(function () {
  const noBtn = document.getElementById("noBtn");
  const yesBtn = document.getElementById("yesBtn");
  const successMessage = document.getElementById("successMessage");
  const initialContent = document.getElementById("initialContent");
  if (!noBtn) return;

  const runAwayRadius = 100;
  const moveStep = 32;
  const bounceNudge = 24;

  function getCenter(el) {
    const rect = el.getBoundingClientRect();
    return {
      x: rect.left + rect.width / 2,
      y: rect.top + rect.height / 2,
    };
  }

  function applyBounce() {
    const rect = noBtn.getBoundingClientRect();
    let left = parseFloat(noBtn.style.left) || 0;
    let top = parseFloat(noBtn.style.top) || 0;

    if (rect.left < 0) {
      left = left - rect.left + bounceNudge;
    }
    if (rect.right > window.innerWidth) {
      left = left - (rect.right - window.innerWidth) - bounceNudge;
    }
    if (rect.top < 0) {
      top = top - rect.top + bounceNudge;
    }
    if (rect.bottom > window.innerHeight) {
      top = top - (rect.bottom - window.innerHeight) - bounceNudge;
    }

    noBtn.style.left = `${left}px`;
    noBtn.style.top = `${top}px`;
  }

  function handleMouseMove(e) {
    const mouse = { x: e.clientX, y: e.clientY };
    const center = getCenter(noBtn);
    const dx = mouse.x - center.x;
    const dy = mouse.y - center.y;
    const distance = Math.hypot(dx, dy);

    if (distance < runAwayRadius) {
      const angle = Math.atan2(dy, dx);
      const moveX = Math.cos(angle) * moveStep;
      const moveY = Math.sin(angle) * moveStep;

      const currentLeft = parseFloat(noBtn.style.left) || 0;
      const currentTop = parseFloat(noBtn.style.top) || 0;

      const newLeft = currentLeft - moveX;
      const newTop = currentTop - moveY;

      noBtn.style.left = `${newLeft}px`;
      noBtn.style.top = `${newTop}px`;
      applyBounce();
    }
  }

  noBtn.style.position = "relative";
  document.addEventListener("mousemove", handleMouseMove);

  if (yesBtn && successMessage && initialContent) {
    yesBtn.addEventListener("click", function () {
      initialContent.classList.add("hidden");
      successMessage.classList.remove("hidden");
    });
  }
})();
