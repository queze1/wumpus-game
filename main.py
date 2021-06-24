import pygame
import random
import sys

from config import *
from lib.Player import Player
from lib.Background import Background, MenuBackground
from lib.Menu import *
from lib.GameMap import GameMap
from lib.HUD import Minimap, Healthbar, Cards
from lib.Player.Cards import *

pygame.init()

# Set up window & FPS clock
clock = pygame.time.Clock()

pygame.display.set_caption("game")
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))


def main_menu():
    click = False

    menu_background = MenuBackground()
    game_button = GameButton()
    title = Title()
    exit_button = GameCloseButton()

    menu_sprites = pygame.sprite.OrderedUpdates()
    menu_sprites.add(menu_background)
    menu_sprites.add(game_button)
    menu_sprites.add(title)
    menu_sprites.add(exit_button)

    while True:
        menu_sprites.clear(window, menu_background.image)
        menu_sprites.update()

        mx, my = pygame.mouse.get_pos()
 
        if game_button.rect.collidepoint((mx, my)):
            if click:
                game()
        if exit_button.rect.collidepoint((mx, my)):
            if click:
                pygame.quit()
                sys.exit()                
 
        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit() 
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
 
        rects = menu_sprites.draw(window)
        pygame.display.update(rects)
        clock.tick(60)


def pause_menu():
    click = False

    title = Paused()
    menu_background = MenuBackground()
    game_button = ContinueButton()
    exit_button = ExitButton()

    menu_sprites = pygame.sprite.OrderedUpdates()
    menu_sprites.add(menu_background)
    menu_sprites.add(game_button)
    menu_sprites.add(title)
    menu_sprites.add(exit_button)

    while 1:
        menu_sprites.clear(window, menu_background.image)
        menu_sprites.update()

        mx, my = pygame.mouse.get_pos()
 
        if game_button.rect.collidepoint((mx, my)):
            if click:
                break
        if exit_button.rect.collidepoint((mx, my)):
            if click:
                main_menu()

        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit() 
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
 
        rects = menu_sprites.draw(window)
        pygame.display.update(rects)
        clock.tick(60)


def death_menu():
    click = False

    menu_background = MenuBackground()
    game_button = GameButton()
    title = DeathTitle()
    exit_button = GameCloseButton()

    menu_sprites = pygame.sprite.OrderedUpdates()
    menu_sprites.add(menu_background)
    menu_sprites.add(game_button)
    menu_sprites.add(title)
    menu_sprites.add(exit_button)

    while True:
        menu_sprites.clear(window, menu_background.image)
        menu_sprites.update()

        mx, my = pygame.mouse.get_pos()
 
        if game_button.rect.collidepoint((mx, my)):
            if click:
                game()
        if exit_button.rect.collidepoint((mx, my)):
            if click:
                pygame.quit()
                sys.exit()                
 
        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit() 
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
 
        rects = menu_sprites.draw(window)
        pygame.display.update(rects)
        clock.tick(60)

def game():
    # Create objects
    player = Player((WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
    healthbar = Healthbar(player, center=HEALTHBAR_CENTER)
    cards = Cards(player, center=CARDS_CENTER)
    background = Background()

    # Initialize map
    game_map = GameMap(ROOM_NUM)
    minimap = Minimap(game_map, center=MINIMAP_CENTER)
    minimap.render_minimap(game_map, None)

    all_sprites = pygame.sprite.OrderedUpdates()  # renders sprites in order of addition
    all_sprites.add(background)
    all_sprites.add(game_map.environmental_sprites)
    all_sprites.add(player)
    all_sprites.add(healthbar)
    all_sprites.add(cards)
    all_sprites.add(minimap)

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pause_menu()

        # Level Handling
        game_map.handle_rooms(all_sprites, player, minimap)

        # Add and update sprites
        all_sprites.clear(window, background.image)
        all_sprites.add(player.bullets)

        if not game_map.is_cleared():
            is_cleared = game_map.enemy_spawner.spawn_enemies(all_sprites, player)
            if is_cleared:
                game_map.unlock_room(all_sprites)
                player.deck.append(random.choice([Dash(), HeavyAttack()]))
                game_map.set_cleared(True)

        if player not in all_sprites:
            death_menu()

        all_sprites.add(game_map.enemy_spawner.enemies)
        all_sprites.update(all_sprites, player, game_map)

        rects = all_sprites.draw(window)
        pygame.display.update(rects)
        clock.tick(FPS)


main_menu()
