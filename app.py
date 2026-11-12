
from flask import (
    Flask, render_template, request,
    redirect, url_for, abort, make_response
)
from database import create_table, connect_db
from datetime import date, datetime
import csv
from io import StringIO

app = Flask(__name__)

create_table()


@app.route("/")
def home():

    conn = connect_db()
    cursor = conn.cursor()

    # Get filter values
    selected_date = request.args.get("filter_date", "")
    search_query = request.args.get("search", "").strip()
    selected_category = request.args.get("category", "")

    # Build SQL filters
    conditions = []
    params = []

    if selected_date:
        conditions.append("expense_date = ?")
        params.append(selected_date)

    if search_query:
        conditions.append("expense_name LIKE ?")
        params.append(f"%{search_query}%")

    if selected_category:
        conditions.append("category = ?")
        params.append(selected_category)

    where_clause = ""

    if conditions:
        where_clause = " WHERE " + " AND ".join(conditions)

    # Get filtered expenses
    cursor.execute("""
        SELECT * FROM expenses
    """ + where_clause + """
        ORDER BY id DESC
    """, params)

    expenses = cursor.fetchall()

    # Calculate filtered total
    cursor.execute("""
        SELECT SUM(amount)
        FROM expenses
    """ + where_clause, params)

    total = cursor.fetchone()[0] or 0

    # Transaction count
    count = len(expenses)

    # Category summary
    cursor.execute("""
        SELECT category, SUM(amount)
        FROM expenses
    """ + where_clause + """
        GROUP BY category
        ORDER BY SUM(amount) DESC
    """, params)

    category_summary = cursor.fetchall()

    # Monthly expense summary
    cursor.execute("""
        SELECT
            strftime('%Y-%m', expense_date) AS month,
            SUM(amount) AS monthly_total
        FROM expenses
        GROUP BY strftime('%Y-%m', expense_date)
        ORDER BY month DESC
    """)

    monthly_summary = cursor.fetchall()

    monthly_summary = [
        (
            datetime.strptime(month, "%Y-%m").strftime("%B %Y"),
            monthly_total
        )
        for month, monthly_total in monthly_summary
    ]

    today = date.today().isoformat()

    conn.close()

    return render_template(
        "index.html",
        expenses=expenses,
        total=total,
        count=count,
        category_summary=category_summary,
        monthly_summary=monthly_summary,
        today=today,
        selected_date=selected_date,
        search_query=search_query,
        selected_category=selected_category
    )


# Add Expense
@app.route("/add", methods=["POST"])
def add_expense():

    expense_name = request.form.get("expense_name", "").strip()
    category = request.form.get("category", "").strip()
    custom_category = request.form.get("custom_category", "").strip()
    amount_input = request.form.get("amount", "").strip()
    expense_date = request.form.get("expense_date") or date.today().isoformat()

    # Validate expense name
    if not expense_name:
        return "Expense name cannot be empty", 400

    # Allowed default categories
    allowed_categories = [
        "Food",
        "Travel",
        "Shopping",
        "Education",
        "Health"
    ]

    # Handle custom category
    if category == "Other":

        if not custom_category:
            return "Please enter a custom category", 400

        category = custom_category

    elif category not in allowed_categories:
        return "Please select a valid category", 400

    # Validate amount
    try:
        amount = float(amount_input)
    except ValueError:
        return "Please enter a valid amount", 400

    if amount <= 0:
        return "Amount must be greater than zero", 400

    # Validate date
    try:
        date.fromisoformat(expense_date)
    except ValueError:
        return "Please enter a valid date", 400

    # Insert into database
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO expenses
        (expense_name, category, amount, expense_date)
        VALUES (?, ?, ?, ?)
    """, (expense_name, category, amount, expense_date))

    conn.commit()
    conn.close()

    return redirect(url_for("home"))


# Delete Expense
@app.route("/delete/<int:expense_id>", methods=["POST"])
def delete_expense(expense_id):

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM expenses WHERE id = ?",
        (expense_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("home"))



# Edit Expense
@app.route("/edit/<int:expense_id>", methods=["GET", "POST"])
def edit_expense(expense_id):

    conn = connect_db()
    cursor = conn.cursor()

    if request.method == "POST":

        expense_name = request.form.get("expense_name", "").strip()
        category = request.form.get("category", "").strip()
        custom_category = request.form.get("custom_category", "").strip()
        amount_input = request.form.get("amount", "").strip()
        expense_date = request.form.get("expense_date", "")

        if not expense_name:
            conn.close()
            return "Expense name cannot be empty", 400

        allowed_categories = [
            "Food", "Travel", "Shopping",
            "Education", "Health"
        ]

        if category == "Other":

            if not custom_category:
                conn.close()
                return "Please enter a custom category", 400

            category = custom_category

        elif category not in allowed_categories:
            conn.close()
            return "Please select a valid category", 400

        try:
            amount = float(amount_input)
        except ValueError:
            conn.close()
            return "Please enter a valid amount", 400

        if amount <= 0:
            conn.close()
            return "Amount must be greater than zero", 400

        try:
            date.fromisoformat(expense_date)
        except ValueError:
            conn.close()
            return "Please enter a valid date", 400

        cursor.execute("""
            UPDATE expenses
            SET expense_name = ?,
                category = ?,
                amount = ?,
                expense_date = ?
            WHERE id = ?
        """, (expense_name, category, amount, expense_date, expense_id))

        conn.commit()
        conn.close()

        return redirect(url_for("home"))

    cursor.execute(
        "SELECT * FROM expenses WHERE id = ?",
        (expense_id,)
    )

    expense = cursor.fetchone()
    conn.close()

    if expense is None:
        abort(404)

    return render_template("edit.html", expense=expense)


# Export Expenses to CSV
@app.route("/export")
def export_expenses():

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, expense_name, category, amount, expense_date
        FROM expenses
        ORDER BY id DESC
    """)

    expenses = cursor.fetchall()
    conn.close()

    output = StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "ID",
        "Expense Name",
        "Category",
        "Amount",
        "Date"
    ])

    writer.writerows(expenses)

    response = make_response(output.getvalue())

    response.headers["Content-Disposition"] = (
        "attachment; filename=expenses.csv"
    )
    response.headers["Content-Type"] = "text/csv"

    return response


if __name__ == "__main__":
    app.run(debug=True)
