// Ground Game Consulting Services — small progressive enhancements
document.documentElement.classList.add("js");

// Mobile navigation
(function () {
  var toggle = document.querySelector(".nav-toggle");
  if (!toggle) return;
  toggle.addEventListener("click", function () {
    var open = document.body.classList.toggle("nav-open");
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && document.body.classList.contains("nav-open")) {
      document.body.classList.remove("nav-open");
      toggle.setAttribute("aria-expanded", "false");
    }
  });
})();

// Reveal on scroll
(function () {
  var items = document.querySelectorAll(".reveal");
  if (!("IntersectionObserver" in window)) {
    items.forEach(function (el) { el.classList.add("in"); });
    return;
  }
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add("in");
        io.unobserve(entry.target);
      }
    });
  }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
  items.forEach(function (el) { io.observe(el); });
})();

// Contact form: send to Formspree in the background and show the result in place.
// Without JavaScript the form still posts to the same endpoint.
(function () {
  var form = document.getElementById("inquiry");
  if (!form || !window.fetch) return;
  var status = document.getElementById("form-status");
  var button = form.querySelector("button[type=submit]");
  var label = button.innerHTML;

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    if (!form.reportValidity()) return;
    button.disabled = true;
    button.textContent = "Sending…";
    status.textContent = "";
    status.classList.remove("error");

    fetch(form.action, {
      method: "POST",
      body: new FormData(form),
      headers: { Accept: "application/json" }
    }).then(function (res) {
      if (res.ok) {
        form.innerHTML =
          '<div class="form-done" tabindex="-1"><span class="eyebrow">Received</span>' +
          "<h3>Thank you. Your note is with us.</h3>" +
          "<p>A senior member of our team will read it and reply personally. Everything you shared stays confidential.</p></div>";
        form.querySelector(".form-done").focus();
        return;
      }
      return res.json().then(function (data) {
        var msg = data && data.errors && data.errors.length
          ? data.errors.map(function (err) { return err.message; }).join(" ")
          : "Something went wrong.";
        throw new Error(msg);
      });
    }).catch(function (err) {
      status.classList.add("error");
      status.textContent = (err && err.message ? err.message + " " : "") +
        "Please try again in a moment.";
      button.disabled = false;
      button.innerHTML = label;
    });
  });
})();
