import pytest
from loan.eligibility import evaluate, classify_member


def test_employee_eligible_basic():
    r = evaluate(income=1500, debt=400, tenure_months=24, age=30, savings_balance=800, is_employee=True, is_pensioner=False)
    assert r["eligible"] is True
    assert r["amount"] > 0


def test_employee_high_dti_rejected():
    r = evaluate(income=1000, debt=500, tenure_months=24, age=30, savings_balance=200, is_employee=True, is_pensioner=False)
    assert r["eligible"] is False
    assert "DTI_HIGH" in r["reasons"]


def test_age_too_low():
    r = evaluate(income=1500, debt=200, tenure_months=12, age=17, savings_balance=500, is_employee=True, is_pensioner=False)
    assert r["eligible"] is False
    assert "AGE_LOW" in r["reasons"]


def test_age_too_high_unless_pensioner():
    r = evaluate(income=1500, debt=200, tenure_months=12, age=70, savings_balance=500, is_employee=True, is_pensioner=False)
    assert r["eligible"] is False
    assert "AGE_HIGH" in r["reasons"]


def test_pensioner_over_65_accepted():
    r = evaluate(income=1500, debt=200, tenure_months=12, age=70, savings_balance=500, is_employee=False, is_pensioner=True)
    assert r["eligible"] is True


def test_short_tenure_with_guarantor_passes():
    r = evaluate(income=1500, debt=200, tenure_months=3, age=30, savings_balance=500, has_guarantor=True, is_employee=True, is_pensioner=False)
    assert r["eligible"] is True


def test_short_tenure_without_guarantor_rejected():
    r = evaluate(income=1500, debt=200, tenure_months=3, age=30, savings_balance=500, has_guarantor=False, is_employee=True, is_pensioner=False)
    assert r["eligible"] is False
    assert "TENURE_LOW" in r["reasons"]


def test_employee_rate_floor():
    r = evaluate(income=3000, debt=300, tenure_months=60, age=40, savings_balance=5000, late_payments=0, is_employee=True, is_pensioner=False)
    assert r["rate"] >= 0.08


def test_pensioner_rate_floor():
    r = evaluate(income=2000, debt=200, tenure_months=60, age=70, savings_balance=5000, late_payments=0, is_employee=False, is_pensioner=True)
    assert r["rate"] >= 0.10


def test_late_payments_increase_rate():
    a = evaluate(income=1500, debt=200, tenure_months=24, age=30, savings_balance=300, late_payments=0, is_employee=True, is_pensioner=False)
    b = evaluate(income=1500, debt=200, tenure_months=24, age=30, savings_balance=300, late_payments=8, is_employee=True, is_pensioner=False)
    assert b["rate"] > a["rate"]


def test_amount_capped():
    r = evaluate(income=20000, debt=100, tenure_months=60, age=40, savings_balance=50000, is_employee=True, is_pensioner=False)
    assert r["amount"] <= 15000


def test_classify_member_top():
    assert classify_member(2500, 6000) == "A"


def test_classify_member_bottom():
    assert classify_member(300, 100) == "D"
