# AI-Assisted Chatbot

This project implements an AI-powered chatbot that can process user queries and interact with a SQL database.  
It provides a simple interface to run natural language queries and fetch structured responses.

---

## 📂 Project Structure

AI-Assisted-Chatbot-main/
│── app.py # Main entry point to run the chatbot
│── query_agent.py # Core logic for handling user queries
│── sql.py # SQL helper functions for database interaction
│── requirements.txt # Python dependencies
│── .env # Environment variables (API keys, DB configs)
│── README.md # Project documentation

---

## 🚀 Features

- AI-assisted query handling
- SQL database integration
- Modular code structure:
  - `app.py` runs the application
  - `query_agent.py` processes queries
  - `sql.py` manages database functions
- Configurable environment via `.env`

---

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repo_url>
   cd AI-Assisted-Chatbot-main
Set up a virtual environment (optional but recommended)

bash
Copy code
python -m venv venv
source venv/bin/activate   # On macOS/Linux
venv\Scripts\activate      # On Windows
Install dependencies

bash
Copy code
pip install -r requirements.txt
Configure environment variables
Create a .env file in the project root (already included in this repo).
Add necessary variables such as API keys and database credentials.

▶️ Usage
Run the chatbot with:

bash
Copy code
python app.py
The chatbot will start and process user queries.

Queries are handled via query_agent.py, which may interact with a SQL database through sql.py.

📦 Requirements
Dependencies are listed in requirements.txt.
Install them using:

bash
Copy code
pip install -r requirements.txt
⚙️ Files Overview
app.py – Entry point, orchestrates chatbot execution.

query_agent.py – Contains logic for AI-based query handling.

sql.py – Manages database connections and SQL operations.

requirements.txt – Python dependencies required for the project.

.env – Stores sensitive environment variables (not shared publicly).

📌 Notes
Make sure to properly configure the .env file before running.

Database setup may be required depending on your use case.

This project is intended as a starting point for AI + SQL chatbot integration.

📝 License
This project is under MIT License.
