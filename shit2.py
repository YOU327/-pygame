import pygame
import os
import sys
import math
from random import randint


def display_score():
    text_surface = test_font.render(f'Score:{score}', False, "Black")
    text_rec = text_surface.get_rect(center=(75, 60))
    screen.blit(text_surface, text_rec)
    return score


def obstacle_movement(obstacle_list, is_update=True):
    if obstacle_list:
        for obst in obstacle_list:
            rect, type_idx, frames, frame_idx = obst
            if is_update:
                rect.x -= 4
                
                # Animate
                obst[3] += 0.15 # frame_idx
                if obst[3] >= len(frames): obst[3] = 0
            
            screen.blit(frames[int(obst[3])], rect)

        if is_update:
            obstacle_list = [
                obs for obs in obstacle_list if obs[0].x > -200]
        return obstacle_list
    else:
        return []


def collisions(obstacles):
    global dead_obstacle_list, hit_stop_frames, screen_shake_intensity, combo_count, combo_timer, score, spawn_rate_ms
    if obstacles:
        for obst in obstacles[:]:
            obstacle_rect = obst[0]
            type_idx = obst[1]
            hit_by_effect = False
            if dash_timer > 0 and good_rec.colliderect(obstacle_rect):
                hit_by_effect = True
                
            for p in punch_effects_list:
                if obstacle_rect.collidepoint(p['x'], p['y']):
                    hit_by_effect = True
                    break
                    
            if (good_rec.inflate(-20, -10).colliderect(obstacle_rect.inflate(-10, -5)) and is_attacking) or hit_by_effect:
                hit_stop_frames = 6
                screen_shake_intensity = 5
                combo_count += 1
                combo_timer = 180
                score += 10 * combo_count
                
                new_rate = max(250, 1000 - int(score / 500) * 100)
                if new_rate != spawn_rate_ms:
                    spawn_rate_ms = new_rate
                    pygame.time.set_timer(obstacle_timer, spawn_rate_ms)
                
                for _ in range(15):
                    color = (randint(150, 255), 0, randint(150, 255)) if randint(0,1) else (255, 255, 255)
                    particle_list.append({
                        'x': obstacle_rect.centerx,
                        'y': obstacle_rect.centery,
                        'vx': randint(-10, 10),
                        'vy': randint(-10, 5),
                        'size': randint(4, 10),
                        'color': color,
                        'timer': randint(20, 40)
                    })
                    
                if obstacle_rect.bottom >= 700:
                    dead_obstacle_list.append([obstacle_rect, 0, randint(5, 12), randint(-15, -5)])
                obstacle_rect_list.remove(obst)
                return True
            elif good_rec.inflate(-30, -20).colliderect(obstacle_rect.inflate(-20, -10)) and dash_timer <= 0:
                return False
    return True


def player_animation():
    global good_surface, good_index, good_attack_index, on_ground, facing_right, is_attacking, attack_mode, good_gravity
    keys = pygame.key.get_pressed()
    mouse_click = pygame.mouse.get_pressed()[0]

    # Attack Triggers
    if not is_attacking:
        if not on_ground and keys[pygame.K_s]:
            is_attacking = True
            attack_mode = "kick_down"
            good_attack_index = 0
            good_gravity = 15 # Dive kick momentum
        elif mouse_click:
            is_attacking = True
            good_attack_index = 0
            if keys[pygame.K_w]:
                attack_mode = "kick_up"
            else:
                attack_mode = "slash"

    if is_attacking:
        good_attack_index += 0.25
        frames_to_use = []
        if attack_mode == "slash":
            frames_to_use = good_strike_right if facing_right else good_strike_left
        elif attack_mode == "kick_down":
            frames_to_use = good_thrust_down
        elif attack_mode == "kick_up":
            frames_to_use = good_thrust_up

        if good_attack_index >= len(frames_to_use):
            is_attacking = False
            good_attack_index = 0
            good_surface = good_walk_right[0] if facing_right else good_walk_left[0]
        else:
            good_surface = frames_to_use[int(good_attack_index)]
            # Wave effect spawn
            if attack_mode == "slash" and int(good_attack_index) == 3: # Frame for slash wave
                direction = 1 if facing_right else -1
                spawn_x = good_rec.right - 10 if facing_right else good_rec.left + 10
                punch_effects_list.append({'x': spawn_x, 'y': good_rec.centery, 'timer': 0, 'dir': direction})
    else:
        if not on_ground:
            good_surface = good_walk_right[3] if facing_right else good_walk_left[3] # Jump frame
        else:
            if keys[pygame.K_d]:
                good_index += 0.2
                if good_index >= 8: good_index = 0
                good_surface = good_walk_right[int(good_index)]
                facing_right = True
            elif keys[pygame.K_a]:
                good_index += 0.2
                if good_index >= 8: good_index = 0
                good_surface = good_walk_left[int(good_index)]
                facing_right = False
            else:
                good_surface = good_walk_right[0] if facing_right else good_walk_left[0]
                good_rec.x -= 2
                if good_rec.x < 0: good_rec.x = 0


pygame.init()

WIDTH = 1200
HEIGHT = 800
game_active = True
game_over_falling = False
start_time = 0
score = 0
hit_stop_frames = 0
screen_shake_intensity = 0
combo_count = 0
combo_timer = 0
hover_timer = 0
facing_right = True
on_ground = True
dash_timer = 0
dash_cooldown = 0
dash_ghosts = []
spawn_rate_ms = 1000
platform_list = []
window = pygame.display.set_mode((WIDTH, HEIGHT))
screen = pygame.Surface((WIDTH, HEIGHT))
pygame.display.set_caption("追趕跑跳碰")
clock = pygame.time.Clock()
test_font = pygame.font.Font(None, 50)
current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
background_surface = pygame.transform.scale(pygame.image.load(os.path.join(
    current_dir, "player", "Full-Background.png")), (1200, 800)).convert()
bg_x = 0
bg_y = 0

game_over_surface = pygame.transform.scale(pygame.image.load(os.path.join(
    current_dir, "player", "istockphoto-1307986275-612x612.jpg")), (1200, 800)).convert()
tips_surface = test_font.render(
    'E : attack  W : jump  A : left  D : right', False, "black")
press_space_surface = test_font.render(
    'Press space to restart', False, "White")
press_space_rec = press_space_surface.get_rect(center=(600, HEIGHT-50))

def load_animation(folder, prefix, size, start=1, end=8):
    return [
        pygame.transform.scale(pygame.image.load(os.path.join(
            current_dir, folder, f"{prefix}{i}.png")), size).convert_alpha()
        for i in range(start, end + 1)
    ]

def get_frames_from_sheet(path, rows, cols, size, frame_count=None, row_to_get=None):
    sheet = pygame.image.load(path).convert_alpha()
    sheet_w, sheet_h = sheet.get_size()
    fw, fh = sheet_w // cols, sheet_h // rows
    frames = []
    
    if row_to_get is not None:
        actual_count = frame_count if frame_count is not None else cols
        for c in range(actual_count):
            rect = pygame.Rect(c * fw, row_to_get * fh, fw, fh)
            frame = sheet.subsurface(rect)
            frames.append(pygame.transform.scale(frame, size))
        return frames
        
    for i in range(frame_count):
        row = i // cols
        col = i % cols
        rect = pygame.Rect(col * fw, row * fh, fw, fh)
        frame = sheet.subsurface(rect)
        frames.append(pygame.transform.scale(frame, size))
    return frames

# bad
bad1_frames = load_animation('bad1', "YeOldyNecroGuy", (80, 100), 1, 6)
bad1_frame_index = 0
bad1_surface = bad1_frames[bad1_frame_index]
bad1_dead_surface = pygame.transform.scale(pygame.image.load(os.path.join(
    current_dir, 'bad1', "YeOldyNecroGuy7.png")), (80, 100)).convert_alpha()

# fly
bad2_frames = load_animation("bad2", "32x32-bat-sprite", (70, 70), 2, 4)
bad2_frame_index = 0
bad2_surface = bad2_frames[bad2_frame_index]


obstacle_rect_list = []
dead_obstacle_list = []
punch_effects_list = []
particle_list = []

def dead_obstacle_movement(dead_list, is_update=True):
    if dead_list:
        for dead_item in dead_list:
            obstacle_rect = dead_item[0]
            if is_update:
                obstacle_rect.x += dead_item[2]
                obstacle_rect.y += dead_item[3]
                dead_item[3] += 1
                dead_item[1] += 1
            screen.blit(bad1_dead_surface, obstacle_rect)
        if is_update:
            dead_list = [dead_item for dead_item in dead_list if dead_item[1] < 120 and dead_item[0].y < HEIGHT + 100]
        return dead_list
    else:
        return []


# HD LPC Spritesheet Optimization (Player Folder)
player_sheet_path = os.path.join(current_dir, "player", "SaraFullSheet.png")
# Layout: 13 cols x 21 rows (64x64 pixels/grid)
# LPC Standard Frame Counts: Walk=9, Strike=6, Thrust=8, Die=6
good_walk_right = get_frames_from_sheet(player_sheet_path, 21, 13, (120, 120), row_to_get=11, frame_count=9)
good_walk_left = get_frames_from_sheet(player_sheet_path, 21, 13, (120, 120), row_to_get=9, frame_count=9)
good_strike_right = get_frames_from_sheet(player_sheet_path, 21, 13, (120, 120), row_to_get=15, frame_count=6)
good_strike_left = get_frames_from_sheet(player_sheet_path, 21, 13, (120, 120), row_to_get=13, frame_count=6)
good_thrust_down = get_frames_from_sheet(player_sheet_path, 21, 13, (120, 120), row_to_get=6, frame_count=8)
good_thrust_up = get_frames_from_sheet(player_sheet_path, 21, 13, (120, 120), row_to_get=4, frame_count=8)
good_die_frames = get_frames_from_sheet(player_sheet_path, 21, 13, (120, 120), row_to_get=20, frame_count=6)

good_attack_frames = good_strike_right + good_strike_left + good_thrust_down + good_thrust_up
good_die_surface = good_die_frames[5] # Fully collapsed frame

# Enemies Initialization (Original Ground/Air only)
bad1_frames = load_animation('bad1', "YeOldyNecroGuy", (80, 100), 1, 6) # Zombie
bad2_frames = load_animation("bad2", "32x32-bat-sprite", (70, 70), 2, 4) # Bat

good_attack_index = 0
is_attacking = False
attack_mode = "slash"
good_index = 0
good_surface = good_walk_right[good_index]
good_rec = good_surface.get_rect(midbottom=(100, HEIGHT-90))
good_gravity = 0

# timer
obstacle_timer = pygame.USEREVENT + 1
pygame.time.set_timer(obstacle_timer, spawn_rate_ms)
bad1_animation_timer = pygame.USEREVENT + 2
pygame.time.set_timer(bad1_animation_timer, 150)
bad2_animation_timer = pygame.USEREVENT + 3
pygame.time.set_timer(bad2_animation_timer, 100)
platform_timer = pygame.USEREVENT + 4
pygame.time.set_timer(platform_timer, 3500)


while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if game_active:
            if event.type == platform_timer:
                platform_list.append(pygame.Rect(WIDTH + 50, randint(300, 550), randint(150, 300), 20))
            if event.type == obstacle_timer:
                if randint(0, 2): # Ground Zombie
                    rect = bad1_frames[0].get_rect(midbottom=(randint(WIDTH+100, WIDTH+300), 700))
                    obstacle_rect_list.append([rect, 1, bad1_frames, 0])
                else: # Flying Bat
                    rect = bad2_frames[0].get_rect(midbottom=(randint(WIDTH+100, WIDTH+300), randint(400, 550)))
                    obstacle_rect_list.append([rect, 2, bad2_frames, 0])
            if event.type == bad1_animation_timer:
                if bad1_frame_index < len(bad1_frames) - 1:
                    bad1_frame_index += 1
                else:
                    bad1_frame_index = 0
                bad1_surface = bad1_frames[bad1_frame_index]
            if event.type == bad2_animation_timer:
                if bad2_frame_index < len(bad2_frames) - 1:
                    bad2_frame_index += 1
                else:
                    bad2_frame_index = 0
                bad2_surface = bad2_frames[bad2_frame_index]

    if game_active == True:
        is_update = True
        if hit_stop_frames > 0:
            hit_stop_frames -= 1
            is_update = False
            
        if is_update:
            if combo_timer > 0:
                combo_timer -= 1
                if combo_timer == 0:
                    combo_count = 0
            bg_x -= 2
            if bg_x < -WIDTH:
                bg_x = 0
                
        screen.blit(background_surface, (bg_x, bg_y))
        screen.blit(background_surface, (bg_x + WIDTH, bg_y))
        
        for plat in platform_list[:]:
            if is_update:
                plat.x -= 3
            if plat.x < -300:
                platform_list.remove(plat)
            else:
                pygame.draw.rect(screen, (139, 69, 19), plat)
                pygame.draw.rect(screen, (160, 82, 45), plat, 3)
                
        keys = pygame.key.get_pressed()
        if is_update:
            if dash_cooldown > 0: dash_cooldown -= 1
            if (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]) and dash_cooldown == 0:
                dash_timer = 8
                dash_cooldown = 90
                screen_shake_intensity = 3
                
            if dash_timer > 0:
                dash_timer -= 1
                good_rec.x += 25 if facing_right else -25
                good_gravity = 0
                if dash_timer % 3 == 0:
                    dash_ghosts.append({'img': good_surface, 'rect': good_rec.copy(), 'timer': 12})
            else:
                if keys[pygame.K_w] and on_ground:
                    good_gravity = -26
                    hover_timer = 0
                elif not keys[pygame.K_w] and good_gravity < -8:
                    good_gravity = -8
                if keys[pygame.K_d]:
                    good_rec.x += 6
                    facing_right = True
                    if good_rec.x > WIDTH - 5: good_rec.x = WIDTH - 5
                if keys[pygame.K_a]:
                    good_rec.x -= 6
                    facing_right = False
                    if good_rec.x < 0: good_rec.x = 0
                        
                if keys[pygame.K_e] and not on_ground:
                    if hover_timer < 15:
                        good_gravity = 0
                        hover_timer += 1
                    else:
                        good_gravity += 1
                else:
                    good_gravity += 1
                    
            good_rec.y += good_gravity
            on_platform = False
            if good_gravity > 0 and dash_timer == 0:
                for plat in platform_list:
                    if good_rec.colliderect(plat) and good_rec.bottom <= plat.top + 30:
                        good_rec.bottom = plat.top + 12
                        good_gravity = 0
                        hover_timer = 0
                        on_platform = True
                        break
                        
            if on_platform:
                good_rec.x -= 3
                if good_rec.x < 0: good_rec.x = 0
            
            if good_rec.bottom >= HEIGHT - 90:
                good_rec.bottom = HEIGHT - 90
                good_gravity = 0
                hover_timer = 0
            on_ground = (good_rec.bottom >= HEIGHT - 90) or on_platform
        
        for ghost in dash_ghosts[:]:
            if is_update: ghost['timer'] -= 1
            if ghost['timer'] <= 0: dash_ghosts.remove(ghost)
            else:
                ghost_surf = ghost['img'].copy()
                ghost_surf.set_alpha(100)
                screen.blit(ghost_surf, ghost['rect'])
                
        screen.blit(good_surface, good_rec)
        
        for p in punch_effects_list[:]:
            if is_update:
                p['timer'] += 1
            if p['timer'] > 8:
                if is_update:
                    punch_effects_list.remove(p)
            else:
                if is_update:
                    p['x'] += 15 * p.get('dir', 1) - 2
                    if randint(0, 1):
                        particle_list.append({
                            'x': p['x'] + randint(-10, 10),
                            'y': p['y'] + randint(-20, 20),
                            'vx': p.get('dir', 1) * randint(2, 6) - 2,
                            'vy': randint(-3, 3),
                            'size': randint(2, 6),
                            'color': (150, 220, 255),
                            'timer': randint(5, 12)
                        })
                height = 50 + p['timer'] * 4
                width = max(2, 20 - p['timer'])
                rect = pygame.Rect(0, 0, width, height)
                rect.center = (int(p['x']), int(p['y']))
                pygame.draw.ellipse(screen, (220, 240, 255), rect)
                rect.inflate_ip(-width//2, -height//3)
                if rect.width > 0 and rect.height > 0:
                    pygame.draw.ellipse(screen, (255, 255, 255), rect)
                    
        for p in particle_list[:]:
            if is_update:
                p['x'] += p['vx']
                p['y'] += p['vy']
                p['vy'] += 0.5
                p['timer'] -= 1
                if p['timer'] <= 0:
                    particle_list.remove(p)
            if p['timer'] > 0:
                pygame.draw.rect(screen, p['color'], (int(p['x']), int(p['y']), p['size'], p['size']))
                    
        obstacle_rect_list = obstacle_movement(obstacle_rect_list, is_update)
        dead_obstacle_list = dead_obstacle_movement(dead_obstacle_list, is_update)
        if is_update:
            game_active = collisions(obstacle_rect_list)
            if not game_active:
                game_over_falling = True
                good_gravity = -15
                screen_shake_intensity = 15
            else:
                score = display_score()
                player_animation()
        else:
            score = display_score()
            
        screen.blit(tips_surface, (0, 0))
        
        if combo_count > 1:
            combo_surf = test_font.render(f"{combo_count} COMBO!", False, (255, 50, 50))
            combo_shake_x = randint(-2, 2) if combo_timer > 150 else 0
            combo_shake_y = randint(-2, 2) if combo_timer > 150 else 0
            screen.blit(combo_surf, (WIDTH - 250 + combo_shake_x, 50 + combo_shake_y))
    elif game_over_falling:
        screen.blit(background_surface, (bg_x, bg_y))
        screen.blit(background_surface, (bg_x + WIDTH, bg_y))
        for obst in obstacle_rect_list:
            rect, type_idx, frames, f_idx = obst
            screen.blit(frames[int(f_idx)], rect)
        for dead_item in dead_obstacle_list:
            screen.blit(bad1_dead_surface, dead_item[0])
            
        good_gravity += 1
        good_rec.y += good_gravity
        screen.blit(good_die_surface, good_rec)
        score = display_score()
        
        if good_rec.top > HEIGHT:
            game_over_falling = False
    else:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            game_active = True
            good_rec.midbottom = (100, HEIGHT - 90)
            good_gravity = 0
            start_time = int(pygame.time.get_ticks() / 100)
            score = 0
            spawn_rate_ms = 1000
            pygame.time.set_timer(obstacle_timer, spawn_rate_ms)
        screen.blit(game_over_surface, (0, 0))
        screen.blit(press_space_surface, press_space_rec)
        score_message = test_font.render(f'Your score:{score}', False, "White")
        screen.blit(score_message, (495, 80))
        obstacle_rect_list.clear()
        dead_obstacle_list.clear()
        punch_effects_list.clear()
        particle_list.clear()
        platform_list.clear()
        dash_ghosts.clear()
        combo_count = 0
        obstacle_rect_list = obstacle_movement(obstacle_rect_list, False)

    if screen_shake_intensity > 0:
        render_offset_x = randint(-screen_shake_intensity, screen_shake_intensity)
        render_offset_y = randint(-screen_shake_intensity, screen_shake_intensity)
        screen_shake_intensity -= 1
    else:
        render_offset_x = 0
        render_offset_y = 0

    window.fill("Black")
    window.blit(screen, (render_offset_x, render_offset_y))
    pygame.display.update()
    clock.tick(60)