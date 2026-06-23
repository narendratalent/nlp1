from fastapi import FastAPI
from pydantic import BaseModel
from groq import Groq
import os
from intent import get_intent_sql

app = FastAPI()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


class Question(BaseModel):
    question: str


@app.get("/")
def home():
    return {"status": "running"}


@app.post("/query")
def query(data: Question):

    question = data.question
    print("QUESTION:", question)

    sql_query = get_intent_sql(question.lower())

    if sql_query:
        print("INTENT MATCHED")
        return {"sql": sql_query}

    print("CALLING GROQ")

    try:

        prompt = f"""
Generate only MySQL query.

Table: consumer_nlpdata

Columns:
consumer_no
division
location_code
group_no
rd_no
consumer_name
consumer_status
tariff_category
address1
address2
mobile_no
net_bill
arrear
billed_unit

Table: patandfrdtr
Description : FEEDER WISE DTR DETAIL, DTR MEANS TRANSFORMER WITH COORDINATE LATITUDE LONGITUDE
Columns:
DIVCODE
DCID
DC
SS
FDR
FDRID
DTRID
DTR
DTRCP
DTRCAP
POLELAT
POLELONG
FDRTYPE

Question:
{question}
"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )

        sql_query = response.choices[0].message.content.strip()

        sql_query = sql_query.replace("```sql", "")
        sql_query = sql_query.replace("```", "")

        print("GROQ SQL:", sql_query)

        return {"sql": sql_query}

    except Exception as e:

        print("GROQ ERROR:", str(e))

        return {"error": str(e)}
