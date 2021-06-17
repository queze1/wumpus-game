import random

enemies = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
update_chain = {'a': 'b', 'b': 'c', 'c': 'd'}


def generate_enemies(num_enemies, total_value):
    current_enemies = ['a' for j in range(num_enemies)]
    current_value = sum([enemies[enemy] for enemy in current_enemies])

    while current_value < total_value:
        current_enemy = random.choice(current_enemies)
        if current_enemy in update_chain:
            upgrade = update_chain[current_enemy]
        current_enemies.remove(current_enemy)
        current_enemies.append(upgrade)
        current_value = sum([enemies[enemy] for enemy in current_enemies])

    print(current_enemies)
    print(current_value)
