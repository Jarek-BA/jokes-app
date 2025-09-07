document.getElementById("joke-btn").addEventListener("click", async () => {
  try {
    let res = await fetch("/joke");
    if (!res.ok) throw new Error("Network response was not ok");
    let data = await res.json();
    document.getElementById("joke").innerText = data.joke;
  } catch (err) {
    document.getElementById("joke").innerText = "Failed to load joke.";
    console.error(err);
  }
});
