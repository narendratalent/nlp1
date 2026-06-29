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

# Table Selection Rules

## consumer_nlpdata

Use this table whenever the question contains:

* consumer
* consumer list
* consumer details
* consumer count
* consumer number
* consumer name
* consumer status
* mobile number
* address
* bill
* net bill
* arrear
* billed unit
* tariff
* location code

Columns

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

---

## patandfrdtr

Use this table whenever the question contains:

* feeder
* feeder list
* feeder details
* transformer
* DTR
* substation
* SS
* DC
* DC name
* feeder capacity
* pole latitude
* pole longitude

Columns

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

---

## vigillance

Use this table whenever the question contains:

* vigillance
* vigilance
* panchnama
* inspection
* enforcement
* theft case
* billed amount
* payment received
* load
* compounding
* civil liability
* court rebate

Columns

circle
division
dc
panchnama_number
inspection_date
emp_cd
person_name
person_address
mobile_no
father_name
vigillance_team
billed_unit
total_calculated_load_in_kw
energy_charge
fixed_charge
fca
duty
civil_lia_amount
compounding_amount
court_rebate
billed_amount
payment_received
case_name
tariff_name

---

# Search Rules

Use LIKE '%value%' for

* consumer_name
* address1
* address2
* division
* DC
* SS
* FDR
* DTR
* person_name
* father_name
* person_address
* vigillance_team
* tariff_name
* case_name
* panchnama_number

Use exact match (=) for

consumer_no
location_code
group_no
rd_no
DCID
DIVCODE
FDRID
DTRID
emp_cd

---

# Location Mapping

Patan1
Patan 1
Patan-1

location_code='1444410'

Patan2
Patan 2
Patan-2

location_code='1444415'

Shahpura

location_code='1444420'

Belkheda

location_code='1444425'

Boriya

location_code='1444460'

Katangi

location_code='1444465'

Never search these names directly in consumer_nlpdata.

Always convert them to location_code.

---

# Tariff Mapping

Domestic
Gharelu

LV1

Non Domestic
CLF

LV2

Street Light
STLT
Water Works
WW
Nagar Nigam

LV3

Industrial
IP

LV4

Agriculture
Pump

LV5

EV Station
Charging

LV6

Always convert tariff names to tariff_category.

---

# Important Rules


If the question contains

feeder
transformer
substation
DC details

always use patandfrdtr.

If the question contains

panchnama
inspection
vigillance
enforcement

always use vigillance.

Never use JOIN.

Never use multiple tables.

Generate only one SQL query.

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
