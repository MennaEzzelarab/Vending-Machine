import tkinter as tk
from tinydb import TinyDB, Query
import os

class TrayManager:
    def __init__(self):
        # Ensure database directory exists
        os.makedirs("database", exist_ok=True)
        
        # Initialize database for tray contents
        self.db = TinyDB("database/tray.json")
        self.tray_contents = []
        self.load_tray_contents()
        print(f"TrayManager initialized. Current contents: {self.tray_contents}")

    def load_tray_contents(self):
        """Load tray contents from database"""
        contents = self.db.all()
        if contents:
            self.tray_contents = contents[0].get('items', [])
            print(f"Loaded tray contents: {self.tray_contents}")
        else:
            self.tray_contents = []
            self.save_tray_contents()
            print("No tray contents found, initialized empty tray")

    def save_tray_contents(self):
        """Save tray contents to database"""
        self.db.truncate()  # Clear existing contents
        self.db.insert({'items': self.tray_contents})
        print(f"Saved tray contents: {self.tray_contents}")

    def add_items(self, items):
        """Add items to tray"""
        print(f"Adding items to tray: {items}")
        self.tray_contents.extend(items)
        self.save_tray_contents()
        print(f"Tray contents after adding: {self.tray_contents}")

    def clear_tray(self):
        """Clear all items from tray"""
        print("Clearing tray contents")
        self.tray_contents = []
        self.save_tray_contents()
        print("Tray cleared")

    def get_tray_contents(self):
        """Get current tray contents"""
        print(f"Getting tray contents: {self.tray_contents}")
        return self.tray_contents

    def get_item_count(self):
        """Get total number of items in tray"""
        count = sum(item['amount'] for item in self.tray_contents)
        print(f"Item count: {count}")
        return count

    def get_total_price(self):
        """Get total price of items in tray"""
        total = sum(item['price'] * item['amount'] for item in self.tray_contents)
        print(f"Total price: {total}")
        return total

    def format_tray_summary(self):
        """Format tray contents for display"""
        if not self.tray_contents:
            print("Tray is empty")
            return "Tray is empty", "#666666"
        
        items = []
        total = 0
        for item in self.tray_contents:
            items.append(f"{item['amount']}x {item['name']} - £{item['price']:.2f}")
            total += item['price'] * item['amount']
        
        summary = "Order Summary:\n\n" + "\n".join(items) + f"\n\nTotal: £{total:.2f}"
        print(f"Formatted summary: {summary}")
        return summary, "#3E3E3E" 