"""
Personal Finance Tool for AI Startup Employee Benefits Portal.
This module calculates monthly financial breakdowns, tax deductions,
and annual projections based on employee input.
"""

def get_validated_input(prompt, min_val=None, max_val=None):
    """
    Prompts the user for a float input and validates it against bounds.

    Args:
        prompt (str): The text to display to the user.
        min_val (float): The minimum allowable value.
        max_val (float): The maximum allowable value.

    Returns:
        float: The validated user input.
    """
    while True:
        try:
            value = float(input(prompt))
            if min_val is not None and value <= min_val:
                print(f"Error: Value must be greater than {min_val}.")
                continue
            if max_val is not None and value > max_val:
                print(f"Error: Value cannot exceed {max_val}.")
                continue
            return value
        except ValueError:
            print("Error: Please enter a valid numerical decimal.")

def calculate_finance_data(salary, tax_rate, rent, savings_rate):
    """
    Performs financial calculations based on raw inputs.

    Returns:
        dict: A dictionary containing calculated financial metrics.
    """
    monthly_gross = salary / 12
    monthly_tax = monthly_gross * (tax_rate / 100)
    net_salary = monthly_gross - monthly_tax
    rent_ratio = (rent / net_salary) * 100 if net_salary > 0 else 0
    savings_amount = net_salary * (savings_rate / 100)
    disposable = net_salary - rent - savings_amount

    return {
        "monthly_gross": monthly_gross,
        "monthly_tax": monthly_tax,
        "net_salary": net_salary,
        "rent_ratio": rent_ratio,
        "savings_amount": savings_amount,
        "disposable": disposable,
        "annual_tax": monthly_tax * 12,
        "annual_savings": savings_amount * 12,
        "annual_rent": rent * 12
    }

def display_report(name, salary, tax_rate, rent, savings_rate, data):
    """
    Generates and prints a professionally formatted f-string report.
    """
    line_heavy = "════════════════════════════════════════════"
    line_light = "────────────────────────────────────────────"

    print(line_heavy)
    print("EMPLOYEE FINANCIAL SUMMARY")
    print(line_heavy)
    print(f"Employee        : {name}")
    print(f"Annual Salary   : ₹{salary:,.2f}")
    print(line_light)
    print("Monthly Breakdown:")
    print(f"Gross Salary    : ₹ {data['monthly_gross']:,.2f}")
    print(f"Tax ({tax_rate:.1f}%)    : ₹ {data['monthly_tax']:,.2f}")
    print(f"Net Salary      : ₹ {data['net_salary']:,.2f}")
    print(f"Rent            : ₹ {rent:,.2f} ({data['rent_ratio']:.1f}% of net)")
    print(f"Savings ({savings_rate:.1f}%) : ₹ {data['savings_amount']:,.2f}")
    print(f"Disposable      : ₹ {data['disposable']:,.2f}")
    print(line_light)
    print("Annual Projection:")
    print(f"Total Tax       : ₹ {data['annual_tax']:,.2f}")
    print(f"Total Savings   : ₹ {data['annual_savings']:,.2f}")
    print(f"Total Rent      : ₹ {data['annual_rent']:,.2f}")
    print(line_heavy)

def main():
    """
    Orchestrates the program flow: input, calculation, and output.
    """
    print("Welcome to the Employee Benefits Portal - Finance Tool\n")

    emp_name = input("Enter Employee Name: ").strip()
    ann_salary = get_validated_input("Enter Annual Salary: ₹", min_val=0)
    tax_bracket = get_validated_input("Enter Tax Bracket (%): ", min_val=0, max_val=50)
    monthly_rent = get_validated_input("Enter Monthly Rent: ₹", min_val=0)
    save_goal = get_validated_input("Enter Savings Goal (%): ", min_val=0, max_val=100)

    results = calculate_finance_data(ann_salary, tax_bracket, monthly_rent, save_goal)

    display_report(emp_name, ann_salary, tax_bracket, monthly_rent, save_goal, results)

if __name__ == "__main__":
    main()