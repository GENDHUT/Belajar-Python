from manim import *
import random
import numpy as np

class PythonToSVG(Scene):
    def construct(self):
        # 1. Tampilkan teks "python"
        text = Text("python", font_size=96, color=BLUE)
        self.play(Write(text))
        self.wait(0.5)

        # 2. Efek bintang muncul di sekitar teks
        stars = self.create_stars_around(text)
        self.play(*[FadeIn(star, scale=0.2) for star in stars], run_time=0.5)
        self.play(*[star.animate.set_opacity(0) for star in stars], run_time=0.5)

        # 3. Efek guncangan teks
        self.play(
            text.animate.rotate(PI / 12).set_color(YELLOW).shift(0.1 * UP + 0.1 * RIGHT),
            run_time=0.2
        )
        self.play(
            text.animate.rotate(-PI / 6).set_color(RED).shift(0.2 * DOWN + 0.1 * LEFT),
            run_time=0.2
        )
        self.play(
            text.animate.rotate(PI / 12).set_color(PURPLE).shift(0.1 * UP + 0.2 * RIGHT),
            run_time=0.2
        )

        # 4. Load SVG logo Python
        logo = SVGMobject("python.svg")
        logo.set_color_by_gradient(BLUE, YELLOW)
        logo.scale(1).move_to(text.get_center())

        # 5. Transisi morph dari teks ke SVG logo
        self.play(Rotate(text, angle=PI), run_time=0.5)
        self.play(Transform(text, logo), run_time=2)
        self.wait(0.5)

        # 6. Munculkan logo besar
        self.play(FadeOut(text))
        full_logo = logo.copy().scale(2.5)
        self.play(FadeIn(full_logo, shift=UP))
        self.wait(1)

        # 7. Efek bintang keluar
        end_stars = self.create_stars_around(full_logo, count=10)
        self.play(*[FadeIn(star, scale=0.2) for star in end_stars], run_time=0.5)
        self.wait(1)
        self.play(*[FadeOut(mob) for mob in [full_logo] + end_stars], run_time=1)

    def create_stars_around(self, mobject, count=8):
        stars = []
        for _ in range(count):
            star = Star(color=WHITE, fill_opacity=1).scale(0.2)
            rand_angle = random.uniform(0, 2 * PI)
            rand_radius = random.uniform(1, 2)
            offset = [rand_radius * np.cos(rand_angle), rand_radius * np.sin(rand_angle), 0]
            star.move_to(mobject.get_center() + offset)
            stars.append(star)
        return stars
