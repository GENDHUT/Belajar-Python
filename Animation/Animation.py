from manim import *

class HelloWorld(Scene):
    def construct(self):
        text = Text("Halo, Dunia!")
        self.play(Write(text))
        self.wait(2)

# class FormulaScene(Scene):
#     def construct(self):
#         formula = MathTex("e^{i\\pi} + 1 = 0")
#         self.play(Write(formula))
#         self.wait(2)
