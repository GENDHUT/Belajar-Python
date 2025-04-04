from flask import Flask, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Kalkulator Sederhana</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      background: #f0f0f0;
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
      margin: 0;
    }
    .calculator {
      background: #fff;
      border-radius: 10px;
      box-shadow: 0 4px 10px rgba(0,0,0,0.2);
      width: 320px;
      padding: 20px;
    }
    .display {
      width: 100%;
      height: 60px;
      background: #222;
      color: #fff;
      text-align: right;
      font-size: 28px;
      padding: 10px;
      border-radius: 5px;
      margin-bottom: 15px;
      overflow-x: auto;
    }
    .buttons {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      grid-gap: 10px;
    }
    button {
      padding: 20px;
      font-size: 18px;
      border: none;
      border-radius: 5px;
      cursor: pointer;
      transition: background 0.3s;
    }
    button:hover {
      opacity: 0.9;
    }
    button.operator {
      background-color: #f57c00;
      color: #fff;
    }
    button.equals {
      background-color: #039be5;
      color: #fff;
      grid-column: span 2;
    }
    button.clear {
      background-color: #d32f2f;
      color: #fff;
    }
    button.backspace {
      background-color: #616161;
      color: #fff;
    }
  </style>
</head>
<body>
  <div class="calculator">
    <div id="display" class="display">0</div>
    <div class="buttons">
      <button class="clear" onclick="clearDisplay()">C</button>
      <button class="backspace" onclick="backspace()">←</button>
      <button onclick="appendCharacter('(')">(</button>
      <button onclick="appendCharacter(')')">)</button>
      
      <button onclick="appendCharacter('7')">7</button>
      <button onclick="appendCharacter('8')">8</button>
      <button onclick="appendCharacter('9')">9</button>
      <button class="operator" onclick="appendCharacter('/')">÷</button>
      
      <button onclick="appendCharacter('4')">4</button>
      <button onclick="appendCharacter('5')">5</button>
      <button onclick="appendCharacter('6')">6</button>
      <button class="operator" onclick="appendCharacter('*')">×</button>
      
      <button onclick="appendCharacter('1')">1</button>
      <button onclick="appendCharacter('2')">2</button>
      <button onclick="appendCharacter('3')">3</button>
      <button class="operator" onclick="appendCharacter('-')">−</button>
      
      <button onclick="appendCharacter('0')">0</button>
      <button onclick="appendCharacter('.')">.</button>
      <button class="operator" onclick="appendCharacter('+')">+</button>
      <button class="equals" onclick="calculate()">=</button>
    </div>
  </div>
  
  <script>
    const display = document.getElementById("display");
    
    function appendCharacter(char) {
      if (display.innerText === "0" || display.innerText === "Error") {
        display.innerText = "";
      }
      display.innerText += char;
    }
    
    function clearDisplay() {
      display.innerText = "0";
    }
    
    function backspace() {
      if (display.innerText.length > 1) {
        display.innerText = display.innerText.slice(0, -1);
      } else {
        display.innerText = "0";
      }
    }
    
    function calculate() {
      try {
        // Evaluasi ekspresi menggunakan eval (pastikan hanya input kalkulator yang valid)
        let result = eval(display.innerText);
        display.innerText = result;
      } catch (e) {
        display.innerText = "Error";
      }
    }
  </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

if __name__ == "__main__":
    app.run(debug=True)
