import pygame
import sys
import time

# ── couleurs ────────────────────────────────────────────────────────────────
BG          = (18,  18,  24)
GRID_LINE   = (45,  45,  60)
CELL_BASE   = (28,  28,  38)
CELL_HOVER  = (50,  60,  90)
CELL_MOVE   = (40, 100, 180, 180)   # cases accessibles (avec alpha)
WALL_PREVIEW= (220, 180,  60, 160)
WALL_PLACED = (230, 180,  50)
WALL_BLOCKED= (180,  40,  40)
P1_COLOR    = (220,  70,  70)
P2_COLOR    = (70,  140, 220)
P1_GOAL     = (220,  70,  70, 40)
P2_GOAL     = (70,  140, 220, 40)
TEXT_COLOR  = (200, 200, 220)
PANEL_BG    = (22,  22,  30)
BTN_ACTIVE  = (60,  100, 200)
BTN_IDLE    = (38,  38,  55)
BTN_HOVER   = (50,  80, 160)
BTN_BORDER  = (80,  80, 120)

CELL   = 64          # taille d'une case en px
GAP    = 10          # épaisseur du mur affiché
PANEL  = 240         # largeur panneau droit
MARGIN = 30          # marge autour du plateau

# ── helpers géométriques ────────────────────────────────────────────────────

def cell_rect(row, col):
    x = MARGIN + col * (CELL + GAP)
    y = MARGIN + row * (CELL + GAP)
    return pygame.Rect(x, y, CELL, CELL)

def hwall_rect(row, col):
    """Mur horizontal entre (row-1,col) et (row,col) — occupe 2 cols."""
    x = MARGIN + col * (CELL + GAP)
    y = MARGIN + row * (CELL + GAP) - GAP
    return pygame.Rect(x, y, 2 * CELL + GAP, GAP)

def vwall_rect(row, col):
    """Mur vertical entre (col-1) et (col) — occupe 2 rows."""
    x = MARGIN + col * (CELL + GAP) - GAP
    y = MARGIN + row * (CELL + GAP)
    return pygame.Rect(x, y, GAP, 2 * CELL + GAP)

def board_pixel_size(dim):
    return dim * CELL + (dim - 1) * GAP

# ── rendu principal ──────────────────────────────────────────────────────────

class QuoridorRenderer:
    """
    Rendu Pygame pour le jeu Quoridor.
    Instancier puis appeler .run(plateau, j1, j2, get_other_player, game_ended).
    HumanBot interagit via cette fenêtre.
    """

    def __init__(self, dim=9):
        pygame.init()
        pygame.font.init()
        self.dim = dim
        board_px = board_pixel_size(dim)
        W = MARGIN * 2 + board_px + PANEL
        H = MARGIN * 2 + board_px
        self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("Quoridor")
        self.clock = pygame.time.Clock()

        self.font_big   = pygame.font.SysFont("Georgia",       26, bold=True)
        self.font_med   = pygame.font.SysFont("Georgia",       18)
        self.font_small = pygame.font.SysFont("Courier New",   14)

        # surfaces alpha
        self.surf_moves  = pygame.Surface((W, H), pygame.SRCALPHA)
        self.surf_walls  = pygame.Surface((W, H), pygame.SRCALPHA)
        self.surf_goals  = pygame.Surface((W, H), pygame.SRCALPHA)

        # état UI
        self.mode           = "MOVE"   # "MOVE" | "WALL_H" | "WALL_V"
        self.hover_cell     = None     # (row, col)
        self.hover_wall     = None     # (i, j, is_vertical)
        self.pending_action = None     # rempli quand human a cliqué
        self.waiting        = False    # True quand on attend l'input human
        self.message        = ""
        self.last_legal     = True

    # ── boucle principale ────────────────────────────────────────────────────

    def run(self, plateau, j1, j2, game_ended_fn):
        """Boucle de jeu complète."""
        current = j1
        while not game_ended_fn():
            self._draw(plateau, current)
            pygame.display.flip()
            self.clock.tick(60)

            from bot import HumanBot
            if isinstance(current, HumanBot):
                # attendre input via la fenêtre
                action = self._wait_human_input(plateau, current)
                if action == "QUIT":
                    pygame.quit(); sys.exit()
                # action est déjà appliquée dans _wait_human_input
            else:
                # bot automatique
                self._handle_events_nonblocking()

                t =  time.time()
                current.play()
                print(f"{type(current).__name__} a joué en {time.time() - t:.2f} secondes")

                time.sleep(0.5)

            current = plateau.get_other_player(current)

        # écran fin
        self._draw(plateau, None)
        self._draw_winner(plateau, j1, j2)
        pygame.display.flip()
        self._wait_quit()

    def _handle_events_nonblocking(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()

    # ── input humain ─────────────────────────────────────────────────────────

    def _wait_human_input(self, plateau, joueur):
        """Bloque jusqu'à ce que le joueur humain ait joué un coup valide."""
        self.mode = "MOVE"
        self.message = "Choisissez une case ou un mur."
        accessible = plateau.get_accessible_cases(joueur)

        while True:
            mx, my = pygame.mouse.get_pos()
            self.hover_cell = self._pixel_to_cell(mx, my)
            self.hover_wall = self._pixel_to_wall(mx, my)

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return "QUIT"

                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_m:
                        self.mode = "MOVE"
                    elif e.key == pygame.K_h:
                        self.mode = "WALL_H"
                    elif e.key == pygame.K_v:
                        self.mode = "WALL_V"

                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    # boutons panneau
                    btn = self._click_button(mx, my, joueur)
                    if btn:
                        self.mode = btn
                        continue

                    if self.mode == "MOVE":
                        cell = self._pixel_to_cell(mx, my)
                        if cell:
                            row, col = cell
                            dest = plateau.board[row][col]
                            if dest in accessible:
                                joueur.try_move(dest)
                                self.message = f"Déplacement → ({row},{col})"
                                return True
                            else:
                                self.message = "Case inaccessible !"

                    elif self.mode in ("WALL_H", "WALL_V"):
                        if joueur.barrieres <= 0:
                            self.message = "Plus de barrières !"
                            continue
                        wall = self._pixel_to_wall(mx, my)
                        if wall:
                            i, j, is_v = wall
                            ok = joueur.try_place_wall(i, j, is_v)
                            if ok:
                                self.message = f"Barrière {'V' if is_v else 'H'} posée en ({i},{j})"
                                return True
                            else:
                                self.message = "Barrière illégale !"

            self._draw(plateau, joueur, accessible)
            pygame.display.flip()
            self.clock.tick(60)

    # ── conversion pixel ↔ grille ─────────────────────────────────────────

    def _pixel_to_cell(self, mx, my):
        for row in range(self.dim):
            for col in range(self.dim):
                if cell_rect(row, col).collidepoint(mx, my):
                    return (row, col)
        return None

    def _pixel_to_wall(self, mx, my):
        is_v = self.mode == "WALL_V"
        for i in range(self.dim):
            for j in range(self.dim):
                if is_v:
                    if j >= 1 and i <= self.dim - 2:
                        r = vwall_rect(i, j)
                        # zone étendue pour faciliter le clic
                        r_big = r.inflate(8, 0)
                        if r_big.collidepoint(mx, my):
                            return (i, j, True)
                else:
                    if i >= 1 and j <= self.dim - 2:
                        r = hwall_rect(i, j)
                        r_big = r.inflate(0, 8)
                        if r_big.collidepoint(mx, my):
                            return (i, j, False)
        return None

    def _click_button(self, mx, my, joueur):
        btns = self._button_rects(joueur)
        for name, rect in btns.items():
            if rect.collidepoint(mx, my):
                return name
        return None

    # ── dessin ───────────────────────────────────────────────────────────────

    def _draw(self, plateau, current_player, accessible=None):
        self.screen.fill(BG)
        self._draw_goals(plateau)
        self._draw_grid(plateau)
        if accessible:
            self._draw_accessible(accessible)
        self._draw_wall_preview(plateau, current_player)
        self._draw_walls(plateau)
        self._draw_players(plateau)
        self._draw_panel(plateau, current_player)

    def _draw_goals(self, plateau):
        self.surf_goals.fill((0,0,0,0))
        for col in range(self.dim):
            r = cell_rect(0, col)
            pygame.draw.rect(self.surf_goals, (*P2_COLOR, 35), r, border_radius=4)
        for col in range(self.dim):
            r = cell_rect(self.dim-1, col)
            pygame.draw.rect(self.surf_goals, (*P1_COLOR, 35), r, border_radius=4)
        self.screen.blit(self.surf_goals, (0,0))

    def _draw_grid(self, plateau):
        for row in range(self.dim):
            for col in range(self.dim):
                r = cell_rect(row, col)
                # fond cellule
                color = CELL_BASE
                pygame.draw.rect(self.screen, color, r, border_radius=4)
                # bordure subtile
                pygame.draw.rect(self.screen, GRID_LINE, r, width=1, border_radius=4)

    def _draw_accessible(self, accessible):
        self.surf_moves.fill((0,0,0,0))
        for case in accessible:
            r = cell_rect(case.row, case.col)
            pygame.draw.rect(self.surf_moves, (*CELL_MOVE[:3], 120), r, border_radius=4)
            # anneau lumineux
            pygame.draw.rect(self.surf_moves, (*CELL_MOVE[:3], 200), r, width=2, border_radius=4)
        self.screen.blit(self.surf_moves, (0,0))

    def _draw_wall_preview(self, plateau, current_player):
        if not current_player:
            return
        from bot import HumanBot
        if not isinstance(current_player, HumanBot):
            return
        mx, my = pygame.mouse.get_pos()
        wall = self._pixel_to_wall(mx, my)
        if not wall:
            return
        i, j, is_v = wall
        legal = plateau.is_wall_legal(i, j, is_v) and current_player.barrieres > 0
        color = (*WALL_PREVIEW[:3], 160) if legal else (*WALL_BLOCKED, 130)
        self.surf_walls.fill((0,0,0,0))
        if is_v:
            r = vwall_rect(i, j)
        else:
            r = hwall_rect(i, j)
        pygame.draw.rect(self.surf_walls, color, r, border_radius=3)
        self.screen.blit(self.surf_walls, (0,0))

    def _draw_walls(self, plateau):
        """Déduit les murs à partir des liens manquants entre cases."""
        drawn = set()
        for row in range(self.dim):
            for col in range(self.dim):
                case = plateau.board[row][col]
                # mur horizontal entre (row-1) et row
                if row > 0:
                    above = plateau.board[row-1][col]
                    if case.up is None and above is not None:  # lien coupé
                        # cherche si c'est un vrai mur (et pas juste le bord)
                        key = ("H", row, col)
                        if key not in drawn:
                            drawn.add(key)
                            r = pygame.Rect(
                                MARGIN + col*(CELL+GAP),
                                MARGIN + row*(CELL+GAP) - GAP,
                                CELL, GAP
                            )
                            pygame.draw.rect(self.screen, WALL_PLACED, r, border_radius=2)
                if col > 0:
                    left = plateau.board[row][col-1]
                    if case.left is None and left is not None:
                        key = ("V", row, col)
                        if key not in drawn:
                            drawn.add(key)
                            r = pygame.Rect(
                                MARGIN + col*(CELL+GAP) - GAP,
                                MARGIN + row*(CELL+GAP),
                                GAP, CELL
                            )
                            pygame.draw.rect(self.screen, WALL_PLACED, r, border_radius=2)

    def _draw_players(self, plateau):
        for joueur, color in [(plateau.j1, P1_COLOR), (plateau.j2, P2_COLOR)]:
            r = cell_rect(joueur.case.row, joueur.case.col)
            cx, cy = r.centerx, r.centery
            # ombre
            pygame.draw.circle(self.screen, (0,0,0), (cx+3, cy+3), CELL//2 - 10)
            # cercle principal
            pygame.draw.circle(self.screen, color, (cx, cy), CELL//2 - 10)
            # brillance
            pygame.draw.circle(self.screen, tuple(min(255,c+60) for c in color),
                                (cx-6, cy-6), CELL//6)

    def _draw_panel(self, plateau, current_player):
        board_px = board_pixel_size(self.dim)
        px = MARGIN * 2 + board_px
        panel_rect = pygame.Rect(px, 0, PANEL, self.screen.get_height())
        pygame.draw.rect(self.screen, PANEL_BG, panel_rect)
        pygame.draw.line(self.screen, GRID_LINE, (px, 0), (px, self.screen.get_height()), 1)

        x = px + 20
        y = 30

        title = self.font_big.render("QUORIDOR", True, TEXT_COLOR)
        self.screen.blit(title, (x, y)); y += 40

        # ligne de séparation
        pygame.draw.line(self.screen, GRID_LINE, (px+10, y), (px+PANEL-10, y)); y += 16

        def stat_line(label, val, color):
            nonlocal y
            lbl = self.font_small.render(label, True, (130,130,160))
            self.screen.blit(lbl, (x, y))
            v = self.font_med.render(str(val), True, color)
            self.screen.blit(v, (x+130, y))
            y += 24

        stat_line("Joueur 1 🔴", "", P1_COLOR)
        stat_line("  Barrières :", plateau.j1.barrieres, TEXT_COLOR)
        y += 6
        stat_line("Joueur 2 🔵", "", P2_COLOR)
        stat_line("  Barrières :", plateau.j2.barrieres, TEXT_COLOR)
        y += 10

        pygame.draw.line(self.screen, GRID_LINE, (px+10, y), (px+PANEL-10, y)); y += 16

        from bot import HumanBot
        if current_player and isinstance(current_player, HumanBot):
            turn_txt = self.font_med.render("Votre tour", True,
                P1_COLOR if current_player == plateau.j1 else P2_COLOR)
            self.screen.blit(turn_txt, (x, y)); y += 30

            # boutons mode
            btns = self._button_rects(current_player)
            labels = {"MOVE": "Déplacer  [M]",
                      "WALL_H": "Mur horiz  [H]",
                      "WALL_V": "Mur vert  [V]"}
            mx2, my2 = pygame.mouse.get_pos()
            for name, rect in btns.items():
                active = self.mode == name
                hovering = rect.collidepoint(mx2, my2)
                col_bg = BTN_ACTIVE if active else (BTN_HOVER if hovering else BTN_IDLE)
                pygame.draw.rect(self.screen, col_bg, rect, border_radius=6)
                pygame.draw.rect(self.screen, BTN_BORDER, rect, width=1, border_radius=6)
                lbl = self.font_small.render(labels[name], True, TEXT_COLOR)
                lbl_r = lbl.get_rect(center=rect.center)
                self.screen.blit(lbl, lbl_r)
            y = btns["WALL_V"].bottom + 16

            # message
            if self.message:
                color_msg = (200,80,80) if "illégale" in self.message or "inaccessible" in self.message.lower() else (130,200,130)
                lines = self.message.split("\n")
                for line in lines:
                    m = self.font_small.render(line, True, color_msg)
                    self.screen.blit(m, (x, y)); y += 18
        elif current_player:
            name = type(current_player).__name__
            color = P1_COLOR if current_player == plateau.j1 else P2_COLOR
            t = self.font_med.render(f"{name}…", True, color)
            self.screen.blit(t, (x, y)); y += 30

        # légende touches
        y = self.screen.get_height() - 80
        pygame.draw.line(self.screen, GRID_LINE, (px+10, y), (px+PANEL-10, y)); y += 10
        for hint in ["M : mode déplacement", "H : mur horizontal", "V : mur vertical"]:
            s = self.font_small.render(hint, True, (90,90,120))
            self.screen.blit(s, (x, y)); y += 18

    def _button_rects(self, joueur):
        board_px = board_pixel_size(self.dim)
        px = MARGIN * 2 + board_px + 20
        base_y = 200
        w, h, gap = PANEL - 40, 34, 8
        return {
            "MOVE":   pygame.Rect(px, base_y,        w, h),
            "WALL_H": pygame.Rect(px, base_y+h+gap,  w, h),
            "WALL_V": pygame.Rect(px, base_y+2*(h+gap), w, h),
        }

    def _draw_winner(self, plateau, j1, j2):
        winner = None
        if j1.case in j1.goal:
            winner = ("Joueur 1", P1_COLOR)
        elif j2.case in j2.goal:
            winner = ("Joueur 2", P2_COLOR)
        if not winner:
            return
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0,0,0,160))
        self.screen.blit(overlay, (0,0))
        txt = self.font_big.render(f"🏆  {winner[0]} gagne !", True, winner[1])
        r = txt.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2))
        self.screen.blit(txt, r)
        sub = self.font_small.render("Appuie sur une touche pour quitter", True, TEXT_COLOR)
        self.screen.blit(sub, sub.get_rect(center=(r.centerx, r.bottom+24)))

    def _wait_quit(self):
        while True:
            for e in pygame.event.get():
                if e.type in (pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    pygame.quit(); sys.exit()
            self.clock.tick(30)
