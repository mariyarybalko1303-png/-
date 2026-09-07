#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
===========================================================================
               НЕОНОВИЙ АРКАДНИЙ ПІНГ-ПОНГ (Python Retro Pong)
===========================================================================
Повнофункціональна гра Пінг-Понг у ретро-неоновому стилі з плавним керуванням,
ефектами часток, вібрацією екрана, та двома режимами гри.

Керування:
  • Ліва ракетка (Гравець 1):  W (Вгору), S (Вниз)
  • Права ракетка (Гравець 2/ШІ): Стрілка Вгору, Стрілка Вниз
  • Пауза: Space (Пробіл)
===========================================================================
"""

import tkinter as tk
import random
import math
import time

class PongGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Neon Arcade Pong 🏓")
        self.root.resizable(False, False)
        
        # Параметри екрана
        self.width = 800
        self.height = 500
        
        # Стан гри
        self.game_mode = "sp"  # "sp" - одиночна проти ШІ, "mp" - на двох
        self.difficulty = "medium"  # "easy", "medium", "hard"
        self.score_limit = 10
        self.is_paused = False
        self.game_active = False
        
        # Налаштування кольорів (Neon Cyberpunk)
        self.COLOR_BG = "#0d0e15"
        self.COLOR_GRID = "#1a1c28"
        self.COLOR_P1 = "#00f0ff"  # Cyan
        self.COLOR_P2 = "#ff007f"  # Neon Pink
        self.COLOR_BALL = "#00ff66"  # Lime Green
        self.COLOR_UI = "#ffffff"
        self.COLOR_TEXT = "#4ef2d2"
        
        # Фізичні параметри ракетки
        self.paddle_width = 15
        self.paddle_height = 90
        self.paddle_speed = 8
        
        # Початкові позиції
        self.reset_positions()
        
        # Стан клавіатури (для плавного руху без затримок)
        self.pressed_keys = {}
        
        # Частки (ефекти іскор)
        self.particles = []
        
        # Ефект тремтіння екрана (Screen Shake)
        self.shake_intensity = 0
        self.shake_decay = 0.8
        self.original_geom = None
        
        self.build_menu()

    def reset_positions(self):
        # Координати ракеток (центри по осі Y)
        self.p1_x = 40
        self.p1_y = self.height / 2
        self.p2_x = self.width - 40
        self.p2_y = self.height / 2
        
        # Стан м'яча
        self.ball_x = self.width / 2
        self.ball_y = self.height / 2
        self.ball_radius = 8
        self.ball_base_speed = 5
        self.ball_speed = self.ball_base_speed
        self.ball_dx = 0
        self.ball_dy = 0
        
        # Рахунок
        self.score1 = 0
        self.score2 = 0

    def start_ball(self, to_winner=1):
        """Запускає м'яч у гру з випадковим кутом."""
        self.ball_x = self.width / 2
        self.ball_y = self.height / 2
        self.ball_speed = self.ball_base_speed
        
        # Випадковий кут від -45 до +45 градусів
        angle = random.uniform(-math.pi/6, math.pi/6)
        direction = -1 if to_winner == 2 else 1
        
        self.ball_dx = direction * self.ball_speed * math.cos(angle)
        self.ball_dy = self.ball_speed * math.sin(angle)

    def build_menu(self):
        """Будує стартове головне меню."""
        # Очищення вікна
        for widget in self.root.winfo_children():
            widget.destroy()
            
        self.menu_frame = tk.Frame(self.root, bg=self.COLOR_BG, width=self.width, height=self.height)
        self.menu_frame.pack_propagate(False)
        self.menu_frame.pack()
        
        # Заголовок
        lbl_title = tk.Label(
            self.menu_frame, 
            text="NEON PONG", 
            font=("Segoe UI", 36, "bold italic"), 
            bg=self.COLOR_BG, 
            fg=self.COLOR_P1
        )
        lbl_title.pack(pady=(40, 20))
        
        lbl_subtitle = tk.Label(
            self.menu_frame, 
            text="🏓 Ретро Аркада з нуля 🏓", 
            font=("Segoe UI", 14, "italic"), 
            bg=self.COLOR_BG, 
            fg=self.COLOR_BALL
        )
        lbl_subtitle.pack(pady=(0, 30))
        
        # Вибір режиму
        mode_frame = tk.LabelFrame(
            self.menu_frame, 
            text=" Режим гри ", 
            font=("Segoe UI", 11, "bold"), 
            bg=self.COLOR_BG, 
            fg=self.COLOR_UI,
            padx=20,
            pady=10
        )
        mode_frame.pack(pady=10)
        
        self.var_mode = tk.StringVar(value="sp")
        rb_sp = tk.Radiobutton(
            mode_frame, text="Одиночна гра (Проти ШІ)", variable=self.var_mode, value="sp",
            font=("Segoe UI", 10), bg=self.COLOR_BG, fg=self.COLOR_UI, selectcolor=self.COLOR_BG,
            activebackground=self.COLOR_BG, activeforeground=self.COLOR_P1, command=self.toggle_difficulty_view
        )
        rb_sp.pack(anchor=tk.W)
        
        rb_mp = tk.Radiobutton(
            mode_frame, text="Гра на двох (Локально)", variable=self.var_mode, value="mp",
            font=("Segoe UI", 10), bg=self.COLOR_BG, fg=self.COLOR_UI, selectcolor=self.COLOR_BG,
            activebackground=self.COLOR_BG, activeforeground=self.COLOR_P2, command=self.toggle_difficulty_view
        )
        rb_mp.pack(anchor=tk.W)
        
        # Вибір складності ШІ
        self.diff_frame = tk.LabelFrame(
            self.menu_frame, 
            text=" Рівень ШІ ", 
            font=("Segoe UI", 11, "bold"), 
            bg=self.COLOR_BG, 
            fg=self.COLOR_UI,
            padx=20,
            pady=5
        )
        self.diff_frame.pack(pady=10)
        
        self.var_diff = tk.StringVar(value="medium")
        for code, label in [("easy", "Новачок"), ("medium", "Профі"), ("hard", "Майстер")]:
            rb_diff = tk.Radiobutton(
                self.diff_frame, text=label, variable=self.var_diff, value=code,
                font=("Segoe UI", 10), bg=self.COLOR_BG, fg=self.COLOR_UI, selectcolor=self.COLOR_BG,
                activebackground=self.COLOR_BG, activeforeground=self.COLOR_BALL
            )
            rb_diff.pack(side=tk.LEFT, padx=10)
            
        # Кнопка СТАРТ
        btn_start = tk.Button(
            self.menu_frame,
            text="ЗАПУСТИТИ ГРУ",
            font=("Segoe UI", 14, "bold"),
            bg="#24283b",
            fg=self.COLOR_BALL,
            activebackground=self.COLOR_BALL,
            activeforeground=self.COLOR_BG,
            relief="flat",
            bd=0,
            padx=30,
            pady=10,
            command=self.start_game
        )
        btn_start.pack(pady=(20, 10))
        btn_start.bind("<Enter>", lambda e: btn_start.config(bg=self.COLOR_BALL, fg=self.COLOR_BG))
        btn_start.bind("<Leave>", lambda e: btn_start.config(bg="#24283b", fg=self.COLOR_BALL))

    def toggle_difficulty_view(self):
        """Приховує чи показує панель вибору складності."""
        if self.var_mode.get() == "sp":
            self.diff_frame.pack(pady=10)
        else:
            self.diff_frame.pack_forget()

    def start_game(self):
        """Ініціалізує ігрове вікно та запускає геймплей."""
        self.game_mode = self.var_mode.get()
        self.difficulty = self.var_diff.get()
        
        # Налаштування швидкості ракетки ШІ залежно від рівня
        if self.difficulty == "easy":
            self.ai_speed = 3.5
        elif self.difficulty == "medium":
            self.ai_speed = 5.2
        else:
            self.ai_speed = 7.5
            
        # Очищення та побудова Canvas
        self.menu_frame.destroy()
        
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height, bg=self.COLOR_BG, highlightthickness=0)
        self.canvas.pack()
        
        # Гарячі клавіші
        self.root.bind("<KeyPress>", self.on_key_press)
        self.root.bind("<KeyRelease>", self.on_key_release)
        self.root.bind("<space>", lambda e: self.toggle_pause())
        self.root.bind("<Escape>", lambda e: self.exit_to_menu())
        
        # Скидання параметрів
        self.reset_positions()
        self.game_active = True
        self.is_paused = False
        self.original_geom = self.root.geometry()
        
        # Стартовий запуск м'яча
        self.start_ball(random.choice([1, 2]))
        
        # Запуск головного ігрового циклу
        self.update_game()

    def toggle_pause(self):
        if self.game_active:
            self.is_paused = not self.is_paused
            if not self.is_paused:
                self.update_game()

    def exit_to_menu(self):
        self.game_active = False
        self.root.unbind("<KeyPress>")
        self.root.unbind("<KeyRelease>")
        self.root.unbind("<space>")
        self.root.unbind("<Escape>")
        if self.original_geom:
            self.root.geometry(self.original_geom)
        self.build_menu()

    # ====================================================================
    # КЕРУВАННЯ ТА ФІЗИКА
    # ====================================================================

    def on_key_press(self, event):
        self.pressed_keys[event.keysym.lower()] = True

    def on_key_release(self, event):
        self.pressed_keys[event.keysym.lower()] = False

    def move_paddles(self):
        # Гравець 1 (ліва ракетка) - W / S
        if self.pressed_keys.get("w") or self.pressed_keys.get("ц"):
            self.p1_y -= self.paddle_speed
        if self.pressed_keys.get("s") or self.pressed_keys.get("ы") or self.pressed_keys.get("і"):
            self.p1_y += self.paddle_speed
            
        # Гравець 2 (права ракетка) - Up / Down (якщо мультиплеєр)
        if self.game_mode == "mp":
            if self.pressed_keys.get("up"):
                self.p2_y -= self.paddle_speed
            if self.pressed_keys.get("down"):
                self.p2_y += self.paddle_speed
        else:
            # Інтелект ШІ (права ракетка слідкує за м'ячем)
            target_y = self.ball_y
            # Додаємо невелику затримку реакції для чесності
            if self.ball_dx > 0:  # ШІ активно реагує, тільки коли м'яч летить до нього
                if abs(self.p2_y - target_y) > 10:
                    if self.p2_y < target_y:
                        self.p2_y += self.ai_speed
                    else:
                        self.p2_y -= self.ai_speed
            else:
                # Повернення в центр, коли м'яч летить у інший бік
                center_y = self.height / 2
                if abs(self.p2_y - center_y) > 10:
                    self.p2_y += self.ai_speed * 0.4 if self.p2_y < center_y else -self.ai_speed * 0.4

        # Межі екрана для ракеток
        self.p1_y = clamp(self.p1_y, self.paddle_height/2, self.height - self.paddle_height/2)
        self.p2_y = clamp(self.p2_y, self.paddle_height/2, self.height - self.paddle_height/2)

    def update_physics(self):
        """Оновлює положення м'яча та обчислює колізії."""
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy
        
        # 1. Відскок від верхньої та нижньої стін
        if self.ball_y - self.ball_radius <= 0:
            self.ball_y = self.ball_radius
            self.ball_dy *= -1
            self.create_impact_particles(self.ball_x, 0, self.COLOR_BALL)
            self.trigger_screen_shake(2)
        elif self.ball_y + self.ball_radius >= self.height:
            self.ball_y = self.height - self.ball_radius
            self.ball_dy *= -1
            self.create_impact_particles(self.ball_x, self.height, self.COLOR_BALL)
            self.trigger_screen_shake(2)
            
        # 2. Колізія з лівою ракеткою (P1)
        p1_left = self.p1_x - self.paddle_width/2
        p1_right = self.p1_x + self.paddle_width/2
        p1_top = self.p1_y - self.paddle_height/2
        p1_bottom = self.p1_y + self.paddle_height/2
        
        if (self.ball_x - self.ball_radius <= p1_right and 
            self.ball_x + self.ball_radius >= p1_left and 
            self.ball_y >= p1_top and self.ball_y <= p1_bottom and 
            self.ball_dx < 0):
            
            # Відскок залежить від місця удару по ракетці
            relative_intersect_y = (self.p1_y - self.ball_y) / (self.paddle_height / 2)
            bounce_angle = relative_intersect_y * (math.pi / 4) # макс кут 45 градусів
            
            # Прискорення при кожному ударі
            self.ball_speed = min(self.ball_speed + 0.4, 15)
            self.ball_dx = self.ball_speed * math.cos(bounce_angle)
            self.ball_dy = -self.ball_speed * math.sin(bounce_angle)
            
            # Ефекти
            self.create_impact_particles(p1_right, self.ball_y, self.COLOR_P1)
            self.trigger_screen_shake(4)

        # 3. Колізія з правою ракеткою (P2)
        p2_left = self.p2_x - self.paddle_width/2
        p2_right = self.p2_x + self.paddle_width/2
        p2_top = self.p2_y - self.paddle_height/2
        p2_bottom = self.p2_y + self.paddle_height/2
        
        if (self.ball_x + self.ball_radius >= p2_left and 
            self.ball_x - self.ball_radius <= p2_right and 
            self.ball_y >= p2_top and self.ball_y <= p2_bottom and 
            self.ball_dx > 0):
            
            relative_intersect_y = (self.p2_y - self.ball_y) / (self.paddle_height / 2)
            bounce_angle = relative_intersect_y * (math.pi / 4)
            
            self.ball_speed = min(self.ball_speed + 0.4, 15)
            self.ball_dx = -self.ball_speed * math.cos(bounce_angle)
            self.ball_dy = -self.ball_speed * math.sin(bounce_angle)
            
            self.create_impact_particles(p2_left, self.ball_y, self.COLOR_P2)
            self.trigger_screen_shake(4)

        # 4. Голи та виліт за межі екрана
        if self.ball_x < 0:
            self.score2 += 1
            self.trigger_screen_shake(12)
            self.create_goal_explosion(self.ball_y, self.COLOR_P2)
            self.check_game_over(2)
        elif self.ball_x > self.width:
            self.score1 += 1
            self.trigger_screen_shake(12)
            self.create_goal_explosion(self.ball_y, self.COLOR_P1)
            self.check_game_over(1)

    def check_game_over(self, scorer):
        if self.score1 >= self.score_limit or self.score2 >= self.score_limit:
            self.game_active = False
        else:
            self.start_ball(scorer)

    # ====================================================================
    # ЕФЕКТИ ТА ЧАСТКИ (PARTICLES & SCREEN SHAKE)
    # ====================================================================

    def create_impact_particles(self, x, y, color):
        """Генерує невеликі іскри при зіткненнях."""
        for _ in range(8):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1.5, 4.0)
            life = random.uniform(0.15, 0.4)
            self.particles.append({
                "x": x,
                "y": y,
                "dx": speed * math.cos(angle),
                "dy": speed * math.sin(angle),
                "color": color,
                "radius": random.uniform(2, 4),
                "life": life,
                "max_life": life
            })

    def create_goal_explosion(self, y_goal, color):
        """Вибух з іскор по всій висоті стійки гола."""
        side_x = 10 if color == self.COLOR_P1 else self.width - 10
        for _ in range(35):
            angle = random.uniform(-math.pi/2, math.pi/2)
            if side_x > self.width/2:
                angle += math.pi # вибух всередину поля
            speed = random.uniform(3, 8)
            life = random.uniform(0.3, 0.7)
            self.particles.append({
                "x": side_x,
                "y": y_goal,
                "dx": speed * math.cos(angle),
                "dy": speed * math.sin(angle),
                "color": color,
                "radius": random.uniform(3, 6),
                "life": life,
                "max_life": life
            })

    def update_particles(self):
        """Оновлює та відсіює згаслі частки."""
        active_particles = []
        for p in self.particles:
            p["x"] += p["dx"]
            p["y"] += p["dy"]
            p["life"] -= 0.016  # зменшуємо час життя (~1 крок при 60 FPS)
            
            # Ефект гальмування опором повітря
            p["dx"] *= 0.96
            p["dy"] *= 0.96
            
            if p["life"] > 0:
                active_particles.append(p)
        self.particles = active_particles

    def trigger_screen_shake(self, force):
        """Активує вібрацію екрана для імпакту."""
        self.shake_intensity = max(self.shake_intensity, force)

    def apply_screen_shake(self):
        """Реалізує зміщення вікна для ілюзії тремтіння."""
        if self.shake_intensity > 0.5:
            dx = random.randint(-int(self.shake_intensity), int(self.shake_intensity))
            dy = random.randint(-int(self.shake_intensity), int(self.shake_intensity))
            
            # Зміщуємо вікно відносно початкового геометрічного положення
            geom_parts = self.original_geom.split('+')
            if len(geom_parts) == 3:
                size_part = geom_parts[0]
                orig_x = int(geom_parts[1])
                orig_y = int(geom_parts[2])
                self.root.geometry(f"{size_part}+{orig_x + dx}+{orig_y + dy}")
                
            self.shake_intensity *= self.shake_decay
        else:
            # Повернення в оригінальне положення
            if self.original_geom and self.root.geometry() != self.original_geom:
                self.root.geometry(self.original_geom)

    # ====================================================================
    # РЕНДЕРИНГ ТА ГЕЙМПЛЕЙ-ЦИКЛ
    # ====================================================================

    def draw_scene(self):
        """Малює всі графічні об'єкти на Canvas."""
        self.canvas.delete("all")
        
        # 1. Малювання сітки та центральної лінії (Neon Style)
        # Центральна лінія
        dash_len = 15
        gap_len = 15
        for y in range(0, self.height, dash_len + gap_len):
            self.canvas.create_line(
                self.width/2, y, self.width/2, y + dash_len, 
                fill=self.COLOR_GRID, width=3
            )
            
        # 2. Відмальовування ракеток
        # Гравець 1 (Ліва)
        self.canvas.create_rectangle(
            self.p1_x - self.paddle_width/2, self.p1_y - self.paddle_height/2,
            self.p1_x + self.paddle_width/2, self.p1_y + self.paddle_height/2,
            fill=self.COLOR_P1, outline=self.COLOR_P1, width=2
        )
        
        # Гравець 2 (Права)
        self.canvas.create_rectangle(
            self.p2_x - self.paddle_width/2, self.p2_y - self.paddle_height/2,
            self.p2_x + self.paddle_width/2, self.p2_y + self.paddle_height/2,
            fill=self.COLOR_P2, outline=self.COLOR_P2, width=2
        )
        
        # 3. Відмальовування часток
        for p in self.particles:
            # Згасання яскравості залежно від життя
            alpha = p["life"] / p["max_life"]
            # Замість повноцінного альфа-каналу (який повільний у Tkinter) змінюємо радіус
            rad = max(1, p["radius"] * alpha)
            self.canvas.create_oval(
                p["x"] - rad, p["y"] - rad,
                p["x"] + rad, p["y"] + rad,
                fill=p["color"], outline=""
            )
            
        # 4. Відмальовування м'яча
        if self.game_active:
            self.canvas.create_oval(
                self.ball_x - self.ball_radius, self.ball_y - self.ball_radius,
                self.ball_x + self.ball_radius, self.ball_y + self.ball_radius,
                fill=self.COLOR_BALL, outline=self.COLOR_BALL, width=2
            )
            
        # 5. Рахунок (Цифрові неон-шрифти)
        self.canvas.create_text(
            self.width/2 - 70, 50,
            text=str(self.score1), font=("Segoe UI", 36, "bold"),
            fill=self.COLOR_P1
        )
        
        self.canvas.create_text(
            self.width/2 + 70, 50,
            text=str(self.score2), font=("Segoe UI", 36, "bold"),
            fill=self.COLOR_P2
        )
        
        # 6. Інструкція (Пауза/Вихід) знизу
        self.canvas.create_text(
            self.width/2, self.height - 20,
            text="Space: Пауза  |  Esc: Головне меню  |  W/S (Ліва)  |  Arrows (Права)",
            font=("Segoe UI", 9, "italic"),
            fill="#51556d"
        )
        
        # 7. Накладання екранів станів
        if self.is_paused:
            self.canvas.create_rectangle(0, 0, self.width, self.height, fill="#000000", stipple="gray50")
            self.canvas.create_text(
                self.width/2, self.height/2,
                text="ПАУЗА", font=("Segoe UI", 28, "bold"),
                fill=self.COLOR_TEXT
            )
            self.canvas.create_text(
                self.width/2, self.height/2 + 40,
                text="Натисніть SPACE для продовження", font=("Segoe UI", 12),
                fill=self.COLOR_UI
            )
            
        if not self.game_active:
            # Визначення переможця
            winner_text = "ПЕРЕМІГ ГРАВЕЦЬ 1 🏆" if self.score1 >= self.score_limit else "ПЕРЕМІГ ШІ (КОМП'ЮТЕР) 🤖" if self.game_mode == "sp" else "ПЕРЕМІГ ГРАВЕЦЬ 2 🏆"
            winner_color = self.COLOR_P1 if self.score1 >= self.score_limit else self.COLOR_P2
            
            self.canvas.create_rectangle(0, 0, self.width, self.height, fill="#0d0e15")
            self.canvas.create_text(
                self.width/2, self.height/2 - 30,
                text=winner_text, font=("Segoe UI", 24, "bold"),
                fill=winner_color
            )
            self.canvas.create_text(
                self.width/2, self.height/2 + 30,
                text=f"Кінцевий рахунок:  {self.score1} — {self.score2}", font=("Segoe UI", 16),
                fill=self.COLOR_UI
            )
            self.canvas.create_text(
                self.width/2, self.height/2 + 80,
                text="Натисніть ESC для повернення в меню", font=("Segoe UI", 11, "italic"),
                fill="#51556d"
            )

    def update_game(self):
        """Головний цикл гри, що викликає оновлення з фіксованою затримкою (~60 FPS)."""
        if not self.game_active or self.is_paused:
            self.draw_scene()
            return
            
        # Оновлення рухів та фізики
        self.move_paddles()
        self.update_physics()
        self.update_particles()
        self.apply_screen_shake()
        
        # Візуалізація сцени
        self.draw_scene()
        
        # Рекурсивний виклик (~16 мілісекунд затримки = ~60 FPS)
        self.root.after(16, self.update_game)


def clamp(val, min_v, max_v):
    return max(min_v, min(val, max_v))


if __name__ == "__main__":
    root = tk.Tk()
    game = PongGame(root)
    root.mainloop()
