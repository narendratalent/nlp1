from fastapi import FastAPI
from pydantic import BaseModel
from ollama import chat
from intent import get_intent_sql

app = FastAPI()

class Question(BaseModel):
    question: str

@app.post("/query")
def query(data: Question):

    question = data.question

    sql_query = get_intent_sql(question.lower())

    if not sql_query:

        prompt = f"""
Generate only MySQL query.

Table: consumer_nlpdata

Question:
{question}
"""

        response = chat(
            model='phi3:mini',
            messages=[
                {
                    'role':'user',
                    'content':prompt
                }
            ]
        )

        sql_query = response['message']['content']
        sql_query = sql_query.replace("```sql","")
        sql_query = sql_query.replace("```","")
        sql_query = sql_query.strip()

    return {
        "sql": sql_query
    }
