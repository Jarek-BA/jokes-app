// Wait until the entire web page (HTML content) is fully loaded
// before running this script. This prevents errors when trying
// to access elements that might not exist yet.
document.addEventListener('DOMContentLoaded', () => {

  // Find the button on the page with the ID "joke-btn"
  // This is the button the user will click to get a joke.
  const jokeBtn = document.getElementById("joke-btn");

  // Find the element (like a <div> or <p>) with the ID "joke"
  // This is where the joke will be displayed after fetching it.
  const jokeEl = document.getElementById("joke");

  // Find the element (like a <div> or <p>) with the ID "joke"
  // This is where the joke will be displayed after fetching it
  const langSelect = document.getElementById("language-selection");

  // Load stored language if exists, defaults to English
  const savedLang = localStorage.getItem("jokeLang") || "en";
  langSelect.value = savedLang;

  // Add an action ("event listener") to the button:
  // When the button is clicked, run the function below.
  jokeBtn.addEventListener("click", async () => {
    const lang = langSelect.value;
    localStorage.setItem("jokeLang", lang); // Remember the choice

    try {
      // Ask our backend server (FastAPI in main.py) for a joke
      // by sending a request to the "/joke" address (endpoint).
      const res = await fetch(`/joke?lang=${lang}`);

      // If the server response is not okay (status not 200),
      // throw an error so we can handle it in the "catch" below.
      if (!res.ok) throw new Error("Failed to fetch joke");

      // Convert the server’s response into a JavaScript object (JSON).
      const data = await res.json();

      // Now decide how to show the joke, based on what kind it is:
      // The Joke API can return either a "single" joke
      // or a "twopart" joke (with setup + punchline).
      if (data.type === "single") {
        // If it's a single joke, display it directly in the "joke" element.
        jokeEl.textContent = data.joke;

      } else if (data.type === "twopart") {
        // If it's a two-part joke, show the setup and the delivery
        // separated by an emoji for fun.
        jokeEl.textContent = `${data.setup} 🤔 ... ${data.delivery}`;

      } else {
        // If the data doesn’t match either type, show a fallback message.
        jokeEl.textContent = "No joke found.";
      }

    } catch (err) {
      // If something goes wrong (server down, internet issue, etc.),
      // display an error message to the user.
      jokeEl.textContent = "Error fetching joke!";

      // Also print the actual error details to the browser console
      // (useful for developers to debug).
      console.error(err);
    }
  });
});
