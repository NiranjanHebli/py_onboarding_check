"""
Advanced Financial Tool for AI Startup Employee Benefits.
Features: Indian Number Formatting, Employee Comparison, and Health Scoring.
"""

def format_indian_currency(amount):
    """
    Formats a number into the Indian Lakhs/Crores system (e.g., 12,00,000.00).
    """
    str_amount = f"{amount:.2f}"
    integer_part, decimal_part = str_amount.split(".")
    
    if len(integer_part) <= 3:
        return f"₹{integer_part}.{decimal_part}"
    
    # Last 3 digits remain as a group
    last_three = integer_part[-3:]
    other_digits = integer_part[:-3]
    
    # Remaining digits are grouped in pairs (Lakhs, Crores)
    res = ""
    while len(other_digits) > 2:
        res = "," + other_digits[-2:] + res
        other_digits = other_digits[:-2]
    
    return f"₹{other_digits}{res},{last_three}.{decimal_part}"

def calculate_health_score(rent_ratio, savings_rate, disposable_percent):
    """
    Calculates a health score (0-100) based on financial benchmarks:
    - Rent: < 30% is ideal (40 points)
    - Savings: > 20% is ideal (40 points)
    - Disposable: > 10% is ideal (20 points)
    """
    score = 0
    # Rent Score (Lower is better)
    if rent_ratio <= 30: score += 40
    elif rent_ratio <= 40: score += 20
    
    # Savings Score (Higher is better)
    if savings_rate >= 20: score += 40
    elif savings_rate >= 10: score += 20
    
    # Disposable Score (Higher is better)
    if disposable_percent >= 15: score += 20
    elif disposable_percent >= 5: score += 10
        
    return score

def get_employee_data():
    """Collects and returns a dictionary of employee financial data."""
    name = input("\nEnter Employee Name: ")
    salary = float(input("Annual Salary (₹): "))
    tax_rate = float(input("Tax Bracket (%): "))
    rent = float(input("Monthly Rent (₹): "))
    save_rate = float(input("Savings Goal (%): "))

    # Logic
    m_gross = salary / 12
    m_tax = m_gross * (tax_rate / 100)
    net = m_gross - m_tax
    rent_p = (rent / net) * 100
    save_amt = net * (save_rate / 100)
    disp = net - rent - save_amt
    disp_p = (disp / net) * 100

    return {
        "name": name, "salary": salary, "net": net,
        "rent": rent, "rent_p": rent_p, "save_amt": save_amt,
        "save_p": save_rate, "disp": disp, "disp_p": disp_p,
        "score": calculate_health_score(rent_p, save_rate, disp_p)
    }

def main():
    """Main execution to compare two employees."""
    print("--- Personal Finance Tool: Comparison Mode ---")
    emp1 = get_employee_data()
    emp2 = get_employee_data()

    header = f"{'Metric':<20} | {emp1['name']:<15} | {emp2['name']:<15}"
    sep = "─" * len(header)

    print(f"\n{sep}\n{header}\n{sep}")
    metrics = [
        ("Monthly Net", "net", True),
        ("Rent Paid", "rent", True),
        ("Rent % of Net", "rent_p", False),
        ("Monthly Savings", "save_amt", True),
        ("Health Score", "score", False)
    ]

    for label, key, is_curr in metrics:
        val1 = format_indian_currency(emp1[key]) if is_curr else f"{emp1[key]:.1f}"
        val2 = format_indian_currency(emp2[key]) if is_curr else f"{emp2[key]:.1f}"
        print(f"{label:<20} | {val1:<15} | {val2:<15}")
    print(sep)

if __name__ == "__main__":
    main()