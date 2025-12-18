# RPG.py - Боевая система

import random
import time  # Для задержек в анимациях

# Класс Weapon (Оружие)
class Weapon:
    def __init__(self, name, damage):
        """
        Инициализация оружия.
        - name: Название оружия (строка).
        - damage: Базовый урон оружия (целое число).
        """
        self.name = name  # Название оружия
        self.damage = damage  # Базовый урон

# Класс Character (Персонаж) - базовый класс
class Character:
    alive_count = 0  # Статическая переменная: общее количество живых персонажей (включая наследников)

    def __init__(self, name, weapon, element='neutral', strength=5, dexterity=5, focus=5):
        """
        Инициализация персонажа.
        - name: Имя персонажа (строка).
        - weapon: Объект класса Weapon.
        - element: Элемент (например, 'fire', 'water', 'neutral').
        - strength: Сила (по умолчанию 5), влияет на max_hp и урон.
        - dexterity: Ловкость (по умолчанию 5), влияет на уклонение и контратаки.
        - focus: Фокус (по умолчанию 5), влияет на крит и комбо-атаки.

        Автоматически рассчитывает здоровье и урон на основе характеристик.
        Увеличивает счётчик живых персонажей.
        """
        self.name = name  # Имя персонажа
        self.max_health = 100 + strength * 10  # Максимальное здоровье: базовое 100 + 10 за единицу силы
        self.health = self.max_health  # Текущее здоровье равно максимальному на старте
        self.weapon = weapon  # Оружие персонажа
        self.status = "alive"  # Статус: "alive" или "dead"
        self.strength = strength  # Сила
        self.dexterity = dexterity  # Ловкость
        self.focus = focus  # Фокус
        self.base_damage = weapon.damage + strength * 2  # Базовый урон: урон оружия + 2 за единицу силы
        self.level = 1  # Начальный уровень
        self.experience = 0  # Начальный опыт
        self.element = element  # Элемент
        self.status_effects = []  # Список эффектов, e.g., ['burn', 3] (3 тика)
        Character.alive_count += 1  # Увеличиваем счётчик живых персонажей

    def attack(self, target):
        """
        Функция атаки: Атакует цель.
        - target: Цель атаки (другой объект Character или наследник).

        Рассчитывает урон с учётом возможного крита (на основе фокуса).
        Затем применяет урон к цели через receive_damage.
        После успешной атаки проверяет шанс комбо-атаки (на основе фокуса).
        Если цель умерла, начисляет опыт атакующему.
        """
        if self.status == "dead":
            print(f"{self.name} мёртв и не может атаковать.")
            return

        # Шанс крита: 5% за единицу фокуса (max 40%)
        crit_chance = min(self.focus * 5, 40) / 100
        is_crit = random.random() < crit_chance
        damage = self.base_damage * (2 if is_crit else 1)  # Урон удваивается при крите
        crit_msg = " (крит!)" if is_crit else ""

        # Модификатор элементов
        element_modifier = 1.0
        if self.element == 'fire' and target.element == 'water':
            element_modifier = 0.5
        elif self.element == 'fire' and target.element == 'earth':
            element_modifier = 1.5
        elif self.element == 'water' and target.element == 'fire':
            element_modifier = 1.5
        # Добавьте больше взаимодействий по необходимости
        damage *= element_modifier

        print(f"{self.name} атакует {target.name} оружием {self.weapon.name} на {int(damage)} урона{crit_msg}.")
        time.sleep(0.5)  # Задержка для "анимации"

        # Применяем урон к цели
        target.receive_damage(int(damage), self)

        # Если атака успешна (не уклонена), проверяем комбо-атаку
        if target.status != "dead":  # Комбо только если цель жива после атаки
            combo_chance = min(self.focus * 3, 30) / 100  # Шанс комбо: 3% за фокус, max 30%
            if random.random() < combo_chance:
                print(f"{self.name} проводит комбо-атаку!")
                time.sleep(0.5)
                self.attack(target)  # Рекурсивно атакуем снова (комбо)

            # Наложение статуса
            if random.random() < 0.2:  # 20% шанс
                target.status_effects.append(['burn', 3])  # 3 тика по 5 урона
                print(f"{target.name} горит!")

        # Если цель умерла после атаки, начислить опыт
        if target.status == "dead":
            # Опыт = геометрическое среднее урона и max_health цели: sqrt(damage * max_health)
            exp_gained = int((target.base_damage * target.max_health) ** 0.5)
            self.gain_experience(exp_gained)

    def receive_damage(self, damage, attacker):
        """
        Функция получения урона.
        - damage: Входящий урон.
        - attacker: Атакующий (для возможной контратаки).

        Проверяет шанс уклонения (на основе ловкости).
        Если не уклон, применяет урон к здоровью.
        Если здоровье <=0, вызывает death().
        Если уклон, проверяет шанс контратаки (на основе ловкости).
        """
        if self.status == "dead":
            return

        # Шанс уклонения: 5% за единицу ловкости (max 40%)
        dodge_chance = min(self.dexterity * 5, 40) / 100
        if random.random() < dodge_chance:
            print(f"{self.name} уклоняется от атаки!")
            time.sleep(0.5)
            # Шанс контратаки после уклонения: 3% за ловкость (max 30%)
            counter_chance = min(self.dexterity * 3, 30) / 100
            if random.random() < counter_chance:
                print(f"{self.name} проводит контратаку!")
                time.sleep(0.5)
                self.attack(attacker)  # Контратака
            return

        # Применяем урон
        self.health -= damage
        print(f"{self.name} получает {damage} урона. Здоровье: {self.health}/{self.max_health}.")
        time.sleep(0.5)
        if self.health <= 0:
            self.death()

    def death(self):
        """
        Функция смерти: Устанавливает статус "dead" и уменьшает счётчик живых.
        """
        if self.status == "dead":
            return
        self.status = "dead"
        self.health = 0
        Character.alive_count -= 1
        print(f"{self.name} погибает!")

    def gain_experience(self, exp):
        """
        Начисление опыта.
        - exp: Количество опыта.

        Добавляет опыт, проверяет на leveling up.
        Порог для уровня: level * 100 (например, для lvl1 -> lvl2 нужно 100 exp).
        При leveling up: +1 к случайной характеристике (strength, dexterity, focus) или +10 к max_health.
        Обновляет характеристики (hp, damage).
        """
        self.experience += exp
        print(f"{self.name} получает {exp} опыта. Текущий опыт: {self.experience}.")
        time.sleep(0.5)

        # Проверяем leveling up
        exp_threshold = self.level * 100  # Порог для следующего уровня
        while self.experience >= exp_threshold:
            self.level += 1
            self.experience -= exp_threshold  # Снимаем потраченный опыт
            print(f"{self.name} повышает уровень до {self.level}!")
            time.sleep(0.5)

            # Рандомно улучшаем один параметр
            upgrade = random.choice(["strength", "dexterity", "focus", "health"])
            if upgrade == "strength":
                self.strength += 1
                print("Сила увеличена!")
            elif upgrade == "dexterity":
                self.dexterity += 1
                print("Ловкость увеличена!")
            elif upgrade == "focus":
                self.focus += 1
                print("Фокус увеличен!")
            elif upgrade == "health":
                self.max_health += 10  # Прямое улучшение здоровья
                print("Максимальное здоровье увеличено!")

            # Обновляем производные характеристики
            self.max_health = max(self.max_health, 100 + self.strength * 10)  # Обновляем max_hp если изменилась сила
            self.base_damage = self.weapon.damage + self.strength * 2  # Обновляем урон
            self.health = min(self.health + 20, self.max_health)  # Восстанавливаем немного здоровья при leveling up
            exp_threshold = self.level * 100  # Новый порог

    def apply_status_effects(self):
        """
        Применение статус-эффектов в конце хода.
        """
        for effect in self.status_effects[:]:
            if effect[0] == 'burn':
                burn_damage = 5
                self.health -= burn_damage
                print(f"{self.name} получает {burn_damage} урона от горения! Здоровье: {self.health}/{self.max_health}")
                time.sleep(0.5)
                effect[1] -= 1
                if effect[1] <= 0:
                    self.status_effects.remove(effect)
                    print(f"{self.name} больше не горит.")
        if self.health <= 0:
            self.death()

# Класс Player (Игрок) - наследник от Character
class Player(Character):
    def __init__(self, name, weapon, element='neutral', potions=3, strength=5, dexterity=5, focus=5):
        """
        Инициализация игрока.
        Наследует от Character, добавляет зелья (по умолчанию 3) и инвентарь.
        """
        super().__init__(name, weapon, element, strength, dexterity, focus)
        self.potions = potions  # Количество зелий
        self.inventory = {'potions': potions, 'weapons': [weapon]}  # Инвентарь

    def heal_self(self):
        """
        Хилл себя зельями: Восстанавливает 50% max_health, если есть зелье.
        Уменьшает количество зелий.
        """
        if self.potions > 0 and self.status == "alive":
            heal_amount = int(self.max_health * 0.5)
            self.health = min(self.health + heal_amount, self.max_health)
            self.potions -= 1
            self.inventory['potions'] = self.potions
            print(f"{self.name} использует зелье и восстанавливает {heal_amount} здоровья. Зелий осталось: {self.potions}.")
            time.sleep(0.5)
        else:
            print(f"{self.name} не может использовать зелье (нет зелий или мёртв).")

    def equip_weapon(self, new_weapon=None):
        """
        Смена оружия из инвентаря или добавление нового.
        """
        if new_weapon:
            self.inventory['weapons'].append(new_weapon)
            print(f"Вы нашли {new_weapon.name}! Добавлено в инвентарь.")
        if len(self.inventory['weapons']) > 1:
            print("Доступные оружия:")
            for i, w in enumerate(self.inventory['weapons'], 1):
                print(f"{i}. {w.name} (урон: {w.damage})")
            choice = input("Выберите оружие для экипировки (номер): ")
            try:
                self.weapon = self.inventory['weapons'][int(choice) - 1]
                self.base_damage = self.weapon.damage + self.strength * 2  # Обновляем урон
                print(f"{self.name} экипирует {self.weapon.name}.")
            except:
                print("Неверный выбор, оружие не изменено.")

# Класс Villain (Злодей) - наследник от Character
class Villain(Character):
    def __init__(self, name, weapon, element='neutral', potions=0, strength=5, dexterity=5, focus=5):
        """
        Инициализация злодея.
        Наследует от Character, зелья по умолчанию 0.
        """
        super().__init__(name, weapon, element, strength, dexterity, focus)
        self.potions = potions  # Количество зелий

    def heal_self(self):
        """
        Хилл себя зельями: Аналогично Player, но поскольку potions=0, не сработает без зелий.
        """
        if self.potions > 0 and self.status == "alive":
            heal_amount = int(self.max_health * 0.5)
            self.health = min(self.health + heal_amount, self.max_health)
            self.potions -= 1
            print(f"{self.name} использует зелье и восстанавливает {heal_amount} здоровья. Зелий осталось: {self.potions}.")
            time.sleep(0.5)
        else:
            print(f"{self.name} не может использовать зелье (нет зелий или мёртв).")

# Функция для симуляции боя между игроком и одним злодеем
def simulate_battle(player, villain):
    """
    Симулирует интерактивный бой между игроком и злодеем.
    - player: Объект Player.
    - villain: Объект Villain.

    По очереди атакуют, с выбором действий для игрока.
    Возвращает True, если игрок выиграл, False если проиграл.
    """
    print(f"\nНачинается бой: {player.name} vs {villain.name}")
    turn = 0
    while player.status == "alive" and villain.status == "alive":
        player.apply_status_effects()
        villain.apply_status_effects()
        if player.status == "dead" or villain.status == "dead":
            break

        if turn % 2 == 0:  # Ход игрока
            print(f"\nВаш ход ({player.name}): Здоровье {player.health}/{player.max_health}, Зелий: {player.potions}")
            print("1. Атака\n2. Использовать зелье (хилл)\n3. Активировать щит (временно +2 ловкости и атака)\n4. Сменить оружие")
            choice = input("Выберите действие (1/2/3/4): ")
            if choice == '1':
                player.attack(villain)
            elif choice == '2':
                player.heal_self()
            elif choice == '3':
                # Специальная способность: временно повысить уклонение
                player.dexterity += 2  # Временный буст
                print(f"{player.name} активирует щит! Ловкость повышена на 2 на этот ход.")
                time.sleep(0.5)
                player.attack(villain)
                player.dexterity -= 2  # Сброс после хода
            elif choice == '4':
                player.equip_weapon()
            else:
                print("Неверный выбор, пропуск хода.")
        else:  # Ход злодея
            if random.random() < 0.1 and villain.potions > 0:  # 10% шанс на хилл для злодея
                villain.heal_self()
            else:
                villain.attack(player)
        turn += 1

    # После боя: лут
    if villain.status == "dead":
        if random.random() < 0.25:
            new_weapon = Weapon("Магический " + random.choice(["меч", "топор", "кинжал"]), random.randint(10, 30))
            player.equip_weapon(new_weapon)
        if random.random() < 0.4:
            player.potions += 1
            print(f"{player.name} находит зелье! Зелий теперь: {player.potions}")

    return player.status == "alive"

# Функция для симуляции одновременного боя между игроком и несколькими злодеями
def simulate_group_battle(player, villains):
    """
    Симулирует интерактивный одновременный бой между игроком и списком злодеев.
    - player: Объект Player.
    - villains: Список объектов Villain.

    По очереди: сначала ход игрока (атакует выбранного злодея, или хилл),
    затем все живые злодеи атакуют игрока по очереди.
    Возвращает True, если игрок выиграл (все злодеи мертвы), False если проиграл.
    """
    print(f"\nНачинается групповой бой: {player.name} vs {', '.join(v.name for v in villains)}")

    while player.status == "alive" and any(v.status == "alive" for v in villains):
        # Применение статусов
        player.apply_status_effects()
        for villain in villains:
            villain.apply_status_effects()

        # Ход игрока
        print(f"\nВаш ход ({player.name}): Здоровье {player.health}/{player.max_health}, Зелий: {player.potions}")
        alive_villains_str = ', '.join(f"{i+1}. {v.name} (HP: {v.health}/{v.max_health})" for i, v in enumerate([v for v in villains if v.status == "alive"]))
        print(f"Живые враги: {alive_villains_str if alive_villains_str else 'Нет врагов'}")
        print("1. Атака (выберите цель)\n2. Использовать зелье (хилл)\n3. Активировать щит (временно +2 ловкости и атака на цель)\n4. Сменить оружие")
        choice = input("Выберите действие (1/2/3/4): ")
        alive_villains = [v for v in villains if v.status == "alive"]
        if choice == '1':
            if alive_villains:
                target_num = input("Выберите цель (номер): ")
                try:
                    target = alive_villains[int(target_num) - 1]
                    player.attack(target)
                except:
                    print("Неверный выбор, пропуск хода.")
        elif choice == '2':
            player.heal_self()
        elif choice == '3':
            if alive_villains:
                target_num = input("Выберите цель для атаки с щитом (номер): ")
                try:
                    target = alive_villains[int(target_num) - 1]
                    player.dexterity += 2
                    print(f"{player.name} активирует щит! Ловкость повышена на 2 на этот ход.")
                    time.sleep(0.5)
                    player.attack(target)
                    player.dexterity -= 2
                except:
                    print("Неверный выбор, пропуск хода.")
        elif choice == '4':
            player.equip_weapon()
        else:
            print("Неверный выбор, пропуск хода.")

        # Ходы злодеев: каждый живой злодей атакует игрока
        for villain in alive_villains:
            if villain.status == "alive":
                if random.random() < 0.1 and villain.potions > 0:
                    villain.heal_self()
                else:
                    villain.attack(player)

    # После боя: лут от всех
    for villain in villains:
        if villain.status == "dead":
            if random.random() < 0.25:
                new_weapon = Weapon("Магический " + random.choice(["меч", "топор", "кинжал"]), random.randint(10, 30))
                player.equip_weapon(new_weapon)
            if random.random() < 0.4:
                player.potions += 1
                print(f"{player.name} находит зелье! Зелий теперь: {player.potions}")

    all_villains_dead = all(v.status == "dead" for v in villains)
    return player.status == "alive" and all_villains_dead