import os
from datetime import datetime, date

### Global Variables ###
current_balance = 0.0
iniital_balance = 0.0
transactions = []
filename = ""

### Main Functions ###
def initialization():
    """Initializes the expense tracker, handling first-time users and file creation."""
    global current_balance, filename, transactions, initial_balance

    while True:
        print("\nWelcome to our Expense Tracker App!")
        first_timer_user = input("Are you a first-time user? (Y/N): ").upper()
        if first_timer_user == "Y":
            while True:
                try:
                    initial_balance_str = input("Enter initial balance: ")
                    initial_balance = float(initial_balance_str)
                    if initial_balance < 0:
                        raise ValueError("Initial balance cannot be negative.")
                    current_balance = round(initial_balance, 2)
                    break 
                except ValueError as e:
                    print(f"Invalid input: {e}. Please enter a positive number.")

            filename = generate_filename()
            transactions = [] # Initialize transactions as empty list for a new user
            break
            
        elif first_timer_user == "N":
            while True:
                filename = input("Enter the name of your latest transaction file: ")
                if os.path.isfile(filename):
                    # Assign transactions from the loaded file
                    current_balance, initial_balance, transactions = load_transactions(filename)
                    break
                else:
                    print(f"File '{filename}' not found. Please try again.")
            break
        else:
            print("Invalid input. Please enter 'Y' or 'N'.") 

def main_menu():
    global current_balance, filename, transactions

    commands = {
        "1": add_entry,
        "2": delete_entry,  
        "3": update_entry, 
        "4": filter_entries,
        "5": show_all_entries,
        "6": income_expense_ratio
    }

    command_names = {
        "1": "Add Entry",
        "2": "Delete Entry",
        "3": "Update Entry",
        "4": "Filter Entries",
        "5": "Show All Entries",
        "6": "Income Expenses Ratio"
    }

    while True:
        print("\n---------------------------------------------")
        print("|      Welcome to Expense Tracker App!      |")  # Add your app title here
        print("---------------------------------------------")
        print("\nYour Current Balance: PHP ", format_currency(current_balance))  
        print("\nMain Menu:")
        for choice, command_name in command_names.items():
            print(f"{choice}. {command_name}")
        print("7. Exit")  

        print("\nCommand Line:")
        choice = input("Choose your command (1-7): ")  

        if choice == "7":  
            print("Exiting Expense Tracker App. Goodbye!")  # Exit message
            break
        elif choice in commands:
            result = commands[choice](current_balance, transactions, filename)
            
            # Update values based on the result
            if isinstance(result, tuple):
                current_balance, transactions = result

            # Update the file after any modifications
            if choice in ["1", "2", "3"]: # Save to file only if add, delete, or update
                save_transactions(filename, current_balance, initial_balance, transactions)
        else:
            print("Invalid choice. Please enter a number between 1 and 6.") 

def add_entry(current_balance, transactions, filename):

    while True:
        entry_type = input("Income or Expense? (I/E): ").upper()
        is_valid, error_message, _ = data_entry_validation(entry_type, "", "", "") 
        if is_valid:
            break
        else:
            print(error_message)
    
    while True:
        date_string = input("Enter date (YYYY-MM-DD): ")
        is_valid, error_message, _ = data_entry_validation(entry_type, date_string, "", "") 
        if is_valid:
            break
        else:
            print(error_message)
    
    while True:
        try:
            amount = float(input("Enter amount (up to 2 decimal places only): "))
            is_valid, error_message, amount = data_entry_validation(entry_type, date_string, amount, "") 
            if is_valid:
                break
            else:
                print(error_message)
        except ValueError:
            print("Invalid input. Please enter a number.")
    
    while True:
        details = input("Enter details: ")
        is_valid, error_message, _ = data_entry_validation(entry_type, date_string, amount, details)
        if is_valid:
            break
        else:
            print(error_message)

    if entry_type == "I":
        current_balance += amount
    elif entry_type == "E":
        current_balance -= abs(amount) # Take the absolute value of amount for expenses 

    # Create new entry line (in dictionary format)
    new_entry = {"date": date.fromisoformat(date_string), "category": entry_type, "amount": amount, "details": details}

    # Append new entry to transactions list
    transactions.append(new_entry)

    # Sort transactions by date in descending order
    transactions.sort(key=lambda x: x["date"], reverse=True) # No need to convert to datetime again

    # Save updated transactions
    save_transactions(filename, current_balance, initial_balance, transactions)

    print("Entry added and balance updated.")
    
    # Return updated current balance and transactions for use in the main menu
    return current_balance, transactions

def delete_entry(current_balance, transactions, filename):
    """Deletes an entry from the transactions and updates the balance in the file."""

    # 1. Show All Transactions with Indices
    if not transactions:
        print("No transactions to delete.")
        return current_balance, transactions  # Return unchanged values

    print("\nTransactions:")
    # Table Header
    print("-" * 74)
    print(f"{'No.':<5} {'Date':<12} {'Type':<8} {'Amount':<15} Details")
    print("-" * 74)

    for i, transaction in enumerate(transactions):
        print(f"{i+1:<5} {transaction['date'].strftime('%Y-%m-%d'):<12} {transaction['category']:<8} {format_currency(transaction['amount']):<15} {transaction['details']}")

    # Table Footer
    print("-" * 74)

    # 2. Get Index to Delete (with Input Validation)
    while True:
        try:
            index = int(input("Enter the number of the entry to delete: ")) - 1
            if 0 <= index < len(transactions):
                break
            else:
                print(f"Invalid index. Please enter a number between 1 and {len(transactions)}.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    # Confirmation
    confirm = input(f"Are you sure you want to delete entry {index + 1}? (Y/N): ").upper()
    if confirm != "Y":
        print("Deletion canceled.")
        return current_balance, transactions 

    # Delete Entry and Adjust Balance
    deleted_entry = transactions.pop(index)
    if deleted_entry["category"] == "I":
        current_balance -= deleted_entry["amount"]  # Subtract income
    else:  # 'E' (Expense)
        current_balance -= deleted_entry["amount"]  # Subtract the expense amount (already negative)
    # Save the updated transactions to the file 
    save_transactions(filename, current_balance, initial_balance, transactions) 
    print("Entry deleted and balance updated.")
    return current_balance, transactions

def update_entry(current_balance, transactions, filename):
    """Updates a specified transaction entry."""

    # 1. Check for Entries
    if not transactions:
        print("No transactions to update.")
        return transactions
    
    print("\nTransactions:")
    # Table Header
    print("-" * 74)
    print(f"{'No.':<5} {'Date':<12} {'Type':<8} {'Amount':<15} Details")
    print("-" * 74)

    for i, transaction in enumerate(transactions):
        print(f"{i+1:<5} {transaction['date'].strftime('%Y-%m-%d'):<12} {transaction['category']:<8} {format_currency(transaction['amount']):<15} {transaction['details']}")

    # Table Footer
    print("-" * 74)

    # 3. Get Index to Update
    while True:
        try:
            index = int(input("Enter the number of the entry to update: ")) - 1
            if 0 <= index < len(transactions):
                break
            else:
                print(f"Invalid index. Please enter a number between 1 and {len(transactions)}.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    # Get updated values with validation
    entry = transactions[index]
    print(f"\nCurrent Entry: {entry['date'].strftime('%Y-%m-%d')} {entry['category']} {format_currency(entry['amount'])} {entry['details']}")

    while True:
        edit_choice = input("What to edit? (1) Date, (2) Type, (3) Amount, (4) Details, (5) Cancel: ")

        if edit_choice == "1":
            while True:
                new_date_str = input("New date (YYYY-MM-DD): ")
                is_valid, error_message, _ = data_entry_validation(entry["category"], new_date_str, entry["amount"], entry["details"])
                if is_valid:
                    break
                else:
                    print(error_message)

            # Update the date
            entry["date"] = date.fromisoformat(new_date_str)

        elif edit_choice == "2":
            while True:
                new_type = input("New type (I/E): ").upper()
                is_valid, error_message, _ = data_entry_validation(new_type, entry["date"].strftime("%Y-%m-%d"), entry["amount"], entry["details"])  # Pass current_balance
                if is_valid:
                    break
                else:
                    print(error_message)
            
            old_amount = entry["amount"]  
            entry["category"] = new_type  

            # Adjust amount and balance based on the category change
            if new_type == "I" and old_amount < 0:  # Expense to Income
                current_balance += abs(old_amount)  # Add back the original expense amount
                current_balance += abs(old_amount)  # Add it again as income
                entry["amount"] = abs(old_amount)  
            elif new_type == "E" and old_amount > 0:  # Income to Expense
                current_balance -= old_amount  # Subtract the original income amount
                current_balance -= abs(old_amount)  # Subtract it again as an expense
                entry["amount"] = -abs(old_amount)  
        
        elif edit_choice == "3":
            while True:
                try:
                    new_amount = float(input("New amount: "))

                    # Check if amount sign doesn't match category
                    if (entry["category"] == "I" and new_amount < 0) or (entry["category"] == "E" and new_amount > 0):
                        while True:  # Loop to confirm category change
                            change_category = input(
                                f"The new amount ({new_amount:.2f}) doesn't match the current category ({entry['category']}). "
                                "Change category to " + ("Expense (E)" if new_amount < 0 else "Income (I)") + "? (Y/N): "
                            ).upper()
                            if change_category == "Y":
                                entry["category"] = "E" if new_amount < 0 else "I"
                                print(f"Category changed to {entry['category']} based on amount.")
                                break
                            elif change_category == "N":
                                print("Amount update canceled.")
                                return  # Exit update_entry entirely
                            else:
                                print("Invalid choice. Please enter 'Y' or 'N'.")

                    # If no category change or change is confirmed, validate
                    is_valid, error_message, new_amount = data_entry_validation(entry["category"], entry["date"].strftime("%Y-%m-%d"), new_amount, entry["details"])
                    if is_valid:
                        break
                    else:
                        print(error_message)
                except ValueError:
                    print("Invalid input. Please enter a number.")

            old_amount = entry["amount"]
            current_balance -= old_amount  # Reverse the effect of the old amount

            entry["amount"] = new_amount
            current_balance += entry["amount"]  # Update balance with the new amount


        elif edit_choice == "4":
            while True:
                new_details = input("New details: ")
                if data_entry_validation(entry["category"], entry["date"].strftime("%Y-%m-%d"), entry["amount"], new_details):
                    break
            entry["details"] = new_details

        elif edit_choice == "5":
            print("Update canceled.")
            return transactions
        else:
            print("Invalid choice.")
        
        # Sort the transactions by date
        transactions.sort(key=lambda x: x["date"], reverse=True)
        
        # Save the updated transactions to the file
        save_transactions(filename, current_balance, initial_balance, transactions)
        print("Entry updated successfully!")
        break  

    return current_balance, transactions

def filter_entries(current_balance, transactions, filename):
    """Filters and displays transaction entries based on the user's criteria."""

    filter_type = input("Filter by (1) Month, (2) Year, (3) Day, (4) Date Range, or (5) Category I/E: ")

    filtered_transactions = []

    if filter_type == "1":
        # Filter by month
        month_str = input("Enter month (MM): ")
        try:
            month = int(month_str)
            if not 1 <= month <= 12:
                raise ValueError("Month must be between 1 and 12.")

            filtered_transactions = [entry for entry in transactions if entry["date"].month == month]
        except ValueError:
            print("Invalid month format. Please enter a two-digit number (01-12).")

    elif filter_type == "2":
        # Filter by year
        year_str = input("Enter year (YYYY): ")
        try:
            year = int(year_str)
            filtered_transactions = [entry for entry in transactions if entry["date"].year == year]
        except ValueError:
            print("Invalid year format. Please enter a four-digit year.")

    elif filter_type == "3":
        # Filter by day
        day_str = input("Enter day (DD): ")
        try:
            day = int(day_str)
            if not 1 <= day <= 31:
                raise ValueError("Day must be between 1 and 31.")
            filtered_transactions = [entry for entry in transactions if entry["date"].day == day]
        except ValueError:
            print("Invalid day format. Please enter a two-digit day (01-31).")

    elif filter_type == "4":
        # Filter by date range
        start_date_str = input("Enter start date (YYYY-MM-DD): ")
        end_date_str = input("Enter end date (YYYY-MM-DD): ")

        try:
            start_date = date.fromisoformat(start_date_str)
            end_date = date.fromisoformat(end_date_str)
            if start_date > end_date:
                raise ValueError("Start date cannot be after end date.")

            filtered_transactions = [entry for entry in transactions if start_date <= entry["date"] <= end_date]
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")

    elif filter_type == "5":
        # Filter by category (I/E)
        category = input("Enter category (I for Income, E for Expense): ").upper()
        while category not in ["I", "E"]:
            print("Invalid category. Please enter 'I' for Income or 'E' for Expense.")
            category = input("Enter category (I for Income, E for Expense): ").upper()

        filtered_transactions = [entry for entry in transactions if entry["category"] == category]

    else:
        print("Invalid filter choice.")

    # Display filtered results
    if not filtered_transactions:
        print("No transactions found for the given criteria.")
    else:
        # Display filtered transactions in a table format
        print("\nFiltered Transactions:")
        print("-" * 74)
        print(f"{'Date':<12} {'Type':<8} {'Amount':<15} Details")
        print("-" * 74)

        for transaction in filtered_transactions:
            date_str = transaction["date"].strftime("%Y-%m-%d")
            type = transaction["category"]
            amount = format_currency(transaction["amount"])
            details = transaction["details"]
            print(f"{date_str:<12} {type:<8} {amount:<15} {details}")
        
        print("-" * 74)
            
    return transactions #return transactions in case you use it to update the file

def show_all_entries(current_balance, transactions, filename):
    """Displays all transaction entries."""
    if not transactions:
        print("No transactions found.")
        return

    print("\nAll Transactions:")
    print("-" * 45)  # Header line
    print(f"{'Date':<12} {'Type':<8} {'Amount':<15} Details")
    print("-" * 45) 

    for transaction in transactions:
        date_str = transaction["date"].strftime("%Y-%m-%d")  
        type = transaction["category"]
        amount = format_currency(transaction["amount"])
        details = transaction["details"]
        print(f"{date_str:<12} {type:<8} {amount:<15} {details}")  

    print("-" * 45)  # Footer line

def income_expense_ratio(current_balance, transactions, filename):
    """Calculates and interprets the income vs. expense ratio."""

    total_income = sum(transaction["amount"] for transaction in transactions if transaction["category"] == "I")
    total_expenses = abs(sum(transaction["amount"] for transaction in transactions if transaction["category"] == "E"))

    if total_income == 0 and total_expenses == 0:
        print("No income or expenses recorded.")
        return transactions # Return the transactions list to main_menu()
    elif total_income == 0:
        print("You haven't recorded any income yet.")
        return transactions # Return the transactions list to main_menu()
    elif total_expenses == 0:
        print("You haven't recorded any expenses yet.")
        return transactions # Return the transactions list to main_menu()
    
    #The calculation and display of ratio and the table will be moved inside this else statement
    else:
        ratio = total_income / total_expenses
        
        # Spending Analysis and Feedback (Updated Messages)
        if ratio >= 2.0:
            feedback = "Excellent! You're saving a significant portion of your income."
        elif ratio >= 1.5:
            feedback = "Good! Your income is comfortably covering your expenses, and you have some savings."
        elif ratio >= 1.0:
            feedback = "Okay: Your income is covering your expenses, but consider saving more."
        else:
            feedback = "Warning: Your expenses are higher than your income. You may need to cut back on spending."


    # Display results in a table
    print("\nIncome vs. Expense Summary:")
    print("-" * 75)
    print(f"{'Metric':<25} {'Value':<20}")  
    print("-" * 75)
    print(f"{'Total Income':<25} {format_currency(total_income):<20}")  # Left-aligned amount
    print(f"{'Total Expenses':<25} {format_currency(total_expenses):<20}")  # Left-aligned amount
    print(f"{'Income/Expense Ratio':<25} {ratio:<20.2f}")  # Left-aligned amount
    print("-" * 75)
    print(feedback)   # Print feedback without formatting 
    print("-" * 75)

    return transactions # To maintain consistency with other commands in main_menu

### Helper Functions ###
def format_currency(amount):
    return f"{amount:,.2f}" 

def generate_filename():
    """Generates a unique filename based on current date and time."""
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")  # Format timestamp (customize as needed)
    return f"transactions_{timestamp}.txt"

def data_entry_validation(entry_type, date_string, amount, details):
    """Validates entry type, date, amount, and details for a transaction."""

    # Validate entry type if it's provided (not an empty string)
    if entry_type and entry_type not in ["I", "E"]:
        return False, f"Error: Invalid entry type '{entry_type}'. Please enter 'I' for Income or 'E' for Expense.", amount

    # Validate date (format and ensure it's not in the future) if date_string is provided
    if date_string:
        try:
            entry_date = date.fromisoformat(date_string)
            if entry_date > date.today():
                return False, "Error: Entry date cannot be in the future.", amount
        except ValueError:
            return False, "Error: Invalid date format. Please use YYYY-MM-DD.", amount

    # Validate amount if amount is provided and entry_type is valid
    if entry_type in ["I", "E"] and amount:  # Check if amount is provided (not 0 or None)
        
        # Convert expense amount to negative and prevent zero amount
        if entry_type.upper() == "E":
            amount = -abs(amount)  # Make it negative, regardless of input
            if current_balance + amount < 0:
                return False, "Error: Insufficient funds.", amount

        if amount == 0:
            return False, "Error: Amount must not be zero.", amount
        
    # Validate details if they are provided (not an empty string)
    if details and not details.strip():
        return False, "Error: Please provide details for the entry.", amount

    # If all checks pass, return True and the amount (possibly modified)
    return True, "", amount

def load_transactions(filename, mode="r"):
    """Loads/updates transactions from/to the specified file."""
    try:
        with open(filename, mode) as file:
            # Load current balance (first line) if reading
            if mode == "r":
                # Split the first line by ":"
                current_balance_str = file.readline().strip().split(": ")[-1]

                current_balance = float(current_balance_str.replace(",", "")) 
                
                #Read initial balance (second line)
                initial_balance_str = file.readline().strip().split(": ")[-1]
                initial_balance = float(initial_balance_str.replace(",", ""))
            
            # Load transaction entries (rest of the lines) if reading
            if mode=="r": 
                transactions = []
                for line in file:
                    parts = line.strip().split(" ")
                    if len(parts) >= 3:  
                        date_str, category, amount_str = parts[:3] 
                        details = " ".join(parts[3:]) if len(parts) > 3 else "" 
                        amount = float(amount_str.replace(",", ""))
                        # Convert date_str to date object
                        transactions.append({"date": date.fromisoformat(date_str), "category": category, "amount": amount, "details": details})

                return current_balance, initial_balance, transactions

            # If appending, update balance at the beginning
            elif mode == "a":
                # No need to read the entire file in append mode.  Just overwrite the first line
                file.seek(0)  # Move to the beginning of the file
                file.write(format_currency(current_balance) + "\n")  # Overwrite the first line with the updated balance

    except FileNotFoundError:
        print(f"File not found: {filename}")
        return 0.00, [] 

def save_transactions(filename, current_balance, initial_balance, transactions):
    """Saves transactions and current balance to the given file."""
    with open(filename, "w") as file:
        file.write(f"Current Balance: {format_currency(current_balance)}\n")
        file.write(f"Initial Balance: {format_currency(initial_balance)}\n\n")
        file.write("Transactions Record: \n")
        
        for transaction in transactions:  # Iterate over the transactions list
            file.write(f"{transaction['date'].strftime('%Y-%m-%d')} {transaction['category']} {format_currency(transaction['amount'])} {transaction['details']}\n")



initialization()
main_menu()
