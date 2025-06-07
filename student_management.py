import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sqlite3

# === SQLite Setup ===
conn = sqlite3.connect("students.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    roll TEXT PRIMARY KEY,
    name TEXT,
    class TEXT,
    section TEXT,
    contact TEXT,
    father TEXT,
    address TEXT,
    gender TEXT,
    dob TEXT
)
""")
conn.commit()

# === Tkinter Window ===
win = tk.Tk()
win.title("Student Management System")
win.geometry("1350x700")
win.minsize(800, 600)

# === Styling ===
style = ttk.Style()
style.theme_use('clam')
style.configure("Vertical.TScrollbar", width=15)
style.configure("Horizontal.TScrollbar", width=15)

# === Title ===
tk.Label(win, text="Student Management System", font=("Arial", 30, "bold"),
         bd=12, relief=tk.GROOVE, bg="lightgrey").pack(side=tk.TOP, fill=tk.X)

# === Frames ===
content_frame = tk.Frame(win)
content_frame.pack(fill=tk.BOTH, expand=True)
content_frame.grid_columnconfigure(0, weight=1)
content_frame.grid_columnconfigure(1, weight=2)
content_frame.grid_rowconfigure(0, weight=1)

detail_frame = tk.LabelFrame(content_frame, text="Enter Details", font=("Arial", 20, "bold"),
                             bd=12, relief=tk.GROOVE, bg="lightgrey")
detail_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
detail_frame.grid_columnconfigure(1, weight=1)

data_frame = tk.Frame(content_frame, bd=12, relief=tk.GROOVE, bg="lightgrey")
data_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
data_frame.grid_rowconfigure(1, weight=1)
data_frame.grid_columnconfigure(0, weight=1)

# === Entry Fields ===
entries = {}
fields = ["Roll No", "Name", "Class", "Section", "Contact", "Father's Name", "Address", "Gender", "D.O.B"]

def create_entry(row, label, is_combo=False):
    tk.Label(detail_frame, text=label, font=("Arial", 14), bg="lightgrey").grid(row=row, column=0, sticky="w", padx=5, pady=5)
    if is_combo:
        ent = ttk.Combobox(detail_frame, font=("Arial", 14), state="readonly")
        ent['values'] = ["Male", "Female", "Others"]
    else:
        ent = tk.Entry(detail_frame, font=("Arial", 14), bd=4)
    ent.grid(row=row, column=1, sticky="ew", padx=5, pady=5)
    entries[label] = ent

for idx, field in enumerate(fields):
    create_entry(idx, field, is_combo=(field == "Gender"))

# === Data Functions ===
def refresh_table():
    student_table.delete(*student_table.get_children())
    cursor.execute("SELECT * FROM students")
    for row in cursor.fetchall():
        student_table.insert("", tk.END, values=row)

def clear_entries():
    for key in entries:
        if key == "Gender":
            entries[key].set("")
        else:
            entries[key].delete(0, tk.END)

def validate_inputs():
    contact = entries["Contact"].get().strip()
    dob = entries["D.O.B"].get().strip()
    if not contact.isdigit() or len(contact) != 10:
        messagebox.showerror("Error", "Contact must be 10 digits.")
        return False
    try:
        datetime.strptime(dob, "%d-%m-%Y")
    except ValueError:
        messagebox.showerror("Error", "DOB must be in DD-MM-YYYY format.")
        return False
    return True

def on_add():
    if validate_inputs():
        values = [entries[f].get().strip() for f in fields]
        try:
            cursor.execute("INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", values)
            conn.commit()
            refresh_table()
            clear_entries()
            messagebox.showinfo("Success", "Student added successfully!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Roll No already exists.")

def on_update():
    selected = student_table.selection()
    if selected:
        roll = student_table.item(selected)['values'][0]
        values = [entries[f].get().strip() for f in fields]
        cursor.execute("""
            UPDATE students SET 
                name=?, class=?, section=?, contact=?, father=?, address=?, gender=?, dob=?
            WHERE roll=?""", values[1:] + [roll])
        conn.commit()
        refresh_table()
        clear_entries()
        messagebox.showinfo("Success", "Record updated.")

def on_delete():
    selected = student_table.selection()
    if selected:
        roll = student_table.item(selected)['values'][0]
        cursor.execute("DELETE FROM students WHERE roll=?", (roll,))
        conn.commit()
        refresh_table()
        clear_entries()
        messagebox.showinfo("Success", "Record deleted.")

def on_row_select(event):
    selected = student_table.selection()
    if selected:
        values = student_table.item(selected)['values']
        for i, key in enumerate(fields):
            entries[key].delete(0, tk.END)
            entries[key].insert(0, values[i])
        entries["Gender"].set(values[fields.index("Gender")])

# === Buttons ===
btn_frame = tk.Frame(detail_frame, bg="lightgrey", bd=10, relief=tk.GROOVE)
btn_frame.grid(row=10, column=0, columnspan=2, pady=10)

tk.Button(btn_frame, text="Add", width=12, font=("Arial", 13), command=on_add).grid(row=0, column=0, padx=5, pady=5)
tk.Button(btn_frame, text="Update", width=12, font=("Arial", 13), command=on_update).grid(row=0, column=1, padx=5, pady=5)
tk.Button(btn_frame, text="Delete", width=12, font=("Arial", 13), command=on_delete).grid(row=1, column=0, padx=5, pady=5)
tk.Button(btn_frame, text="Clear", width=12, font=("Arial", 13), command=clear_entries).grid(row=1, column=1, padx=5, pady=5)

# === Search ===
search_frame = tk.Frame(data_frame, bg="lightgrey", bd=10, relief=tk.GROOVE)
search_frame.grid(row=0, column=0, sticky="ew")

tk.Label(search_frame, text="Search", font=("Arial", 13), bg="lightgrey").grid(row=0, column=0, padx=5)
search_by = ttk.Combobox(search_frame, font=("Arial", 13), state="readonly", values=fields)
search_by.grid(row=0, column=1, padx=5)
search_entry = tk.Entry(search_frame, font=("Arial", 13))
search_entry.grid(row=0, column=2, padx=5)

def search():
    key = search_by.get()
    val = search_entry.get().lower()
    student_table.delete(*student_table.get_children())
    cursor.execute(f"SELECT * FROM students WHERE LOWER({key.replace(' ', '_')}) LIKE ?", ('%' + val + '%',))
    for row in cursor.fetchall():
        student_table.insert("", tk.END, values=row)

tk.Button(search_frame, text="Search", font=("Arial", 12), command=search).grid(row=0, column=3, padx=5)
tk.Button(search_frame, text="Show All", font=("Arial", 12), command=refresh_table).grid(row=0, column=4, padx=5)

# === Table ===
table_frame = tk.Frame(data_frame, bg="lightgrey", bd=10, relief=tk.GROOVE)
table_frame.grid(row=1, column=0, sticky="nsew")

y_scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
x_scroll = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)

student_table = ttk.Treeview(
    table_frame, columns=fields, yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set
)
student_table.bind("<<TreeviewSelect>>", on_row_select)

y_scroll.config(command=student_table.yview)
x_scroll.config(command=student_table.xview)
y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
x_scroll.pack(side=tk.BOTTOM, fill=tk.X)

for col in fields:
    student_table.heading(col, text=col)
    student_table.column(col, width=120, anchor="center")
student_table['show'] = 'headings'
student_table.pack(fill=tk.BOTH, expand=True)

# === Load Data on Start ===
refresh_table()

win.mainloop()