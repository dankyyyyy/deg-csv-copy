import os
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
import pyperclip

LANGUAGES = ["English", "German", "French", "Danish"]

class CSVTabbedLangCopierApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Multi-Language Copier")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(2, weight=1)

        # Open CSV Button
        open_button = tk.Button(root, text="Open CSV File", command=self.open_file)
        open_button.grid(row=0, column=0, sticky='ew', padx=10, pady=5)

        # Filename label
        self.filename_label = tk.Label(root, text="", anchor='w', fg='gray')
        self.filename_label.grid(row=1, column=0, sticky='ew', padx=10, pady=5)

        # Notebook for languages
        self.notebook = ttk.Notebook(root)
        self.notebook.grid(row=2, column=0, sticky='nsew', padx=10, pady=10)

# File loading
    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8-sig") as csvfile:
                reader = csv.DictReader(csvfile)
                rows = list(reader)

                if "Field" not in reader.fieldnames or "Section" not in reader.fieldnames: # type: ignore
                    messagebox.showerror("Error", "CSV must contain 'Section' and 'Field' columns.")
                    return

                # Clear tabs
                for tab in self.notebook.tabs():
                    self.notebook.forget(tab)

                for lang in LANGUAGES:
                    if lang in reader.fieldnames: # type: ignore
                        self.add_language_tab(lang, rows)
                    else:
                        print(f"Warning: Language '{lang}' not found in CSV columns.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to read CSV:\n{e}")

        filename = os.path.basename(file_path)
        self.filename_label.config(text=f"Opened file: {filename}")

# Add language tab
    def add_language_tab(self, language, rows):
        tab = ttk.Frame(self.notebook)
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(0, weight=1)
        self.notebook.add(tab, text=language)

        canvas = tk.Canvas(tab)
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.columnconfigure(0, weight=1)

        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        scrollable_frame.bind("<Configure>", on_frame_configure)

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        # Group by Section
        sections = {}
        for row in rows:
            section = row.get("Section", "General")
            sections.setdefault(section, []).append(row)

        def section_sort_key(section_name):
            if section_name == "General":
                return (0, 0)
            m = re.match(r"Collection (\d+)", section_name)
            if m:
                return (1, int(m.group(1)))
            return (2, section_name)

        sorted_sections = sorted(sections.keys(), key=section_sort_key)

        current_row = 0
        for section_name in sorted_sections:
            section_rows = sections[section_name]

            # Header frame + toggle button
            header_frame = ttk.Frame(scrollable_frame)
            header_frame.grid(row=current_row, column=0, sticky='ew', pady=5)
            header_frame.columnconfigure(1, weight=1)

            toggle_btn = tk.Button(header_frame, text='−', width=2, font=("Arial", 12, "bold"))
            toggle_btn.grid(row=0, column=0, sticky='w')

            title_label = ttk.Label(header_frame, text=section_name, font=("Arial", 11, "bold"))
            title_label.grid(row=0, column=1, sticky='w', padx=5)

            current_row += 1

            content_frame = ttk.Frame(scrollable_frame)
            content_frame.grid(row=current_row, column=0, sticky='ew', padx=20)
            content_frame.columnconfigure(1, weight=1)
            current_row += 1

            # Create rows in content_frame for each field
            row_idx = 0
            for row in section_rows:
                field_name = row.get("Field", "")
                value = row.get(language, "")
                self.create_copy_button(field_name, value, content_frame, row_idx)
                row_idx += 1

            # Toggle behavior
            def toggle(cf=content_frame, btn=toggle_btn):
                if cf.winfo_viewable():
                    cf.grid_remove()
                    btn.config(text='+')
                else:
                    cf.grid()
                    btn.config(text='−')

            toggle_btn.config(command=toggle)

# Create a single field row: label, preview, copy button
    def create_copy_button(self, key, value, container, row_idx):
        # Create three widgets in grid on one row
        label = tk.Label(container, text=key, anchor='w', justify='left', wraplength=400)
        label.grid(row=row_idx, column=0, sticky='w', padx=(0, 5), pady=2)

        preview_text = (value[:50] + "…") if len(value) > 50 else value
        preview_label = tk.Label(container, text=preview_text, anchor='w', fg='gray', font=("Arial", 9, "italic"))
        preview_label.grid(row=row_idx, column=1, sticky='w', padx=(0, 5), pady=2)

        button = tk.Button(container, text="Copy", width=8, bg="SystemButtonFace")
        button.config(command=lambda v=value, b=button: self.copy_to_clipboard(v, b))
        button.grid(row=row_idx, column=2, sticky='w', pady=2)

# Copy logic with button feedback
    def copy_to_clipboard(self, value, button):
        pyperclip.copy(value)
        original_text = button["text"]
        original_color = button["bg"]

        button.config(text="✔", bg='green')

        button.after(2000, lambda: button.config(text=original_text, bg=original_color))

if __name__ == "__main__":
    root = tk.Tk()
    app = CSVTabbedLangCopierApp(root)
    root.mainloop()
