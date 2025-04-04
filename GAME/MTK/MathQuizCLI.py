import random
import threading
import operator

TIME_LIMIT = 10  
MAX_LIVES = 3   

ops = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.floordiv  
}

def generate_question():
    """Menghasilkan pertanyaan matematika dengan 2 hingga 6 angka dan operator acak"""
    num_count = random.randint(2, 6)  
    numbers = [random.randint(1, 10) for _ in range(num_count)]
    operators = [random.choice(list(ops.keys())) for _ in range(num_count - 1)]

    question = f"{numbers[0]}"
    for i in range(len(operators)):
        question += f" {operators[i]} {numbers[i + 1]}"

    result = numbers[0]
    for i in range(len(operators)):
        if operators[i] == "/" and numbers[i + 1] == 0: 
            numbers[i + 1] = 1
        result = ops[operators[i]](result, numbers[i + 1])

    return question, result

def timeout_handler():
    """Menangani ketika pemain tidak menjawab dalam waktu yang ditentukan"""
    print("\n⏳ Waktu habis! Jawaban dianggap salah.")
    global time_out
    time_out = True

def math_quiz():
    print("🎯 Selamat datang di Kuis Matematika!")
    print(f"Jawablah pertanyaan dalam {TIME_LIMIT} detik atau ketik 'exit' untuk keluar.")
    print(f"❤️ Nyawa: {MAX_LIVES}\n")

    score = 0
    lives = MAX_LIVES  

    while lives > 0:
        question, correct_answer = generate_question()
        print(f"\nSoal: {question} = ?   ❤️ {lives}")

        global time_out
        time_out = False  

        timer = threading.Timer(TIME_LIMIT, timeout_handler)  
        timer.start()

        user_input = input("Jawaban Anda: ")  
        timer.cancel()  

        if time_out:  
            lives -= 1
            if lives == 0:
                break
            continue

        if user_input.lower() == "exit":
            print(f"🎉 Skor Akhir Anda: {score}")
            print("Terima kasih telah bermain!")
            return

        try:
            user_answer = int(user_input)
            if user_answer == correct_answer:
                print("✅ Benar!\n")
                score += 1
            else:
                print(f"❌ Salah! Jawaban yang benar adalah {correct_answer}\n")
                lives -= 1
        except ValueError:
            print("⚠️ Masukkan angka yang valid!\n")
            lives -= 1

    print("\n💀 Game Over! Semua nyawa habis.")
    print(f"🎯 Skor Akhir Anda: {score}")
    print("Terima kasih telah bermain!\n")

if __name__ == "__main__":
    math_quiz()
