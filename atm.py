import sqlite3
import os
import time
import sys

conn = sqlite3.connect('atm.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        balance REAL NOT NULL,
        pin INTEGER NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Transactions (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        transaction_type TEXT NOT NULL,
        amount REAL NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES Users (id)
    )
''')

conn.commit()


def countdown(seconds):
    for remaining in range(seconds, 0, -1):
        sys.stdout.write("\r")
        sys.stdout.write(f"Waiting for {remaining} seconds...  ")
        time.sleep(1)
    sys.stdout.write("\r")


def create_user(username, initial_balance, pin):
    cursor.execute('INSERT INTO Users (username, balance, pin) VALUES (?, ?, ?)',
                   (username, initial_balance, pin))
    conn.commit()
    return cursor.lastrowid


def get_user_balance(user_id):
    cursor.execute('SELECT balance FROM Users WHERE id = ?', (user_id,))
    balance = cursor.fetchone()
    return balance[0] if balance else None


def update_balance(user_id, new_balance):
    cursor.execute('UPDATE Users SET balance = ? WHERE id = ?',
                   (new_balance, user_id))
    conn.commit()


def add_transaction(user_id, transaction_type, amount):
    cursor.execute('INSERT INTO Transactions (user_id, transaction_type, amount) VALUES (?, ?, ?)',
                   (user_id, transaction_type, amount))
    conn.commit()


def update_pin(user_id, new_pin):
    cursor.execute('UPDATE Users SET pin = ? WHERE id = ?', (new_pin, user_id))
    conn.commit()


def get_mini_statement(user_id):
    cursor.execute('SELECT * FROM Transactions WHERE user_id = ?', (user_id,))
    return cursor.fetchall()


def format_mini_statement(transactions, user_balance, user_name):
    formatted_statement = f"Bank Mini Statement for {user_name}\n"
    formatted_statement += "-" * 50 + "\n"
    formatted_statement += "Date/Time\t\tTransaction\t\tAmount\n"
    formatted_statement += "-" * 50 + "\n"
    for transaction in transactions:
        transaction_id, user_id, transaction_type, amount, timestamp = transaction
        formatted_timestamp = timestamp.replace("T", " ").split(".")[0]
        formatted_amount = "{:.2f}".format(amount)
        formatted_statement += f"{formatted_timestamp}\t{transaction_type}\t\t{formatted_amount}\n"
    formatted_statement += "-" * 50 + "\n"
    formatted_statement += f"Current Balance: {user_balance:.2f}\n"
    return formatted_statement


def print_mini_statement_to_file(user_id, transactions, user_balance, user_name):
    formatted_statement = format_mini_statement(
        transactions, user_balance, user_name)
    filename = f"mini_statement_{user_name}_{user_id}.txt"
    with open(filename, 'w') as file:
        file.write(formatted_statement)
    print(f"Mini statement has been saved to {filename}")


def get_valid_pin_input(message):
    while True:
        pin = input(message)
        if pin.isdigit() and len(pin) == 4:
            return int(pin)
        else:
            print("Please enter a valid 4-digit PIN.")


def get_user_name(user_id):
    cursor.execute('SELECT username FROM Users WHERE id = ?', (user_id,))
    name = cursor.fetchone()
    return name[0] if name else None


def main():
    while True:
        os.system('cls')
        print("=================Welcome to the ATM Machine==================")
        print("1. Create Account")
        print("2. Login")
        print("3. Exit")
        try:
            choice = int(input("Enter your choice: "))
        except ValueError:
            print("Invalid input. Please enter a valid choice.")
            countdown(5)
            continue

        if choice == 1:
            os.system('cls')
            username = input("Enter your username: ")
            initial_balance = float(input("Enter initial balance: "))
            pin = int(input("Enter a 4-digit PIN: "))
            user_id = create_user(username, initial_balance, pin)
            print("Account created with ID:", user_id)
            time.sleep(2)
            print("IMPORTANT!!!... Please remember ID")
            time.sleep(4)

        elif choice == 2:
            try:
                os.system('cls')
                user_id = int(input("Enter your user ID: "))
            except ValueError:
                print("Invalid input. Please enter a valid User ID.")
                countdown(5)
                continue
            cursor.execute('SELECT * FROM Users WHERE id = ?', (user_id,))
            user = cursor.fetchone()
            if not user:
                print("User ID not found. Please enter a valid User ID.")
                countdown(5)
                continue

            pin_attempt = 0
            while pin_attempt < 2:
                try:
                    entered_pin = int(input("Enter your 4-digit PIN: "))
                except ValueError:
                    print("Invalid input. Please enter a valid PIN.")
                    countdown(5)
                    continue
                cursor.execute(
                    'SELECT * FROM Users WHERE id = ? AND pin = ?', (user_id, entered_pin))
                user = cursor.fetchone()
                if user:
                    print("SUCCESSFULLY! Logged in as User ID:", user_id)
                    user_balance = user[2]
                    while True:
                        countdown(5)

                        os.system('cls')
                        print(
                            "=================Welcome to the ATM Machine==================")
                        user_name = get_user_name(user_id)
                        print(
                            f"Welcome, {user_name}! You are logged in as User ID:", user_id)
                        print("1. Check Balance")
                        print("2. Deposit Money")
                        print("3. Withdraw Money")
                        print("4. Mini Statement")
                        print("5. Update PIN")
                        print("6. Logout")
                        action = int(input("Enter your choice: "))
                        if action == 1:
                            print("Your balance:", user_balance)
                        elif action == 2:
                            amount = float(input("Enter amount to deposit: "))
                            user_balance += amount
                            update_balance(user_id, user_balance)
                            add_transaction(user_id, 'Credit', amount)
                            print("Amount deposited successfully.")
                        elif action == 3:
                            amount = float(input("Enter amount to withdraw: "))
                            if amount > user_balance:
                                print("Insufficient balance")
                                continue
                            user_balance -= amount
                            update_balance(user_id, user_balance)
                            add_transaction(user_id, 'Debit', amount)
                            print("Amount withdrawn successfully.")
                        elif action == 4:
                            transactions = get_mini_statement(user_id)
                            user_balance = get_user_balance(user_id)
                            user_name = get_user_name(user_id)
                            formatted_statement = format_mini_statement(
                                transactions, user_balance, user_name)
                            print("\nMini Statement:")
                            print(formatted_statement)
                            print_mini_statement_to_file(
                                user_id, transactions, user_balance, user_name)
                            time.sleep(8)
                        elif action == 5:
                            print("Update PIN:")
                            new_pin = get_valid_pin_input(
                                "Enter new 4-digit PIN: ")
                            confirm_new_pin = get_valid_pin_input(
                                "Confirm new 4-digit PIN: ")
                            if new_pin == confirm_new_pin:
                                update_pin(user_id, new_pin)
                                print("PIN updated successfully.")
                            else:
                                print("PINs do not match. PIN update failed.")
                        elif action == 6:
                            print("Logged out")
                            break
                        else:
                            print("Invalid choice")
                            countdown(5)
                    break
                else:
                    print("Incorrect PIN. Please try again.")
                    pin_attempt += 1
                    if pin_attempt >= 2:
                        print("Too many incorrect PIN attempts. Exiting...")
                        countdown(5)
                        break
        elif choice == 3:
            print("==============Goodbye! Thanks for using ATM=================")
            break
        else:
            print("Invalid choice")
            countdown(5)


if __name__ == '__main__':
    main()
