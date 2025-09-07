🤣 Jokes App
A simple FastAPI-powered web app that serves random jokes using JokeAPI.
Includes a minimal frontend, automated tests, and a CI/CD pipeline with GitHub Actions + free deployment on Render.
💡 Built as a learning project: backend, frontend, testing, and deployment all in one!
 
✨ Features
•	⚡ FastAPI backend serving jokes from JokeAPI
•	🎨 Frontend with HTML, CSS, and JavaScript (static files served by FastAPI)
•	✅ Unit tests with Pytest
•	🔄 CI/CD: automated testing via GitHub Actions on every push
•	🌍 Deployment to Render (free tier)
 
🚀 Live Demo
👉 [Your Render link will go here once deployed]
 
📦 Installation (Run Locally)
Clone the repo and set up a virtual environment:
# 1. Clone the repository
git clone https://github.com/Jarek-BA/jokes-app.git
cd jokes-app

# 2. Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # on Mac/Linux
venv\Scripts\activate     # on Windows

# 3. Install dependencies
pip install -r requirements.txt
Run the app locally:
uvicorn app.main:app --reload
Now open 👉 http://127.0.0.1:8000
 
🧪 Running Tests
Tests are written with Pytest.
pytest
CI will run these tests automatically on GitHub Actions for every push.
 
⚙️ CI/CD Setup
•	GitHub Actions workflow (.github/workflows/ci.yml) runs linting + tests
•	Render automatically deploys the app on push to main
CI/CD ensures you never ship broken code 🚢
 
📁 Project Structure
jokes-app/
│
├── app/
│   ├── main.py          # FastAPI app
│   └── templates/       # Jinja2 HTML templates
│       └── index.html
│   └── static/          # JS & CSS
│
├── tests/
│   └── test_main.py     # Unit tests
│
├── requirements.txt     # Dependencies
├── .github/workflows/   # CI/CD config
└── README.md            # You are here 😄
 
🔮 Future Ideas
•	Allow users to pick joke categories (Programming, Misc, Dark…)
•	Add “Dad Jokes Only” mode
•	Add database support (store favourite jokes)
•	Add Docker support for easy deployment
 
👨‍💻 Author
Built with ❤️ by @Jarek-BA as a fun learning project.

