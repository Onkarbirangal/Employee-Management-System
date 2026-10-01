/**
 * Employee Management System - Client Side Enhancements
 */

document.addEventListener("DOMContentLoaded", function () {
  // 1. Auto-dismiss alerts after 5 seconds
  const autoDismissAlerts = document.querySelectorAll(
    ".alert:not(.alert-permanent)",
  );
  autoDismissAlerts.forEach(function (alertElement) {
    setTimeout(function () {
      const bsAlert = new bootstrap.Alert(alertElement);
      bsAlert.close();
    }, 5000);
  });

  // 2. Prevent Double Form Submission
  const forms = document.querySelectorAll("form");
  forms.forEach(function (form) {
    form.addEventListener("submit", function () {
      // Find primary submit button
      const submitBtn = form.querySelector("button[type='submit']");
      if (submitBtn && !form.classList.contains("no-disable-on-submit")) {
        submitBtn.disabled = true;
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = `
                    <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                    Processing...
                `;
        // Safety fallback to re-enable if submission hangs or triggers validation error
        setTimeout(function () {
          submitBtn.disabled = false;
          submitBtn.innerHTML = originalText;
        }, 8000);
      }
    });
  });

  // 3. Highlight current active link in sidebar
  const currentPath = window.location.pathname;
  const sidebarLinks = document.querySelectorAll(".sidebar-wrapper .nav-link");
  sidebarLinks.forEach(function (link) {
    if (link.getAttribute("href") === currentPath) {
      link.classList.add("active");
    }
  });
});
