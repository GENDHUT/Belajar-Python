from manim import *

class LogoAnimation(Scene):
    def construct(self):
        # Load gambar logo
        logo = ImageMobject("logo.jpg")
        logo.scale(2)  # Perbesar biar kelihatan

        # Step 1: Fade In
        self.play(FadeIn(logo, shift=UP), run_time=2)

        # Step 2: Zoom sedikit
        self.play(logo.animate.scale(1.2), run_time=1.5)

        # Step 3: Rotasi kecil bolak-balik
        self.play(Rotate(logo, angle=0.1), run_time=0.5)
        self.play(Rotate(logo, angle=-0.2), run_time=0.5)
        self.play(Rotate(logo, angle=0.1), run_time=0.5)

        # Step 4: Tunggu sedikit sebelum keluar
        self.wait(2)

        # (Optional) Fade out
        self.play(FadeOut(logo))

