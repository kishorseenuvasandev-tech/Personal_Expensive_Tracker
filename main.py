from expense import add_expense, view_expenses
from expense import total_expenses, search_expense
from database import create_table


create_table()

while True:

    print("\n========== PERSONAL EXPENSE TRACKER ==========")

    print("1. Add Expense")
    print("2. View All Expenses")
    print("3. Search Expense")
    print("4. Total Expenses")
    print("5. Exit")

    choice = input("\nEnter your choice: ")

    if choice == "1":
        add_expense()

    elif choice == "2":
        view_expenses()

    elif choice == "3":
        search_expense()

    elif choice == "4":
        total_expenses()

    elif choice == "5":
        print("Thank you for using Expense Tracker!")
        break

    else:
        print("Invalid choice! Try again.")