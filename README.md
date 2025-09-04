# AI-Assisted Chatbot

This project implements an AI-powered chatbot that can process user queries and interact with a SQL database.  
It provides a simple interface to run natural language queries and fetch structured responses.

---

## 📁 Project Structure

```
AI-Assisted-Chatbot/
├── app.py                 # Main Streamlit application
├── query_agent.py         # Basic Gemini chat (fallback)
├── sql.py                 # SQL helper functions for database interaction
├── requirements.txt       # Python dependencies
├── README.md              # Project Documentation
├── .env                   # Environment variables (create this)
└── .gitignore             # Git ignore rules
```

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

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/AI-Assisted-Chatbot.git
cd AI-Assisted-Chatbot
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables
Create a `.env` file in the project root and add your Google Gemini API key:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

**How to get your Google Gemini API key:**
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key to your `.env` file

## 🎯 Usage
1. **Start the Streamlit app:**
   ```bash
   streamlit run app.py
   ```

2. **Open your browser** and navigate to the URL shown in the terminal (usually `http://localhost:8501`)

--- 

## 📝 License
This project is under the MIT License.
