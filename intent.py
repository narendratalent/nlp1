import re

def get_intent_sql(question):

    print(question)

    question = question.lower()

    # ==========================
    # ARREAR GREATER THAN AMOUNT
    # ==========================

    if (
        ("arrear" in question or "arrears" in question)
        and (
            "above" in question
            or "greater than" in question
            or "more than" in question
        )
    ):

        amount = None

        # 1 lakh, 2 lakh, 5 lakh
        lakh_match = re.search(r'(\d+)\s*lakh', question)
        if lakh_match:
            amount = int(lakh_match.group(1)) * 100000

        # 10 thousand, 25 thousand
        thousand_match = re.search(r'(\d+)\s*thousand', question)
        if thousand_match:
            amount = int(thousand_match.group(1)) * 1000

        # 5000, 10000, 25000
        if amount is None:
            number_match = re.search(r'(\d+)', question)
            if number_match:
                amount = int(number_match.group(1))

        if amount:

            status_condition = ""

            if "active" in question or "connected" in question:
                status_condition = "AND consumer_status IN ('ACTIVE','CONNECTED')"

            elif "inactive" in question or "pdc" in question:
                status_condition = "AND consumer_status IN ('INACTIVE','PDC')"

            return f"""
            SELECT
                location_code,
                group_no,
                rd_no,
                consumer_no,
                consumer_name,
                address1,
                address2,
                mobile_no,
                consumer_status,
                arrear,
                net_bill
            FROM consumer_data
            WHERE arrear > {amount}
            {status_condition}
            ORDER BY arrear DESC
            """

    # ==========================
    # TOP ARREAR CONSUMERS
    # ==========================

    elif (
        ("arrear" in question or "arrears" in question)
        and ("top" in question or "highest" in question or "maximum" in question)
        and not (
            "active" in question
            or "connected" in question
            or "inactive" in question
            or "pdc" in question
        )
    ):

        return """
        SELECT location_code,group_no,rd_no,
               consumer_no,consumer_name,
               address1,address2,
               mobile_no,arrear,net_bill
        FROM consumer_data
        ORDER BY arrear DESC
        LIMIT 10
        """

    # ==========================
    # TOP INACTIVE/PDC ARREAR
    # ==========================

    elif (
        ("arrear" in question or "arrears" in question)
        and ("top" in question or "highest" in question or "maximum" in question)
        and ("inactive" in question or "pdc" in question)
    ):

        return """
        SELECT location_code,group_no,rd_no,
               consumer_no,consumer_name,
               address1,address2,
               mobile_no,arrear,net_bill
        FROM consumer_data
        WHERE consumer_status IN ('INACTIVE','PDC')
        ORDER BY arrear DESC
        LIMIT 10
        """

    # ==========================
    # TOP ACTIVE/CONNECTED ARREAR
    # ==========================

    elif (
        ("arrear" in question or "arrears" in question)
        and ("top" in question or "highest" in question or "maximum" in question)
        and ("active" in question or "connected" in question)
    ):

        return """
        SELECT location_code,group_no,rd_no,
               consumer_no,consumer_name,
               address1,address2,
               mobile_no,arrear,net_bill
        FROM consumer_data
        WHERE consumer_status IN ('ACTIVE','CONNECTED')
        ORDER BY arrear DESC
        LIMIT 10
        """

    # ==========================
    # TOP BILL CONSUMERS
    # ==========================

    elif (
        ("bill" in question)
        and ("top" in question or "highest" in question or "maximum" in question)
    ):

        return """
        SELECT location_code,group_no,rd_no,
               consumer_no,consumer_name,
               address1,address2,
               mobile_no,net_bill
        FROM consumer_data
        ORDER BY net_bill DESC
        LIMIT 10
        """

    return None