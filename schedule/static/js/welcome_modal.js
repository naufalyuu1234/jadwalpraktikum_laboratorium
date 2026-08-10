document.addEventListener('DOMContentLoaded', () => {
  const modal = document.getElementById('welcomeModal');
  const closeBtn = document.getElementById('closeModalBtn');
  const dontShowCheckbox = document.getElementById('dontShowAgain');
  const ctaButtons = modal ? modal.querySelectorAll('.modal-actions a') : [];

  if (!modal) return;

  // 1. Cek status localStorage saat halaman dimuat
  const isHidden = localStorage.getItem('hideWelcomeModal') === 'true';

  if (!isHidden) {
    setTimeout(() => {
      modal.showModal();
    }, 400);
  }

  // 2. Fungsi penutupan modal & simpan preferensi
  function closeModal() {
    if (dontShowCheckbox && dontShowCheckbox.checked) {
      localStorage.setItem('hideWelcomeModal', 'true');
    }
    modal.close();
  }

  if (closeBtn) closeBtn.addEventListener('click', closeModal);

  // 3. Jika user mengklik tombol Login/Register di dalam modal, langsung tutup modalnya
  ctaButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      modal.close();
    });
  });

  // 4. Tutup saat pengguna mengklik area backdrop di luar modal
  modal.addEventListener('click', (e) => {
    const rect = modal.getBoundingClientRect();
    const isClickedInside = (
      rect.top <= e.clientY && e.clientY <= rect.top + rect.height &&
      rect.left <= e.clientX && e.clientX <= rect.left + rect.width
    );
    if (!isClickedInside) {
      closeModal();
    }
  });
});