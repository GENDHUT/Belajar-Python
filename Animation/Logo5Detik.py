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

        self.play(
            FadeIn(glow, scale=0.5), 
            FadeIn(black_logo),
            run_time=0.3
        )
        self.wait(0.2)

        outline = black_logo.copy().set_fill(opacity=0).set_stroke(GREY_C, width=2)
        self.play(Create(outline), run_time=0.8)
        self.wait(0.1)

        gradient_logo = logo.copy()
        for submob in gradient_logo.submobjects:
            submob.set_color_by_gradient(*gradient_colors)

        self.play(Transform(black_logo, gradient_logo), run_time=0.6)
        self.wait(0.1)

        self.play(
            black_logo.animate.scale(1.05).shift(UP * 0.05), 
            run_time=0.3,
            rate_func=there_and_back
        )
        self.wait(0.05)
        self.play(
            black_logo.animate.scale(1.1), 
            run_time=0.4,
            rate_func=smooth
        )
        self.wait(0.05)

        self.play(glow.animate.scale(1.3).set_opacity(0.03), run_time=0.5)
        self.remove(glow)
        self.wait(0.05)

        self.play(
            black_logo.animate.scale(1.5).set_opacity(0.4), 
            run_time=0.5,
            rate_func=smooth
        )
        self.play(FadeOut(black_logo, scale=0.2), run_time=0.5)

        self.wait(0.1)
