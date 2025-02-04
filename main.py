import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import requests
import html
import random

# TriviaGame class manages the trivia game logic
class TriviaGame:
    def __init__(self, root, mobile_frame):
        # Initialize the TriviaGame instance
        self.root = root
        self.mobile_frame = mobile_frame
        self.question_label = tk.Label(root, wraplength=400, font=("Arial", 12))
        self.question_label.pack(pady=40)  # Add more padding at the top
        self.choices = []
        self.correct_answer = None
        self.question_index = 0
        self.play_game()

    # Fetch a pool of questions from the Open Trivia Database API
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

    # Shuffle the answers for a given question
    def shuffle_answers(self, question: dict) -> dict:
        answers = question["incorrect_answers"] + [question["correct_answer"]]
        random.shuffle(answers)
        question["shuffled_answers"] = answers
        return question

    # Print the current question and its choices to the screen
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
            choice = tk.Button(self.root, text=f"{i+1}. {answer_text}", width=button_width, command=lambda i=i: self.check_answer(i))
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

    # Finish the game and restart if desired
    def finish_game(self):
        messagebox.showinfo("Game Over", "Game finished!")

        # Destroy the choice buttons
        for choice in self.choices:
            choice.destroy()
        self.choices = []

        # Recreate the app window
        self.mobile_frame.destroy()
        app = MobileFrame()
        app.mainloop()

    # Restart the game
    def restart_game(self):
        # Reset question index and clear user answers
        self.question_index = 0
        for question in self.questions:
            question["user_answer"] = None

        # Destroy the restart button
        self.root.pack_forget()

        # Restart the game
        self.play_game()

    # Check the user's answer and display the correct answer
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

    # Start the game
    def play_game(self):
        amount = 4  # Number of questions
        category = 18  # Category ID (Computer Science)
        self.questions = self.get_question_pool(amount, category)
        if not self.questions:
            messagebox.showerror("Error", "Failed to fetch questions. Please try again later.")
            self.mobile_frame.destroy()
            return
        self.questions = [self.shuffle_answers(q) for q in self.questions]
        self.print_question(self.questions[self.question_index])

# MobileFrame class represents the main application window
class MobileFrame(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Mobile Frame")
        self.geometry("768x383")

        # Disable resizing and maximize button
        self.resizable(False, False)

        self.selected_menu_item = "Quiz"  # Set the default selected menu item to "Quiz"
        self.create_menu()
        self.create_content()

        if self.selected_menu_item == "Quiz":
            self.trivia_game = TriviaGame(self, self)

        # Create profile image
        self.create_profile_image()

    # Create the menu buttons
    def create_menu(self):
        # Create and place the menu frame
        menu_frame = tk.Frame(self, bg="#333333")
        menu_frame.place(relx=0, rely=0.1, relwidth=0.2, relheight=0.9)

        # Create and place the menu label
        menu_label = tk.Label(menu_frame, text="Menu", font=("Helvetica", 16), fg="white", bg="#333333")
        menu_label.pack(pady=10)

        # Define menu items
        menu_items = ["Quiz", "About", "Exit"]

        # Create buttons for each menu item
        for item in menu_items:
            button = tk.Button(menu_frame, text=item, font=("Helvetica", 12), bg="#444444", fg="white", padx=10, pady=5,
                               relief=tk.FLAT, command=lambda i=item: self.menu_click(i))
            button.pack(fill=tk.X, pady=5)

    # Create the content based on the selected menu item
    def create_content(self):
        self.content_frame = tk.Frame(self, bg="light blue")  # Set the background color to light blue
        self.content_frame.place(relx=0.2, rely=0, relwidth=0.8, relheight=1)

        if self.selected_menu_item == "About":
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

    # Create and display the profile image
    def create_profile_image(self):
        # Load and resize the image
        image = Image.open("profile.jpg")
        image = image.resize((50, 50), Image.LANCZOS)
        photo = ImageTk.PhotoImage(image)

        # Create a label to display the image
        image_label = tk.Label(self, image=photo)
        image_label.image = photo  # Keep a reference to the image to prevent it from being garbage collected
        image_label.place(relx=0, rely=0, relwidth=0.2, relheight=0.2)

    # Handle menu item clicks
    def menu_click(self, item):
        if item == "Quiz":
            self.selected_menu_item = "Quiz"
            self.create_content()
            if hasattr(self, 'trivia_game') and self.trivia_game is not None:
                self.trivia_game = None  # Destroy the existing TriviaGame object
            self.trivia_game = TriviaGame(self, self)
        elif item == "About":
            self.selected_menu_item = "About"
            self.create_content()

        elif item == "Exit":
            self.destroy()

# Main execution
if __name__ == "__main__":
    app = MobileFrame()
    app.mainloop()
