/**
 * DegreeLelo — site behaviour: mobile nav, enquiry modal (Formspree), college predictor.
 * No framework, no dependencies.
 */

/* -------------------------------------------------------------
 * CONFIG — replace before going live
 * ----------------------------------------------------------- */
var DEGREELELO_CONFIG = {
  // Create a form at https://formspree.io pointed at degreelelo@gmail.com
  // and paste its form ID here (the part after /f/ in your endpoint).
  formspreeFormId: "YOUR_FORMSPREE_ID",
  // WhatsApp Business number in international format, digits only (no + or spaces).
  whatsappNumber: "911234567890"
};

(function () {
  "use strict";

  /* ---------------- Mobile nav ---------------- */
  var navToggle = document.querySelector("[data-nav-toggle]");
  var primaryNav = document.querySelector("[data-primary-nav]");

  if (navToggle && primaryNav) {
    navToggle.addEventListener("click", function () {
      var isOpen = primaryNav.classList.toggle("is-open");
      navToggle.setAttribute("aria-expanded", String(isOpen));
      document.body.style.overflow = isOpen ? "hidden" : "";
    });

    primaryNav.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () {
        primaryNav.classList.remove("is-open");
        navToggle.setAttribute("aria-expanded", "false");
        document.body.style.overflow = "";
      });
    });
  }

  // Close any open nav dropdown when clicking outside it
  document.addEventListener("click", function (e) {
    document.querySelectorAll(".nav-dropdown[open]").forEach(function (dd) {
      if (!dd.contains(e.target)) dd.removeAttribute("open");
    });
  });

  /* ---------------- WhatsApp links ---------------- */
  document.querySelectorAll("[data-whatsapp-link]").forEach(function (el) {
    var message = encodeURIComponent(
      "Hi DegreeLelo, I'd like guidance on college admissions."
    );
    el.href = "https://wa.me/" + DEGREELELO_CONFIG.whatsappNumber + "?text=" + message;
  });

  /* ---------------- Enquiry modal ---------------- */
  var modal = document.getElementById("enquiry-modal");
  if (!modal) return;

  var overlay = modal; // overlay IS the outer element
  var dialog = modal.querySelector(".modal");
  var form = modal.querySelector("form");
  var closeBtn = modal.querySelector("[data-modal-close]");
  var statusBox = modal.querySelector("[data-form-status]");
  var successBox = modal.querySelector("[data-form-success]");
  var lastFocused = null;

  // wire the formspree action from config if left as data-endpoint
  if (form) {
    var endpoint = form.getAttribute("data-endpoint-template");
    if (endpoint) {
      form.setAttribute(
        "action",
        endpoint.replace("YOUR_FORMSPREE_ID", DEGREELELO_CONFIG.formspreeFormId)
      );
    }
  }

  function getFocusable() {
    return dialog.querySelectorAll(
      'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled])'
    );
  }

  function openModal(prefill) {
    lastFocused = document.activeElement;
    overlay.hidden = false;
    document.body.style.overflow = "hidden";

    // reset to form view
    if (form) form.hidden = false;
    if (successBox) successBox.hidden = true;
    if (statusBox) {
      statusBox.hidden = true;
      statusBox.textContent = "";
      statusBox.classList.remove("is-error");
    }

    if (prefill && form) {
      var courseField = form.querySelector("#enq-course");
      if (courseField && prefill.course) courseField.value = prefill.course;
      var scoreField = form.querySelector("#enq-score");
      if (scoreField && prefill.score) scoreField.value = prefill.score;
    }

    var focusables = getFocusable();
    if (focusables.length) focusables[0].focus();

    document.addEventListener("keydown", onKeydown);
  }

  function closeModal() {
    overlay.hidden = true;
    document.body.style.overflow = "";
    document.removeEventListener("keydown", onKeydown);
    if (lastFocused && typeof lastFocused.focus === "function") {
      lastFocused.focus();
    }
  }

  function onKeydown(e) {
    if (e.key === "Escape") {
      closeModal();
      return;
    }
    if (e.key === "Tab") {
      var focusables = Array.prototype.slice.call(getFocusable());
      if (!focusables.length) return;
      var first = focusables[0];
      var last = focusables[focusables.length - 1];
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    }
  }

  document.querySelectorAll("[data-modal-trigger]").forEach(function (trigger) {
    trigger.addEventListener("click", function () {
      var course = trigger.getAttribute("data-prefill-course");
      var score = trigger.getAttribute("data-prefill-score");
      openModal(course ? { course: course, score: score } : null);
    });
  });

  if (closeBtn) closeBtn.addEventListener("click", closeModal);
  overlay.addEventListener("click", function (e) {
    if (e.target === overlay) closeModal();
  });

  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var submitBtn = form.querySelector('button[type="submit"]');
      var formData = new FormData(form);

      if (statusBox) {
        statusBox.hidden = true;
        statusBox.classList.remove("is-error");
      }
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = "Sending…";
      }

      fetch(form.action, {
        method: "POST",
        body: formData,
        headers: { Accept: "application/json" }
      })
        .then(function (response) {
          if (response.ok) {
            form.hidden = true;
            if (successBox) successBox.hidden = false;
            form.reset();
          } else {
            return response.json().then(function (data) {
              throw new Error(
                data && data.errors
                  ? data.errors.map(function (er) { return er.message; }).join(", ")
                  : "Something went wrong. Please try again or WhatsApp us."
              );
            });
          }
        })
        .catch(function (err) {
          if (statusBox) {
            statusBox.hidden = false;
            statusBox.classList.add("is-error");
            statusBox.textContent =
              err.message || "Something went wrong. Please try again or WhatsApp us.";
          }
        })
        .finally(function () {
          if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = "Submit Enquiry";
          }
        });
    });
  }

  /* ---------------- College Predictor ---------------- */
  var predictorForm = document.getElementById("predictor-form");
  if (predictorForm) {
    var resultBox = document.getElementById("predictor-result");

    predictorForm.addEventListener("submit", function (e) {
      e.preventDefault();
      var state = predictorForm.state.value;
      var course = predictorForm.course.value;
      var score = predictorForm.score.value;

      var heading, message, positive;

      if (state === "Karnataka" && course === "Engineering") {
        positive = true;
        heading = "Good news — routes are available";
        message =
          "For B.Tech admission in Karnataka, COMEDK and direct-entry routes are open to explore. Share a few details below and a counsellor will map out your options.";
      } else if (
        state === "Maharashtra" &&
        (course === "Engineering" || course === "Management")
      ) {
        positive = true;
        heading = "Good news — routes are available";
        message =
          "For " +
          course +
          " admission in Maharashtra, MAH-CET and direct-entry routes are open to explore. Share a few details below and a counsellor will map out your options.";
      } else {
        positive = false;
        heading = "Let's get this reviewed personally";
        message =
          "We don't yet have verified admission-route data for this combination. Rather than guess, our counsellors will personally review your profile and get back to you with accurate guidance.";
      }

      resultBox.hidden = false;
      resultBox.classList.remove("is-positive", "is-review");
      resultBox.classList.add(positive ? "is-positive" : "is-review");
      resultBox.innerHTML =
        "<h3>" +
        heading +
        "</h3><p>" +
        message +
        '</p><div class="cta-row"><button type="button" class="btn btn-primary" data-modal-trigger data-prefill-course="' +
        course +
        '" data-prefill-score="' +
        (score || "") +
        '">Enquire Now</button></div>';

      // wire the newly injected trigger
      var newTrigger = resultBox.querySelector("[data-modal-trigger]");
      if (newTrigger) {
        newTrigger.addEventListener("click", function () {
          openModal({ course: course, score: score });
        });
      }

      resultBox.scrollIntoView({ behavior: "smooth", block: "center" });
      resultBox.setAttribute("tabindex", "-1");
      resultBox.focus();
    });
  }

  /* ---------------- Footer year ---------------- */
  document.querySelectorAll("[data-year]").forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });
})();
