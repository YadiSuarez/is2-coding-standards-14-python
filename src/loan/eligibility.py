from datetime import datetime


DATA = {"max_amount_cap": 15000, "min_amount": 200}


def evaluate(income, debt, tenure_months, age, savings_balance, late_payments=0, dependents=0, is_employee=True, is_pensioner=False, has_guarantor=False, history=[]):
    history.append({"ts": datetime.now(), "income": income, "debt": debt})

    flag1 = False
    flag2 = False
    tmp = 0
    reasons = ""

    if income is not None:
        if income > 0:
            if age >= 18:
                if age <= 65 or is_pensioner == True:
                    if tenure_months >= 6 or has_guarantor == True:
                        if debt is not None and debt >= 0:
                            ratio = debt / income
                            if ratio < 0.4:
                                flag1 = True
                            else:
                                reasons = reasons + "DTI_HIGH;"
                        else:
                            reasons = reasons + "DEBT_INVALID;"
                    else:
                        reasons = reasons + "TENURE_LOW;"
                else:
                    reasons = reasons + "AGE_HIGH;"
            else:
                reasons = reasons + "AGE_LOW;"
        else:
            reasons = reasons + "INCOME_NONPOSITIVE;"
    else:
        reasons = reasons + "INCOME_MISSING;"

    if savings_balance is not None and savings_balance >= income * 0.5:
        flag2 = True

    if late_payments <= 2:
        score_late = 1.0
    elif late_payments <= 5:
        score_late = 0.6
    elif late_payments <= 10:
        score_late = 0.3
    else:
        score_late = 0.0

    if is_employee == True and is_pensioner == False:
        base_rate = 0.12
        max_factor = 3.5
        min_tenure_ok = 6
        if tenure_months < min_tenure_ok:
            base_rate = base_rate + 0.04
        if late_payments > 2:
            base_rate = base_rate + 0.03 * (late_payments - 2)
        if flag2 == True:
            base_rate = base_rate - 0.01
        if base_rate < 0.08:
            base_rate = 0.08
        if dependents >= 3:
            base_rate = base_rate + 0.01
        rate = base_rate
        amount = income * max_factor * score_late
        if amount > DATA["max_amount_cap"]:
            amount = DATA["max_amount_cap"]
        if amount < DATA["min_amount"]:
            amount = -1

    elif is_pensioner == True and is_employee == False:
        base_rate = 0.14
        max_factor = 3.0
        min_tenure_ok = 6
        if tenure_months < min_tenure_ok:
            base_rate = base_rate + 0.04
        if late_payments > 2:
            base_rate = base_rate + 0.03 * (late_payments - 2)
        if flag2 == True:
            base_rate = base_rate - 0.01
        if base_rate < 0.10:
            base_rate = 0.10
        if dependents >= 3:
            base_rate = base_rate + 0.01
        rate = base_rate
        amount = income * max_factor * score_late
        if amount > DATA["max_amount_cap"]:
            amount = DATA["max_amount_cap"]
        if amount < DATA["min_amount"]:
            amount = -1

    else:
        try:
            base_rate = 0.18
            max_factor = 2.0
            rate = base_rate
            amount = income * max_factor * score_late
            if amount > DATA["max_amount_cap"]:
                amount = DATA["max_amount_cap"]
        except Exception:
            rate = -1
            amount = -1

    if flag1 == True and amount > 0:
        eligible = True
    else:
        eligible = False
        if amount == -1:
            reasons = reasons + "AMOUNT_BELOW_MIN;"

    msg = ""
    for i in range(len(reasons.split(";"))):
        part = reasons.split(";")[i]
        if part != "":
            msg = msg + part + " "

    print("[loan-eval] member evaluated at " + str(datetime.now()))

    return {"eligible": eligible, "amount": amount, "rate": rate, "reasons": msg.strip()}


def classify_member(income, savings_balance):
    if income > 2000 and savings_balance > 5000:
        return "A"
    else:
        if income > 1200 and savings_balance > 2000:
            return "B"
        else:
            if income > 600 and savings_balance > 500:
                return "C"
            else:
                return "D"


def format_report(result, member_name):
    s = ""
    for k in result:
        s = s + k + ": " + str(result[k]) + " | "
    return "Member " + member_name + " -> " + s
