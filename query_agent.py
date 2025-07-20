import google.generativeai as genai
import os
import json
import re
from dotenv import load_dotenv
import datetime
import streamlit as st
from decimal import Decimal

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

SCHEMAS = {
    "public": """
    Tables in Pagila:

    - public.actor(actor_id, first_name, last_name, last_update)
    - public.address(address_id, address, address2, district, city_id, postal_code, phone, last_update)
    - public.category(category_id, name, last_update)
    - public.city(city_id, city, country_id, last_update)
    - public.country(country_id, country, last_update)
    - public.customer(customer_id, store_id, first_name, last_name, email, address_id, activebool, create_date, last_update, active)
    - public.film(film_id, title, description, release_year, language_id, rental_duration, rental_rate, length, replacement_cost, rating, last_update, special_features, fulltext)
    - public.film_actor(actor_id, film_id, last_update)
    - public.film_category(film_id, category_id, last_update)
    - public.inventory(inventory_id, film_id, store_id, last_update)
    - public.language(language_id, name, last_update)
    - public.payment(payment_id, customer_id, staff_id, rental_id, amount, payment_date)
    - public.rental(rental_id, rental_date, inventory_id, customer_id, return_date, staff_id, last_update)
    - public.staff(staff_id, first_name, last_name, address_id, email, store_id, active, username, password, last_update, picture)
    - public.store(store_id, manager_staff_id, address_id, last_update)
    """
}

def extract_json(response):
    try:
        match = re.search(r"{[\s\S]+}", response)
        if match:
            return json.loads(match.group())
        return {}
    except json.JSONDecodeError:
        return {}

def english_to_sql(prompt, chat_context=None):
    if re.search(r'\b(format|clean|style|table|tabular|list|bullets|rewrite|shorter|rephrase|reword|simplify|again|visual|text-based|in text|as table|re-display)\b', prompt, re.IGNORECASE):
        last_data = st.session_state.get("last_result")
        if not last_data:
            return {
                "sql": None,
                "follow_up": None,
                "force_format_response": "I'm sorry, I can't reformat because there is no recent data available. Can you please restate your original question?"
            }

        return {
            "sql": None,
            "follow_up": None,
            "force_format_response": {
                "question": last_data["question"],
                "columns": last_data["columns"],
                "rows": last_data["rows"],
                "format_hint": prompt
            }
        }

    history_text = ""
    if chat_context:
        for entry in reversed(chat_context):
            history_text += f"User: {entry['user']}\nBot: {entry.get('response', '')}\n"

    schema_text = "\n\n".join([f"Schema ({name}):\n{definition}" for name, definition in SCHEMAS.items()])

    full_prompt = f"""
You are an intelligent SQL generator assistant for multiple PostgreSQL schemas.

{schema_text}

Always use PostgreSQL-compatible datetime functions like EXTRACT(), DATE_TRUNC(), and TO_CHAR() instead of SQLite functions like strftime().

Your task:
1. Analyze the user's question.
2. Identify which schema it belongs to.
3. Return ONLY a JSON with:
   {{
        "schema": "schema_name or null",
        "sql": "PostgreSQL SQL query string or null",
        "response": "Short natural-language placeholder answer (e.g., 'Sure, let me get that for you.')",
        "follow_up": "suggested helpful follow-up question or null"
    }}

But DO NOT include actual DB results in this stage.

- Always be aware that certain terms or phrases (e.g., "maximum duration", "total amount", "count", "usage", "activity") can have **multiple interpretations** depending on context.

Strict Rules:
- Return only the JSON — no markdown, headers, or extra commentary.
- Use **schema-qualified table names** (e.g., `public.customer`) — no unqualified names.
- Use schema-qualified table names (e.g., public.inventory) — but **do not duplicate the schema**.
- Always write **PostgreSQL-compatible queries** — use functions like `EXTRACT()`, `DATE_TRUNC()`, `TO_CHAR()` instead of SQLite functions like `strftime()`.
- Do not guess at database values or include sample output — just write correct SQL.
- Do NOT say "no data available" unless you're specifically told there is no matching row.


Query Design:
- For date-based filters, use:
   - `EXTRACT(YEAR FROM column) = 2022`, or
   - `column BETWEEN '2022-01-01' AND '2022-12-31'`
- Do not use `YEAR(column)` or non-standard SQL.

Handle Ambiguity Carefully:
- Certain terms (like "duration", "count", "usage", "activity", "amount") may have multiple meanings.
- When such a term appears:
   1. Infer the most likely intent from the current user question.
   2. Check if the meaning differs from earlier questions in the conversation.
   3. If ambiguous, clearly explain the logic you're using **in the 'response' field**.
   4. Make sure to include all the possible paths for reaching to a total of something
   For example (this is ONLY an example):
   If you are asked to tell which stores have a total revenue of $5000, then you are supposed to follow the full pathway of calculating total revenue which would include calculating the earning by store managers, rentals, inventory etc. 

- If the user switches from talking about one entity (like "product") to another (like "customer"), and reuses similar terms (e.g., "usage", "duration", "amount"), you must clarify whether their intent has shifted.

- In all such cases, briefly explain the **contextual meaning** of the value you're returning, and what field or logic it came from.
- Use `INNER JOIN` unless `LEFT JOIN` is clearly needed (e.g., showing items with no matches).
- Never guess field names — rely on schema definitions.

- DO NOT REPLY WITH NO DATA AVAILABLE UNLESS THERE IS ACTUALLY NO DATA.

 Examples:
- "duration" might mean:
   - A predefined column value,
   - A calculated value (e.g., end_time - start_time),
   - A user-defined filter (e.g., sessions longer than 30 minutes)

- If the user shifts context (e.g., from "film" to "customer") but keeps using words like "amount" or "usage", your interpretation must also shift accordingly — and you must reflect that in the explanation.

Conversation so far:
{history_text}
User: {prompt}
"""

    try:
        response = model.generate_content(full_prompt).text
        return extract_json(response)
    except Exception:
        return {
            "schema": None,
            "sql": None,
            "response": "Sorry, I couldn't process that.",
            "follow_up": None
        }

def generate_final_response(user_question, columns, rows):
    rows_json = []
    for r in rows:
        row_dict = {}
        for col, val in zip(columns, r):
            if isinstance(val, datetime.timedelta):
                days = val.days
                hours = val.seconds // 3600
                minutes = (val.seconds % 3600) // 60
                text = f"{days} days"
                if hours:
                    text += f", {hours} hours"
                if minutes:
                    text += f", {minutes} minutes"
                row_dict[col] = text
            elif isinstance(val, (datetime.datetime, datetime.date)):
                row_dict[col] = val.isoformat()
            elif isinstance(val, (float, Decimal)):
                row_dict[col] = round(float(val), 2)
            else:
                row_dict[col] = val
        rows_json.append(row_dict)

    formatted_data = json.dumps(rows_json, separators=(',', ':'))

    formatting_prompt = f"""
You are a helpful assistant. Given the user's question and the database results in JSON, return a clean, readable answer.

IMPORTANT:
- You must base your answer strictly on the exact keys and values provided in the JSON.
- Do not assume missing data or exclude fields unless they are truly absent.
- If 'first_name' and 'last_name' are present, use both.
- Do not generalize based on partial values.
- Do not say “no data available” unless you're sure the previous result had no relevant entity.

If the user question includes words like pie chart, bar chart, line chart, plot, or visualize:
- Do NOT attempt to convert or assume chart data.
- Instead, politely respond that visual/chart-based outputs are not available here.

- If the user explicity mentions 'table', 'tabular' then make a table of the data and represent it.
Correct format:
| Title | Value |
|       |       |
|       |       |

- IF THE RESPONSE IS GOING TO HAVE MORE THAN 3 ROWS AND HAS 3 COLUMNS ATLEAST, RETURN THE ANSWER IN FORM OF A USER- FRIENDLY TABLE.

- If the user does not mention any format particularly, then THINK YOURSELF ABOUT THE MOST SUITABLE FORMAT AND RESPOND WITH THAT.

- If the user refers to "that customer", "her", or "him", assume it refers to the most recent person or entity mentioned in the previous result.

If user asks to reformat previously given data:
- Do NOT reinterpret or regenerate data from scratch. Instead, reuse exactly what was shown before.

- IF YOU DO NOT HAVE DATA FOR ANY QUESTION AND CANNOT RETURN A PROPER ANSWER JUST SAY THAT ' I dont have any data for this question'. DO NOT GIVE ME ANSWERS OF THE PREVIOUS QUESTION TILL IT IS REFERRED TO EVEN IF THE QUESTIONS HAVE SIMILAR WORDS OR TERMS.
- DO NOT SAY THAT YOU DO NOT HAVE DATA AVAILABLE WITHOUT CROSS CHECKING FOR THE DATA IN THE DATABASE.

Ensure the result:
- Has minimal vertical whitespace.
- Avoids blank lines before tables.
- Avoids guessing unrelated summaries.
- Avoid having unnecessary extra spaces between your answers or line breaks between words.
- Make sure that the answers always have a proper structure. Do NOT give an unstructured answer.
- Is structured consistently based on result size:
  - If only 1 row and ≤3 columns → summary sentence.
  - If 2-4 columns and ≤20 rows → markdown table.
  - If >20 rows or 1 column → bullet list or expander if long.

- FOR A ANSWER IN FORM OF TABLE, MAKE SURE IT ALWAYS REMAINS A TABLE EVEN IF THE QUESTION IS REPEATED LATER ON.
User Question:
{user_question}

Database Results:
{formatted_data}

If the result has exactly one row and 3 or fewer columns, you MUST respond with a summary sentence.

Return the cleaned, user-friendly answer only:
"""

    try:
        response = model.generate_content(formatting_prompt)
        raw_response = response.text.strip()

        cleaned_response = re.sub(r'\n{3,}', '\n\n', raw_response)
        cleaned_response = re.sub(r'(\n\s*)+\Z', '', cleaned_response)
        cleaned_response = re.sub(r' +\n', '\n', cleaned_response)


        st.session_state["last_result_summary"] = {
            "columns": columns,
            "rows": rows_json,
            "user_question": user_question
        }

        entities = []
        if rows_json and columns:
            top_row = rows_json[0]
            for col in columns:
                val = top_row.get(col)
                if isinstance(val, str) and val.isalpha():
                    entities.append(val)

        st.session_state["last_result_entities"] = entities


        return cleaned_response
    except Exception as e:
        return f"Error formatting response: {e}"


def format_row_data(rows):
    formatted = []
    for row in rows:
        new_row = []
        for item in row:
            if isinstance(item, str) and "T" in item and "+" in item:
                try:
                    dt = datetime.fromisoformat(item)
                    item = dt.strftime("%B %d, %Y at %I:%M %p UTC%z")
                except:
                    pass 

            if isinstance(item, float):
                item = f"${item:.2f}"

            new_row.append(item)
        formatted.append(new_row)
    return formatted


def gemini_direct_answer(prompt, chat_context=None):

    history_text = ""
    if chat_context:
        for entry in reversed(chat_context[-1:]):
            history_text += f"User: {entry['user']}\nBot: {entry.get('response', '')}\n"

    if "last_result_summary" in st.session_state:
        last_summary = st.session_state["last_result_summary"]
        columns = last_summary.get("columns", [])
        rows = last_summary.get("rows", [])
        last_user_q = last_summary.get("user_question", "")
        formatted_rows = format_row_data(rows[:5]) if rows else []
        preview = json.dumps(formatted_rows, indent=2)
        colnames = ", ".join(columns) if columns else "none"

        entities_info = ""
        if "last_result_entities" in st.session_state and st.session_state["last_result_entities"]:
            top_entities = ", ".join(st.session_state["last_result_entities"][:5])
            entities_info = f"\nThe last result included key values such as: {top_entities}."

        result_context = f"""
            The last structured query came from the question: '{last_user_q}'.
            It returned the following columns: {colnames}.{entities_info}

Sample of the data:
{preview}
"""
    else:
        result_context = "There is no structured result saved from the last query."

    full_prompt = f"""
You are a helpful conversational assistant. Use the conversation history and the result context to understand what the user is referring to.

Important:
- If the user says things like "this data", "that table", "filter this", etc., refer to the **most recent structured query output** (columns and context).
- Do NOT make up data or regenerate summaries unless explicitly asked.
- If unsure, politely ask the user to clarify what data they want to continue with.
- Only use previous result if user's follow-up clearly refers to it using overlapping terms (e.g. "this", "these", "filter", or repeats previous columns/entities).
- If user's new question is **independent**, answer it fresh without using the last result.
- If the user's query is a clarification/confirmation like "are you sure?", "is that correct?", "can you verify?", then respond accordingly:
   - Confirm the based on the last result if you are confident.
   - Or say: "Let me double-check..." and re-evaluate the last result.
- Avoid using outdated context unless the user explicitly refers back to an earlier topic.
- Do NOT say "I don't know" if the data is present.
- Only say "no data available" if the last result clearly lacks that field or row.
- If a new question is unrelated (e.g., changes topic completely), start fresh.
- IF YOU DO NOT HAVE DATA FOR ANY QUESTION AND CANNOT RETURN A PROPER ANSWER JUST SAY THAT ' I dont have any data for this question'. DO NOT GIVE ME ANSWERS OF THE PREVIOUS QUESTION TILL IT IS REFERRED TO EVEN IF THE QUESTIONS HAVE SIMILAR WORDS OR TERMS.

- Always be aware that certain terms or phrases (e.g., "maximum duration", "total amount", "count", "usage", "activity") can have **multiple interpretations** depending on context.
- If you detect ambiguity (e.g., "duration" could mean predefined vs calculated), briefly clarify what you're using.

- When such a term appears, do the following:
   1. Infer the most likely meaning based on the **current question**, and
   2. Compare it to what was previously asked in the conversation.
   3. If the meaning may differ (e.g., the same word could refer to a different table or concept), clearly **explain the distinction**.

- If there are timestamps like "2022-07-27T16:09:20.739759+05:30", convert them to readable date formats like "July 27, 2022 at 4:09 PM (IST)"
- If showing monetary values, format them as $x.xx (e.g., "$2.99")
- The final answer containing both should be in form a sentence which is user- friendly so that it is legible to the user.
- MAKE SURE THAT ANY Questions including time date are responded in proper time date format which is user friendly.
- IF THE DURATION IS LARGE THEN CHOOSE APPROPRIATE WAY OF ANSWERING THE DURATION WHICH IS USER- FRIENDLY AND IS EASIER TO UNDERSTAND.


-If the user uses pronouns like "he", "she", or "they", resolve them based on the last mentioned entity in `last_result_entities`, if available. Do not switch to unrelated earlier answers.

- For example, "duration" might refer to:
   - A **predefined value** stored in a metadata table,
   - A **computed value** based on timestamps (e.g., end_time - start_time),
   - A **user-defined period**, based on filters or ranges.

- If the user switches from talking about one entity (like "product") to another (like "customer"), and reuses similar terms (e.g., "usage", "duration", "amount"), you must clarify whether their intent has shifted.

- In all such cases, briefly explain the **contextual meaning** of the value you're returning, and what field or logic it came from.

{result_context}


Conversation history:
{history_text}

User: {prompt}
"""

    try:
        response = model.generate_content(full_prompt)
        return response.text.strip()
    except Exception as e:
        return f"Gemini error: {e}"


