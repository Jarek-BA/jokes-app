document.addEventListener('DOMContentLoaded', () => {
  const jokeBtn = document.getElementById("joke-btn");
  const jokeEl = document.getElementById("joke");

  jokeBtn.addEventListener("click", async () => {
    try {
      const res = await fetch("/joke");
      if (!res.ok) throw new Error("Failed to fetch joke");
      const data = await res.json();

      // Handle single vs twopart jokes
      if (data.type === "single") {
        jokeEl.textContent = data.joke;
      } else if (data.type === "twopart") {
        jokeEl.textContent = `${data.setup} 🤔 ... ${data.delivery}`;
      } else {
        jokeEl.textContent = "No joke found.";
      }
    } catch (err) {
      jokeEl.textContent = "Error fetching joke!";
      console.error(err);
    }
  });
});
