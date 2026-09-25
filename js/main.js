/**
 * DegreeLelo — site behaviour: mobile nav, enquiry modal (Google Form), college predictor.
 * No framework, no dependencies.
 */

/* -------------------------------------------------------------
 * CONFIG
 * ----------------------------------------------------------- */
var DEGREELELO_CONFIG = {
  // WhatsApp Business number in international format, digits only (no + or spaces).
  whatsappNumber: "917304305424"
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
  var hiddenIframe = modal.querySelector('iframe[name="hidden_iframe"]');
  var lastFocused = null;

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

  // Submits into the hidden iframe (target="hidden_iframe" on the form) so the
  // page never navigates to Google. Cross-origin, so we can't read the actual
  // response — success is inferred from the iframe's load event, with a
  // timeout fallback in case the request never completes (e.g. offline).
  if (form && hiddenIframe) {
    var submissionPending = false;
    var submissionTimeout = null;
    var activeSubmitBtn = null;

    function finishSubmission(succeeded) {
      if (!submissionPending) return;
      submissionPending = false;
      clearTimeout(submissionTimeout);

      if (activeSubmitBtn) {
        activeSubmitBtn.disabled = false;
        activeSubmitBtn.textContent = "Submit Enquiry";
      }

      if (succeeded) {
        form.hidden = true;
        if (successBox) successBox.hidden = false;
        form.reset();
      } else if (statusBox) {
        statusBox.hidden = false;
        statusBox.classList.add("is-error");
        statusBox.textContent =
          "That's taking longer than expected. Please try again, or message us on WhatsApp.";
      }
    }

    hiddenIframe.addEventListener("load", function () {
      finishSubmission(true);
    });

    form.addEventListener("submit", function () {
      // No preventDefault: the native submission into the hidden iframe is
      // what actually sends the data to Google.
      activeSubmitBtn = form.querySelector('button[type="submit"]');
      submissionPending = true;

      if (statusBox) {
        statusBox.hidden = true;
        statusBox.classList.remove("is-error");
      }
      if (activeSubmitBtn) {
        activeSubmitBtn.disabled = true;
        activeSubmitBtn.textContent = "Sending…";
      }

      clearTimeout(submissionTimeout);
      submissionTimeout = setTimeout(function () {
        finishSubmission(false);
      }, 8000);
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
