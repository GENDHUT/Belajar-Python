import random
import operator
import tkinter as tk
from tkinter import messagebox

TIME_LIMIT = 10 
MAX_LIVES = 3  
ops = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.floordiv  
}

class MathQuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Math Quiz")
        self.root.geometry("400x300")

        self.score = 0
        self.lives = MAX_LIVES
        self.time_left = TIME_LIMIT

        self.label_question = tk.Label(root, text="Soal Akan Muncul di Sini", font=("Arial", 14))
        self.label_question.pack(pady=10)

        self.label_timer = tk.Label(root, text=f"⏳ Waktu: {self.time_left} detik", font=("Arial", 12), fg="red")
        self.label_timer.pack()

        self.label_lives = tk.Label(root, text=f"❤️ Nyawa: {self.lives}", font=("Arial", 12))
        self.label_lives.pack()

        self.label_score = tk.Label(root, text=f"🎯 Skor: {self.score}", font=("Arial", 12))
        self.label_score.pack()

        self.entry_answer = tk.Entry(root, font=("Arial", 12))
        self.entry_answer.pack(pady=10)
        self.entry_answer.bind("<Return>", self.check_answer)

        self.button_submit = tk.Button(root, text="Jawab", command=self.check_answer, font=("Arial", 12))
        self.button_submit.pack()

        self.button_exit = tk.Button(root, text="Keluar", command=root.quit, font=("Arial", 12), bg="red", fg="white")
        self.button_exit.pack(pady=10)

        self.generate_question()
        self.update_timer()

    def generate_question(self):
        """Membuat soal matematika secara acak"""
        num_count = random.randint(2, 6)
        numbers = [random.randint(1, 10) for _ in range(num_count)]
        operators = [random.choice(list(ops.keys())) for _ in range(num_count - 1)]

        question = f"{numbers[0]}"
        result = numbers[0]

        for i in range(len(operators)):
            question += f" {operators[i]} {numbers[i + 1]}"
            if operators[i] == "/" and numbers[i + 1] == 0:
                numbers[i + 1] = 1
            result = ops[operators[i]](result, numbers[i + 1])

        self.correct_answer = result
        self.label_question.config(text=f"Soal: {question} = ?")
        self.entry_answer.delete(0, tk.END) 
        self.time_left = TIME_LIMIT  

    def update_timer(self):
        """Mengupdate tampilan timer setiap detik"""
        if self.time_left > 0:
            self.time_left -= 1
            self.label_timer.config(text=f"⏳ Waktu: {self.time_left} detik")
            self.root.after(1000, self.update_timer)
        else:
            self.time_out()

    def check_answer(self, event=None):
        """Memeriksa jawaban pengguna"""
        user_input = self.entry_answer.get()

        if not user_input:
            self.lives -= 1
            self.update_lives()
            return

        try:
            user_answer = int(user_input)
            if user_answer == self.correct_answer:
                self.score += 1
                self.label_score.config(text=f"🎯 Skor: {self.score}")
                self.generate_question()
            else:
                self.lives -= 1
                self.update_lives()
        except ValueError:
            messagebox.showwarning("Peringatan", "Masukkan angka yang valid!")

    def time_out(self):
        """Menangani waktu habis"""
        self.lives -= 1
        self.update_lives()

    def update_lives(self):
        """Memeriksa dan memperbarui nyawa"""
        self.label_lives.config(text=f"❤️ Nyawa: {self.lives}")

        if self.lives <= 0:
            messagebox.showerror("Game Over", f"💀 Semua nyawa habis!\n🎯 Skor Akhir: {self.score}")
            self.root.quit()
        else:
            self.generate_question()

if __name__ == "__main__":
    root = tk.Tk()
    app = MathQuizApp(root)
    root.mainloop()
