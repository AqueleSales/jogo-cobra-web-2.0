# ARQUIVO main.py VERSÃO COM IA MELHORADA E CONTAGEM DE MAÇÃS (APENAS NO GAME OVER)
import pygame
import random
import os
import sys
import asyncio
from collections import deque

try:
    import platform
except ImportError:
    platform = None

# --- Constantes e Configurações Iniciais ---
pygame.init()
pygame.mixer.init()

PRETO = (0, 0, 0)
BRANCO_FUNDO = (20, 20, 20)
VERDE_COBRA = (4, 184, 53)
BRANCO_TEXTO = (240, 240, 240)
AMARELO_AVISO = (255, 221, 0)
VERMELHO_ERRO = (255, 60, 60)
CORES_FANTASMAS = [(255, 0, 0), (255, 182, 193), (0, 255, 255), (255, 165, 0), (160, 32, 240)]
COR_FANTASMA_FUGINDO = (60, 60, 255)
COR_FANTASMA_FUGINDO_PISCANDO = (240, 240, 240)
COR_FANTASMA_COMIDO = (200, 200, 200)
TAMANHO_BLOCO = 22
LARGURA_GRADE = 25
ALTURA_GRADE = 25
LARGURA_TELA = LARGURA_GRADE * TAMANHO_BLOCO
ALTURA_TELA = ALTURA_GRADE * TAMANHO_BLOCO
MEIO_X, MEIO_Y = LARGURA_GRADE // 2, ALTURA_GRADE // 2
tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption('SnackPack')
relogio = pygame.time.Clock()
DURACAO_MODO_CACADOR = 10000
DURACAO_CONGELAMENTO = 8000
INTERVALO_POWERUP = 30000
INTERVALO_POWERUP_VIDA = 60000

fonte_placar = pygame.font.Font(None, 36)
fonte_ui = pygame.font.Font(None, 30)
fonte_menu = pygame.font.Font(None, 50)
fonte_game_over = pygame.font.Font(None, 50)
fonte_texto_conteudo = pygame.font.Font(None, 28)

# --- ESTADOS DO JOGO ---
ESTADO_MENU = 'menu'
ESTADO_JOGANDO = 'jogando'
ESTADO_AJUDA = 'ajuda'
ESTADO_SOBRE = 'sobre'
ESTADO_CREDITOS = 'creditos'
ESTADO_GAME_OVER = 'game_over'
ESTADO_ERRO = 'erro'
ESTADO_SAIR = 'sair'

# --- CONTEÚDOS DE TEXTO PARA AS TELAS ---
TEXTO_SOBRE = [
    "Snackpack é um jogo 2D desenvolvido no VS Code,",
    "com foco em diversão e desafio. Criado como parte",
    "de um projeto acadêmico, ele traz mecânicas simples",
    "e dinâmicas que garantem entretenimento ao jogador.",
    "",
    "Desenvolvido por Geovani Braz Dantas Junior"
]
TEXTO_CREDITOS = [
    "Desenvolvido por: Geovani Braz Dantas Junior",
    "Design: Geovani Braz Dantas Junior",
    "Agradecimentos Especiais:",
    "Rafaela Azevedo pela orientação do projeto."
]

# --- Dicionários Globais para Recursos ---
texturas_parede = {}
texturas_fantasmas = {}
texturas_cobra = {}
texturas_cobra_cacada = {}
textura_maca = None
textura_fantasma_fugindo = None
textura_fantasma_fugindo_piscando = None
textura_fantasma_comido = None
textura_ajuda = None
textura_vida = None
textura_powerup_congelar = None
textura_logo = None
erro_carregamento = ""
high_score = 0
def salvar_recorde(pontos):
    if platform and hasattr(platform, 'window'):
        try:
            platform.window.localStorage.setItem('high_score_snackpack', str(pontos))
        except Exception as e:
            print(f"Não foi possível salvar o recorde: {e}")

def carregar_recorde():
    global high_score
    if platform and hasattr(platform, 'window'):
        try:
            score = platform.window.localStorage.getItem('high_score_snackpack')
            if score:
                high_score = int(score)
            else:
                high_score = 0
        except Exception as e:
            print(f"Não foi possível carregar o recorde: {e}")
            high_score = 0

def carregar_todos_os_recursos():
    global textura_maca, textura_fantasma_fugindo, textura_fantasma_fugindo_piscando, textura_fantasma_comido
    global textura_ajuda, textura_vida, textura_powerup_congelar, erro_carregamento, textura_logo
    
    try:
        caminho_texturas = 'PyTexture2'
        if not os.path.isdir(caminho_texturas):
            erro_carregamento = f"Pasta '{caminho_texturas}' nao encontrada!"
            return False
        try:
            caminho_musica = os.path.join(caminho_texturas, 'musica_tema.ogg')
            pygame.mixer.music.load(caminho_musica)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
        except pygame.error:
            print(f"AVISO: '{caminho_musica}' não encontrado.")
        try:
            logo_original = pygame.image.load(os.path.join(caminho_texturas, 'logo.png')).convert_alpha()
            tamanho_logo = 200 
            textura_logo = pygame.transform.scale(logo_original, (tamanho_logo, tamanho_logo))
        except pygame.error:
            print("AVISO: 'logo.png' não encontrado.") 
        try:
            textura_vida_original = pygame.image.load(os.path.join(caminho_texturas, 'vida.png')).convert_alpha()
            textura_vida = pygame.transform.scale(textura_vida_original, (25, 25))
        except pygame.error:
            print("AVISO: 'vida.png' não encontrado.")
        try:
            textura_powerup_original = pygame.image.load(os.path.join(caminho_texturas, 'powerup_congelar.png')).convert_alpha()
            textura_powerup_congelar = pygame.transform.scale(textura_powerup_original, (TAMANHO_BLOCO, TAMANHO_BLOCO))
        except pygame.error:
            print("AVISO: 'powerup_congelar.png' não encontrado.")
        try:
            caminho_ajuda_img = os.path.join(caminho_texturas, 'ajuda_screen.png')
            textura_ajuda_original = pygame.image.load(caminho_ajuda_img).convert_alpha()
            textura_ajuda = pygame.transform.scale(textura_ajuda_original, (LARGURA_TELA, ALTURA_TELA))
        except pygame.error:
            print(f"AVISO: '{caminho_ajuda_img}' nao encontrada.")
        textura_maca_original = pygame.image.load(os.path.join(caminho_texturas, 'maca.png')).convert_alpha()
        textura_maca = pygame.transform.scale(textura_maca_original, (TAMANHO_BLOCO, TAMANHO_BLOCO))
        
        nomes_texturas_parede = ['vertical', 'horizontal', 'canto_se', 'canto_sd', 'canto_ie', 'canto_id', 't_cima', 't_baixo',
                                 't_esquerda', 't_direita', 'fim_cima', 'fim_baixo', 'fim_esquerda', 'fim_direita', 'cruz',
                                 'parede_cheia', 'parede_isolada']
        for nome in nomes_texturas_parede:
            arquivo = f"{nome}.png"
            img = pygame.image.load(os.path.join(caminho_texturas, arquivo)).convert()
            texturas_parede[nome] = pygame.transform.scale(img, (TAMANHO_BLOCO, TAMANHO_BLOCO))

        nomes_arquivos_fantasmas = ['fantasma_vermelho.png', 'fantasma_rosa.png', 'fantasma_azul.png', 'fantasma_laranja.png', 'fantasma_roxo.png']
        for i, nome_arquivo in enumerate(nomes_arquivos_fantasmas):
            cor_fantasma = CORES_FANTASMAS[i]
            img_original = pygame.image.load(os.path.join(caminho_texturas, nome_arquivo)).convert_alpha()
            texturas_fantasmas[cor_fantasma] = pygame.transform.scale(img_original, (TAMANHO_BLOCO, TAMANHO_BLOCO))

        textura_fantasma_fraco_original = pygame.image.load(os.path.join(caminho_texturas, 'fantasma_fraco.png')).convert_alpha()
        textura_fantasma_fugindo = pygame.transform.scale(textura_fantasma_fraco_original, (TAMANHO_BLOCO, TAMANHO_BLOCO))
        
        def carregar_sprites_cobra_interno(dicionario, sufixo=''):
            cabeca_original = pygame.image.load(os.path.join(caminho_texturas, f'cobra_cabeca{sufixo}.png')).convert_alpha()
            dicionario['cabeca_cima'] = pygame.transform.scale(cabeca_original, (TAMANHO_BLOCO, TAMANHO_BLOCO))
            dicionario['cabeca_baixo'] = pygame.transform.rotate(dicionario['cabeca_cima'], 180)
            dicionario['cabeca_direita'] = pygame.transform.rotate(dicionario['cabeca_cima'], 270)
            dicionario['cabeca_esquerda'] = pygame.transform.rotate(dicionario['cabeca_cima'], 90)
            cauda_original = pygame.image.load(os.path.join(caminho_texturas, f'cobra_cauda{sufixo}.png')).convert_alpha()
            dicionario['cauda_baixo'] = pygame.transform.scale(cauda_original, (TAMANHO_BLOCO, TAMANHO_BLOCO))
            dicionario['cauda_cima'] = pygame.transform.rotate(dicionario['cauda_baixo'], 180)
            dicionario['cauda_direita'] = pygame.transform.rotate(dicionario['cauda_baixo'], 90)
            dicionario['cauda_esquerda'] = pygame.transform.rotate(dicionario['cauda_baixo'], 270)
            nomes_corpo_cobra = ['horizontal', 'vertical', 'ie', 'id', 'se', 'sd']
            for nome in nomes_corpo_cobra:
                arquivo = f'cobra_{nome}{sufixo}.png'
                img_original = pygame.image.load(os.path.join(caminho_texturas, arquivo)).convert_alpha()
                dicionario[nome] = pygame.transform.scale(img_original, (TAMANHO_BLOCO, TAMANHO_BLOCO))
        
        carregar_sprites_cobra_interno(texturas_cobra)
        carregar_sprites_cobra_interno(texturas_cobra_cacada, sufixo='_cacada')
        
        textura_fantasma_fugindo_piscando = pygame.Surface((TAMANHO_BLOCO, TAMANHO_BLOCO), pygame.SRCALPHA)
        pygame.draw.circle(textura_fantasma_fugindo_piscando, COR_FANTASMA_FUGINDO_PISCANDO, (TAMANHO_BLOCO // 2, TAMANHO_BLOCO // 2), TAMANHO_BLOCO // 2 - 2)
        textura_fantasma_comido = pygame.Surface((TAMANHO_BLOCO, TAMANHO_BLOCO), pygame.SRCALPHA)
        olho_rect = pygame.Rect(TAMANHO_BLOCO // 4 - 1, TAMANHO_BLOCO // 3, 4, 4)
        pygame.draw.rect(textura_fantasma_comido, BRANCO_TEXTO, olho_rect)
        olho_rect.x += TAMANHO_BLOCO // 2
        pygame.draw.rect(textura_fantasma_comido, BRANCO_TEXTO, olho_rect)

        return True

    except Exception as e:
        erro_carregamento = str(e)
        print(f"ERRO CRÍTICO AO CARREGAR RECURSOS: {e}")
        return False

# --- Funções e Classes do Jogo ---

class PowerUp:
    def __init__(self, labirinto, textura):
        self.labirinto = labirinto
        self.textura = textura
        self.pos = None
        self.ativo = False
    def desenhar(self, tela_surface):
        if self.ativo and self.pos and self.textura:
            rect = pygame.Rect(self.pos.x * TAMANHO_BLOCO, self.pos.y * TAMANHO_BLOCO, TAMANHO_BLOCO, TAMANHO_BLOCO)
            tela_surface.blit(self.textura, rect)
    def ativar(self, corpo_cobra, portal_tiles):
        if not self.textura: return
        self.ativo = True
        locais_possiveis = []
        for y in range(ALTURA_GRADE):
            for x in range(LARGURA_GRADE):
                pos_tupla = (x, y)
                pos_vector = pygame.math.Vector2(x, y)
                if self.labirinto[y][x] == 0 and pos_vector not in corpo_cobra and pos_tupla not in portal_tiles:
                    locais_possiveis.append(pos_vector)
        if locais_possiveis:
            self.pos = random.choice(locais_possiveis)
        else:
            self.desativar()
    def desativar(self):
        self.ativo = False
        self.pos = None

def escolher_textura_parede(labirinto, x, y):
    cima = labirinto[y - 1][x] == 1 if y > 0 else True
    baixo = labirinto[y + 1][x] == 1 if y < ALTURA_GRADE - 1 else True
    esq = labirinto[y][x - 1] == 1 if x > 0 else True
    dir = labirinto[y][x + 1] == 1 if x < LARGURA_GRADE - 1 else True
    vizinhos = (cima, baixo, esq, dir)
    num_vizinhos = sum(vizinhos)
    textura = None
    if num_vizinhos == 4: textura = texturas_parede.get('parede_cheia')
    elif num_vizinhos == 3:
        if not cima: textura = texturas_parede.get('t_cima')
        elif not baixo: textura = texturas_parede.get('t_baixo')
        elif not esq: textura = texturas_parede.get('t_esquerda')
        elif not dir: textura = texturas_parede.get('t_direita')
    elif num_vizinhos == 2:
        if cima and baixo: textura = texturas_parede.get('vertical')
        elif esq and dir: textura = texturas_parede.get('horizontal')
        elif baixo and dir: textura = texturas_parede.get('canto_se')
        elif baixo and esq: textura = texturas_parede.get('canto_sd')
        elif cima and dir: textura = texturas_parede.get('canto_ie')
        elif cima and esq: textura = texturas_parede.get('canto_id')
    elif num_vizinhos == 1:
        if baixo: textura = texturas_parede.get('fim_cima')
        elif cima: textura = texturas_parede.get('fim_baixo')
        elif dir: textura = texturas_parede.get('fim_esquerda')
        elif esq: textura = texturas_parede.get('fim_direita')
    elif num_vizinhos == 0: textura = texturas_parede.get('cruz')
    return textura if textura else texturas_parede.get('parede_cheia')

def buscar_caminho_bfs(labirinto, inicio, fim):
    fila = deque([[inicio]])
    visitados = {inicio}
    while fila:
        caminho = fila.popleft()
        x, y = caminho[-1]
        if (x, y) == fim: return caminho
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            prox_x, prox_y = x + dx, y + dy
            if (0 <= prox_x < LARGURA_GRADE and 0 <= prox_y < ALTURA_GRADE and
                    labirinto[prox_y][prox_x] == 0 and (prox_x, prox_y) not in visitados):
                novo_caminho = list(caminho)
                novo_caminho.append((prox_x, prox_y))
                fila.append(novo_caminho)
                visitados.add((prox_x, prox_y))
    return None

def criar_atalhos_no_labirinto(labirinto):
    becos_sem_saida = []
    for y in range(2, ALTURA_GRADE - 2):
        for x in range(2, LARGURA_GRADE - 2):
            if labirinto[y][x] == 0:
                vizinhos_parede = sum(
                    [labirinto[y - 1][x], labirinto[y + 1][x], labirinto[y][x - 1], labirinto[y][x + 1]])
                if vizinhos_parede == 3:
                    becos_sem_saida.append((x, y))
    for x, y in becos_sem_saida:
        paredes_quebraveis = []
        if y > 1 and labirinto[y - 1][x] == 1 and labirinto[y - 2][x] == 0: paredes_quebraveis.append((x, y - 1))
        if y < ALTURA_GRADE - 2 and labirinto[y + 1][x] == 1 and labirinto[y + 2][x] == 0: paredes_quebraveis.append((x, y + 1))
        if x > 1 and labirinto[y][x - 1] == 1 and labirinto[y][x - 2] == 0: paredes_quebraveis.append((x - 1, y))
        if x < LARGURA_GRADE - 2 and labirinto[y][x + 1] == 1 and labirinto[y][x + 2] == 0: paredes_quebraveis.append((x + 1, y))
        if paredes_quebraveis:
            px, py = random.choice(paredes_quebraveis)
            labirinto[py][px] = 0
    QUANTIDADE_DE_LOOPS = 80
    for _ in range(QUANTIDADE_DE_LOOPS):
        x = random.randrange(2, LARGURA_GRADE - 2)
        y = random.randrange(2, ALTURA_GRADE - 2)
        if labirinto[y][x] == 1:
            if labirinto[y - 1][x] == 0 and labirinto[y + 1][x] == 0:
                labirinto[y][x] = 0
            elif labirinto[y][x - 1] == 0 and labirinto[y][x + 1] == 0:
                labirinto[y][x] = 0

def gerar_labirinto_hibrido():
    labirinto = [[0 for _ in range(LARGURA_GRADE)] for _ in range(ALTURA_GRADE)]
    for x in range(LARGURA_GRADE):
        labirinto[0][x] = 1
        labirinto[ALTURA_GRADE - 1][x] = 1
    for y in range(ALTURA_GRADE):
        labirinto[y][0] = 1
        labirinto[y][LARGURA_GRADE - 1] = 1
    casa_l, casa_a = 11, 6
    x_inicio_casa, y_inicio_casa = MEIO_X - casa_l // 2, MEIO_Y - casa_a // 2
    for y in range(y_inicio_casa, y_inicio_casa + casa_a):
        for x in range(x_inicio_casa, x_inicio_casa + casa_l):
            labirinto[y][x] = 1
    for y in range(y_inicio_casa + 1, y_inicio_casa + casa_a - 1):
        for x in range(x_inicio_casa + 1, x_inicio_casa + casa_l - 1):
            labirinto[y][x] = 0
    labirinto[y_inicio_casa][MEIO_X] = 0
    for y in range(2, ALTURA_GRADE - 2):
        for x in range(2, LARGURA_GRADE - 2):
            is_in_house = (x_inicio_casa <= x < x_inicio_casa + casa_l and y_inicio_casa <= y < y_inicio_casa + casa_a)
            if not is_in_house:
                labirinto[y][x] = 1
    start_x, start_y = random.randrange(3, LARGURA_GRADE - 3, 2), random.randrange(3, ALTURA_GRADE - 3, 2)
    while (x_inicio_casa <= start_x < x_inicio_casa + casa_l and y_inicio_casa <= start_y < y_inicio_casa + casa_a):
        start_x, start_y = random.randrange(3, LARGURA_GRADE - 3, 2), random.randrange(3, ALTURA_GRADE - 3, 2)
    def cavar(x, y):
        labirinto[y][x] = 0
        direcoes = [(0, -2), (0, 2), (-2, 0), (2, 0)]
        random.shuffle(direcoes)
        for dx, dy in direcoes:
            nx, ny = x + dx, y + dy
            if 2 < ny < ALTURA_GRADE - 3 and 2 < nx < LARGURA_GRADE - 3 and labirinto[ny][nx] == 1:
                labirinto[y + dy // 2][x + dx // 2] = 0
                cavar(nx, ny)
    cavar(start_x, start_y)
    criar_atalhos_no_labirinto(labirinto)
    labirinto[0][MEIO_X] = 0; labirinto[1][MEIO_X] = 0
    labirinto[ALTURA_GRADE - 1][MEIO_X] = 0; labirinto[ALTURA_GRADE - 2][MEIO_X] = 0
    labirinto[MEIO_Y][0] = 0; labirinto[MEIO_Y][1] = 0
    labirinto[MEIO_Y][LARGURA_GRADE - 1] = 0; labirinto[MEIO_Y][LARGURA_GRADE - 2] = 0
    pos_iniciais_fantasmas = []
    locais_spawn_possiveis = []
    for y in range(y_inicio_casa + 1, y_inicio_casa + casa_a - 1):
        for x in range(x_inicio_casa + 1, x_inicio_casa + casa_l - 1):
            locais_spawn_possiveis.append(pygame.math.Vector2(x, y))
    random.shuffle(locais_spawn_possiveis)
    for i in range(min(5, len(locais_spawn_possiveis))):
        pos_iniciais_fantasmas.append(locais_spawn_possiveis[i])
    portais = {
        (0, MEIO_X): (ALTURA_GRADE - 2, MEIO_X), (ALTURA_GRADE - 1, MEIO_X): (1, MEIO_X),
        (MEIO_Y, 0): (MEIO_Y, LARGURA_GRADE - 2), (MEIO_Y, LARGURA_GRADE - 1): (MEIO_Y, 1)
    }
    pos_inicial_cobra = pygame.math.Vector2(MEIO_X, ALTURA_GRADE - 2)
    return labirinto, pos_inicial_cobra, portais, pos_iniciais_fantasmas

class Fantasma:
    def __init__(self, pos_inicial, labirinto, cor_cacando, personalidade):
        self.pos = pos_inicial.copy(); self.labirinto = labirinto; self.base = pos_inicial.copy()
        self.cor_cacando = cor_cacando; self.estado = 'cacando'; self.caminho = []
        self.movimento_ticker = 0; self.recalculo_ticker = 0
        self.congelado = False
        self.tempo_fim_congelamento = 0
        self.personalidade = personalidade
    def desenhar(self, tempo_fim_cacador):
        rect = pygame.Rect(self.pos.x * TAMANHO_BLOCO, self.pos.y * TAMANHO_BLOCO, TAMANHO_BLOCO, TAMANHO_BLOCO)
        textura_a_desenhar = None
        if self.estado == 'fugindo':
            tempo_atual = pygame.time.get_ticks()
            if tempo_fim_cacador - tempo_atual < 3000 and (tempo_atual // 250) % 2 == 0:
                textura_a_desenhar = textura_fantasma_fugindo_piscando
            else:
                textura_a_desenhar = textura_fantasma_fugindo
        elif self.estado == 'comido': textura_a_desenhar = textura_fantasma_comido
        else: textura_a_desenhar = texturas_fantasmas.get(self.cor_cacando)
        if textura_a_desenhar: tela.blit(textura_a_desenhar, rect.topleft)
        if self.congelado:
            sombra = pygame.Surface((TAMANHO_BLOCO, TAMANHO_BLOCO), pygame.SRCALPHA)
            sombra.fill((0, 150, 255, 100))
            tela.blit(sombra, rect.topleft)
    def congelar(self):
        self.congelado = True
        self.tempo_fim_congelamento = pygame.time.get_ticks() + DURACAO_CONGELAMENTO
    def obter_movimento_aleatorio_valido(self):
        movimentos_validos = []
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            prox_x, prox_y = self.pos.x + dx, self.pos.y + dy
            if (0 <= prox_x < LARGURA_GRADE and 0 <= prox_y < ALTURA_GRADE and self.labirinto[int(prox_y)][int(prox_x)] == 0):
                movimentos_validos.append(pygame.math.Vector2(prox_x, prox_y))
        return random.choice(movimentos_validos) if movimentos_validos else self.pos
    def mover(self, cobra, dificuldade, outros_fantasmas):
        tempo_atual = pygame.time.get_ticks()
        if self.congelado:
            if tempo_atual > self.tempo_fim_congelamento:
                self.congelado = False
            else:
                return
        velocidade_fantasma = 1 + dificuldade
        self.movimento_ticker += 1
        if self.movimento_ticker < (10 - velocidade_fantasma): return
        self.movimento_ticker = 0
        pos_alvo_final = None
        if self.estado == 'cacando':
            if dificuldade == 1:
                if random.random() < 0.8: self.pos = self.obter_movimento_aleatorio_valido(); return
                else: pos_alvo_final = cobra.corpo[0]
            elif dificuldade == 2:
                if random.random() < 0.25: self.pos = self.obter_movimento_aleatorio_valido(); return
                else: pos_alvo_final = cobra.corpo[0]
            elif dificuldade == 3:
                if self.personalidade == 0:
                    pos_alvo_final = cobra.corpo[0]
                elif self.personalidade == 1:
                    pos_alvo_final = cobra.corpo[0] + cobra.direcao * 4
                elif self.personalidade == 2:
                    alvo = cobra.corpo[0] + cobra.direcao * 2
                    alvo.x += 4
                    pos_alvo_final = alvo
                elif self.personalidade == 3:
                    distancia = self.pos.distance_to(cobra.corpo[0])
                    if distancia > 8:
                        pos_alvo_final = cobra.corpo[0]
                    else:
                        pos_alvo_final = pygame.math.Vector2(1, ALTURA_GRADE - 2) 
                else:
                    alvo = cobra.corpo[0] + cobra.direcao * 2
                    alvo.y += 4
                    pos_alvo_final = alvo
        elif self.estado == 'fugindo':
            pos_alvo_final = random.choice([
                pygame.math.Vector2(1, 1),
                pygame.math.Vector2(LARGURA_GRADE - 2, 1),
                pygame.math.Vector2(1, ALTURA_GRADE - 2),
                pygame.math.Vector2(LARGURA_GRADE - 2, ALTURA_GRADE - 2)
            ])
        elif self.estado == 'comido':
            pos_alvo_final = self.base
            if self.pos == self.base: self.estado = 'cacando'
        if pos_alvo_final:
            self.recalculo_ticker += 1
            limite_recalculo = 5 if dificuldade == 3 else 15
            if not self.caminho or self.recalculo_ticker > limite_recalculo:
                alvo_x = max(0, min(LARGURA_GRADE - 1, int(pos_alvo_final.x)))
                alvo_y = max(0, min(ALTURA_GRADE - 1, int(pos_alvo_final.y)))
                self.caminho = buscar_caminho_bfs(self.labirinto, (int(self.pos.x), int(self.pos.y)), (alvo_x, alvo_y))
                self.recalculo_ticker = 0
            if self.caminho and len(self.caminho) > 1:
                prox_passo_pos = pygame.math.Vector2(self.caminho[1][0], self.caminho[1][1])
                if prox_passo_pos in [f.pos for f in outros_fantasmas if f is not self]: return
                self.pos = prox_passo_pos
                self.caminho.pop(0)
            else: 
                self.caminho = []
class Cobra:
    def __init__(self, labirinto, pos_inicial, portais):
        self.labirinto = labirinto; self.corpo = [pos_inicial.copy()]; self.portais = portais
        self.direcao = pygame.math.Vector2(0, 0); self.crescer = False
        self.buffer_direcao = deque(); self.movimento_ticker = 0
    def mover(self):
        self.movimento_ticker += 1
        if self.movimento_ticker < 4: return 
        self.movimento_ticker = 0
        if self.direcao.length() == 0: return
        if self.buffer_direcao:
            proxima_direcao = self.buffer_direcao.popleft()
            if proxima_direcao * -1 != self.direcao: self.direcao = proxima_direcao
        proxima_cabeca = self.corpo[0] + self.direcao
        pos_tupla = (int(proxima_cabeca.y), int(proxima_cabeca.x))
        if pos_tupla in self.portais: proxima_cabeca.y, proxima_cabeca.x = self.portais[pos_tupla]
        if not (0 <= int(proxima_cabeca.y) < ALTURA_GRADE and 0 <= int(proxima_cabeca.x) < LARGURA_GRADE):
            return
        if self.labirinto[int(proxima_cabeca.y)][int(proxima_cabeca.x)] == 1:
            self.buffer_direcao.clear(); return
        corpo_copia = self.corpo[:-1]
        if self.crescer:
            corpo_copia = self.corpo[:]; self.crescer = False
        self.corpo = [proxima_cabeca] + corpo_copia
    def mudar_direcao(self, nova_direcao):
        if len(self.buffer_direcao) < 2: self.buffer_direcao.append(nova_direcao)
    def desenhar(self, modo_cacador):
        sprites = texturas_cobra_cacada if modo_cacador else texturas_cobra
        if not self.corpo: return
        cabeca = self.corpo[0]
        rect_cabeca = pygame.Rect(cabeca.x * TAMANHO_BLOCO, cabeca.y * TAMANHO_BLOCO, TAMANHO_BLOCO, TAMANHO_BLOCO)
        if self.direcao.y == -1: tela.blit(sprites['cabeca_cima'], rect_cabeca)
        elif self.direcao.y == 1: tela.blit(sprites['cabeca_baixo'], rect_cabeca)
        elif self.direcao.x == -1: tela.blit(sprites['cabeca_esquerda'], rect_cabeca)
        elif self.direcao.x == 1: tela.blit(sprites['cabeca_direita'], rect_cabeca)
        else: tela.blit(sprites['cabeca_cima'], rect_cabeca)
        for i, segmento in enumerate(self.corpo):
            if i == 0: continue
            rect = pygame.Rect(segmento.x * TAMANHO_BLOCO, segmento.y * TAMANHO_BLOCO, TAMANHO_BLOCO, TAMANHO_BLOCO)
            anterior = self.corpo[i - 1]
            if i == len(self.corpo) - 1:
                vetor_cauda = anterior - segmento
                if vetor_cauda.y == -1: tela.blit(sprites['cauda_cima'], rect)
                elif vetor_cauda.y == 1: tela.blit(sprites['cauda_baixo'], rect)
                elif vetor_cauda.x == -1: tela.blit(sprites['cauda_esquerda'], rect)
                elif vetor_cauda.x == 1: tela.blit(sprites['cauda_direita'], rect)
            else:
                proximo = self.corpo[i + 1]
                vetor_anterior = anterior - segmento
                vetor_proximo = proximo - segmento
                if vetor_anterior.x == vetor_proximo.x: tela.blit(sprites['vertical'], rect)
                elif vetor_anterior.y == vetor_proximo.y: tela.blit(sprites['horizontal'], rect)
                else:
                    if (vetor_anterior.y == -1 and vetor_proximo.x == 1) or (vetor_anterior.x == 1 and vetor_proximo.y == -1): tela.blit(sprites['se'], rect)
                    elif (vetor_anterior.y == -1 and vetor_proximo.x == -1) or (vetor_anterior.x == -1 and vetor_proximo.y == -1): tela.blit(sprites['sd'], rect)
                    elif (vetor_anterior.y == 1 and vetor_proximo.x == 1) or (vetor_anterior.x == 1 and vetor_proximo.y == 1): tela.blit(sprites['ie'], rect)
                    elif (vetor_anterior.y == 1 and vetor_proximo.x == -1) or (vetor_anterior.x == -1 and vetor_proximo.y == 1): tela.blit(sprites['id'], rect)
    def solicitar_crescimento(self): self.crescer = True
    def checar_colisao_fatal(self): return self.corpo[0] in self.corpo[1:]
class Comida:
    def __init__(self, labirinto, corpo_cobra):
        self.labirinto = labirinto
        self.pos = None
    def desenhar(self):
        if textura_maca and self.pos: 
            tela.blit(textura_maca, (self.pos.x * TAMANHO_BLOCO, self.pos.y * TAMANHO_BLOCO))
    def reposicionar(self, corpo_cobra, portal_tiles):
        locais_possiveis = []
        for y in range(ALTURA_GRADE):
            for x in range(LARGURA_GRADE):
                pos_tupla = (x, y)
                pos_vector = pygame.math.Vector2(x, y)
                if self.labirinto[y][x] == 0 and pos_vector not in corpo_cobra and pos_tupla not in portal_tiles:
                    locais_possiveis.append(pos_vector)
        if locais_possiveis: self.pos = random.choice(locais_possiveis)
        else: self.pos = pygame.math.Vector2(-1, -1)

def desenhar_elementos(labirinto, cobra, comida, fantasmas, pontuacao, dificuldade, macas_para_cacar, modo_cacador, mostrar_ui, tempo_fim_cacador, vidas, powerups):
    for y, linha in enumerate(labirinto):
        for x, celula in enumerate(linha):
            if celula == 1:
                textura = escolher_textura_parede(labirinto, x, y)
                if textura:
                    tela.blit(textura, (x * TAMANHO_BLOCO, y * TAMANHO_BLOCO))
    cobra.desenhar(modo_cacador)
    comida.desenhar()
    for powerup in powerups:
        if powerup:
            powerup.desenhar(tela)
    for fantasma in fantasmas:
        fantasma.desenhar(tempo_fim_cacador)
    if mostrar_ui:
        altura_barra_ui = 40
        barra_ui = pygame.Surface((LARGURA_TELA, altura_barra_ui), pygame.SRCALPHA)
        barra_ui.fill((20, 20, 20, 200))
        tela.blit(barra_ui, (0, 0))
        
        texto_placar = fonte_ui.render(f"Pontos: {pontuacao}", True, BRANCO_TEXTO)
        tela.blit(texto_placar, (10, 8))
        
        if modo_cacador:
            texto_cacada = fonte_ui.render("MODO CACADA!", True, AMARELO_AVISO)
        else:
            texto_cacada = fonte_ui.render(f"Caçada em: {macas_para_cacar} maçãs", True, BRANCO_TEXTO)
        rect_cacada = texto_cacada.get_rect(center=(LARGURA_TELA / 2, altura_barra_ui / 2))
        tela.blit(texto_cacada, rect_cacada)
        
        pos_x_vidas = LARGURA_TELA - 20
        if textura_vida:
            for i in range(vidas):
                rect_vida = textura_vida.get_rect(right=pos_x_vidas - (i * 35), centery=altura_barra_ui/2)
                tela.blit(textura_vida, rect_vida)
                if i == vidas - 1:
                    pos_x_vidas = rect_vida.left
        
def desenhar_menu_pausa():
    filtro = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
    filtro.fill((0, 0, 0, 170))
    tela.blit(filtro, (0, 0))
    largura_botao, altura_botao = 200, 50
    btn_voltar = pygame.Rect(LARGURA_TELA / 2 - largura_botao / 2, ALTURA_TELA / 2 - 80, largura_botao, altura_botao)
    btn_reiniciar = pygame.Rect(LARGURA_TELA / 2 - largura_botao / 2, ALTURA_TELA / 2, largura_botao, altura_botao)
    btn_sair = pygame.Rect(LARGURA_TELA / 2 - largura_botao / 2, ALTURA_TELA / 2 + 80, largura_botao, altura_botao)
    botoes = {'voltar': btn_voltar, 'reiniciar': btn_reiniciar, 'sair': btn_sair}
    for nome, rect in botoes.items():
        pygame.draw.rect(tela, (60, 60, 60), rect, border_radius=10)
        texto_surf = fonte_menu.render(nome.capitalize(), True, BRANCO_TEXTO)
        texto_rect = texto_surf.get_rect(center=rect.center)
        tela.blit(texto_surf, texto_rect)
    return botoes

def desenhar_tela_game_over(pontuacao, recorde, macas_comidas):
    filtro = pygame.Surface((LARGURA_TELA, ALTURA_TELA), pygame.SRCALPHA)
    filtro.fill((0, 0, 0, 180))
    tela.blit(filtro, (0, 0))
    texto_go = fonte_game_over.render("GAME OVER", True, BRANCO_TEXTO)
    rect_go = texto_go.get_rect(center=(LARGURA_TELA / 2, ALTURA_TELA / 2 - 100))
    tela.blit(texto_go, rect_go)
    
    texto_pontos = fonte_placar.render(f"Sua pontuacao: {pontuacao}", True, BRANCO_TEXTO)
    rect_pontos = texto_pontos.get_rect(center=(LARGURA_TELA / 2, ALTURA_TELA / 2 - 40))
    tela.blit(texto_pontos, rect_pontos)

    texto_macas = fonte_placar.render(f"Maçãs comidas: {macas_comidas}", True, BRANCO_TEXTO)
    rect_macas = texto_macas.get_rect(center=(LARGURA_TELA / 2, ALTURA_TELA / 2))
    tela.blit(texto_macas, rect_macas)
    
    texto_recorde = fonte_placar.render(f"Recorde: {recorde}", True, AMARELO_AVISO)
    rect_recorde = texto_recorde.get_rect(center=(LARGURA_TELA / 2, ALTURA_TELA / 2 + 40))
    tela.blit(texto_recorde, rect_recorde)
    
    texto_restart = fonte_placar.render("Aperte ESPACO para voltar ao Menu", True, AMARELO_AVISO)
    rect_restart = texto_restart.get_rect(center=(LARGURA_TELA / 2, ALTURA_TELA / 2 + 100))
    tela.blit(texto_restart, rect_restart)

def setup_jogo():
    labirinto, pos_cobra, portais, pos_fantasmas = gerar_labirinto_hibrido()
    portal_tiles = set()
    for y in range(ALTURA_GRADE):
        for x in range(LARGURA_GRADE):
            if x < 2 or x > LARGURA_GRADE - 3 or y < 2 or y > ALTURA_GRADE - 3:
                if labirinto[y][x] == 0:
                    portal_tiles.add((x, y))

    comida_obj = Comida(labirinto, [pos_cobra])
    comida_obj.reposicionar([pos_cobra], portal_tiles)

    powerup_congelar_obj = PowerUp(labirinto, textura_powerup_congelar) if textura_powerup_congelar else None
    powerup_vida_obj = PowerUp(labirinto, textura_vida) if textura_vida else None
    
    game_vars = {
        "labirinto_atual": labirinto,
        "cobra": Cobra(labirinto, pos_cobra, portais),
        "comida": comida_obj,
        "fantasmas": [Fantasma(pos, labirinto, CORES_FANTASMAS[i % len(CORES_FANTASMAS)], i) for i, pos in enumerate(pos_fantasmas)],
        "pontuacao": 0,
        "macas_comidas": 0,
        "dificuldade_fantasma": 1,
        "modo_cacador": False,
        "tempo_fim_cacador": 0,
        "jogo_pausado": False,
        "mostrar_ui": True,
        "vidas": 3,
        "pos_inicial_cobra": pos_cobra.copy(),
        "powerup_congelar": powerup_congelar_obj,
        "powerup_vida": powerup_vida_obj,
        "tempo_proximo_powerup_congelar": pygame.time.get_ticks() + INTERVALO_POWERUP,
        "tempo_proximo_powerup_vida": pygame.time.get_ticks() + INTERVALO_POWERUP_VIDA,
        "portal_tiles": portal_tiles,
    }
    return game_vars

def rodar_jogo(game_vars):
    global high_score
    cobra = game_vars["cobra"]
    fantasmas = game_vars["fantasmas"]
    comida = game_vars["comida"]
    powerup_congelar = game_vars["powerup_congelar"]
    powerup_vida = game_vars["powerup_vida"]
    
    game_vars['mostrar_ui'] = pygame.key.get_pressed()[pygame.K_TAB]
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return ESTADO_SAIR, game_vars
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                game_vars["jogo_pausado"] = not game_vars["jogo_pausado"]
            if not game_vars["jogo_pausado"]:
                nova_direcao = None
                if event.key in (pygame.K_UP, pygame.K_w): nova_direcao = pygame.math.Vector2(0, -1)
                if event.key in (pygame.K_DOWN, pygame.K_s): nova_direcao = pygame.math.Vector2(0, 1)
                if event.key in (pygame.K_LEFT, pygame.K_a): nova_direcao = pygame.math.Vector2(-1, 0)
                if event.key in (pygame.K_RIGHT, pygame.K_d): nova_direcao = pygame.math.Vector2(1, 0)
                if nova_direcao:
                    if cobra.direcao.length() == 0:
                        cobra.direcao = nova_direcao
                    else:
                        cobra.mudar_direcao(nova_direcao)
        if event.type == pygame.MOUSEBUTTONDOWN and game_vars["jogo_pausado"]:
            botoes_pausa = desenhar_menu_pausa()
            if botoes_pausa['voltar'].collidepoint(event.pos): game_vars["jogo_pausado"] = False
            if botoes_pausa['reiniciar'].collidepoint(event.pos):
                return ESTADO_JOGANDO, setup_jogo()
            if botoes_pausa['sair'].collidepoint(event.pos):
                return ESTADO_MENU, game_vars
    if not game_vars["jogo_pausado"]:
        tempo_atual = pygame.time.get_ticks()
        
        if powerup_congelar and not powerup_congelar.ativo and tempo_atual > game_vars["tempo_proximo_powerup_congelar"]:
            powerup_congelar.ativar(cobra.corpo, game_vars["portal_tiles"])
        if powerup_vida and not powerup_vida.ativo and tempo_atual > game_vars["tempo_proximo_powerup_vida"]:
            powerup_vida.ativar(cobra.corpo, game_vars["portal_tiles"])

        cobra.mover()
        for fantasma in fantasmas:
            fantasma.mover(cobra, game_vars["dificuldade_fantasma"], fantasmas)
        
        if game_vars["modo_cacador"] and tempo_atual > game_vars["tempo_fim_cacador"]:
            game_vars["modo_cacador"] = False
            for fantasma in fantasmas:
                if fantasma.estado != 'comido': fantasma.estado = 'cacando'
        
        nova_dificuldade = 1 + (game_vars["pontuacao"] // 100)
        game_vars["dificuldade_fantasma"] = min(3, nova_dificuldade)
        
        morreu = False
        if cobra.checar_colisao_fatal():
            morreu = True
        for fantasma in fantasmas:
            if not fantasma.congelado and fantasma.pos == cobra.corpo[0]:
                if game_vars["modo_cacador"] and fantasma.estado == 'fugindo':
                    fantasma.estado = 'comido'
                    game_vars["pontuacao"] += 50
                elif fantasma.estado == 'cacando':
                    morreu = True
        
        if morreu:
            game_vars["vidas"] -= 1
            if game_vars["vidas"] > 0:
                cobra.corpo = [game_vars["pos_inicial_cobra"].copy()]
                cobra.direcao = pygame.math.Vector2(0, 0)
                pygame.time.delay(1000)
            else:
                if game_vars["pontuacao"] > high_score:
                    high_score = game_vars["pontuacao"]
                    salvar_recorde(high_score)
                return ESTADO_GAME_OVER, game_vars

        if not morreu and comida.pos and cobra.corpo[0] == comida.pos:
            cobra.solicitar_crescimento()
            game_vars["pontuacao"] += 10
            game_vars["macas_comidas"] += 1
            comida.reposicionar(cobra.corpo, game_vars["portal_tiles"])
            macas_comidas_total = len(cobra.corpo) - 1
            if macas_comidas_total > 0 and macas_comidas_total % 10 == 0:
                game_vars["modo_cacador"] = True
                game_vars["tempo_fim_cacador"] = tempo_atual + DURACAO_MODO_CACADOR
                for fantasma in fantasmas:
                    if fantasma.estado != 'comido':
                        fantasma.estado = 'fugindo'
                        fantasma.caminho = []
        
        if powerup_congelar and powerup_congelar.ativo and cobra.corpo[0] == powerup_congelar.pos:
            for fantasma in fantasmas:
                fantasma.congelar()
            powerup_congelar.desativar()
            game_vars["tempo_proximo_powerup_congelar"] = tempo_atual + INTERVALO_POWERUP
            game_vars["pontuacao"] += 25
            
        if powerup_vida and powerup_vida.ativo and cobra.corpo[0] == powerup_vida.pos:
            if game_vars["vidas"] < 3:
                game_vars["vidas"] += 1
                game_vars["pontuacao"] += 15
            powerup_vida.desativar()
            game_vars["tempo_proximo_powerup_vida"] = tempo_atual + INTERVALO_POWERUP_VIDA

    tela.fill(BRANCO_FUNDO)
    macas_para_cacar = 10 - ((len(cobra.corpo) - 1) % 10) if len(cobra.corpo) > 1 else 10
    desenhar_elementos(game_vars["labirinto_atual"], cobra, comida, fantasmas, game_vars["pontuacao"],
                       game_vars["dificuldade_fantasma"], macas_para_cacar, game_vars["modo_cacador"],
                       game_vars["mostrar_ui"], game_vars["tempo_fim_cacador"], game_vars["vidas"], 
                       [game_vars["powerup_congelar"], game_vars["powerup_vida"]])
    
    if game_vars["jogo_pausado"]:
        desenhar_menu_pausa()
    return ESTADO_JOGANDO, game_vars

def desenhar_tela_texto(titulo, texto_linhas, texto_botao_voltar="Pressione ESC ou clique para Voltar", use_image_for_content=False, image_asset=None):
    tela.fill(BRANCO_FUNDO)
    if use_image_for_content and image_asset:
        tela.blit(image_asset, (0, 0))
    else:
        texto_titulo_surf = fonte_menu.render(titulo, True, VERDE_COBRA)
        rect_titulo = texto_titulo_surf.get_rect(center=(LARGURA_TELA / 2, ALTURA_TELA * 0.2))
        tela.blit(texto_titulo_surf, rect_titulo)
        y_pos = ALTURA_TELA * 0.35
        for linha in texto_linhas:
            texto_linha_surf = fonte_texto_conteudo.render(linha, True, BRANCO_TEXTO)
            rect_linha = texto_linha_surf.get_rect(center=(LARGURA_TELA / 2, y_pos))
            tela.blit(texto_linha_surf, rect_linha)
            y_pos += 30
    texto_voltar_surf = fonte_placar.render(texto_botao_voltar, True, AMARELO_AVISO)
    rect_voltar = texto_voltar_surf.get_rect(center=(LARGURA_TELA / 2, ALTURA_TELA * 0.85))
    tela.blit(texto_voltar_surf, rect_voltar)

def gerenciar_tela_conteudo(titulo, texto_linhas, use_image=False, image_asset=None):
    desenhar_tela_texto(titulo, texto_linhas, use_image_for_content=use_image, image_asset=image_asset)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return ESTADO_SAIR
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return ESTADO_MENU
        if event.type == pygame.MOUSEBUTTONDOWN:
            return ESTADO_MENU
    return None

def gerenciar_tela_menu():
    tela.fill(BRANCO_FUNDO)
    if textura_logo:
        rect_logo = textura_logo.get_rect(center=(LARGURA_TELA / 2, ALTURA_TELA * 0.25))
        tela.blit(textura_logo, rect_logo)
    else: 
        texto_titulo = fonte_menu.render("SnackPack", True, VERDE_COBRA)
        rect_titulo = texto_titulo.get_rect(center=(LARGURA_TELA / 2, ALTURA_TELA * 0.2))
        tela.blit(texto_titulo, rect_titulo)
    botoes = {
        'Jogar': {'pos': (LARGURA_TELA / 2, ALTURA_TELA * 0.45), 'estado': ESTADO_JOGANDO},
        'Ajuda': {'pos': (LARGURA_TELA / 2, ALTURA_TELA * 0.55), 'estado': ESTADO_AJUDA},
        'Sobre': {'pos': (LARGURA_TELA / 2, ALTURA_TELA * 0.65), 'estado': ESTADO_SOBRE},
        'Créditos': {'pos': (LARGURA_TELA / 2, ALTURA_TELA * 0.75), 'estado': ESTADO_CREDITOS}
    }
    texto_recorde_surf = fonte_ui.render(f"Recorde: {high_score}", True, AMARELO_AVISO)
    rect_recorde = texto_recorde_surf.get_rect(center=(LARGURA_TELA/2, ALTURA_TELA * 0.9))
    tela.blit(texto_recorde_surf, rect_recorde)
    
    proximo_estado = ESTADO_MENU
    mouse_pos = pygame.mouse.get_pos()
    for texto, info in botoes.items():
        texto_surf = fonte_placar.render(texto, True, BRANCO_TEXTO)
        rect = texto_surf.get_rect(center=info['pos'])
        if rect.collidepoint(mouse_pos):
            texto_surf = fonte_placar.render(texto, True, AMARELO_AVISO)
        tela.blit(texto_surf, rect)
        botoes[texto]['rect'] = rect
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            return ESTADO_SAIR
        if event.type == pygame.MOUSEBUTTONDOWN:
            for texto, info in botoes.items():
                if info['rect'].collidepoint(event.pos):
                    return info['estado']
    return proximo_estado

async def main():
    carregar_recorde()
    recursos_carregados = carregar_todos_os_recursos()
    
    if not recursos_carregados:
        game_state = ESTADO_ERRO
    else:
        game_state = ESTADO_MENU
        
    game_vars = None
    
    while game_state != ESTADO_SAIR:
        if game_state == ESTADO_ERRO:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    game_state = ESTADO_SAIR
            
            tela.fill(PRETO)
            texto_erro1 = fonte_menu.render("Erro ao Carregar Recursos", True, VERMELHO_ERRO)
            texto_erro2 = fonte_placar.render("Verifique a pasta 'PyTexture2'", True, BRANCO_TEXTO)
            texto_erro3 = fonte_placar.render(f"Detalhe: {erro_carregamento}", True, BRANCO_TEXTO)
            texto_erro4 = fonte_placar.render("Pressione ESC para sair", True, AMARELO_AVISO)
            
            tela.blit(texto_erro1, texto_erro1.get_rect(center=(LARGURA_TELA/2, ALTURA_TELA/2 - 60)))
            tela.blit(texto_erro2, texto_erro2.get_rect(center=(LARGURA_TELA/2, ALTURA_TELA/2)))
            tela.blit(texto_erro3, texto_erro3.get_rect(center=(LARGURA_TELA/2, ALTURA_TELA/2 + 40)))
            tela.blit(texto_erro4, texto_erro4.get_rect(center=(LARGURA_TELA/2, ALTURA_TELA/2 + 100)))

        elif game_state == ESTADO_MENU:
            proximo_estado = gerenciar_tela_menu()
            if proximo_estado == ESTADO_JOGANDO:
                game_vars = setup_jogo()
            game_state = proximo_estado
        elif game_state == ESTADO_AJUDA:
            proximo_estado = gerenciar_tela_conteudo("Ajuda", [], use_image=True, image_asset=textura_ajuda)
            if proximo_estado: game_state = proximo_estado
        elif game_state == ESTADO_SOBRE:
            proximo_estado = gerenciar_tela_conteudo("Sobre", TEXTO_SOBRE)
            if proximo_estado: game_state = proximo_estado
        elif game_state == ESTADO_CREDITOS:
            proximo_estado = gerenciar_tela_conteudo("Créditos", TEXTO_CREDITOS)
            if proximo_estado: game_state = proximo_estado
        elif game_state == ESTADO_JOGANDO:
            novo_estado, game_vars_atualizadas = rodar_jogo(game_vars)
            game_state = novo_estado
            game_vars = game_vars_atualizadas
        elif game_state == ESTADO_GAME_OVER:
            desenhar_tela_game_over(game_vars["pontuacao"], high_score, game_vars["macas_comidas"])
            pygame.display.update() # <--- CORREÇÃO ADICIONADA AQUI
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_state = ESTADO_SAIR
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_ESCAPE:
                        carregar_recorde()
                        game_state = ESTADO_MENU
        
        pygame.display.update()
        await asyncio.sleep(1 / 60)
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":

    asyncio.run(main())
