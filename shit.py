import pygame
import os
import sys
import math
from random import randint, uniform

# --- Stylization ---
GOLD, RED = (255, 215, 0), (220, 20, 20)

def draw_shadow_text(surf, txt, font, pos, color):
    s = font.render(txt, True, (0,0,0))
    m = font.render(txt, True, color)
    surf.blit(s, (pos[0]+2, pos[1]+2))
    surf.blit(m, pos)

def load_frames(folder, prefix, size, count=6):
    return [pygame.transform.scale(pygame.image.load(os.path.join(current_dir, folder, f"{prefix}{i}.png")), size).convert_alpha() for i in range(1, count + 1)]

# --- Systems ---
def move_enemies(enemies):
    if not game_active: return enemies
    px, py = player_rec.centerx, player_rec.bottom
    # Tsunami Swarm Logic
    for i, e in enumerate(enemies):
        # Individual variation to avoid "lining up"
        speed = e['speed']
        dx, dy = px - e['rect'].centerx, py - (e['rect'].bottom + e['off_y'])
        dist = math.hypot(dx, dy) or 1
        
        # Surge movement with slight sinusoidal variation
        e['rect'].x += (dx/dist) * speed + math.sin(pygame.time.get_ticks()*0.005 + i)*0.5
        e['rect'].y += (dy/dist) * (speed * 0.5)
        
        # Stronger Dynamic Separation O(N)
        if i > 0:
            prev = enemies[i-1]['rect']
            if e['rect'].colliderect(prev.inflate(10, 5)):
                e['rect'].x += 1.5 if e['rect'].centerx > prev.centerx else -1.5
                e['rect'].y += 1 if e['rect'].bottom > prev.bottom else -1
                
    return [e for e in enemies if -400 < e['rect'].x < 1600]

def check_hit(enemies):
    global combo, score, spawn_ms, kill_cnt, score_cached
    for e in enemies[:]:
        ob = e['rect']
        hit = False
        on_p = abs(player_rec.bottom - ob.bottom) < 45
        if on_p and ((is_atk and ob.colliderect(player_rec)) or (dash_timer > 0 and ob.colliderect(player_rec))):
            hit = True
        else:
            for a in axes:
                # Requested: Absolute image overlap
                if abs(a['x'] - ob.centerx) < 65 and abs(a['y'] - ob.centery) < 65:
                    hit = True; break
        
        if hit:
            combo += 1; score += 10 * combo; kill_cnt += 1
            global shake_v; shake_v = 8 # Add screenshake
            dmg_pops.append({'x': ob.centerx, 'y': ob.top, 'txt': f"+{10*combo}", 't': 40, 'c': GOLD if combo > 5 else (255,255,255)})
            score_cached = None
            spawn_ms = max(50, 1000 - (score // 300) * 85) # Faster tsunami spawn
            pygame.time.set_timer(EV_SPAWN, spawn_ms)
            
            blood_layer.blit(splat_img, (ob.centerx-35, ob.bottom-15))
            for _ in range(4): parts.append({'x':ob.centerx,'y':ob.centery,'vx':randint(-6,6),'vy':randint(-10,-4),'t':15})
            dead_list.append([ob, 0, 12 if ob.centerx < player_rec.centerx else -12, -15])
            enemies.remove(e)
            return True
        elif on_p and ob.colliderect(player_rec) and dash_timer <= 0:
            return False
    return True

# --- Initialization ---
pygame.init()
WIDTH, HEIGHT = 1200, 800
window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF | pygame.HWSURFACE)
clock, f_heavy, f_small = pygame.time.Clock(), pygame.font.Font(None, 64), pygame.font.Font(None, 32)
current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

# Assets
bg = pygame.transform.scale(pygame.image.load(os.path.join(current_dir,"background","Desert.png")),(WIDTH,HEIGHT)).convert()
go_scr = pygame.transform.scale(pygame.image.load(os.path.join(current_dir,"player","istockphoto-1307986275-612x612.jpg")),(WIDTH,HEIGHT)).convert()
def get_sheet_frames(path, r, c, size, row, count):
    s = pygame.image.load(path).convert_alpha()
    fw, fh = s.get_width()//c, s.get_height()//r
    return [pygame.transform.scale(s.subsurface(pygame.Rect(i*fw, row*fh, fw, fh)), size) for i in range(count)]

ps = os.path.join(current_dir,"player","SaraFullSheet.png")
walk_r, walk_l = get_sheet_frames(ps, 21, 13, (110,110), 11, 9), get_sheet_frames(ps, 21, 13, (110,110), 9, 9)
walk_u, walk_d = get_sheet_frames(ps, 21, 13, (110,110), 8, 9), get_sheet_frames(ps, 21, 13, (110,110), 10, 9)
atk_r, atk_l = get_sheet_frames(ps, 21, 13, (110,110), 15, 6), get_sheet_frames(ps, 21, 13, (110,110), 13, 6)
dead_p = get_sheet_frames(ps, 21, 13, (110,110), 20, 6)[5]

axe_p = os.path.join(current_dir,"axe","battleaxe-sheet.png")
axe_r = get_sheet_frames(axe_p, 1, 8, (90,90), 0, 8)
axe_l = [pygame.transform.flip(f, True, False) for f in axe_r]

bad_base = load_frames('bad1', "YeOldyNecroGuy", (80,80), 6)
bad_l_anim, bad_r_anim = bad_base, [pygame.transform.flip(f, True, False) for f in bad_base]

def make_flash(frames):
    flash_list = []
    for f in frames:
        fc = f.copy(); fc.fill((255, 255, 255, 180), special_flags=pygame.BLEND_RGBA_ADD)
        flash_list.append(fc)
    return flash_list

bad_l_flash, bad_r_flash = make_flash(bad_l_anim), make_flash(bad_r_anim)
bad_dead_base = pygame.transform.scale(pygame.image.load(os.path.join(current_dir,'bad1',"YeOldyNecroGuy7.png")),(80,80)).convert_alpha()
bad_dead_l, bad_dead_r = bad_dead_base, pygame.transform.flip(bad_dead_base, True, False)
bad_dead_f_l, bad_dead_f_r = make_flash([bad_dead_l])[0], make_flash([bad_dead_r])[0]

splat_img = pygame.Surface((80, 50), pygame.SRCALPHA)
for _ in range(12): pygame.draw.circle(splat_img, (140,0,0,160), (randint(20,60), randint(15,35)), randint(6,12))

# State
game_active, game_over_f, score, combo, kill_cnt = True, False, 0, 0, 0
facing_r, is_atk, atk_done, dash_timer = True, False, False, 0
g_idx, a_idx, b_idx = 0, 0, 0
player_rec = walk_r[0].get_rect(midbottom=(600, 680))
player_surf = walk_r[0]
blood_layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
objs, dead_list, axes, parts, ghosts, dmg_pops = [], [], [], [], [], []
score_cached, shake_v = None, 0

EV_SPAWN = pygame.USEREVENT + 1; pygame.time.set_timer(EV_SPAWN, 1000)
EV_ANIM = pygame.USEREVENT + 2; pygame.time.set_timer(EV_ANIM, 120)

# --- Main ---
while True:
    for e in pygame.event.get():
        if e.type == pygame.QUIT: pygame.quit(); sys.exit()
        if game_active and e.type == EV_SPAWN:
            # TSUNAMI SPAWN: More monsters at once
            for _ in range(randint(2, 6)):
                x = -150 if randint(0,1)==0 else WIDTH+150
                rect = bad_base[0].get_rect(midbottom=(x, randint(450, 780)))
                objs.append({'rect': rect, 'speed': uniform(1.8, 3.5), 'off_y': randint(-30, 30)})
        if e.type == EV_ANIM: b_idx = (b_idx + 1) % 6

    if game_active:
        k, m = pygame.key.get_pressed(), pygame.mouse.get_pressed()
        if not is_atk and (m[0] or k[pygame.K_e]): 
            is_atk, atk_done, a_idx = True, False, 0
        if m[2] and dash_timer <= 0: dash_timer = 15

        if is_atk:
            a_idx += 0.6 # Faster animation (was 0.3)
            f_pool = atk_r if facing_r else atk_l
            if a_idx >= len(f_pool): is_atk = False; player_surf = (walk_r if facing_r else walk_l)[0]
            else:
                p_frame = f_pool[::-1][int(a_idx)]
                if int(a_idx) < 4:
                    player_surf = p_frame.copy()
                    axe_fr = (axe_r if facing_r else axe_l)[::-1][min(int(a_idx), 7)]
                    hx, hy = [(45,100),(65,105),(85,90),(95,70),(85,50),(65,40)][min(int(a_idx), 5)]
                    player_surf.blit(axe_fr, (hx-45 if facing_r else 90-hx, hy-75))
                    if not atk_done and int(a_idx) == 3:
                        mx, my = pygame.mouse.get_pos(); facing_r = mx >= player_rec.centerx
                        dx, dy = mx - player_rec.centerx, my - (player_rec.centery-40); dist = math.hypot(dx, dy) or 1
                        # Balanced 360-degree aiming velocity
                        axes.append({'x':player_rec.centerx, 'y':player_rec.centery-40, 'vx':(dx/dist)*16, 'vy':(dy/dist)*12, 'py':player_rec.bottom, 't':0, 'ty':my})
                        atk_done = True
                else: player_surf = p_frame

        # Movement (Always active - allows walk-and-throw)
        mh, mv = False, False
        if k[pygame.K_d]: player_rec.x += 4.5; facing_r, mh = True, True
        elif k[pygame.K_a]: player_rec.x -= 4.5; facing_r, mh = False, True
        if k[pygame.K_w]: player_rec.y -= 3; mv = True
        elif k[pygame.K_s]: player_rec.y += 3; mv = True
        
        # Base Walk Animation (Only if not attacking)
        if not is_atk:
            if mh: g_idx += 0.28; player_surf = (walk_r if facing_r else walk_l)[int(g_idx % 9)]
            elif mv: g_idx += 0.28; player_surf = (walk_u if k[pygame.K_w] else walk_d)[int(g_idx % 9)]
            else: player_surf = (walk_r if facing_r else walk_l)[0]

        if dash_timer > 0:
            dash_timer -= 1; player_rec.x += 28 if facing_r else -28
            if dash_timer % 5 == 0: ghosts.append({'img':player_surf, 'r':player_rec.copy(), 't':10})
        
        player_rec.x = max(20, min(player_rec.x, 1140)); player_rec.bottom = max(450, min(player_rec.bottom, 780))
        objs = move_enemies(objs)
        for d in dead_list: d[0].x += d[2]; d[0].y += d[3]; d[3]+=1; d[1]+=1
        dead_list = [d for d in dead_list if d[1] < 45]
        for a in axes[:]:
            a['t'] += 1; a['x'] += a['vx']; a['y'] += a['vy']; a['py'] += (a['ty'] - a['py']) / 10
            if a['t'] > 80: axes.remove(a)
        for p in parts[:]:
            p['x'] += p['vx']; p['y'] += p['vy']; p['vy'] += 0.8; p['t'] -= 1
            if p['t'] <= 0: parts.remove(p)
        for g in ghosts[:]:
            g['t'] -= 1
            if g['t'] <= 0: ghosts.remove(g)
        for d in dmg_pops[:]:
            d['y'] -= 1; d['t'] -= 1
            if d['t'] <= 0: dmg_pops.remove(d)
        if shake_v > 0: shake_v -= 1
        
        if not check_hit(objs): game_active, game_over_f, j_v = False, True, -15

        # Rendering with screenshake
        off = (randint(-shake_v,shake_v), randint(-shake_v,shake_v)) if shake_v > 0 else (0,0)
        window.blit(bg, off)
        window.blit(blood_layer, off)
        
        q = [(player_rec.bottom, player_surf, player_rec, 255)]
        for e in objs:
            ob = e['rect']
            q.append((ob.bottom, (bad_r_anim if ob.centerx < player_rec.centerx else bad_l_anim)[b_idx], ob, 255))
        for d in dead_list:
            img = (bad_dead_r if d[2]>0 else bad_dead_l)
            q.append((d[0].bottom, img, d[0], 255))
        for g in ghosts: q.append((g['r'].bottom, g['img'], g['r'], int(140*(g['t']/10))))
        
        q.sort(key=lambda x: x[0])
        for it in q:
            shad_rect = pygame.Rect(0, 0, it[2].width * 0.8, 15)
            shad_rect.center = (it[2].centerx, it[0])
            pygame.draw.ellipse(window, (0,0,0,60), (shad_rect.x+off[0], shad_rect.y+off[1], shad_rect.width, shad_rect.height))
            r_rect = it[2].move(off)
            if it[3] < 255: it[1].set_alpha(it[3]); window.blit(it[1], r_rect); it[1].set_alpha(255)
            else: window.blit(it[1], r_rect)

        for a in axes:
            fr = (axe_r if a['vx']>0 else axe_l)[(a['t']//2)%8]
            window.blit(fr, fr.get_rect(center=(int(a['x']+off[0]), int(a['y']+off[1]))))
        for p in parts: pygame.draw.rect(window, (180,0,0), (int(p['x']+off[0]), int(p['y']+off[1]), 4, 4))
        
        for d in dmg_pops:
            alpha = min(255, d['t'] * 7)
            s = f_small.render(d['txt'], True, d['c'])
            s.set_alpha(alpha)
            window.blit(s, (d['x']+off[0], d['y']+off[1]))
        
        if score_cached is None:
            score_cached = pygame.Surface((WIDTH, 80), pygame.SRCALPHA); score_cached.fill((0,0,0,130))
            draw_shadow_text(score_cached, f"SCORE: {score}", f_heavy, (30, 20), GOLD)
            draw_shadow_text(score_cached, f"KILLS: {kill_cnt}", f_small, (WIDTH-180, 30), "White")
            if combo > 1: draw_shadow_text(score_cached, f"{combo} COMBO", f_heavy, (WIDTH//2-100, 20), RED)
        window.blit(score_cached, (0,0))

    elif game_over_f:
        window.blit(bg, (0,0)); j_v += 1; player_rec.y += j_v; window.blit(dead_p, player_rec)
        if player_rec.top > HEIGHT: game_over_f = False
    else:
        if pygame.key.get_pressed()[pygame.K_SPACE]:
            game_active, score, objs, axes, parts, dead_list, kill_cnt, combo, dmg_pops = True, 0, [], [], [], [], 0, 0, []
            blood_layer.fill((0,0,0,0)); player_rec.midbottom = (600,680); score_cached = None
        window.blit(go_scr, (0,0))
        score_surf = f_heavy.render(f"FINAL SCORE: {score}", True, "White")
        score_rect = score_surf.get_rect(center=(WIDTH//2, HEIGHT - 180))
        instruct_surf = f_small.render("PRESS [SPACE] TO REVENGE", True, GOLD)
        instruct_rect = instruct_surf.get_rect(center=(WIDTH//2, HEIGHT - 100))
        window.blit(f_heavy.render(f"FINAL SCORE: {score}", True, (0,0,0)), (score_rect.x+3, score_rect.y+3))
        window.blit(score_surf, score_rect)
        window.blit(f_small.render("PRESS [SPACE] TO REVENGE", True, (0,0,0)), (instruct_rect.x+2, instruct_rect.y+2))
        window.blit(instruct_surf, instruct_rect)

    pygame.display.flip(); clock.tick(60)
