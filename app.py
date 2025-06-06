import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
import pyperclip

# Define the languages we expect in the CSV
LANGUAGES = ["English", "German", "French", "Danish"]

class CSVTabbedLangCopierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Multi-Language Copier")

        # Button to open a CSV file
        open_button = tk.Button(root, text="Open CSV File", command=self.open_file)
        open_button.pack(pady=5)

        # Label to display the name of the opened file
        self.filename_label = tk.Label(root, text="", anchor='w', fg='gray')
        self.filename_label.pack(pady=5)

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

# Handles the file import =---------------------------------------------------------------------------

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8-sig") as csvfile:
                reader = csv.DictReader(csvfile)
                rows = list(reader)


                if "Field" not in reader.fieldnames or "Section" not in reader.fieldnames:
                    messagebox.showerror("Error", "CSV must contain 'Section' and 'Field' columns.")
                    return

                # Clear tabs
                for tab in self.notebook.tabs():
                    self.notebook.forget(tab)

                for lang in LANGUAGES:
                    if lang in reader.fieldnames:
                        self.add_language_tab(lang, rows)
                    else:
                        print(f"Warning: Language '{lang}' not found in CSV columns.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to read CSV:\n{e}")
        
        filename = os.path.basename(file_path)
        self.filename_label.config(text=f"Opened file: {filename}")

# ----------------------------------------------------------------------------------------------------

# Handles the language tabs =-------------------------------------------------

    def add_language_tab(self, language, rows):
        frame = tk.Frame(self.notebook)
        self.notebook.add(frame, text=language)

        for row in rows:
            field = row.get("Field", "").strip()
            section = row.get("Section", "").strip()
            value = row.get(language, "").strip()

            if not field or not value:
                continue

            full_field_name = f"{section} - {field}" if section else field
            self.create_copy_button(full_field_name, value, frame)

# ----------------------------------------------------------------------------

# Handles the button creation =-----------------------------------------------

    def create_copy_button(self, key, value, container):
        frame = tk.Frame(container)
        frame.pack(anchor='w', pady=2, fill='x')

        label = tk.Label(frame, text=key, width=50, anchor='w', justify='left', wraplength=400)
        label.pack(side='left', padx=(0, 5))

        button = tk.Button(
            frame,
            text="Copy",
            width=8,
            bg='SystemButtonFace'
        )
        button.config(command=lambda v=value, b=button: self.copy_to_clipboard(v, b))
        button.pack(side='left')

# ----------------------------------------------------------------------------

# Handles copying the field =-------------------------------------------------

    def copy_to_clipboard(self, value, button):
        pyperclip.copy(value)
        original_text = button["text"]
        original_color = button["bg"]

        button.config(text="✔", bg='green')

        # Revert after 2 seconds
        button.after(2000, lambda: button.config(text=original_text, bg=original_color))

# ----------------------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = CSVTabbedLangCopierApp(root)
    root.mainloop()
