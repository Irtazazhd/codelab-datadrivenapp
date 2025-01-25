import tkinter as tk
from tkinter import ttk, messagebox
import random
import requests
import html


class TriviaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Trivia Quiz App")
        self.root.geometry("900x600")
        self.root.resizable(False, False)
        self.root.configure(bg="#34495e")  # Background color

        # Custom style
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure(
            "TButton",
            font=("Arial", 12, "bold"),  # Reduced font size for buttons
            padding=5,  # Reduced padding for buttons
            background="#1abc9c",
            foreground="white",
            borderwidth=2,
            relief="ridge",
        )
        self.style.map(
            "TButton",
            background=[("active", "#16a085")],
            foreground=[("active", "white")],
        )
        self.style.configure(
            "TLabel",
            font=("Arial", 12),
            background="#34495e",
            foreground="white",
            padding=5,
        )
        self.style.configure("TFrame", background="#2c3e50", relief="groove", borderwidth=3)

        # Variables
        self.category = tk.StringVar()
        self.difficulty = tk.StringVar()
        self.question_count = tk.IntVar(value=10)
        self.questions = []
        self.current_question_index = 0
        self.score = 0

        # Container frame
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(fill="both", expand=True)

        # Load welcome page
        self.show_welcome_page()

    def show_welcome_page(self):
        self.clear_frame()
        header_frame = ttk.Frame(self.main_frame, relief="raised", borderwidth=3)
        header_frame.pack(fill="x", pady=10)

        ttk.Label(
            header_frame,
            text="🎉 Welcome to the Trivia Quiz App! 🎉",
            font=("Arial", 26, "bold"),
            background="#1abc9c",
            foreground="white",
        ).pack(pady=10)

        ttk.Button(self.main_frame, text="Start Quiz", command=self.show_settings_page).pack(pady=15)
        ttk.Button(self.main_frame, text="Instructions", command=self.show_instructions).pack(pady=10)
        ttk.Button(self.main_frame, text="Quit", command=self.root.quit).pack(pady=10)

    def show_instructions(self):
        messagebox.showinfo(
            "Instructions",
            "1. Choose your quiz settings (category, difficulty, number of questions).\n"
            "2. Answer the multiple-choice questions.\n"
            "3. Each correct answer gives you 1 point.\n"
            "4. Try to get the highest score!",
        )

    def show_settings_page(self):
        self.clear_frame()
        ttk.Label(
            self.main_frame,
            text="Quiz Settings",
            font=("Arial", 20, "bold"),
            background="#2c3e50",
            foreground="#1abc9c",
        ).pack(pady=20)

        settings_frame = ttk.Frame(self.main_frame, padding=15, relief="ridge", borderwidth=3)
        settings_frame.pack(pady=20)

        categories = ["Any", "General Knowledge", "Science", "Sports", "History", "Entertainment"]
        ttk.Label(settings_frame, text="Select Category:").grid(row=0, column=0, pady=10, sticky="w")
        category_menu = ttk.Combobox(settings_frame, textvariable=self.category, values=categories, state="readonly")
        category_menu.grid(row=0, column=1, pady=10)

        difficulties = ["Any", "Easy", "Medium", "Hard"]
        ttk.Label(settings_frame, text="Select Difficulty:").grid(row=1, column=0, pady=10, sticky="w")
        difficulty_menu = ttk.Combobox(settings_frame, textvariable=self.difficulty, values=difficulties, state="readonly")
        difficulty_menu.grid(row=1, column=1, pady=10)

        ttk.Label(settings_frame, text="Number of Questions (1-20):").grid(row=2, column=0, pady=10, sticky="w")
        question_count_entry = ttk.Entry(settings_frame, textvariable=self.question_count, width=5, font=("Arial", 12))
        question_count_entry.grid(row=2, column=1, pady=10)

        ttk.Button(self.main_frame, text="Begin Quiz", command=self.fetch_questions).pack(pady=20)

    def fetch_questions(self):
        category_mapping = {
            "Any": "",
            "General Knowledge": "9",
            "Science": "17",
            "Sports": "21",
            "History": "23",
            "Entertainment": "11",
        }

        category_id = category_mapping[self.category.get()]
        difficulty = self.difficulty.get().lower() if self.difficulty.get() != "Any" else ""
        question_count = self.question_count.get()

        if question_count < 1 or question_count > 20:
            messagebox.showerror("Error", "Please enter a number between 1 and 20 for questions.")
            return

        url = f"https://opentdb.com/api.php?amount={question_count}&category={category_id}&difficulty={difficulty}&type=multiple"

        try:
            response = requests.get(url)
            data = response.json()
            if data["response_code"] == 0:
                self.questions = data["results"]
                self.current_question_index = 0
                self.score = 0
                self.show_question_page()
            else:
                messagebox.showerror("Error", "No questions found for the selected options. Try different settings.")
        except requests.RequestException as e:
            messagebox.showerror("Error", f"Failed to fetch questions.\n{e}")

    def show_question_page(self):
        self.clear_frame()

        if self.current_question_index < len(self.questions):
            question_data = self.questions[self.current_question_index]
            question_text = html.unescape(question_data["question"])
            correct_answer = html.unescape(question_data["correct_answer"])
            incorrect_answers = [html.unescape(ans) for ans in question_data["incorrect_answers"]]

            options = incorrect_answers + [correct_answer]
            random.shuffle(options)

            ttk.Label(
                self.main_frame,
                text=f"Question {self.current_question_index + 1}/{len(self.questions)}",
                font=("Arial", 16, "bold"),
                background="#34495e",
                foreground="#1abc9c",
            ).pack(pady=10)

            ttk.Label(
                self.main_frame,
                text=question_text,
                wraplength=700,
                background="#34495e",
                foreground="white",
                font=("Arial", 14),
                borderwidth=2,
                relief="groove",
            ).pack(pady=10)

            for option in options:
                ttk.Button(
                    self.main_frame,
                    text=option,
                    command=lambda opt=option: self.check_answer(correct_answer, opt),
                    style="TButton"
                ).pack(pady=5, padx=10)  # Reduced padding for compactness

        else:
            self.show_results_page()

    def check_answer(self, correct_answer, selected_option):
        if selected_option == correct_answer:
            self.score += 1

        self.current_question_index += 1
        self.show_question_page()

    def show_results_page(self):
        self.clear_frame()
        ttk.Label(
            self.main_frame,
            text="🎉 Quiz Completed! 🎉",
            font=("Arial", 24, "bold"),
            background="#34495e",
            foreground="#1abc9c",
        ).pack(pady=20)
        ttk.Label(
            self.main_frame,
            text=f"Your Score: {self.score}/{len(self.questions)}",
            font=("Arial", 16),
            background="#34495e",
            foreground="#ecf0f1",
        ).pack(pady=10)

        ttk.Button(self.main_frame, text="Retry", command=self.show_settings_page).pack(pady=10)
        ttk.Button(self.main_frame, text="Quit", command=self.root.quit).pack(pady=10)

    def clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = TriviaApp(root)
    root.mainloop()
