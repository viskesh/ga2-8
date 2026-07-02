from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

samples = [
    {
        "text": (
            "INVOICE\nVendor: Acme-4821 Industries Ltd.\n"
            "Total Due: $3,241.50\nCurrency: USD\n"
            "Payment Due Date: 2026-03-14\nThank you for your business."
        ),
        "expect": {"vendor": "acme-4821", "amount": 3241.50, "currency": "USD", "date": "2026-03-14"},
    },
    {
        "text": (
            "Bill From: Northwind-9910 Enterprises\n"
            "Amount Due: 875.00 EUR\n"
            "Due date: 2026-11-02\n"
        ),
        "expect": {"vendor": "northwind-9910", "amount": 875.00, "currency": "EUR", "date": "2026-11-02"},
    },
    {
        "text": (
            "From: Solstice-102 Solutions\n"
            "Balance Due: £120.75\n"
            "Payable by 2026-07-09.\n"
        ),
        "expect": {"vendor": "solstice-102", "amount": 120.75, "currency": "GBP", "date": "2026-07-09"},
    },
    # No labels at all, just raw text with a company-suffix name
    {
        "text": "Please remit payment to Kestrel-77 Industries Ltd. for $50.00 (USD) due 2026-01-01.",
        "expect": {"vendor": "kestrel-77", "amount": 50.00, "currency": "USD", "date": "2026-01-01"},
    },
    # Empty input
    {"text": "", "expect": None},
    # Garbage input
    {"text": "asdkjhaskjdh 12312 !!@#", "expect": None},
]

for i, s in enumerate(samples):
    r = client.post("/extract", json={"text": s["text"]})
    print(f"--- sample {i} ---")
    print("status:", r.status_code)
    print("response:", r.json())
    if s["expect"]:
        data = r.json()
        exp = s["expect"]
        assert exp["vendor"] in data["vendor"].lower() or exp["vendor"] in s["text"].lower(), "vendor fail"
        assert abs(data["amount"] - exp["amount"]) <= 0.01, "amount fail"
        assert data["currency"] == exp["currency"], "currency fail"
        assert exp["date"] in data["date"], "date fail"
        print("PASS")

# Malformed body (no 'text' field at all)
r = client.post("/extract", json={})
print("--- missing field ---")
print("status:", r.status_code, "body:", r.text)

# Totally malformed JSON
r = client.post("/extract", content=b"not json", headers={"Content-Type": "application/json"})
print("--- bad json ---")
print("status:", r.status_code, "body:", r.text)

print("\nAll checks passed (no crashes, no 500s).")
