from manim import *

class LogoAnimation(Scene):
    def construct(self):
        logo = ImageMobject("logo.jpg")
        logo.scale(2)  
        self.play(FadeIn(logo, shift=UP), run_time=2)

        self.play(logo.animate.scale(1.2), run_time=1.5)

        self.play(Rotate(logo, angle=0.1), run_time=0.5)
        self.play(Rotate(logo, angle=-0.2), run_time=0.5)
        self.play(Rotate(logo, angle=0.1), run_time=0.5)

        self.wait(2)

        self.play(FadeOut(logo))

