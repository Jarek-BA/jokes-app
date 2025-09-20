document.addEventListener('DOMContentLoaded', () => {
  const jokeBtn = document.getElementById("joke-btn");
  const jokeEl = document.getElementById("joke");
  const langSelect = document.getElementById("language-selection");
  const flagCheckboxes = document.querySelectorAll(".flag");

  // --- Load stored language ---
  const savedLang = localStorage.getItem("jokeLang") || "en";
  langSelect.value = savedLang;

  // --- Load stored blacklist flags ---
  const savedFlags = (localStorage.getItem("jokeFlags") || "").split(",");
  flagCheckboxes.forEach(cb => {
    if (savedFlags.includes(cb.value)) {
      cb.checked = true;
    }
  });

  // --- Save flags to localStorage when user toggles ---
  flagCheckboxes.forEach(cb => {
    cb.addEventListener("change", () => {
      const selected = Array.from(flagCheckboxes)
        .filter(c => c.checked)
        .map(c => c.value);
      localStorage.setItem("jokeFlags", selected.join(","));
    });
  });

  // --- Fetch joke on button click ---
  jokeBtn.addEventListener("click", async () => {
    const lang = langSelect.value;
    localStorage.setItem("jokeLang", lang);

    const selectedFlags = Array.from(flagCheckboxes)
      .filter(cb => cb.checked)
      .map(cb => cb.value)
      .join(",");

    try {
      const url = new URL("/joke", window.location.origin);
      url.searchParams.append("lang", lang);
      if (selectedFlags) {
        url.searchParams.append("blacklist", selectedFlags);
      }

      const res = await fetch(url);
      if (!res.ok) throw new Error("Failed to fetch joke");

      const data = await res.json();

      // --- Determine joke text ---
      let jokeText = "No joke found.";
      if (data.type === "single") {
        jokeText = data.joke;
      } else if (data.type === "twopart") {
        jokeText = `${data.setup} 🤔 ... ${data.delivery}`;
      }

      // --- Animate joke card ---
      jokeEl.classList.remove("animate"); // remove class if already present
      jokeEl.textContent = jokeText;      // update text
      void jokeEl.offsetWidth;            // force reflow
      jokeEl.classList.add("animate");    // trigger fade-in

    } catch (err) {
      jokeEl.textContent = "Error fetching joke!";
      console.error(err);
    }
  });
});
