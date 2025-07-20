# AI-Assisted-Chatbot

A conversational AI-powered chatbot that translates natural language questions into SQL queries, interacts with a PostgreSQL database, and presents results in a clean, user-friendly interface — powered by Google Gemini's LLM.


## 🧠 Project Overview

This chatbot enables users to query a PostgreSQL database using simple English. It:
- Converts natural language questions into PostgreSQL-compatible SQL.
- Retrieves and formats query results from your database.
- Displays answers in a user-friendly table or summary.
- Maintains chat history and suggests helpful follow-up queries.
- Offers both light and dark themes for an enhanced UX.

Built using **Streamlit**, **Gemini Pro (via Google Generative AI)**, and **psycopg2** for PostgreSQL integration.


## 📁 Project Structure

AI_Assisted_Chatbot/
│
├── app.py # Main Streamlit frontend application
├── query_agent.py # Gemini-based query and response logic
├── sql.py # PostgreSQL connection and helper functions
├── requirements.txt # Python dependencies
├── .env # Environment variables (user-provided, not committed)


## ⚙️ Features
• Natural language to SQL conversion
• PostgreSQL compatibility
• Theme toggle (Dark/Light)
• Follow-up prompts and chat history
• Markdown to HTML table formatting
• Safe SQL execution and sanitization

## 📜 License
This project is licensed under the MIT License.
