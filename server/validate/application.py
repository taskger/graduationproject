import tkinter as tk
from tkinter import ttk
import requests
#refesh ถ้าข้อมูลมีอยู่จะไม่รับข้อมูลใหม่มาเพิ่มจะรับแค่ข้อมูลใหม่
class BananaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("")

        self.create_widgets()
        self.read_data()  
        self.auto_refresh()  

    def create_widgets(self):
        self.data_text = tk.Text(self.root, height=20, width=80)
        self.data_text.pack(pady=20)
        self.data_text.pack(padx=20)

    def read_data(self):
        response = requests.get("http://localhost:4000/read")
        data = response.json()

        formatted_data = ""
        for entry in data:
            formatted_data += f"Grade: {entry['grade']},Weight: {entry['weight']}, Timestamp: {entry['timestamp']},State: {entry['state']} \n"

        self.data_text.delete(1.0, tk.END)  # Clear previous data
        self.data_text.insert(tk.END, formatted_data)

    def auto_refresh(self):
        self.read_data()  # Refresh data
        self.root.after(5000, self.auto_refresh)  # Schedule the next refresh after 5000 milliseconds (5 seconds)

if __name__ == "__main__":
    root = tk.Tk()
    app = BananaApp(root)
    root.mainloop()
