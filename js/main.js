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

  // Submits to a Google Apps Script Web App bound to the leads Sheet. Sent as
  // FormData (not JSON) so the request stays a CORS "simple request" — Apps
  // Script doesn't handle a preflight OPTIONS request. Unlike the Google Form
  // endpoint, this one has no anti-abuse session token, so a real
  // success/failure response can be read back.
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

      fetch(form.action, { method: "POST", body: formData })
        .then(function (response) {
          if (!response.ok) throw new Error("Request failed");
          return response.json();
        })
        .then(function (data) {
          if (!data || data.result !== "success") {
            throw new Error("Unexpected response");
          }
          form.hidden = true;
          if (successBox) successBox.hidden = false;
          form.reset();
        })
        .catch(function () {
          if (statusBox) {
            statusBox.hidden = false;
            statusBox.classList.add("is-error");
            statusBox.textContent =
              "Something went wrong. Please try again, or message us on WhatsApp.";
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
          "We don't yet have a verified admission-route match for this exact combination. Our partner network does cover Engineering, Management, Medical, Law and Design colleges across several states, though — browse the College Directory below for a sense of what's out there, and a counsellor will confirm what's realistic for your profile rather than us guessing.";
      }

      var directoryUrl = "colleges.html?category=" + encodeURIComponent(course);
      if (state && state !== "Other") {
        directoryUrl += "&state=" + encodeURIComponent(state);
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
        '">Enquire Now</button><a href="' +
        directoryUrl +
        '" class="btn btn-outline">Browse Colleges</a></div>';

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

  /* ---------------- College Directory ---------------- */
  var directoryList = document.getElementById("directory-list");
  if (directoryList) {
    var dirSearch = document.getElementById("dir-search");
    var dirState = document.getElementById("dir-state");
    var dirCategory = document.getElementById("dir-category");
    var dirCount = document.getElementById("directory-count");
    var dirEmpty = document.getElementById("directory-empty");
    var allColleges = [];

    function escapeHtml(str) {
      return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
    }

    function renderColleges() {
      var q = (dirSearch.value || "").trim().toLowerCase();
      var stateFilter = dirState.value;
      var categoryFilter = dirCategory.value;

      var filtered = allColleges.filter(function (c) {
        if (stateFilter && c.state !== stateFilter) return false;
        if (categoryFilter && c.category !== categoryFilter) return false;
        if (q) {
          var haystack = ((c.name || "") + " " + (c.city || "") + " " + (c.state || "")).toLowerCase();
          if (haystack.indexOf(q) === -1) return false;
        }
        return true;
      });

      dirCount.innerHTML =
        "Showing <strong>" + filtered.length + "</strong> of " + allColleges.length + " colleges";

      if (!filtered.length) {
        directoryList.innerHTML = "";
        dirEmpty.hidden = false;
        return;
      }
      dirEmpty.hidden = true;

      directoryList.innerHTML = filtered
        .map(function (c) {
          var metaParts = [];
          if (c.city) metaParts.push(c.city);
          if (c.state) metaParts.push(c.state);
          var meta = metaParts.join(", ") + (c.type ? " · " + escapeHtml(c.type) : "");

          var facts = [];
          if (c.fee) facts.push("<span>" + escapeHtml(c.fee) + "</span>");
          if (c.entrance_exam) facts.push("<span>" + escapeHtml(c.entrance_exam) + "</span>");
          if (!c.fee && !c.entrance_exam && c.avg_placement) {
            facts.push("<span>Avg. placement: " + escapeHtml(c.avg_placement) + "</span>");
          }

          var badgeClass = c.verified ? "is-verified" : "is-partner";
          var badgeText = c.verified ? "Verified" : "Partner network";

          return (
            '<article class="directory-row">' +
            '<div class="directory-row-main"><h3>' +
            escapeHtml(c.name) +
            '</h3><p class="directory-row-meta">' +
            escapeHtml(meta) +
            "</p></div>" +
            '<div class="directory-row-facts">' +
            facts.join("") +
            "</div>" +
            '<span class="directory-badge ' +
            badgeClass +
            '">' +
            badgeText +
            "</span>" +
            "</article>"
          );
        })
        .join("");
    }

    fetch("data/colleges.json")
      .then(function (r) {
        return r.json();
      })
      .then(function (data) {
        allColleges = data;

        var params = new URLSearchParams(window.location.search);
        var initialCategory = params.get("category");
        var initialState = params.get("state");
        if (initialCategory && Array.prototype.some.call(dirCategory.options, function (o) { return o.value === initialCategory; })) {
          dirCategory.value = initialCategory;
        }
        if (initialState && Array.prototype.some.call(dirState.options, function (o) { return o.value === initialState; })) {
          dirState.value = initialState;
        }

        renderColleges();
      })
      .catch(function () {
        dirCount.textContent = "Couldn't load the college list. Please refresh the page.";
      });

    dirSearch.addEventListener("input", renderColleges);
    dirState.addEventListener("change", renderColleges);
    dirCategory.addEventListener("change", renderColleges);
  }

  /* ---------------- Footer year ---------------- */
  document.querySelectorAll("[data-year]").forEach(function (el) {
    el.textContent = new Date().getFullYear();
  });
})();
