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
Description : FEEDER WISE DTR DETAIL, DTR MEANS TRANSFORMER,SS MEANS SUBSTATION, DC MEANS DC NAME WITH COORDINATE LATITUDE LONGITUDE
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

Rules:

1. Return only a valid MySQL query.
2. Never return explanations, comments, markdown, or code fences.
3. Never use JOIN, INNER JOIN, LEFT JOIN, RIGHT JOIN, FULL JOIN, CROSS JOIN, or any subquery involving multiple tables.
4. Use only one table per query.
5. Use LIKE with wildcards (%) when searching feeder names (FDR, FEEDER_NAME).
6. Use LIKE with wildcards (%) when searching transformer names (DTR, DTR_NAME).
7. Use LIKE with wildcards (%) when searching DC names (DC, DC_NAME).
8. Use LIKE with wildcards (%) when searching substation names (SS, SUBSTATION_NAME, SUB STATION).
9. Use LIKE with wildcards (%) when searching consumer names.
10. Use exact match (=) only for codes and IDs such as consumer_no, FDRID, DTRID, location_code, tariff_category.

Location Code Mapping:

* Patan1 = 1444410
* Patan2 = 1444415
* Shahpura = 1444420
* Belkheda = 1444425
* Boriya = 1444460
* Katangi = 1444465

Location Rules:

* Never search location names directly.
* Always convert location names to location_code.
* If user mentions Patan1, use: location_code = '1444410'
* If user mentions Patan2, use: location_code = '1444415'
* If user mentions Shahpura, use: location_code = '1444420'
* If user mentions Belkheda, use: location_code = '1444425'
* If user mentions Boriya, use: location_code = '1444460'
* If user mentions Katangi, use: location_code = '1444465'

Tariff Category Mapping:

* Domestic, Gharelu = LV1
* Non Domestic, CLF = LV2
* Street Light, STLT, Water Works, WW, Nagar Nigam = LV3
* Industrial, IP = LV4
* Agriculture, Pump = LV5
* EV Station, Electric Charging = LV6

Tariff Rules:

* Never search tariff names directly.
* Always convert tariff names to tariff_category.
* Domestic or Gharelu → tariff_category = 'LV1'
* Non Domestic or CLF → tariff_category = 'LV2'
* Street Light, STLT, Water Works, WW, Nagar Nigam → tariff_category = 'LV3'
* Industrial or IP → tariff_category = 'LV4'
* Agriculture or Pump → tariff_category = 'LV5'
* EV Station or Electric Charging → tariff_category = 'LV6'

Query Construction Rules:

* If multiple filters are mentioned, combine them using AND.
* Use COUNT(*) for total/count questions.
* Use SUM(net_bill) for bill total questions.
* Use SUM(arrear) for arrear total questions.
* Use ORDER BY and LIMIT when user asks for top/highest/lowest records.
* Generate only executable MySQL query output.


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
