from datetime import datetime
from enum import Enum

# Transaction Types
class TransactionType(Enum):
    DEPOSIT = 'deposit'
    WITHDRAW = 'withdraw'

# Domain Layer
class Account:
    def __init__(self, account_id, customer_id, account_number, balance=0.00):
        self.account_id = account_id
        self.customer_id = customer_id
        self.account_number = account_number
        self.balance = balance
        self.transactions = [] 
        self.min_balance = 100  # Minimum balance 

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Amount must be positive.")
        self.balance += amount
        transaction = {
            'type': TransactionType.DEPOSIT.value,
            'amount': amount,
            'timestamp': datetime.now()
        }
        self.transactions.append(transaction)
        print(f"Successfully deposited PHP {amount:.2f}. New Balance: PHP {self.balance:.2f}")

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Amount must be positive.")
        if self.balance - amount < self.min_balance:
            raise ValueError(f"Cannot withdraw. Your account must maintain a minimum balance of PHP {self.min_balance:.2f}.")
        if amount > self.balance:
            raise ValueError("Insufficient Funds.")
        self.balance -= amount
        transaction = {
            'type': TransactionType.WITHDRAW.value,
            'amount': amount,
            'timestamp': datetime.now()
        }
        self.transactions.append(transaction)
        print(f"Successfully withdrew PHP {amount:.2f}. New Balance: PHP {self.balance:.2f}")

    def get_balance(self):
        return f"PHP {self.balance:.2f}"

class Transaction:
    def __init__(self, account_id, transaction_type, amount):
        self.account_id = account_id
        self.transaction_type = transaction_type
        self.amount = amount

    def __str__(self):
        return f"{self.transaction_type.capitalize()} of PHP {self.amount:.2f}"

class Customer:
    def __init__(self, customer_id, name, email, phone_number):
        self.customer_id = customer_id
        self.name = name
        self.email = email
        self.phone_number = phone_number

# Use Case Layer
class CreateAccountUseCase:
    def __init__(self, account_repository):
        self.account_repository = account_repository

    def create_account(self, customer_id, name, email, phone_number):
        account_number = f"ACC-{customer_id}-{int(datetime.now().timestamp())}"  
        account = Account(len(self.account_repository.accounts) + 1, customer_id, account_number)
        self.account_repository.save_account(account)
        print(f"\nThe account successfully created, the account number {account_number} for {name}.")
        return account

class MakeTransactionUseCase:
    def __init__(self, account_repository):
        self.account_repository = account_repository

    def make_transaction(self, account_id, amount, transaction_type):
        account = self.account_repository.find_account_by_id(account_id)
        if not account:
            raise ValueError("Account Not Found.")
        
        if transaction_type == TransactionType.DEPOSIT.value:
            account.deposit(amount)
        elif transaction_type == TransactionType.WITHDRAW.value:
            account.withdraw(amount)
        else:
            raise ValueError("Invalid Transaction Type.")
        
        print(f"{transaction_type.capitalize()} of PHP {amount:.2f} completed successfully. New Balance: {account.get_balance()}")
        return account.get_balance()

class GenerateAccountStatementUseCase:
    def __init__(self, account_repository):
        self.account_repository = account_repository

    def generate_account_statement(self, account_id):
        account = self.account_repository.find_account_by_id(account_id)
        if not account:
            raise ValueError("Account Not Found.")
        
        statement = f"Account Statement for {account.account_number}:\n"
        for transaction in account.transactions:
            timestamp = transaction['timestamp'].strftime('%d-%m-%Y %H:%M:%S')  # timestamp
            statement += f"{timestamp} - {transaction['type'].capitalize()} of PHP {transaction['amount']:.2f}\n"
        statement += f"Current Balance: {account.get_balance()}"
        
        print("\n" + statement + "\n")
        return statement

# Infrastructure Layer
class AccountRepository:
    def __init__(self):
        self.accounts = {}

    def save_account(self, account):
        self.accounts[account.account_id] = account

    def find_account_by_id(self, account_id):
        return self.accounts.get(account_id)

    def find_accounts_by_customer_id(self, customer_id):
        return [acc for acc in self.accounts.values() if acc.customer_id == customer_id]

# Test Scenario Examples
if __name__ == "__main__":
    account_repo = AccountRepository()
    create_account_use_case = CreateAccountUseCase(account_repo)
    transaction_use_case = MakeTransactionUseCase(account_repo)
    statement_use_case = GenerateAccountStatementUseCase(account_repo)

    # Create a new account
    customer_id = 1
    customer = Customer(customer_id, "Chelsea Purificacion", "chelsea@gmail.com", "0923232321")
    account = create_account_use_case.create_account(customer.customer_id, customer.name, customer.email, customer.phone_number)
    print(f"Account Created: {account.account_number}, Balance: {account.get_balance()}\n")

    # Make transactions
    transaction_use_case.make_transaction(account.account_id, 500, TransactionType.DEPOSIT.value)
    transaction_use_case.make_transaction(account.account_id, 200, TransactionType.WITHDRAW.value)
    print(f"Updated Balance: {account.get_balance()}\n")

    # Generate account statement
    statement = statement_use_case.generate_account_statement(account.account_id)
    
    # Test scenarios for error cases
    print("\n--- Test Cases for Error Handling ---\n")

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
    print("\n--- Account Details ---\n")
    print(f"Account ID: {account.account_id}, Customer ID: {account.customer_id}, Account Number: {account.account_number}, Name: {customer.name}, Email: {customer.email}, Phone: {customer.phone_number}, Balance: {account.get_balance()}\n")
