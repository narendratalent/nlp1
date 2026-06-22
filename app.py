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
    print("QUESTION:", question)
    sql_query = get_intent_sql(question.lower())
    if sql_query:
        print("INTENT MATCHED")
        return {"sql": sql_query}

    print("CALLING OLLAMA")
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
        """

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
        print("OLLAMA RESPONSE:", response)

        sql_query = response['message']['content']
        sql_query = sql_query.replace("```sql","")
        sql_query = sql_query.replace("```","")
        sql_query = sql_query.strip()

        return {
        "sql": sql_query
        }
    except Exception as e:

        print("OLLAMA ERROR:", str(e))

        return {
            "error": str(e)
        }
