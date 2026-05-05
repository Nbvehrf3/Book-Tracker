import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class BookTrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Book Tracker")
        self.geometry("800x600")

        self.books = []          # all books
        self.genre_filter = tk.StringVar(value="All")
        self.pages_threshold = tk.StringVar()

        self.create_widgets()
        self.load_data()
        self.refresh_treeview()

    def create_widgets(self):
        # Input frame
        input_frame = ttk.LabelFrame(self, text="Add New Book")
        input_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(input_frame, text="Title:").grid(row=0, column=0, padx=5, pady=2, sticky="e")
        self.title_entry = ttk.Entry(input_frame, width=30)
        self.title_entry.grid(row=0, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(input_frame, text="Author:").grid(row=0, column=2, padx=5, pady=2, sticky="e")
        self.author_entry = ttk.Entry(input_frame, width=30)
        self.author_entry.grid(row=0, column=3, padx=5, pady=2, sticky="w")

        ttk.Label(input_frame, text="Genre:").grid(row=1, column=0, padx=5, pady=2, sticky="e")
        self.genre_entry = ttk.Entry(input_frame, width=30)
        self.genre_entry.grid(row=1, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(input_frame, text="Pages:").grid(row=1, column=2, padx=5, pady=2, sticky="e")
        self.pages_entry = ttk.Entry(input_frame, width=30)
        self.pages_entry.grid(row=1, column=3, padx=5, pady=2, sticky="w")

        ttk.Button(input_frame, text="Add Book", command=self.add_book).grid(row=2, column=1, pady=5)
        ttk.Button(input_frame, text="Save", command=self.save_data).grid(row=2, column=3, pady=5)

        # Filter frame
        filter_frame = ttk.LabelFrame(self, text="Filters")
        filter_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(filter_frame, text="Genre:").grid(row=0, column=0, padx=5, pady=2)
        self.genre_combo = ttk.Combobox(filter_frame, textvariable=self.genre_filter,
                                        state="readonly", width=20)
        self.genre_combo.grid(row=0, column=1, padx=5, pady=2)
        self.genre_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_treeview())

        ttk.Label(filter_frame, text="Pages >").grid(row=0, column=2, padx=5, pady=2)
        self.pages_filter_entry = ttk.Entry(filter_frame, textvariable=self.pages_threshold, width=10)
        self.pages_filter_entry.grid(row=0, column=3, padx=5, pady=2)
        ttk.Button(filter_frame, text="Filter by Pages", command=self.refresh_treeview).grid(row=0, column=4, padx=5)
        ttk.Button(filter_frame, text="Show All", command=self.reset_filters).grid(row=0, column=5, padx=5)

        # Treeview
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.tree = ttk.Treeview(tree_frame, columns=("Title", "Author", "Genre", "Pages"), show="headings")
        self.tree.heading("Title", text="Title")
        self.tree.heading("Author", text="Author")
        self.tree.heading("Genre", text="Genre")
        self.tree.heading("Pages", text="Pages")
        self.tree.column("Title", width=200)
        self.tree.column("Author", width=180)
        self.tree.column("Genre", width=150)
        self.tree.column("Pages", width=80)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def add_book(self):
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        genre = self.genre_entry.get().strip()
        pages_str = self.pages_entry.get().strip()

        if not title or not author or not genre or not pages_str:
            messagebox.showerror("Input Error", "All fields must be filled.")
            return

        if not pages_str.isdigit():
            messagebox.showerror("Input Error", "Pages must be a number.")
            return

        pages = int(pages_str)
        self.books.append({"title": title, "author": author, "genre": genre, "pages": pages})

        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.genre_entry.delete(0, tk.END)
        self.pages_entry.delete(0, tk.END)

        self.update_genre_combo()
        self.refresh_treeview()
        self.save_data()   # auto-save after addition

    def update_genre_combo(self):
        genres = sorted({book["genre"] for book in self.books})
        self.genre_combo["values"] = ["All"] + genres
        if not self.genre_filter.get() or self.genre_filter.get() not in ["All"] + genres:
            self.genre_filter.set("All")

    def refresh_treeview(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        filtered = self.books

        selected_genre = self.genre_filter.get()
        if selected_genre != "All":
            filtered = [b for b in filtered if b["genre"] == selected_genre]

        pages_str = self.pages_threshold.get().strip()
        if pages_str:
            if pages_str.isdigit():
                threshold = int(pages_str)
                filtered = [b for b in filtered if b["pages"] > threshold]
            else:
                messagebox.showerror("Input Error", "Pages threshold must be a number.")

        for book in filtered:
            self.tree.insert("", tk.END, values=(book["title"], book["author"], book["genre"], book["pages"]))

    def reset_filters(self):
        self.genre_filter.set("All")
        self.pages_threshold.set("")
        self.refresh_treeview()

    def save_data(self):
        with open("books.json", "w", encoding="utf-8") as f:
            json.dump(self.books, f, indent=4, ensure_ascii=False)

    def load_data(self):
        if not os.path.exists("books.json"):
            self.books = []
            self.update_genre_combo()
            return
        try:
            with open("books.json", "r", encoding="utf-8") as f:
                self.books = json.load(f)
            self.update_genre_combo()
        except (json.JSONDecodeError, IOError):
            self.books = []
            self.update_genre_combo()

if __name__ == "__main__":
    app = BookTrackerApp()
    app.mainloop()