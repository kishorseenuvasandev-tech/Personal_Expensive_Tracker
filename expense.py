import sqlite3


def add_expense():

    print("========== ADD EXPENSE ==========")

    expense_name = input("Enter expense name: ")
    category = input("Enter category: ")
    amount = float(input("Enter amount: "))

    if amount <= 0:
        print("Invalid amount!")
        return

    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO expenses (expense_name, category, amount)
        VALUES (?, ?, ?)
    """, (expense_name, category, amount))

    conn.commit()
    conn.close()

    print("\nExpense Added Successfully!")




def view_expenses():

    conn = sqlite3.connect("expenses.db")

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM expenses")

    records = cursor.fetchall()

    print("\n========== ALL EXPENSES ==========")

    if len(records) == 0:
        print("No expenses found!")

    else:
        for record in records:

            print("\nExpense ID:", record[0])
            print("Expense Name:", record[1])
            print("Category:", record[2])
            print("Amount: Rs.", record[3])

    conn.close()



def total_expenses():

    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(amount) FROM expenses")

    total = cursor.fetchone()[0]

    if total is None:
        total = 0

    print("\n========== TOTAL EXPENSES ==========")
    print("Total Spending: Rs.", total)

    conn.close()




def search_expense():

    category = input("Enter category to search: ")

    conn = sqlite3.connect("expenses.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM expenses WHERE category = ?",
        (category,)
    )

    records = cursor.fetchall()

    print("\n========== SEARCH RESULTS ==========")

    if len(records) == 0:
        print("No expenses found!")

    else:
        for record in records:
            print("\nExpense ID:", record[0])
            print("Expense Name:", record[1])
            print("Category:", record[2])
            print("Amount: Rs.", record[3])

    conn.close()


