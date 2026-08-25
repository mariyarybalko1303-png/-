import random

class Plant:
    def __init__(self, name, emoji, growth_rate, harvest_yield):
        self.name = name
        self.emoji = emoji
        self.growth = 0  # Відсоток росту (0-100)
        self.growth_rate = growth_rate  # Скільки росте за день
        self.harvest_yield = harvest_yield  # Кількість реагентів при зборі

    def grow(self, watered=False):
        rate = self.growth_rate
        if watered:
            rate = int(rate * 1.5)
        self.growth = min(100, self.growth + rate)

    def is_mature(self):
        return self.growth >= 100

    def harvest(self):
        if self.is_mature():
            self.growth = 0
            return random.randint(self.harvest_yield[0], self.harvest_yield[1])
        return 0


class Garden:
    def __init__(self):
        self.plants = {
            "moonleaf": Plant("Місячний лист", "🌿", 25, (2, 4)),       # Для цілющих зілль
            "solflower": Plant("Сонцецвіт", "🌸", 20, (2, 3)),        # Для зілля енергії
            "ironroot": Plant("Залізнокорінь", "🪵", 15, (1, 3)),      # Для зміцнення та захисту
            "deathweed": Plant("Гнилоцвіт", "🥀", 30, (3, 5))         # Для розчинників та небезпечних реакцій
        }
        self.watered_today = False

    def grow_plants(self):
        for plant in self.plants.values():
            plant.grow(watered=self.watered_today)
        self.watered_today = False  # Скидаємо прапорець поливу на наступний день

    def water(self):
        self.watered_today = True

    def print_garden_status(self):
        status_lines = []
        for plant in self.plants.values():
            maturity = "Дозрів! [Готовий до збору]" if plant.is_mature() else f"Росте: {plant.growth}%"
            status_lines.append(f"  {plant.emoji} {plant.name}: {maturity}")
        return "\n".join(status_lines)


class Alchemist:
    def __init__(self, name="Ауреліус"):
        self.name = name
        self.max_hp = 100
        self.hp = 100
        self.max_stamina = 50
        self.stamina = 50
        
        # Інгредієнти в сумці
        self.inventory = {
            "moonleaf": 2,
            "solflower": 2,
            "ironroot": 1,
            "deathweed": 0
        }
        
        # Готові розчини/зілля
        self.potions = {
            "healing_potion": 1,      # Відновлює HP
            "stamina_elixir": 1,      # Відновлює витривалість
            "shield_oil": 0,          # Захищає від аварій у лабораторії
            "acid_catalyst": 0        # Потрібен для фінальної трансмутації
        }
        
        self.magnum_opus_progress = 0  # Прогрес створення Філософського Каменя
        self.lab_instability = 0       # Рівень небезпеки в лабораторії (0-100)

    def print_status(self):
        print(f"\n🧙‍♂️ {self.name}: HP={self.hp}/{self.max_hp}, Витривалість={self.stamina}/{self.max_stamina}")
        inv_str = ", ".join([f"{qty}x {name}" for name, qty in self.inventory.items() if qty > 0])
        pot_str = ", ".join([f"{qty}x {name.replace('_', ' ').title()}" for name, qty in self.potions.items() if qty > 0])
        print(f"🎒 Інгредієнти: {inv_str if inv_str else 'порожньо'}")
        print(f"🧪 Шафа із зіллям: {pot_str if pot_str else 'порожньо'}")
        print(f"🔮 Прогрес Великого Творіння (Magnum Opus): {self.magnum_opus_progress}% | Нестабільність лаби: {self.lab_instability}%")

    def is_alive(self):
        return self.hp > 0

    def rest(self):
        self.stamina = min(self.max_stamina, self.stamina + 20)
        self.hp = min(self.max_hp, self.hp + 10)
        self.lab_instability = max(0, self.lab_instability - 15)
        print(f"💤 {self.name} прибирає в лабораторії та відпочиває. (Стабільність покращено, відновлено Витривалість та HP)")


class AlchemistSimulation:
    def __init__(self):
        self.alchemist = Alchemist()
        self.garden = Garden()
        self.day = 1

    def run_day(self):
        print(f"\n================ 📅 ДЕНЬ {self.day} ================")
        self.alchemist.print_status()
        print("\n🏡 Стан домашнього саду:")
        print(self.garden.print_garden_status())

        # Автоматизована система прийняття рішень алхіміка (ШІ-поведінка)
        # 1. Захист життя
        if self.alchemist.hp < 40 and self.alchemist.potions["healing_potion"] > 0:
            print(f"\n🚨 Здоров'я критично низьке! {self.alchemist.name} випиває Цілюще Зілля.")
            self.alchemist.potions["healing_potion"] -= 1
            self.alchemist.hp = min(self.alchemist.max_hp, self.alchemist.hp + 50)
            print(f"💚 HP відновлено до {self.alchemist.hp}/{self.alchemist.max_hp}!")

        # 2. Відновлення витривалості
        elif self.alchemist.stamina < 15 and self.alchemist.potions["stamina_elixir"] > 0:
            print(f"\n⚡ Виснаження! {self.alchemist.name} випиває Еліксир Бадьорості.")
            self.alchemist.potions["stamina_elixir"] -= 1
            self.alchemist.stamina = min(self.alchemist.max_stamina, self.alchemist.stamina + 35)
            print(f"🔋 Витривалість відновлено до {self.alchemist.stamina}/{self.alchemist.max_stamina}!")

        # 3. Відпочинок, якщо витривалість на нулі або лаба занадто нестабільна
        elif self.alchemist.stamina < 10 or self.alchemist.lab_instability > 75:
            self.alchemist.rest()

        # 4. Робота в саду (Збір врожаю та догляд)
        else:
            self.perform_daily_work()

        # Наприкінці дня рослини ростуть
        self.garden.grow_plants()
        
        # Лабораторні аварії через високу нестабільність
        self.check_lab_hazards()

        self.day += 1

    def perform_daily_work(self):
        # Перевіряємо, які рослини дозріли
        harvested_any = False
        for key, plant in list(self.garden.plants.items()):
            if plant.is_mature() and self.alchemist.stamina >= 10:
                self.alchemist.stamina -= 10
                yielded = plant.harvest()
                self.alchemist.inventory[key] += yielded
                print(f"👨‍🌾 {self.alchemist.name} збирає врожай: {plant.emoji} {plant.name} (+{yielded} од.)")
                harvested_any = True

        # Якщо нічого не збирали, але земля суха, поливаємо сад
        if not harvested_any and self.alchemist.stamina >= 5:
            self.alchemist.stamina -= 5
            self.garden.water()
            print(f"💦 {self.alchemist.name} поливає сад, щоб прискорити ріст рослин.")

        # Фаза великої трансмутації (тепер має ПРІОРИТЕТ, якщо у нас достатньо зілль)
        self.transmutation_phase()

        # Фаза варіння розчинів та зілль (тільки якщо в запасі мало зілль)
        self.brew_phase()

    def brew_phase(self):
        inv = self.alchemist.inventory
        pots = self.alchemist.potions

        # Варимо Цілюще зілля: 2 Moonleaf + 1 Solflower (тримаємо ліміт у запасі не більше 2 штук)
        if pots["healing_potion"] < 2 and inv["moonleaf"] >= 2 and inv["solflower"] >= 1 and self.alchemist.stamina >= 12:
            self.alchemist.stamina -= 12
            inv["moonleaf"] -= 2
            inv["solflower"] -= 1
            pots["healing_potion"] += 1
            print("🧪 [ВАРІННЯ] Створено Цілюще Зілля (Moonleaf x2, Solflower x1) ❤️")

        # Варимо Еліксир бадьорості: 1 Solflower + 1 Ironroot (тримаємо ліміт у запасі не більше 2 штук)
        if pots["stamina_elixir"] < 2 and inv["solflower"] >= 1 and inv["ironroot"] >= 1 and self.alchemist.stamina >= 10:
            self.alchemist.stamina -= 10
            inv["solflower"] -= 1
            inv["ironroot"] -= 1
            pots["stamina_elixir"] += 1
            print("🧪 [ВАРІННЯ] Створено Еліксир Бадьорості (Solflower x1, Ironroot x1) ⚡")

        # Варимо Захисну олію (від вибухів): 2 Ironroot + 1 Moonleaf
        if pots["shield_oil"] < 1 and inv["ironroot"] >= 2 and inv["moonleaf"] >= 1 and self.alchemist.stamina >= 15:
            self.alchemist.stamina -= 15
            inv["ironroot"] -= 2
            inv["moonleaf"] -= 1
            pots["shield_oil"] += 1
            print("🧪 [ВАРІННЯ] Створено Захисну Олію (Ironroot x2, Moonleaf x1) 🛡️")

        # Варимо Кислотний каталізатор (для Magnum Opus): 2 Deathweed + 1 Ironroot
        if inv["deathweed"] >= 2 and inv["ironroot"] >= 1 and self.alchemist.stamina >= 15:
            self.alchemist.stamina -= 15
            inv["deathweed"] -= 2
            inv["ironroot"] -= 1
            pots["acid_catalyst"] += 1
            print("🧪 [ВАРІННЯ] Створено Кислотний Каталізатор (Deathweed x2, Ironroot x1) ☣️")

    def transmutation_phase(self):
        # Якщо є Кислотний каталізатор, проводимо складні трансмутації (дають дуже багато прогресу)
        if self.alchemist.potions["acid_catalyst"] > 0 and self.alchemist.stamina >= 15:
            self.alchemist.stamina -= 15
            self.alchemist.potions["acid_catalyst"] -= 1
            
            progress_gain = random.randint(15, 25)
            self.alchemist.magnum_opus_progress += progress_gain
            
            # Складні трансмутації сильно дестабілізують лабу
            instability_gain = random.randint(20, 35)
            self.alchemist.lab_instability += instability_gain
            
            print(f"🔮 [ТРАНСМУТАЦІЯ] Складний експеримент з каталізатором! Прогрес Великого Творіння +{progress_gain}%! (Нестабільність зросла на +{instability_gain}%)")
        
        # Прості трансмутації (без каталізатора, просто з сировини, якщо зібралося з надлишком)
        elif self.alchemist.inventory["solflower"] >= 1 and self.alchemist.inventory["moonleaf"] >= 1 and self.alchemist.stamina >= 10:
            self.alchemist.stamina -= 10
            self.alchemist.inventory["solflower"] -= 1
            self.alchemist.inventory["moonleaf"] -= 1
            
            progress_gain = random.randint(5, 10)
            self.alchemist.magnum_opus_progress += progress_gain
            
            instability_gain = random.randint(10, 18)
            self.alchemist.lab_instability += instability_gain
            
            print(f"🔮 [ТРАНСМУТАЦІЯ] Базовий синтез реагентів. Прогрес +{progress_gain}%! (Нестабільність +{instability_gain}%)")

    def check_lab_hazards(self):
        if self.alchemist.lab_instability > 0:
            # Чим вища нестабільність, тим більший шанс аварії
            trigger_chance = self.alchemist.lab_instability
            if random.randint(1, 100) <= trigger_chance:
                # Обираємо тип аварії
                hazard = random.choice(["explosion", "toxic_gas", "acid_spill"])
                
                # Захисна олія може повністю запобігти аварії
                if self.alchemist.potions["shield_oil"] > 0:
                    self.alchemist.potions["shield_oil"] -= 1
                    self.alchemist.lab_instability = max(0, self.alchemist.lab_instability - 25)
                    print(f"🛡️ [ЗАХИСТ] Використано Захисну Олію! Аварію вдалося локалізувати без ушкоджень.")
                    return

                if hazard == "explosion":
                    damage = random.randint(20, 35)
                    self.alchemist.hp -= damage
                    self.alchemist.lab_instability = max(0, self.alchemist.lab_instability - 30)
                    print(f"💥 [АВАРІЯ] У лабораторії вибухнула реторта! {self.alchemist.name} отримує {damage} урону!")
                
                elif hazard == "toxic_gas":
                    damage = random.randint(10, 20)
                    self.alchemist.hp -= damage
                    self.alchemist.stamina = max(0, self.alchemist.stamina - 15)
                    print(f"☣️ [АВАРІЯ] Кімнату заповнив отруйний газ! {self.alchemist.name} втрачає {damage} HP та витривалість!")
                
                else: # acid_spill
                    damage = random.randint(15, 25)
                    self.alchemist.hp -= damage
                    self.alchemist.lab_instability = max(0, self.alchemist.lab_instability - 15)
                    print(f"🧪 [АВАРІЯ] Розлилася концентрована кислота! Нанесено {damage} урону!")

            else:
                # Природне розсіювання нестабільності, якщо нічого не вибухнуло
                self.alchemist.lab_instability = max(0, self.alchemist.lab_instability - 5)

    def start_sim(self, max_days=30):
        print(f"🧙‍♂️ Ласкаво просимо до затишної Лабораторії Алхіміка {self.alchemist.name}! 🏡")
        print("Ваша мета — вирощувати рідкісні інгредієнти в саду, варити зілля та завершити Magnum Opus (100%), не підірвавши лабораторію!")
        
        while self.day <= max_days and self.alchemist.is_alive():
            self.run_day()
            
            if self.alchemist.magnum_opus_progress >= 100:
                print(f"\n✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨")
                print(f"🏆 ПЕРЕМОГА! На {self.day - 1} день експериментів {self.alchemist.name} успішно створив ФІЛОСОФСЬКИЙ КАМІНЬ! 🔮")
                print(f"Тепер будь-який метал перетворюється на золото, а еліксир життя дарує безсмертя!")
                print(f"✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨✨")
                return True

        if not self.alchemist.is_alive():
            print(f"\n💀 ГРА ЗАВЕРШЕНА. {self.alchemist.name} загинув унаслідок чергової небезпечної хімічної аварії...")
        else:
            print(f"\n⌛ Час вийшов! Алхіміку не вистачило {max_days} днів, щоб закінчити Велике Творіння (прогрес: {self.alchemist.magnum_opus_progress}%).")
        return False


if __name__ == "__main__":
    sim = AlchemistSimulation()
    sim.start_sim(max_days=30)
