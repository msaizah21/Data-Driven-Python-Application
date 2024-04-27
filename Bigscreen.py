import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import requests
import html
import random


class MenuFrame(tk.Frame):
    def __init__(self, parent, controller, title, items):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        menu_frame = tk.Frame(self, bg="#333333")
        menu_frame.place(relx=0, rely=0.1, relwidth=0.2, relheight=0.9)

        menu_label = tk.Label(menu_frame, text=title, font=("Helvetica", 16), fg="white", bg="#333333")
        menu_label.pack(pady=10)

        for item in items:
            button = tk.Button(menu_frame, text=item, font=("Helvetica", 12), bg="#444444", fg="white", padx=10, pady=5,
                               relief=tk.FLAT, command=lambda i=item: self.menu_click(i))
            button.pack(fill=tk.X, pady=5)

    def menu_click(self, item):
        if item == "Quiz":
            self.controller.show_frame("QuizFrame")
        elif item == "About":
            self.controller.show_frame("AboutFrame")
        elif item == "Exit":
            self.controller.destroy()


class QuizFrame(MenuFrame, tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        MenuFrame.__init__(self, parent, controller, "Quiz Menu", ["Quiz", "About", "Exit"])
        self.choices = []  # Initialize the choices attribute
        self.question_index = 0  # Initialize the question_index attribute
        
        self.create_profile_image()  # Add profile picture
        
        self.question_label = tk.Label(self, text="", font=("Helvetica", 14))
        self.question_label.pack(pady=10)
        self.play_game()  # Start the game

    def get_question_pool(self, amount: int, category: int) -> list:
        # Construct the API URL
        url = f"https://opentdb.com/api.php?amount={amount}&category={category}"
        try:
            response = requests.get(url)
            response.raise_for_status()  # Check for any HTTP errors
            data = response.json()
            if 'results' in data:
                return data["results"]
            else:
                print("Unexpected response format:")
                print(data)
                return []
        except requests.exceptions.HTTPError as err:
            print(f"HTTP error occurred: {err}")
            return []
        except requests.exceptions.RequestException as e:
            print(f"Request error occurred: {e}")
            return []

    def shuffle_answers(self, question: dict) -> dict:
        answers = question["incorrect_answers"] + [question["correct_answer"]]
        random.shuffle(answers)
        question["shuffled_answers"] = answers
        return question

    def print_question(self, question: dict) -> None:
        # Display the question text
        self.correct_answer = question["correct_answer"]
        self.question_label.config(text=html.unescape(question["question"]))
        shuffled_answers = question["shuffled_answers"]

        # Destroy existing choice buttons
        for choice in self.choices:
            choice.destroy()
        self.choices = []

        # Create buttons for each answer choice
        num_choices = len(shuffled_answers)
        for i in range(num_choices):
            answer_text = html.unescape(shuffled_answers[i])
            button_width = 50  # Fixed width for better layout
            choice = tk.Button(self, text=f"{i+1}. {answer_text}", width=button_width, command=lambda i=i: self.check_answer(i))
            choice.pack(pady=5)
            self.choices.append(choice)

        # Check if the current question has a user_answer and update the UI accordingly
        if question.get("user_answer") is not None:
            user_choice = int(question["user_answer"]) - 1
            self.choices[user_choice].config(bg="light green")  # Highlight the user's choice

            # Disable all buttons after user has answered
            for i in range(num_choices):
                if i != user_choice:
                    self.choices[i].config(state=tk.DISABLED)

    def finish_game(self):
        messagebox.showinfo("Game Over", "Game finished!")

        # Destroy the choice buttons
        for choice in self.choices:
            choice.destroy()
        self.choices = []

        # Recreate the app window
        self.destroy()
        app = MobileFrame()
        app.mainloop()

    def restart_game(self):
        # Reset question index and clear user answers
        self.question_index = 0
        for question in self.questions:
            question["user_answer"] = None

        # Destroy the restart button
        self.pack_forget()

        # Restart the game
        self.play_game()

    def check_answer(self, choice: int):
        user_choice = str(choice + 1)
        current_question = self.questions[self.question_index]
        current_question["user_answer"] = user_choice

        correct_answer = html.unescape(current_question["correct_answer"])
        messagebox.showinfo("Result", f"The correct answer is: {correct_answer}")

        self.question_index += 1
        if self.question_index < len(self.questions):
            # Destroy the choice buttons
            for choice in self.choices:
                choice.destroy()
            self.choices = []

            self.print_question(self.questions[self.question_index])
        else:
            self.finish_game()

    def play_game(self):
        amount = 4  # Number of questions
        category = 18  # Category ID (Computer Science)
        self.questions = self.get_question_pool(amount, category)
        if not self.questions:
            messagebox.showerror("Error", "Failed to fetch questions. Please try again later.")
            self.destroy()
            return
        self.questions = [self.shuffle_answers(q) for q in self.questions]
        self.print_question(self.questions[self.question_index])

    def create_profile_image(self):
        # Load and resize the image
        image = Image.open("profile.jpg")
        image = image.resize((50, 50), Image.LANCZOS)
        photo = ImageTk.PhotoImage(image)

        # Create a label to display the image
        image_label = tk.Label(self, image=photo)
        image_label.image = photo  # Keep a reference to the image to prevent it from being garbage collected
        image_label.place(relx=0, rely=0, relwidth=0.2, relheight=0.2)


class AboutFrame(MenuFrame, tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        MenuFrame.__init__(self, parent, controller, "About Menu", ["Quiz", "About", "Exit"])
        self.create_content()
        self.create_profile_image()

    def create_content(self):
        self.content_frame = tk.Frame(self, bg="light blue")  # Set the background color to light blue
        self.content_frame.place(relx=0.2, rely=0, relwidth=0.8, relheight=1)

        # Create a scrollable text widget
        text_scroll = tk.Scrollbar(self.content_frame, orient=tk.VERTICAL)
        text_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        text_widget = tk.Text(self.content_frame, wrap=tk.WORD, yscrollcommand=text_scroll.set, bg="light blue", padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)

        # Configure the scrollbars
        text_scroll.config(command=text_widget.yview)

        # About text
        about_text = """
        Welcome to the ultimate trivia experience, brought to you by our Tkinter app! Dive into a world of knowledge and fun with our sleek and user-friendly interface. Powered by the Open Trivia Database API, our app offers a vast array of trivia categories, from history and geography to sports and entertainment. Whether you're a trivia novice or a seasoned expert, there's something for everyone to enjoy.

        Customize your quiz experience by choosing your preferred difficulty level and category, then challenge yourself with a series of engaging trivia questions. Test your knowledge, learn new facts, and see how you stack up against friends and players from around the world on our global leaderboard.

        One of the unique features of our app is its adaptive difficulty system, which adjusts the question difficulty based on your performance. This ensures that you're always challenged and engaged, no matter your level of expertise. Plus, with our regularly updated question database, you'll never run out of new trivia to explore.

        Looking for a solo challenge? Our app offers a single-player mode where you can test your knowledge against the clock. Race against time to answer as many questions as you can correctly and earn your spot on the solo leaderboard.

        Join our community of trivia enthusiasts and start your journey to becoming a trivia master today. With its captivating gameplay, educational content, and competitive features, our Tkinter app is the perfect choice for anyone looking to expand their knowledge and have fun in the process. Download now and let the trivia adventure begin!
        """
        text_widget.insert(tk.END, about_text)

        # Disable text widget editing
        text_widget.config(state=tk.DISABLED)

    def create_profile_image(self):
        # Load and resize the image
        image = Image.open("profile.jpg")
        image = image.resize((50, 50), Image.LANCZOS)
        photo = ImageTk.PhotoImage(image)

        # Create a label to display the image
        image_label = tk.Label(self, image=photo)
        image_label.image = photo  # Keep a reference to the image to prevent it from being garbage collected
        image_label.place(relx=0, rely=0, relwidth=0.2, relheight=0.2)


class MobileFrame(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.geometry("1200x590")
        self.title("Trivea Game")

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (QuizFrame, AboutFrame):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("QuizFrame")

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

# Main execution
if __name__ == "__main__":
    app = MobileFrame()
    app.mainloop()
