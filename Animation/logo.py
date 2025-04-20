from manim import *

class LogoAnimation(Scene):
    def construct(self):
        gradient_colors = [WHITE, GOLD]
        logo = SVGMobject("logosvg.svg").scale(2).move_to(ORIGIN)

        black_logo = logo.copy()
        for submob in black_logo.submobjects:
            submob.set_color(BLACK)

        glow = black_logo.copy().set_color(GOLD).set_opacity(0.1).scale(1.1)
        self.add(glow, black_logo)

        #  Glow cepat
        self.play(
            FadeIn(glow, scale=0.5), 
            FadeIn(black_logo),
            run_time=0.5
        )
        self.wait(1)

        #  Outline 
        outline = black_logo.copy().set_fill(opacity=0).set_stroke(GREY_C, width=2)
        self.play(Create(outline), run_time=3)
        self.wait(0.5)

        #  Gradasi
        gradient_logo = logo.copy()
        for submob in gradient_logo.submobjects:
            submob.set_color_by_gradient(*gradient_colors)

        self.play(Transform(black_logo, gradient_logo), run_time=2)
        self.wait(0.5)

        #  Efek energi 
        self.play(
            black_logo.animate.scale(1.05).shift(UP * 0.05), 
            run_time=0.5,
            rate_func=there_and_back
        )
        self.wait(0.10)
        self.play(
            black_logo.animate.scale(1.1), 
            run_time=1,
            rate_func=smooth
        )
        self.wait(0.10)

        #  Glow memudar
        self.play(glow.animate.scale(1.3).set_opacity(0.03), run_time=2)
        self.remove(glow)
        self.wait(0.10)

        #  Logo menghilang
        self.play(
            black_logo.animate.scale(1.5).set_opacity(0.4), 
            run_time=2,
            rate_func=smooth
        )
        self.play(FadeOut(black_logo, scale=0.2), run_time=2)

        self.wait(1)
