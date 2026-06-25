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

Table: vigillance
description: vigillance means enforcement detail or panchnama

Columns:

* circle
* division
* dc
* panchnama_number
* inspection_date
* emp_cd
* person_name
* person_address
* mobile_no
* father_name
* vigillance_team
* billed_unit
* total_calculated_load_in_kw
* energy_charge
* fixed_charge
* fca
* duty
* civil_lia_amount
* compounding_amount
* court_rebate
* billed_amount
* payment_received
* case_name
* tariff_name

Rules:

1. Return only MySQL SELECT queries.
2. Never generate INSERT, UPDATE, DELETE, DROP, ALTER, CREATE or TRUNCATE queries.
3. Use LIKE '%value%' for text searches.
4. Search person names in column person_name.
5. Search father names in column father_name.
6. Search mobile numbers in column mobile_no.
7. Search addresses in column person_address.
8. Search employee codes in column emp_cd.
9. Search vigillance team names in column vigillance_team.
10. Search tariff names in column tariff_name.
11. Search case names in column case_name.
12. Search panchnama numbers in column panchnama_number.
13. Use inspection_date for date filtering.
14. For billed amount use column billed_amount.
15. For payment received use column payment_received.
16. For billed units use column billed_unit.
17. For load use column total_calculated_load_in_kw.
18. For energy charge use column energy_charge.
19. For fixed charge use column fixed_charge.
20. For FCA use column fca.
21. For duty use column duty.
22. For civil liability amount use column civil_lia_amount.
23. For compounding amount use column compounding_amount.
24. For court rebate use column court_rebate.
25. 3. Use LIKE '%value%' for panchnama number searches.

Examples:

User: Show all consumers from Patan division
SQL:
SELECT * FROM vigillance
WHERE division LIKE '%Patan%';

User: Show all consumers from Patan1 dc or patan 1 dc
SQL:
SELECT * FROM vigillance
WHERE dc LIKE '%patan-1%';

User: Show billed amount greater than 50000
SQL:
SELECT * FROM vigillance
WHERE billed_amount > 50000;

User: Show payment received less than 10000
SQL:
SELECT * FROM vigillance
WHERE payment_received < 10000;

User: Show consumer mobile number 9876543210
SQL:
SELECT * FROM vigillance
WHERE mobile_no LIKE '%9876543210%';

User: Show panchanama between 01-04-2024 to 01-04-2025
SQL:
SELECT * FROM vigillance WHERE inspection_date BETWEEN '01-04-2024' AND '01-04-2025'

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
