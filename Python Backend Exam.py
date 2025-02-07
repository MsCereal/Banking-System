from datetime import datetime
from enum import Enum
import random

# Transaction Types Enum
class TransactionType(Enum):
    DEPOSIT = 'deposit'
    WITHDRAW = 'withdraw'

# Domain Layer
class Account:
    def __init__(self, account_id, customer_id, account_number, balance=0.00):
        self.account_id = account_id  # Unique identifier
        self.customer_id = customer_id  # Customer ID 
        self.account_number = account_number  # Unique account number
        self.balance = balance  # Current balance of the account
        self.transactions = []  # List to store transaction history
        self.min_balance = 100  # Minimum balance that must be maintained

    def deposit(self, amount): # Deposit function to add funds to the account
        if amount <= 0:
            raise ValueError("Deposit amount must be greater than zero.")
        self.balance += amount  # Increase account balance
        transaction = {         # Log the transaction with a timestamp
            'type': TransactionType.DEPOSIT.value,
            'amount': amount,
            'timestamp': datetime.now()
        }
        self.transactions.append(transaction)
        print(f"Successfully deposited PHP {amount:.2f}. New Balance: PHP {self.balance:.2f}")

    def withdraw(self, amount): # Withdraw function to remove funds from the account
        if amount <= 0:
            raise ValueError("Withdrawal amount must be greater than zero.")
        if self.balance - amount < self.min_balance:
            raise ValueError(f"Cannot withdraw. Your account must maintain a minimum balance of PHP {self.min_balance:.2f}.")
        if amount > self.balance:
            raise ValueError("Insufficient Funds.")
        self.balance -= amount  # Decrease account balance
        transaction = {         # Log the transaction with a timestamp
            'type': TransactionType.WITHDRAW.value,
            'amount': amount,
            'timestamp': datetime.now()
        }
        self.transactions.append(transaction)
        print(f"Successfully withdrew PHP {amount:.2f}. New Balance: PHP {self.balance:.2f}")

    def get_balance(self):
        return f"PHP {self.balance:.2f}" # Function to return the current balance of the account in PHP format

class Customer:
    def __init__(self, customer_id, name, email, phone_number):
        self.customer_id = customer_id  # Unique customer identifier
        self.name = name  # Customer's name
        self.email = email  # Customer's email address
        self.phone_number = phone_number  # Customer's phone number

# Use Case Layer
class CreateAccountUseCase:
    def __init__(self, account_repository):
        self.account_repository = account_repository  # Dependency injection for account repository

    def create_account(self, customer_id, name, email, phone_number):
        # Creates a unique account number based on customer_id and timestamp
        unique_suffix = random.randint(1000, 9999)  # Random part for account number
        timestamp_part = int(datetime.now().timestamp())  # Timestamp to ensure uniqueness
        account_number = f"ACC-{customer_id}-{timestamp_part}-{unique_suffix}"  # Unique account number

        # Ensure the uniqueness of account number by checking repository
        while self.account_repository.find_account_by_account_number(account_number):
            unique_suffix = random.randint(1000, 9999) # If account number exists, regenerate it
            timestamp_part = int(datetime.now().timestamp())
            account_number = f"ACC-{customer_id}-{timestamp_part}-{unique_suffix}"

        account = Account(len(self.account_repository.accounts) + 1, customer_id, account_number)
        self.account_repository.save_account(account)  # Save the account in repository
        print(f"\nThe account successfully created, the account number {account_number} for {name}.")
        return account

class MakeTransactionUseCase:
    def __init__(self, account_repository):
        self.account_repository = account_repository  # Dependency injection for account repository

    def make_transaction(self, account_id, amount, transaction_type):  # Perform a deposit or withdraw transaction
        account = self.account_repository.find_account_by_id(account_id)  # Fetch account by ID
        if not account:
            raise ValueError("Account Not Found.")
        
        if transaction_type == TransactionType.DEPOSIT.value:
            account.deposit(amount)  # Perform deposit
        elif transaction_type == TransactionType.WITHDRAW.value:
            account.withdraw(amount)  # Perform withdrawal
        else:
            raise ValueError("Invalid Transaction Type.")
        
        print(f"{transaction_type.capitalize()} of PHP {amount:.2f} completed successfully. New Balance: {account.get_balance()}")
        return account.get_balance()

class GenerateAccountStatementUseCase:
    def __init__(self, account_repository):
        self.account_repository = account_repository  # Dependency injection for account repository

    def generate_account_statement(self, account_id):  # Generate a statement for a given account
        account = self.account_repository.find_account_by_id(account_id)
        if not account:
            raise ValueError("Account Not Found.")
        
        statement = f"Account Statement for {account.account_number}:\n" # Build the statement with transaction details and current balance
        for transaction in account.transactions:
            timestamp = transaction['timestamp'].strftime('%d-%m-%Y %H:%M:%S')  # Format timestamp
            statement += f"{timestamp} - {transaction['type'].capitalize()} of PHP {transaction['amount']:.2f}\n"
        statement += f"Current Balance: {account.get_balance()}"
        
        print("\n" + statement + "\n")
        return statement

# Infrastructure Layer
class AccountRepository:
    def __init__(self):
        self.accounts = {}  # In-memory store for accounts

    def save_account(self, account):  # Save account to the repository (in-memory store)
        self.accounts[account.account_id] = account

    def find_account_by_id(self, account_id):  # Find and return an account by its ID
        return self.accounts.get(account_id)

    def find_accounts_by_customer_id(self, customer_id):  # Find all accounts for a given customer ID
        return [acc for acc in self.accounts.values() if acc.customer_id == customer_id]

    def find_account_by_account_number(self, account_number):  # Find an account by its unique account number
        return next((acc for acc in self.accounts.values() if acc.account_number == account_number), None)

# Test Scenario Examples
if __name__ == "__main__":
    account_repo = AccountRepository()  # Initialize account repository
    create_account_use_case = CreateAccountUseCase(account_repo)  # Create account use case
    transaction_use_case = MakeTransactionUseCase(account_repo)  # Make transaction use case
    statement_use_case = GenerateAccountStatementUseCase(account_repo)  # Generate statement use case

    # Create a new account
    customer_id = 1
    customer = Customer(customer_id, "Ace Deym", "ace@gmail.com", "0923232321")
    account = create_account_use_case.create_account(customer.customer_id, customer.name, customer.email, customer.phone_number)
    print(f"Account Created: {account.account_number}, Balance: {account.get_balance()}\n")

    # Make transactions (deposit and withdrawal)
    transaction_use_case.make_transaction(account.account_id, 500, TransactionType.DEPOSIT.value)
    transaction_use_case.make_transaction(account.account_id, 200, TransactionType.WITHDRAW.value)
    print(f"Updated Balance: {account.get_balance()}\n")

    # Generate account statement
    statement = statement_use_case.generate_account_statement(account.account_id)
    
    # Test scenarios for error cases
    print("\n--- Test Cases for Error Handling ---")

    # 1 - Account not found
    try:
        transaction_use_case.make_transaction(99, 100, TransactionType.DEPOSIT.value)
    except ValueError as e:
        print(f"Error: {e}")
    
    # 2 - Insufficient balance
    try:
        transaction_use_case.make_transaction(account.account_id, 1000, TransactionType.WITHDRAW.value)
    except ValueError as e:
        print(f"Error: {e}")
    
    # 3 - Invalid transaction type
    try:
        transaction_use_case.make_transaction(account.account_id, 100, 'transfer')
    except ValueError as e:
        print(f"Error: {e}")
    
    # Display account details
    print("\n--- Account Details ---")
    print(f"Account ID: {account.account_id}, Customer ID: {account.customer_id}, Account Number: {account.account_number}, Name: {customer.name}, Email: {customer.email}, Phone: {customer.phone_number}, Balance: {account.get_balance()}\n")
