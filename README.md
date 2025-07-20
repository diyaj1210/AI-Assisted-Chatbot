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

- app.py
- query_agent.py
- sql.py
- requirements.txt
- .env # Environment variables


## ⚙️ Features
- Natural language to SQL conversion
- PostgreSQL compatibility
- Theme toggle (Dark/Light)
- Follow-up prompts and chat history
- Markdown to HTML table formatting
- Safe SQL execution and sanitization

## 📦 Dataset
This project uses the Pagila PostgreSQL dataset, a rich sample schema for DVD rental businesses.

## 📜 License
This project is licensed under the MIT License.
