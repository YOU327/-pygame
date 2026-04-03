import pygame
import os
import sys
from random import randint


def display_score():
    current_time = int(pygame.time.get_ticks() / 100)-start_time
    text_surface = test_font.render(f'Score:{current_time}', False, "Black")
    text_rec = text_surface.get_rect(center=(75, 60))
    screen.blit(text_surface, text_rec)
    return current_time


def obstacle_movement(obstacle_list):
    if obstacle_list:
        for obstacle_rect in obstacle_list:
            obstacle_rect.x -= 4
            if obstacle_rect.bottom == 700:
                screen.blit(bad1_surface, obstacle_rect)
            else:
                screen.blit(bad2_surface, obstacle_rect)

            obstacle_list = [
                obstacle for obstacle in obstacle_list if obstacle.x > -100]
        return obstacle_list
    else:
        return []


def collisions(obstacles):
    if obstacles:
        for obstacle_rect in obstacles:
            if good_rec.colliderect(obstacle_rect) and good_surface == good_attack:
                obstacle_rect_list.remove(obstacle_rect)
                return True
            elif good_rec.colliderect(obstacle_rect):
                return False
    return True


def player_animation():
    global good_surface, good_index, good_backward_index, good_attack_index
    keys = pygame.key.get_pressed()

    if good_rec.bottom < HEIGHT - 90:
        good_surface = good_jump
    else:
        if keys[pygame.K_d]:
            good_index += 0.2
            if good_index >= 7:
                good_index = 0
            good_surface = good_walk[int(good_index)]
        elif keys[pygame.K_a]:
            good_backward_index += 0.2
            if good_backward_index >= 16:
                good_backward_index = 8
            good_surface = good_walk[int(good_backward_index)]
        elif keys[pygame.K_e]:
            good_rec.x -= 2
            good_attack_index += 0.1
            if good_attack_index >= 18:
                good_attack_index = 18
            good_surface = good_walk[int(good_attack_index)]
            if good_rec.x < 0:
                good_rec.x = 0
        else:
            good_attack_index = 16
            good_surface = good_walk1
            good_rec.x -= 2
            if good_rec.x < 0:
                good_rec.x = 0


pygame.init()

WIDTH = 1200
HEIGHT = 800
game_active = True
start_time = 0
score = 0
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("追趕跑跳碰")
clock = pygame.time.Clock()
test_font = pygame.font.Font(None, 50)
current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
background_surface = pygame.transform.scale(pygame.image.load(os.path.join(
    current_dir, "player", "Full-Background.png")), (1200, 800)).convert()
bg_x = 0
bg_y = 0

# bad
bad1_frame1 = pygame.transform.scale(pygame.image.load(os.path.join(
    current_dir, 'bad1', "YeOldyNecroGuy1.png")), (80, 100)).convert_alpha()
bad1_frame2 = pygame.transform.scale(pygame.image.load(os.path.join(
    current_dir, 'bad1', "YeOldyNecroGuy2.png")), (80, 100)).convert_alpha()
bad1_frame3 = pygame.transform.scale(pygame.image.load(os.path.join(
    current_dir, 'bad1', "YeOldyNecroGuy3.png")), (80, 100)).convert_alpha()
bad1_frame4 = pygame.transform.scale(pygame.image.load(os.path.join(
    current_dir, 'bad1', "YeOldyNecroGuy4.png")), (80, 100)).convert_alpha()
bad1_frame5 = pygame.transform.scale(pygame.image.load(os.path.join(
    current_dir, 'bad1', "YeOldyNecroGuy5.png")), (80, 100)).convert_alpha()
bad1_frame6 = pygame.transform.scale(pygame.image.load(os.path.join(
    current_dir, 'bad1', "YeOldyNecroGuy6.png")), (80, 100)).convert_alpha()

bad1_frames = [bad1_frame1, bad1_frame2, bad1_frame3,
               bad1_frame4, bad1_frame5, bad1_frame6]
bad1_frame_index = 0
bad1_surface = bad1_frames[bad1_frame_index]

# fly
bad2_frame2 = pygame.transform.scale(pygame.image.load(os.path.join(
    current_dir, "bad2", "32x32-bat-sprite2.png")), (70, 70)).convert_alpha()
bad2_frame3 = pygame.transform.scale(pygame.image.load(os.path.join(
    current_dir, "bad2", "32x32-bat-sprite3.png")), (70, 70)).convert_alpha()
bad2_frame4 = pygame.transform.scale(pygame.image.load(os.path.join(
    current_dir, "bad2", "32x32-bat-sprite4.png")), (70, 70)).convert_alpha()
bad2_frames = [bad2_frame2, bad2_frame3, bad2_frame4]
bad2_frame_index = 0
bad2_surface = bad2_frames[bad2_frame_index]


obstacle_rect_list = []


good_walk1 = pygame.transform.scale(pygame.image.load(os.path.join(
    current_dir, "player", "SaraFullSheet1.png")), (100, 100)).convert_alpha()
good_walk2 = pygame.transform.scale(pygame.image.load(os.path.join(
    current_dir, "player", "SaraFullSheet2.png")), (100, 100)).convert_alpha()
good_walk3 = pygame.transform.scale(pygame.image.load(os.path.join(
    current_dir, "player", "SaraFullSheet3.png")), (100, 100)).convert_alpha()
good_walk4 = pygame.transform.scale(pygame.image.load(os.path.join(
    current_dir, "player", "SaraFullSheet4.png")), (100, 100)).convert_alpha()
good_walk5 = pygame.transform.scale(pygame.image.load(os.path.join(
    current_dir, "player", "SaraFullSheet5.png")), (100, 100)).convert_alpha()
good_walk6 = pygame.transform.scale(pygame.image.load(os.path.join(
    current_dir, "player", "SaraFullSheet6.png")), (100, 100)).convert_alpha()
good_walk7 = pygame.transform.scale(pygame.image.load(os.path.join(
    current_dir, "player", "SaraFullSheet7.png")), (100, 100)).convert_alpha()
good_walk8 = pygame.transform.scale(pygame.image.load(os.path.join(
    current_dir, "player", "SaraFullSheet8.png")), (100, 100)).convert_alpha()
good_backward_walk1 = pygame.transform.scale(pygame.image.load(os.path.join(
    current_dir, "player", "SaraFullSheet_1.png")), (100, 100)).convert_alpha()
good_backward_walk2 = pygame.transform.scale(pygame.image.load(os.path.join(
    current_dir, "player", "SaraFullSheet_2.png")), (100, 100)).convert_alpha()
good_backward_walk3 = pygame.transform.scale(pygame.image.load(os.path.join(
    current_dir, "player", "SaraFullSheet_3.png")), (100, 100)).convert_alpha()
good_backward_walk4 = pygame.transform.scale(pygame.image.load(os.path.join(
    current_dir, "player", "SaraFullSheet_4.png")), (100, 100)).convert_alpha()
good_backward_walk5 = pygame.transform.scale(pygame.image.load(os.path.join(
    current_dir, "player", "SaraFullSheet_5.png")), (100, 100)).convert_alpha()
good_backward_walk6 = pygame.transform.scale(pygame.image.load(os.path.join(
    current_dir, "player", "SaraFullSheet_6.png")), (100, 100)).convert_alpha()
good_backward_walk7 = pygame.transform.scale(pygame.image.load(os.path.join(
    current_dir, "player", "SaraFullSheet_7.png")), (100, 100)).convert_alpha()
good_backward_walk8 = pygame.transform.scale(pygame.image.load(os.path.join(
    current_dir, "player", "SaraFullSheet_8.png")), (100, 100)).convert_alpha()


good_attack = pygame.transform.scale(pygame.image.load(os.path.join(
    current_dir, "player", "SaraFullSheethit.png")), (100, 100)).convert_alpha()
good_attack_index = 16

good_walk = [good_walk1, good_walk2, good_walk3, good_walk4, good_walk5, good_walk6, good_walk7, good_walk8, good_backward_walk1, good_backward_walk2,
             good_backward_walk3, good_backward_walk4, good_backward_walk5, good_backward_walk6, good_backward_walk7, good_backward_walk8, good_attack, good_attack, good_walk1]
good_index = 0
good_backward_index = 8
good_jump = pygame.transform.scale(pygame.image.load(os.path.join(
    current_dir, "player", "SaraFullSheet_jump.png")), (100, 100)).convert_alpha()
good_surface = good_walk[good_index] or good_walk[good_backward_index] or good_walk[good_attack_index]
good_rec = good_surface.get_rect(midbottom=(100, HEIGHT-90))
good_gravity = 0

# timer
obstacle_timer = pygame.USEREVENT + 1
pygame.time.set_timer(obstacle_timer, 1000)
bad1_animation_timer = pygame.USEREVENT + 2
pygame.time.set_timer(bad1_animation_timer, 150)
bad2_animation_timer = pygame.USEREVENT + 3
pygame.time.set_timer(bad2_animation_timer, 100)


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if game_active:
            if event.type == obstacle_timer:
                if randint(0, 2):
                    obstacle_rect_list.append(bad1_surface.get_rect(
                        midbottom=(randint(1300, 1500), 700)))
                else:
                    obstacle_rect_list.append(bad2_surface.get_rect(
                        midbottom=(randint(1300, 1500), randint(400, 600))))
            if event.type == bad1_animation_timer:
                if bad1_frame_index != 5:
                    bad1_frame_index += 1
                else:
                    bad1_frame_index = 0
                bad1_surface = bad1_frames[bad1_frame_index]
            if event.type == bad2_animation_timer:
                if bad2_frame_index != 2:
                    bad2_frame_index += 1
                else:
                    bad2_frame_index = 0
                bad2_surface = bad2_frames[bad2_frame_index]

    if game_active == True:
        # 背景圖像的移動和繪製
        bg_x -= 2
        if bg_x < -WIDTH:
            bg_x = 0
        screen.blit(background_surface, (bg_x, bg_y))
        screen.blit(background_surface, (bg_x + WIDTH, bg_y))
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and good_rec.bottom >= HEIGHT - 90:
            good_gravity = -26
        if keys[pygame.K_d]:
            good_rec.x += 6
            if good_rec.x > WIDTH - 5:
                good_rec.x = WIDTH - 5
        if keys[pygame.K_a]:
            good_rec.x -= 6
            if good_rec.x < 0:
                good_rec.x = 0
        good_gravity += 1
        good_rec.y += good_gravity
        if good_rec.bottom > HEIGHT - 90:
            good_rec.bottom = HEIGHT - 90
            good_gravity = 0
        screen.blit(good_surface, good_rec)
        obstacle_rect_list = obstacle_movement(obstacle_rect_list)
        game_active = collisions(obstacle_rect_list)
        tips = test_font.render(
            f'E : attack  W : jump  A : left  D : right', False, "black")
        score = display_score()
        player_animation()
        screen.blit(tips, (0, 0))
    else:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            game_active = True
            start_time = int(pygame.time.get_ticks() / 100)
        screen.blit(pygame.transform.scale(pygame.image.load(os.path.join(
            current_dir, "player", "istockphoto-1307986275-612x612.jpg")), (1200, 800)).convert(), (0, 0))
        press_space = test_font.render(
            f'Press space to restart', False, "White")
        press_space_rec = press_space.get_rect(center=(600, HEIGHT-50))
        screen.blit(press_space, press_space_rec)
        score_message = test_font.render(f'Your score:{score}', False, "White")
        screen.blit(score_message, (495, 80))
        obstacle_rect_list.clear()

    pygame.display.update()
    clock.tick(60)
