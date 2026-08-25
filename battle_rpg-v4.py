import random

class Person:
    def __init__(self, name, life, damage, shield, miss_chance=15, max_mp=0, crit_chance=10, dodge_chance=5):
        self.name = name
        self.max_life = life
        self.life = life
        self.damage = damage
        self.shield = shield
        self.miss_chance = miss_chance
        self.max_mp = max_mp
        self.mp = max_mp
        self.crit_chance = crit_chance  
        self.dodge_chance = dodge_chance
        self.statuses = {}

    def is_alive(self):
        return self.life > 0

    def print_status(self):
        mp_status = f", MP={self.mp}/{self.max_mp}" if self.max_mp > 0 else ""
        statuses_str = ""
        if self.statuses:
            status_labels = []
            for s, info in self.statuses.items():
                emoji = "🩸" if s == "bleeding" else "🔥" if s == "burning" else "💫"
                status_labels.append(f"{emoji}({info['duration']}р.)")
            statuses_str = f", EFFECTS: {' '.join(status_labels)}"
            
        print(f"{self.name}: HP={self.life}/{self.max_life}{mp_status}, DMG={self.damage}, SH={self.shield}, MISS={self.miss_chance}%, CRIT={self.crit_chance}%, DODGE={self.dodge_chance}%{statuses_str}")

    def can_take_turn(self):
        """🆕 Перевірка можливості ходу (обробка ефекту приголомшення)"""
        if not self.is_alive():
            return False
        
        if "stunned" in self.statuses:
            info = self.statuses["stunned"]
            info["duration"] -= 1
            print(f"💫 {self.name} приголомшений і пропускає свій хід!")
            if info["duration"] <= 0:
                del self.statuses["stunned"]
                print(f"✨ {self.name} оговтався від приголомшення!")
            return False
        return True

    def attack(self, other):
        if not self.is_alive() or not other.is_alive():
            return

        # 1. Перевірка на промах атакуючого
        if random.randint(1, 100) <= self.miss_chance:
            print(f"💨 {self.name} намагається атакувати {other.name}, але промахується!")
            return

        # 2. 🆕 Перевірка на ухилення (тільки якщо ціль НЕ приголомшена)
        is_stunned = "stunned" in other.statuses
        if not is_stunned and random.randint(1, 100) <= other.dodge_chance:
            print(f"🏃 {other.name} спритно ухиляється від атаки {self.name}!")
            return
        elif is_stunned:
            print(f"💫 {other.name} приголомшений, тому не може ухилитися!")

        is_crit = random.randint(1, 100) <= self.crit_chance
        base_damage = self.dealt_damage()
        
        if is_crit:
            base_damage = int(base_damage * 2)
            crit_prefix = "🎯 [КРИТИЧНИЙ УДАР] "
        else:
            crit_prefix = ""

        damage_dealt = max(1, base_damage - other.create_shield())
        other.take_damage(damage_dealt)
        
        print(f"⚔️ {crit_prefix}{self.name} атакує {other.name} та завдає {damage_dealt} урону!")

        # 🆕 Додаємо шанс приголомшення при критичному ударі базової атаки (30%)
        if is_crit and other.is_alive():
            if random.randint(1, 100) <= 30:
                other.apply_status("stunned", duration=1)

        if not other.is_alive():
            print(f"💀 {other.name} загинув!")

    def take_damage(self, amount):
        old_life = self.life
        self.life = max(0, self.life - amount)
        return old_life - self.life

    def heal(self, amount):
        if not self.is_alive():
            return
        
        old_life = self.life
        self.life = min(self.max_life, self.life + amount)
        healed_amount = self.life - old_life
        print(f"❤️ {self.name} відновлює {healed_amount} HP! (Поточне HP: {self.life}/{self.max_life})")

    def apply_status(self, status_name, duration, power=0):
        if not self.is_alive():
            return
        
        self.statuses[status_name] = {"duration": duration, "power": power}
        emoji = "🩸" if status_name == "bleeding" else "🔥" if status_name == "burning" else "💫"
        name_ua = "Кровотеча" if status_name == "bleeding" else "Горіння" if status_name == "burning" else "Приголомшення"
        power_str = f" (урон: {power}/р.)" if power > 0 else ""
        print(f"⚠️ На {self.name} накладено ефект {emoji} {name_ua} на {duration} раунди(ів){power_str}!")

    def tick_statuses(self):
        if not self.is_alive():
            return
        
        for status in list(self.statuses.keys()):
            # Пропускаємо хід для приголомшення у tick_statuses, бо воно обробляється безпосередньо у can_take_turn()
            if status == "stunned":
                continue
                
            info = self.statuses[status]
            if info["duration"] > 0:
                power = info["power"]
                actual_taken = self.take_damage(power)
                
                emoji = "🩸" if status == "bleeding" else "🔥"
                name_ua = "Кровотеча" if status == "bleeding" else "Горіння"
                print(f"{emoji} {self.name} отримує {actual_taken} періодичного урону від ефекту {name_ua}! (HP: {self.life}/{self.max_life})")
                
                info["duration"] -= 1
                if info["duration"] <= 0:
                    del self.statuses[status]
                    print(f"✨ Ефект {name_ua} на {self.name} закінчився.")
                
                if not self.is_alive():
                    print(f"💀 {self.name} загинув від ефекту {name_ua}!")
                    break

    def use_mana(self, amount):
        if self.mp >= amount:
            self.mp -= amount
            return True
        return False

    def regenerate_mana(self, amount=8):
        if self.max_mp > 0 and self.is_alive():
            old_mp = self.mp
            self.mp = min(self.max_mp, self.mp + amount)
            regended = self.mp - old_mp
            if regended > 0:
                print(f"🔷 {self.name} відновлює {regended} MP. (Поточне MP: {self.mp}/{self.max_mp})")

    def dealt_damage(self):
        return self.damage

    def create_shield(self):
        return self.shield

    def take_turn(self, allies, enemies):
        if not self.can_take_turn():
            return
        if enemies:
            defender = random.choice(enemies)
            self.attack(defender)


class Warrior(Person):
    def __init__(self, name):
        super().__init__(name, random.randint(80, 120), random.randint(20, 50), random.randint(10, 30), 
                         miss_chance=random.randint(15, 25), max_mp=0, crit_chance=random.randint(10, 18),
                         dodge_chance=random.randint(3, 8))
        self.harddamage = random.randint(5, 15)
        self.rage = 0
        self.max_rage = 100

    def print_status(self):
        statuses_str = ""
        if self.statuses:
            status_labels = []
            for s, info in self.statuses.items():
                emoji = "🩸" if s == "bleeding" else "🔥" if s == "burning" else "💫"
                status_labels.append(f"{emoji}({info['duration']}р.)")
            statuses_str = f", EFFECTS: {' '.join(status_labels)}"
            
        print(f"{self.name}: HP={self.life}/{self.max_life}, Rage={self.rage}/{self.max_rage}, DMG={self.damage}, SH={self.shield}, MISS={self.miss_chance}%, CRIT={self.crit_chance}%, DODGE={self.dodge_chance}%{statuses_str}")

    def take_damage(self, amount):
        actual_damage = super().take_damage(amount)
        if self.is_alive() and actual_damage > 0:
            rage_gained = min(self.max_rage - self.rage, int(actual_damage * 0.5) + 5)
            self.rage += rage_gained
            print(f"😡 {self.name} розлючується від отриманого урону! (+{rage_gained} Люті, Поточна Лють: {self.rage}/{self.max_rage})")
        return actual_damage

    def attack(self, other):
        if not self.is_alive() or not other.is_alive():
            return

        # 1. Перевірка на промах
        if random.randint(1, 100) <= self.miss_chance:
            print(f"💨 {self.name} намагається атакувати {other.name}, але промахується!")
            return

        # 2. Перевірка на ухилення (тільки якщо ціль НЕ приголомшена)
        is_stunned = "stunned" in other.statuses
        if not is_stunned and random.randint(1, 100) <= other.dodge_chance:
            print(f"🏃 {other.name} спритно ухиляється від атаки {self.name}!")
            return
        elif is_stunned:
            print(f"💫 {other.name} приголомшений, тому не може ухилитися!")

        is_crit = random.randint(1, 100) <= self.crit_chance
        base_damage = self.dealt_damage()
        
        if is_crit:
            base_damage = int(base_damage * 2)
            crit_prefix = "🎯 [КРИТИЧНИЙ УДАР] "
        else:
            crit_prefix = ""

        damage_dealt = max(1, base_damage - other.create_shield())
        other.take_damage(damage_dealt)
        print(f"⚔️ {crit_prefix}{self.name} атакує {other.name} та завдає {damage_dealt} урону!")

        # Воїн накладає ефект Кровотечі при критичному ударі
        if is_crit and other.is_alive():
            bleed_power = random.randint(10, 16)
            other.apply_status("bleeding", duration=2, power=bleed_power)
            
            # 🆕 35% шанс приголомшити від потужного критичного удару Воїна
            if random.randint(1, 100) <= 35:
                other.apply_status("stunned", duration=1)

        if self.is_alive():
            rage_gained = min(self.max_rage - self.rage, 15)
            self.rage += rage_gained
            print(f"😡 {self.name} задоволений вдалим ударом! (+{rage_gained} Люті, Поточна Лють: {self.rage}/{self.max_rage})")

        if not other.is_alive():
            print(f"💀 {other.name} загинув!")

    def dealt_damage(self):
        return self.damage + self.harddamage

    def take_turn(self, allies, enemies):
        # 🆕 Викликаємо can_take_turn()
        if not self.can_take_turn():
            return

        if enemies:
            defender = random.choice(enemies)
            if self.rage >= 50:
                self.rage -= 50
                super_damage = int(self.dealt_damage() * 2.5)
                defender.take_damage(super_damage)
                print(f"💥 {self.name} впадає в шаленство і проводить [Нищівний удар] по {defender.name} (витрачено 50 Люті) на {super_damage} чистого урону!")
                
                # Нищівний удар Воїна гарантовано накладає сильну Кровотечу!
                if defender.is_alive():
                    bleed_power = random.randint(14, 22)
                    defender.apply_status("bleeding", duration=2, power=bleed_power)
                
                if not defender.is_alive():
                    print(f"💀 {defender.name} розрубано навпіл!")
            else:
                self.attack(defender)


class Mage(Person):
    def __init__(self, name):
        super().__init__(name, random.randint(50, 90), random.randint(15, 30), random.randint(5, 15), 
                         miss_chance=random.randint(5, 15), max_mp=random.randint(40, 60), crit_chance=random.randint(15, 25),
                         dodge_chance=random.randint(15, 25))
        self.supershield = random.randint(5, 15)
        self.spell_cost = 20

    def create_shield(self):
        return self.shield + self.supershield

    def take_turn(self, allies, enemies):
        # 🆕 Викликаємо can_take_turn()
        if not self.can_take_turn():
            return

        if enemies:
            defender = random.choice(enemies)
            if self.use_mana(self.spell_cost):
                spell_damage = int(self.damage * 2)
                
                is_crit = random.randint(1, 100) <= self.crit_chance
                if is_crit:
                    spell_damage = int(spell_damage * 2)
                    spell_prefix = "🎯 [КРИТИЧНИЙ ВИБУХ] "
                else:
                    spell_prefix = ""

                reduced_shield = int(defender.create_shield() * 0.5)
                damage_dealt = max(1, spell_damage - reduced_shield)
                defender.take_damage(damage_dealt)
                
                # Магічна Вогняна куля летить точно в ціль — від неї НЕ ухилитися!
                print(f"🔥 {spell_prefix}{self.name} кастує [Вогняну кулю] на {defender.name} (витрачено {self.spell_cost} MP) та завдає {damage_dealt} магічного урону!")
                
                # Критичний вибух гарантовано накладає Горіння. Звичайна вогняна куля має 30% шанс накласти Горіння.
                apply_burn = is_crit or (random.randint(1, 100) <= 30)
                if apply_burn and defender.is_alive():
                    burn_power = random.randint(14, 20)
                    defender.apply_status("burning", duration=2, power=burn_power)

                # 🆕 Критичний вибух з шансом 30% оглушує (приголомшує) супротивника ударною хвилею!
                if is_crit and defender.is_alive():
                    if random.randint(1, 100) <= 30:
                        defender.apply_status("stunned", duration=1)

                if not defender.is_alive():
                    print(f"💀 {defender.name} загинув від магічного вогню!")
            else:
                print(f"🧪 У {self.name} недостатньо мани! Атакує посохом.")
                self.attack(defender)


class Priest(Person):
    def __init__(self, name):
        super().__init__(name, random.randint(60, 80), random.randint(10, 20), random.randint(5, 15), 
                         miss_chance=random.randint(10, 20), max_mp=random.randint(50, 70), crit_chance=random.randint(8, 15),
                         dodge_chance=random.randint(8, 15))
        self.heal_power = random.randint(25, 45)
        self.heal_cost = 15

    def take_turn(self, allies, enemies):
        # 🆕 Викликаємо can_take_turn()
        if not self.can_take_turn():
            return

        wounded_allies = [ally for ally in allies if ally.is_alive() and ally.life < ally.max_life]

        if wounded_allies and self.mp >= self.heal_cost and random.random() < 0.8:
            target_to_heal = min(wounded_allies, key=lambda ally: ally.life / ally.max_life)
            if self.use_mana(self.heal_cost):
                is_crit_heal = random.randint(1, 100) <= self.crit_chance
                heal_amount = self.heal_power
                
                if is_crit_heal:
                    heal_amount = int(heal_amount * 1.5)
                    print(f"✨💖 [КРИТИЧНЕ ЛІКУВАННЯ] {self.name} спрямовує потужний потік світла на {target_to_heal.name}!")
                    
                    # 🆕 Магія світла розсіює ВСІ негативні статуси (Кровотечу, Горіння ТА Приголомшення) при критичному лікуванні!
                    if target_to_heal.statuses:
                        removed = list(target_to_heal.statuses.keys())
                        target_to_heal.statuses.clear()
                        status_names_ua = {"bleeding": "Кровотеча", "burning": "Горіння", "stunned": "Приголомшення"}
                        removed_str = ", ".join([status_names_ua.get(s, s) for s in removed])
                        print(f"✨ Магія світла повністю очищує {target_to_heal.name} від негативних ефектів: {removed_str}!")
                else:
                    print(f"✨ {self.name} кастує [Велике лікування] на {target_to_heal.name} (витрачено {self.heal_cost} MP)!")
                
                target_to_heal.heal(heal_amount)
        else:
            if wounded_allies and self.mp < self.heal_cost:
                print(f"🧪 {self.name} хоче допомогти пораненим, але не має мани ({self.mp}/{self.heal_cost} MP)!")
            super().take_turn(allies, enemies)


class Battleground:
    def __init__(self, num_heroes=3):
        self.command1 = []
        self.command2 = []
        self.create_teams(num_heroes)

    def create_teams(self, num_heroes):
        def get_random_hero(name):
            roll = random.choice(["warrior", "mage", "priest"])
            if roll == "warrior":
                return Warrior(name)
            elif roll == "mage":
                return Mage(name)
            else:
                return Priest(name)

        print("=== Команда 1 ===")
        for i in range(num_heroes):
            hero = get_random_hero(f"Hero_{i + 1}_T1")
            self.command1.append(hero)
            hero.print_status()
            
        print("\n=== Команда 2 ===")
        for i in range(num_heroes):
            hero = get_random_hero(f"Hero_{i + 1 + num_heroes}_T2")
            self.command2.append(hero)
            hero.print_status()

    def battle(self):
        round_number = 1
        while self.has_alive(self.command1) and self.has_alive(self.command2):
            print(f"\n⚡=== Раунд {round_number} ===⚡")
            self.fight_round()
            
            # Перевіряємо, чи гра не завершилася під час атак
            if not (self.has_alive(self.command1) and self.has_alive(self.command2)):
                break

            # Фаза ефектів стану наприкінці кожного раунду (зверніть увагу: stunned пропускає хід під час ходу, а не тут)
            print("\n--- Фаза ефектів стану ---")
            any_status_active = False
            for hero in self.command1 + self.command2:
                if hero.is_alive() and any(status != "stunned" for status in hero.statuses):
                    hero.tick_statuses()
                    any_status_active = True
            if not any_status_active:
                print("Активних ефектів стану немає.")

            # Перевіряємо, чи хтось не загинув від періодичного урону
            if not (self.has_alive(self.command1) and self.has_alive(self.command2)):
                break
            
            print("\n--- Фаза регенерації мани ---")
            for hero in self.command1 + self.command2:
                if hero.is_alive() and hero.max_mp > 0:
                    hero.regenerate_mana(8)
            
            round_number += 1

        winner = "Команда 1" if self.has_alive(self.command1) else "Команда 2"
        print(f"\n🏆 Перемогла {winner}!")

    def fight_round(self):
        all_fighters = []
        for hero in self.command1:
            if hero.is_alive():
                all_fighters.append((hero, "team1"))
        for hero in self.command2:
            if hero.is_alive():
                all_fighters.append((hero, "team2"))

        random.shuffle(all_fighters)

        for attacker, team in all_fighters:
            if not attacker.is_alive():
                continue

            if team == "team1":
                allies = [h for h in self.command1 if h.is_alive()]
                enemies = [h for h in self.command2 if h.is_alive()]
            else:
                allies = [h for h in self.command2 if h.is_alive()]
                enemies = [h for h in self.command1 if h.is_alive()]

            attacker.take_turn(allies, enemies)

    def has_alive(self, team):
        return any(hero.is_alive() for hero in team)


if __name__ == "__main__":
    battleground = Battleground(num_heroes=3)
    battleground.battle()
