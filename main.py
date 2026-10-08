"""
Electricity Bill Generation System
A modular console-based application for managing consumer profiles and generating utility bills.
"""
import os

FILE_NAME = "utility_consumers.txt"

class Consumer:
    def __init__(self, consumer_id, name, consumer_type, previous_reading, current_reading=0.0):
        self.consumer_id = consumer_id
        self.name = name
        self.consumer_type = consumer_type  # 'D' for Domestic, 'C' for Commercial
        self.previous_reading = float(previous_reading)
        self.current_reading = float(current_reading)
        self.units_consumed = 0.0
        self.bill_amount = 0.0
        self.calculate_bill()

    def calculate_bill(self):
        """Calculates units consumed and bill amount based on tiered slab rates."""
        if self.current_reading >= self.previous_reading:
            self.units_consumed = self.current_reading - self.previous_reading
        else:
            self.units_consumed = 0.0  # Reset if invalid metrics encountered
            
        # Slab calculations based on consumer type
        if self.consumer_type.upper() == 'D':
            # Domestic Rates
            fixed_charge = 5.00
            if self.units_consumed <= 100:
                energy_charge = self.units_consumed * 0.15
            elif self.units_consumed <= 300:
                energy_charge = (100 * 0.15) + ((self.units_consumed - 100) * 0.25)
            else:
                energy_charge = (100 * 0.15) + (200 * 0.25) + ((self.units_consumed - 300) * 0.40)
        else:
            # Commercial Rates
            fixed_charge = 15.00
            if self.units_consumed <= 200:
                energy_charge = self.units_consumed * 0.30
            else:
                energy_charge = (200 * 0.30) + ((self.units_consumed - 200) * 0.50)

        self.bill_amount = fixed_charge + energy_charge

def create_consumer_profile():
    print("\n--- Register New Consumer ---")
    consumer_id = input("Enter 6-Digit Consumer ID: ").strip()
    name = input("Enter Consumer Name: ").strip()
    consumer_type = input("Enter Type (D for Domestic, C for Commercial): ").strip().upper()
    
    if consumer_type not in ['D', 'C']:
        print("Invalid Consumer Type Selection! Registration cancelled.")
        return

    try:
        prev_reading = float(input("Enter Initial Meter Reading (kWh): "))
    except ValueError:
        print("Invalid numerical input! Registration cancelled.")
        return

    try:
        with open(FILE_NAME, "a") as f:
            f.write(f"{consumer_id}|{name}|{consumer_type}|{prev_reading:.2f}|{prev_reading:.2f}\n")
        print("Consumer profile created successfully! Ready for billing cycles.\n")
    except IOError:
        print("Error accessing local database storage structure.")

def authenticate_consumer():
    search_id = input("\nEnter 6-Digit Consumer ID: ").strip()
    consumers = []
    target_consumer = None

    if not os.path.exists(FILE_NAME):
        print("No registered consumer profiles discovered. Please register first.\n")
        return None

    try:
        with open(FILE_NAME, "r") as f:
            for line in f:
                if line.strip():
                    parts = line.strip().split('|')
                    if len(parts) == 5:
                        c = Consumer(parts[0], parts[1], parts[2], parts[3], parts[4])
                        if c.consumer_id == search_id:
                            target_consumer = c
                        consumers.append(c)
    except IOError:
        print("Critical tracking failure reading persistent flat file database.")
        return None

    if target_consumer:
        print(f"Authentication Confirmed! Account Owner: {target_consumer.name}")
        return target_consumer
    else:
        print("Error: Account parameters mismatch or ID not found!\n")
        return None

def update_billing_metrics(active_user):
    try:
        new_reading = float(input(f"Enter Current Meter Reading (Previous: {active_user.previous_reading:.2f} kWh): "))
        if new_reading < active_user.previous_reading:
            print("Invalid Matrix! Current reading cannot be less than previous metric parameters.")
            return
    except ValueError:
        print("Invalid decimal input format provided.")
        return

    active_user.current_reading = new_reading
    active_user.calculate_bill()

    # Sync alterations to database file
    if os.path.exists(FILE_NAME):
        updated_records = []
        with open(FILE_NAME, "r") as f:
            for line in f:
                parts = line.strip().split('|')
                if parts[0] == active_user.consumer_id:
                    # Update metrics with current rolling updates
                    updated_records.append(f"{active_user.consumer_id}|{active_user.name}|{active_user.consumer_type}|{active_user.current_reading:.2f}|{active_user.current_reading:.2f}\n")
                else:
                    updated_records.append(line)
        
        with open(FILE_NAME, "w") as f:
            f.writelines(updated_records)
            
    print("\n>>> BILL GENERATED SUCCESSFULLY <<<")
    print(f"Units Consumed: {active_user.units_consumed:.2f} kWh")
    print(f"Total Amount Due: ${active_user.bill_amount:.2f}")

def display_statement(active_user):
    c_type = "Domestic" if active_user.consumer_type == 'D' else "Commercial"
    print("\n==========================================")
    print("        ELECTRICITY ACCOUNT STATEMENT       ")
    print("==========================================")
    print(f" Consumer ID   : {active_user.consumer_id}")
    print(f" Account Name  : {active_user.name}")
    print(f" Tariff Category: {c_type}")
    print("------------------------------------------")
    print(f" Previous Meter: {active_user.previous_reading:.2f} kWh")
    print(f" Current Meter : {active_user.current_reading:.2f} kWh")
    print(f" Net Consumption: {active_user.units_consumed:.2f} kWh")
    print("------------------------------------------")
    print(f" GRAND TOTAL DUE: ${active_user.bill_amount:.2f}")
    print("==========================================\n")

def main():
    while True:
        print("=== UTILITY BILLING & MANAGEMENT SYSTEM ===")
        print("1. Register New Consumer Profile")
        print("2. Access Billing Terminal Dashboard")
        print("3. Shutdown Terminal Session")
        choice = input("Enter choice parameter: ").strip()

        if choice == '1':
            create_consumer_profile()
        elif choice == '2':
            user = authenticate_consumer()
            if user:
                sub_choice = '0'
                while sub_choice != '3':
                    print(f"\n--- CONSUMER METRIC INTERFACE ({user.consumer_id}) ---")
                    print("1. Compute Live Bill Cycle")
                    print("2. Display Account Statement")
                    print("3. Close Profile Session")
                    sub_choice = input("Enter interface option: ").strip()

                    if sub_choice == '1':
                        update_billing_metrics(user)
                    elif sub_choice == '2':
                        display_statement(user)
                    elif sub_choice == '3':
                        print("Session terminated safely.")
                    else:
                        print("Invalid selection parameters.")
        elif choice == '3':
            print("System shutting down. Goodbye!")
            break
        else:
            print("Invalid control selection. Try again.\n")

if __name__ == "__main__":
    main()
