# text_adventure.py - Сценарий текстовой консольной игры

from RPG import Weapon, Player, Villain, simulate_battle, simulate_group_battle

import random

# Класс Room для текстовой игры
class Room:
    def __init__(self, name, description, enemies=None, loot=None, exits=None):
        self.name = name
        self.description = description
        self.enemies = enemies or []  # Список кортежей (имя, оружие, элемент, potions, strength, dexterity, focus)
        self.loot = loot or []  # Список Weapon
        self.exits = exits or {}  # Словарь выходов: направление -> комната


# Создание комнат
def create_rooms():
    # Оружия для врагов и лута
    rusty_sword = Weapon("Ржавый меч", 10)
    goblin_axe = Weapon("Гоблинский топор", 15)
    boss_hammer = Weapon("Молот босса", 30)
    golden_dagger = Weapon("Золотой кинжал", 25)
    legendary_sword = Weapon("Легендарный меч", 35)

    room0 = Room("Вход в пещеру", "Тёмная пещера. Вы видите вход в неё. Направление: на север",
                 enemies=[],
                 loot=[])
    room1 = Room("Входная пещера", "Тёмная пещера с эхом. Вы видите продолжение на север или выход на юг.",
                 enemies=[("Гоблин", goblin_axe, 'neutral', 0, 3, 1, 5)],
                 loot=[rusty_sword], exits={})
    room2 = Room("Комната сокровищ", "Комната полна золота, но охраняется. Выход на юг и восток.",
                 enemies=[("Гоблин", goblin_axe, 'neutral', 0, 2, 6, 1), ("Гоблин", goblin_axe, 'neutral', 0, 2, 6, 1), ("Гоблин", goblin_axe, 'neutral', 0, 2, 6, 1)],
                 loot=[golden_dagger], exits={})
    room3 = Room("Зал босса", "Большой зал с троном. Здесь главный босс! Выход на запад.",
                 enemies=[("Главный Босс", boss_hammer, 'fire', 2, 8, 4, 7)],
                 loot=[legendary_sword], exits={})
    secret_room = Room("Секретная комната",
                       "Пасхалка! Вы нашли скрытое сокровище. Здесь бесконечные зелья (но на самом деле просто текст).",
                       enemies=[], loot=[], exits={})

    # Связываем комнаты
    room0.exits = {'север': room1}
    room1.exits = {'север': room2, 'юг': room0}
    room2.exits = {'юг': room1, 'восток': room3}
    room3.exits = {'запад': room2}
    room2.exits['секрет'] = secret_room  # Пасхалка

    return room0  # Стартовая комната


# Основная игра
def play_game():
    # Начальное оружие игрока
    fists = Weapon("Кулаки", 5)
    player = Player("Авантюрист", fists, element='neutral', potions=3)

    current_room = create_rooms()

    print("Добро пожаловать в Текстовую RPG-Игру!")
    print("Команды: идти на [направление], инвентарь, выход.")

    while player.status == "alive":
        print(f"\n{current_room.name}: {current_room.description}")
        won = 0
        # Враги: создаём Villain и сражаемся с использованием боевой системы
        villains = []
        for enemy_data in current_room.enemies:
            name, weapon, element, potions, strength, dexterity, focus = enemy_data
            villain = Villain(name, weapon, element, potions, strength, dexterity, focus)
            villains.append(villain)

        if villains:
            if len(villains) == 1:
                won = simulate_battle(player, villains[0])
            else:
                won = simulate_group_battle(player, villains)
            if not won:
                print("Игра окончена.")
                return
            current_room.enemies = []  # Удаляем побеждённых

        # Лут
        for item in current_room.loot[:]:
            print(f"Вы нашли {item.name}!")
            take = input("Взять? (да/нет): ")
            if take.lower() == 'да':
                player.equip_weapon(item)
            current_room.loot.remove(item)

        if(won):
            print(f"\n{current_room.name}: {current_room.description}")
            print("Команды: идти на [направление], инвентарь, выход.")

        # Команда
        command = input("> ").lower().split()
        if not command:
            continue
        if command[0] == 'идти':
            direction = command[2]
            if direction in current_room.exits:
                current_room = current_room.exits[direction]
            else:
                print("Нельзя пойти туда.")
        elif command[0] == 'инвентарь':
            print("Инвентарь:")
            for item in player.inventory['weapons']:
                print(f"- {item.name} (урон: {item.damage})")
            print(f"Зелий: {player.potions}")
        elif command[0] == 'выход':
            print("Выход из игры.")
            return
        else:
            print("Неверная команда.")

    print("Игра окончена.")


# Запуск
if __name__ == "__main__":
    play_game()