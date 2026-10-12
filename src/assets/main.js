/* Launch Lead Gen — site interactions. No network calls unless a form has a data-endpoint. */
(function () {
  "use strict";
  var doc = document.documentElement;
  doc.classList.remove("no-js");
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* Mobile menu */
  var toggle = document.querySelector(".menu-toggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      var open = document.body.classList.toggle("menu-open");
      toggle.setAttribute("aria-expanded", String(open));
    });
    document.querySelectorAll(".nav-links a").forEach(function (a) {
      a.addEventListener("click", function () {
        document.body.classList.remove("menu-open");
        toggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  /* Reveal on scroll */
  var revealables = document.querySelectorAll(".reveal, .season");
  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add("is-visible"); io.unobserve(e.target); }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
    revealables.forEach(function (el) { io.observe(el); });
  } else {
    revealables.forEach(function (el) { el.classList.add("is-visible"); });
  }

  /* Mobile sticky CTA appears after the hero */
  var mobileCta = document.querySelector(".mobile-cta");
  var hero = document.querySelector(".hero");
  if (mobileCta && hero) {
    window.addEventListener("scroll", function () {
      mobileCta.classList.toggle("show", window.scrollY > hero.offsetHeight - 80);
    }, { passive: true });
  }

  /* Sample lead feed (hero). Clearly labelled as sample data in the markup. */
  var feed = document.querySelector("[data-feed]");
  if (feed) {
    var icons = {
      drain: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2.7s6 6.4 6 11a6 6 0 0 1-12 0c0-4.6 6-11 6-11z"/></svg>',
      irr: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22v-7"/><path d="M8 15h8"/><path d="M12 11c-3-3-7-3-9-2"/><path d="M12 11c3-3 7-3 9-2"/><path d="M12 11V7"/><path d="M9 4c1.5-1 4.5-1 6 0"/></svg>'
    };
    var samples = [
      ["drain", "French drain — backyard pooling", "Franklin, TN · 140 ft · Wants quote this week", "Verified"],
      ["irr", "New sprinkler system — 6 zones", "Frisco, TX · New build · Owner occupied", "Exclusive"],
      ["drain", "Downspouts + regrading", "Marietta, GA · Water at foundation", "Verified"],
      ["irr", "Irrigation repair — broken heads", "Chandler, AZ · Leak + low pressure", "Exclusive"],
      ["drain", "Sump pump + interior drain", "Carmel, IN · Wet basement after storms", "Verified"],
      ["irr", "Drip conversion + smart controller", "Boise, ID · Water restrictions", "Exclusive"],
      ["drain", "Channel drain on driveway", "Raleigh, NC · Garage flooding", "Verified"],
      ["irr", "Spring start-up + backflow test", "Lehi, UT · Annual service", "Exclusive"]
    ];
    var i = 0;
    var make = function (s, isNew) {
      var el = document.createElement("div");
      el.className = "lead-card" + (isNew ? " is-new" : "");
      var icon = document.createElement("div");
      icon.className = "lead-icon " + s[0];
      icon.innerHTML = icons[s[0]];
      var body = document.createElement("div");
      var t = document.createElement("div"); t.className = "lead-title"; t.textContent = s[1];
      var m = document.createElement("div"); m.className = "lead-meta"; m.textContent = s[2];
      body.appendChild(t); body.appendChild(m);
      var b = document.createElement("span"); b.className = "lead-badge"; b.textContent = s[3];
      el.appendChild(icon); el.appendChild(body); el.appendChild(b);
      return el;
    };
    for (; i < 4; i++) feed.appendChild(make(samples[i], false));
    if (!reduceMotion) {
      setInterval(function () {
        var prev = feed.querySelector(".is-new");
        if (prev) prev.classList.remove("is-new");
        feed.insertBefore(make(samples[i % samples.length], true), feed.firstChild);
        i++;
        while (feed.children.length > 4) feed.removeChild(feed.lastChild);
      }, 3200);
    }
  }

  /* ROI calculator */
  var calc = document.querySelector("[data-calc]");
  if (calc) {
    var presets = {
      drainage: { cost: 95, close: 30, ticket: 4800, leads: 25 },
      irrigation: { cost: 70, close: 35, ticket: 3600, leads: 30 }
    };
    var money = function (n) { return "$" + Math.round(n).toLocaleString("en-US"); };
    var inputs = calc.querySelectorAll("input[type=range]");
    var setFill = function (r) {
      var pct = (r.value - r.min) / (r.max - r.min) * 100;
      r.style.setProperty("--fill", pct + "%");
    };
    var fmt = { cost: money, ticket: money, close: function (v) { return v + "%"; }, leads: function (v) { return v; } };
    var update = function () {
      var v = {};
      inputs.forEach(function (r) {
        v[r.name] = Number(r.value);
        setFill(r);
        var o = calc.querySelector('output[for="' + r.id + '"]');
        if (o) o.textContent = fmt[r.name](r.value);
      });
      var spend = v.cost * v.leads;
      var jobs = v.leads * v.close / 100;
      var revenue = jobs * v.ticket;
      var roi = spend ? revenue / spend : 0;
      calc.querySelector("[data-out=revenue]").textContent = money(revenue);
      calc.querySelector("[data-out=jobs]").textContent = jobs.toFixed(1);
      calc.querySelector("[data-out=spend]").textContent = money(spend);
      calc.querySelector("[data-out=cpa]").textContent = jobs ? money(spend / jobs) : "—";
      calc.querySelector("[data-out=roi]").textContent = roi.toFixed(1) + "×";
    };
    inputs.forEach(function (r) { r.addEventListener("input", update); });
    calc.querySelectorAll("[data-preset]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        calc.querySelectorAll("[data-preset]").forEach(function (b) { b.setAttribute("aria-pressed", String(b === btn)); });
        var p = presets[btn.getAttribute("data-preset")];
        inputs.forEach(function (r) { r.value = p[r.name]; });
        update();
      });
    });
    update();
  }

  /* Territory check (front-end only: points the visitor to the full request form) */
  document.querySelectorAll("[data-territory]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var zip = form.querySelector("[name=zip]");
      var svc = form.querySelector("[name=service]");
      var out = form.querySelector(".territory-result");
      var field = zip.closest(".field");
      if (!/^\d{5}$/.test(zip.value.trim())) {
        field.classList.add("invalid");
        field.querySelector(".err").textContent = "Enter a 5-digit ZIP code.";
        zip.focus();
        return;
      }
      field.classList.remove("invalid");
      field.querySelector(".err").textContent = "";
      out.textContent = "";
      var strong = document.createElement("strong");
      strong.textContent = "Next step: ";
      out.appendChild(strong);
      out.appendChild(document.createTextNode("tell us a bit more and we'll confirm whether " + svc.options[svc.selectedIndex].text.toLowerCase() + " leads are open in " + zip.value.trim() + ". "));
      var a = document.createElement("a");
      a.href = "/contact.html?zip=" + encodeURIComponent(zip.value.trim()) + "&service=" + encodeURIComponent(svc.value);
      a.textContent = "Finish my territory request →";
      out.appendChild(a);
      out.classList.add("show");
    });
  });

  /* Contact form: validate, optionally POST to data-endpoint, otherwise show not-sent notice */
  var contact = document.querySelector("[data-contact]");
  if (contact) {
    var params = new URLSearchParams(location.search);
    if (params.get("zip")) contact.querySelector("[name=zips]").value = params.get("zip");
    var svcParam = params.get("service");
    if (svcParam) contact.querySelectorAll("[name=services]").forEach(function (c) {
      if (svcParam === "both" || c.value === svcParam) c.checked = true;
    });
    var plan = params.get("plan");
    if (plan) { var sel = contact.querySelector("[name=plan]"); if (sel) sel.value = plan; }

    var rules = {
      name: function (v) { return v.trim().length > 1 || "Tell us your name."; },
      company: function (v) { return v.trim().length > 1 || "Add your company name."; },
      email: function (v) { return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v.trim()) || "Enter a valid email."; },
      phone: function (v) { return v.replace(/\D/g, "").length >= 10 || "Enter a 10-digit phone number."; },
      zips: function (v) { return /\d{5}/.test(v) || "Add at least one ZIP code you serve."; }
    };
    var check = function (name) {
      var el = contact.querySelector("[name=" + name + "]");
      var res = rules[name](el.value);
      var f = el.closest(".field");
      f.classList.toggle("invalid", res !== true);
      f.querySelector(".err").textContent = res === true ? "" : res;
      return res === true;
    };
    Object.keys(rules).forEach(function (n) {
      contact.querySelector("[name=" + n + "]").addEventListener("blur", function () { check(n); });
    });
    contact.addEventListener("submit", function (e) {
      e.preventDefault();
      var ok = Object.keys(rules).map(check).every(Boolean);
      var svcs = contact.querySelectorAll("[name=services]:checked").length;
      var svcField = contact.querySelector(".services-field");
      svcField.classList.toggle("invalid", !svcs);
      svcField.querySelector(".err").textContent = svcs ? "" : "Pick at least one lead type.";
      var status = contact.querySelector(".form-status");
      if (!ok || !svcs) {
        var first = contact.querySelector(".invalid input, .invalid select");
        if (first) first.focus();
        return;
      }
      var endpoint = contact.getAttribute("data-endpoint");
      if (!endpoint) {
        status.className = "form-status show warn";
        status.textContent = "Your details look good. Heads up: this form isn't connected to an inbox yet, so nothing was sent. Email us directly while we finish setup.";
        return;
      }
      var btn = contact.querySelector("button[type=submit]");
      btn.disabled = true;
      fetch(endpoint, { method: "POST", body: new FormData(contact), headers: { Accept: "application/json" } })
        .then(function (r) {
          if (!r.ok) throw new Error(r.status);
          status.className = "form-status show ok";
          status.textContent = "Got it. We'll check your territory and reach out within one business day.";
          contact.reset();
        })
        .catch(function () {
          status.className = "form-status show warn";
          status.textContent = "Something went wrong sending your request. Please try again or email us directly.";
        })
        .then(function () { btn.disabled = false; });
    });
  }

  /* Newsletter (not connected) */
  document.querySelectorAll("[data-news]").forEach(function (f) {
    f.addEventListener("submit", function (e) {
      e.preventDefault();
      var btn = f.querySelector("button");
      btn.textContent = "Coming soon";
      btn.disabled = true;
    });
  });

  /* Pricing billing toggle */
  var pt = document.querySelector("[data-price-toggle]");
  if (pt) {
    pt.querySelectorAll("button").forEach(function (b) {
      b.addEventListener("click", function () {
        pt.querySelectorAll("button").forEach(function (x) { x.setAttribute("aria-pressed", String(x === b)); });
        var mode = b.getAttribute("data-mode");
        document.querySelectorAll("[data-price]").forEach(function (el) {
          el.textContent = el.getAttribute("data-" + mode);
        });
        document.querySelectorAll("[data-price-note]").forEach(function (el) {
          el.textContent = el.getAttribute("data-note-" + mode);
        });
      });
    });
  }

  /* Blog filters */
  var filters = document.querySelector("[data-filters]");
  if (filters) {
    filters.querySelectorAll("button").forEach(function (b) {
      b.addEventListener("click", function () {
        filters.querySelectorAll("button").forEach(function (x) { x.setAttribute("aria-pressed", String(x === b)); });
        var cat = b.getAttribute("data-cat");
        document.querySelectorAll("[data-post-cat]").forEach(function (p) {
          p.hidden = cat !== "all" && p.getAttribute("data-post-cat") !== cat;
        });
      });
    });
  }

  /* Article: reading progress + TOC highlight */
  var prose = document.querySelector(".prose");
  var bar = document.querySelector(".progress");
  if (prose && bar) {
    var tocLinks = document.querySelectorAll(".toc a");
    var heads = prose.querySelectorAll("h2[id]");
    window.addEventListener("scroll", function () {
      var r = prose.getBoundingClientRect();
      var total = r.height - window.innerHeight;
      var pct = Math.min(1, Math.max(0, -r.top / (total || 1)));
      bar.style.width = (pct * 100) + "%";
      var current = null;
      heads.forEach(function (h) { if (h.getBoundingClientRect().top < 140) current = h.id; });
      tocLinks.forEach(function (a) { a.classList.toggle("active", a.getAttribute("href") === "#" + current); });
    }, { passive: true });
  }
})();
