document.addEventListener('DOMContentLoaded', () => {
  document.getElementById("joke-btn").addEventListener("click", async () => {
    try {
      const res = await fetch("/joke");
      if (!res.ok) throw new Error("Network response was not ok");
      const data = await res.json();
      document.getElementById("joke").innerText =
        data.type === "single" ? data.joke : `${data.setup} ... ${data.delivery}`;
    } catch (err) {
      document.getElementById("joke").innerText = "Failed to load joke.";
      console.error(err);
    }
  });
});