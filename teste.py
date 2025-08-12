import pygame
import random
import sys

# ==============================================================================
# CLASSE DOS ITENS DO JOGO
# ==============================================================================

# A classe define como um item (chave, bota, etc.) se comporta.
# É como uma "planta" para criar todos os itens que o jogador pode coletar.
class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, tipo, imagem):
        super().__init__()
        self.tipo = tipo
        self.imagem = imagem
        self.rect = self.imagem.get_rect(center=(x, y))


# ==============================================================================
# INICIALIZAÇÃO E CONFIGURAÇÕES GERAIS
# ==============================================================================

# Inicia o Pygame e o módulo de fontes
pygame.init()
pygame.font.init()

# Prepara a janela do jogo em tela cheia
info = pygame.display.Info()
largura_tela = info.current_w
altura_tela = info.current_h
tela = pygame.display.set_mode((largura_tela, altura_tela))

# Define o nome que aparece na barra da janela
pygame.display.set_caption("CIn Saída!")

# Cria um relógio que vai controlar a velocidade do jogo (FPS)
relogio = pygame.time.Clock()


# ==============================================================================
# CORES E FONTES USADAS NO JOGO
# ==============================================================================

COR_BRANCA = (255, 255, 255)
COR_AMARELA = (255, 255, 0)
COR_TITULO = (220, 230, 255)
COR_CONTORNO = (10, 10, 10)

# Carrega as fontes em diferentes tamanhos
fonte_titulo = pygame.font.SysFont('Consolas', 100, bold=True)
fonte_menu = pygame.font.SysFont('Consolas', 65, bold=True)
fonte_dificuldade = pygame.font.SysFont('Consolas', 45, bold=True)
fonte_hud = pygame.font.SysFont('Consolas', 30, bold=True)
fonte_mensagem_central = pygame.font.SysFont('Consolas', 40, bold=True)


# ==============================================================================
# CARREGAMENTO DAS IMAGENS
# ==============================================================================

print("Carregando imagens...")

mapa_img_original = pygame.image.load("mapa.jpg").convert()
mapa_colisao_img = pygame.image.load("mapa_colisao.png").convert()
mapa_colisao_img.set_colorkey((255, 255, 255))

personagem_img_original = pygame.image.load("perso.webp").convert_alpha()
personagem_img = pygame.transform.scale(personagem_img_original, (64, 64))

chave_img = pygame.transform.scale(pygame.image.load("chave.png").convert_alpha(), (32, 32))
porta_img = pygame.transform.scale(pygame.image.load("porta.png").convert_alpha(), (64, 64))
velocidade_img = pygame.transform.scale(pygame.image.load("bota.png").convert_alpha(), (32, 32))
tempo_img = pygame.transform.scale(pygame.image.load("relogio.png").convert_alpha(), (32, 32))

escala_blur = 0.05
mapa_pequeno = pygame.transform.smoothscale(
    mapa_img_original,
    (int(largura_tela * escala_blur), int(altura_tela * escala_blur))
)
mapa_fundo_blur = pygame.transform.scale(mapa_pequeno, (largura_tela, altura_tela))

print("Imagens carregadas com sucesso!")


# ==============================================================================
# MÁSCARAS DE COLISÃO
# ==============================================================================

paredes = pygame.mask.from_surface(mapa_colisao_img)
colisao_personagem = pygame.mask.from_surface(personagem_img)


# ==============================================================================
# VARIÁVEIS GLOBAIS DA PARTIDA
# ==============================================================================

personagem_rect = pygame.Rect(0, 0, 0, 0)
velocidade_personagem = 0
tempo_restante = 0
ultimo_evento_tempo = 0
vitoria = False
derrota = False

total_chaves = 3
coletaveis_velocidade = 5
coletaveis_tempo = 4
chaves_coletadas = 0
botas_coletadas = 0
relogios_coletados = 0
chaves_encontradas = False
lista_de_itens = []
porta_saida = None

mensagem_chaves = False
tempo_mensagem_inicio = 0
duracao_mensagem = 5000

dificuldade_selecionada = 'medio'


# ==============================================================================
# FUNÇÃO PARA INICIAR UMA NOVA PARTIDA
# ==============================================================================

def iniciar_novo_jogo(dificuldade):
    """Prepara ou "reseta" todas as variáveis para começar a jogar."""
    global personagem_rect, velocidade_personagem, tempo_restante, ultimo_evento_tempo
    global vitoria, derrota, chaves_coletadas, botas_coletadas, relogios_coletados
    global chaves_encontradas, lista_de_itens, porta_saida, mensagem_chaves, tempo_mensagem_inicio

    print(f"\n--- INICIANDO NOVA PARTIDA NA DIFICULDADE: {dificuldade.upper()} ---")

    chaves_coletadas, botas_coletadas, relogios_coletados = 0, 0, 0
    chaves_encontradas, vitoria, derrota = False, False, False
    velocidade_personagem = 4
    lista_de_itens = []
    
    if dificuldade == 'facil': tempo_restante = 480
    elif dificuldade == 'medio': tempo_restante = 360
    elif dificuldade == 'dificil': tempo_restante = 240
    
    ultimo_evento_tempo = pygame.time.get_ticks()
    mensagem_chaves, tempo_mensagem_inicio = False, 0
    
    largura_mapa, altura_mapa = mapa_img_original.get_size()
    posicoes_validas = []
    passo, w_pers, h_pers = 24, personagem_img.get_width(), personagem_img.get_height()

    for x in range(0, largura_mapa, passo):
        for y in range(0, altura_mapa, passo):
            pos_x_canto, pos_y_canto = x - w_pers // 2, y - h_pers // 2
            if not paredes.overlap(colisao_personagem, (pos_x_canto, pos_y_canto)):
                posicoes_validas.append((x, y))
    
    def encontrar_posicao_valida():
        if not posicoes_validas: return (largura_mapa // 2, altura_mapa // 2)
        pos = random.choice(posicoes_validas)
        posicoes_validas.remove(pos)
        return pos

    personagem_rect = personagem_img.get_rect(center=encontrar_posicao_valida())
    
    itens_a_gerar = []
    for _ in range(total_chaves):
        itens_a_gerar.append(('chave', chave_img))
    for _ in range(coletaveis_velocidade):
        itens_a_gerar.append(('velocidade', velocidade_img))
    for _ in range(coletaveis_tempo):
        itens_a_gerar.append(('tempo', tempo_img))
    
    random.shuffle(itens_a_gerar)

    for tipo, img in itens_a_gerar:
        ### CORREÇÃO ###
        # Primeiro, pegamos a posição (x, y) e depois criamos o item.
        # Antes, a tupla (x,y) estava sendo passada inteira como um único argumento.
        x, y = encontrar_posicao_valida()
        lista_de_itens.append(Item(x, y, tipo, img))

    x_porta, y_porta = encontrar_posicao_valida()
    porta_saida = Item(x_porta, y_porta, 'porta', porta_img)
    
    print("--- GERAÇÃO CONCLUÍDA ---")


# ==============================================================================
# FUNÇÕES DE LÓGICA E DESENHO
# ==============================================================================

def desenhar_texto_com_contorno(texto, fonte, cor_texto, centro_pos):
    """Função auxiliar para desenhar um texto bonito com contorno."""
    offset_contorno = 3
    pontos = [(-offset_contorno, -offset_contorno), (offset_contorno, -offset_contorno),
              (-offset_contorno, offset_contorno), (offset_contorno, offset_contorno),
              (0, -offset_contorno), (0, offset_contorno), (-offset_contorno, 0), (offset_contorno, 0)]
    
    texto_surf_contorno = fonte.render(texto, True, COR_CONTORNO)
    for dx, dy in pontos:
        rect_contorno = texto_surf_contorno.get_rect(center=(centro_pos[0] + dx, centro_pos[1] + dy))
        tela.blit(texto_surf_contorno, rect_contorno)

    texto_surf_principal = fonte.render(texto, True, cor_texto)
    rect_principal = texto_surf_principal.get_rect(center=centro_pos)
    tela.blit(texto_surf_principal, rect_principal)


def desenhar_menu():
    """Desenha toda a tela do menu principal."""
    tela.blit(mapa_fundo_blur, (0, 0))

    desenhar_texto_com_contorno("CIn Saída!", fonte_titulo, COR_TITULO, (largura_tela / 2, altura_tela * 0.25))
    desenhar_texto_com_contorno("Dificuldade", fonte_dificuldade, COR_BRANCA, (largura_tela / 2, altura_tela * 0.45))
    
    mouse_pos = pygame.mouse.get_pos()
    
    pos_y_dificuldade = altura_tela * 0.53
    espacamento_dificuldade = 200
    rect_facil = fonte_dificuldade.render("Fácil", True, COR_BRANCA).get_rect(center=(largura_tela/2 - espacamento_dificuldade, pos_y_dificuldade))
    rect_medio = fonte_dificuldade.render("Médio", True, COR_BRANCA).get_rect(center=(largura_tela/2, pos_y_dificuldade))
    rect_dificil = fonte_dificuldade.render("Difícil", True, COR_BRANCA).get_rect(center=(largura_tela/2 + espacamento_dificuldade, pos_y_dificuldade))
    
    cor_facil = COR_AMARELA if dificuldade_selecionada == 'facil' else COR_BRANCA
    cor_medio = COR_AMARELA if dificuldade_selecionada == 'medio' else COR_BRANCA
    cor_dificil = COR_AMARELA if dificuldade_selecionada == 'dificil' else COR_BRANCA
    
    desenhar_texto_com_contorno("Fácil", fonte_dificuldade, cor_facil, rect_facil.center)
    desenhar_texto_com_contorno("Médio", fonte_dificuldade, cor_medio, rect_medio.center)
    desenhar_texto_com_contorno("Difícil", fonte_dificuldade, cor_dificil, rect_dificil.center)

    pos_y_botoes = altura_tela * 0.75
    rect_comecar = fonte_menu.render("Começar", True, COR_BRANCA).get_rect(center=(largura_tela / 2, pos_y_botoes))
    cor_comecar = COR_AMARELA if rect_comecar.collidepoint(mouse_pos) else COR_BRANCA
    desenhar_texto_com_contorno("Começar", fonte_menu, cor_comecar, rect_comecar.center)
    
    rect_sair = fonte_menu.render("Sair", True, COR_BRANCA).get_rect(center=(largura_tela / 2, pos_y_botoes + 90))
    cor_sair = COR_AMARELA if rect_sair.collidepoint(mouse_pos) else COR_BRANCA
    desenhar_texto_com_contorno("Sair", fonte_menu, cor_sair, rect_sair.center)
    
    return rect_comecar, rect_sair, rect_facil, rect_medio, rect_dificil


def processar_movimento_jogador():
    """Lida com as teclas de movimento e a colisão com as paredes."""
    global personagem_rect
    
    pos_anterior = personagem_rect.copy()
    teclas = pygame.key.get_pressed()

    if teclas[pygame.K_LEFT] or teclas[pygame.K_a]: personagem_rect.x -= velocidade_personagem
    if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]: personagem_rect.x += velocidade_personagem
    if teclas[pygame.K_UP] or teclas[pygame.K_w]: personagem_rect.y -= velocidade_personagem
    if teclas[pygame.K_DOWN] or teclas[pygame.K_s]: personagem_rect.y += velocidade_personagem
    
    if paredes.overlap(colisao_personagem, (personagem_rect.x, personagem_rect.y)):
        personagem_rect = pos_anterior


def processar_coleta_itens():
    """Verifica se o jogador colidiu com algum item e aplica o efeito."""
    global chaves_coletadas, chaves_encontradas, mensagem_chaves, tempo_mensagem_inicio
    global botas_coletadas, velocidade_personagem, relogios_coletados, tempo_restante
    
    itens_para_remover = []
    for item in lista_de_itens:
        if personagem_rect.colliderect(item.rect):
            if item.tipo == 'chave':
                chaves_coletadas += 1
                if chaves_coletadas == total_chaves:
                    chaves_encontradas = True
                    mensagem_chaves = True
                    tempo_mensagem_inicio = pygame.time.get_ticks()
            elif item.tipo == 'velocidade':
                velocidade_personagem *= 1.2
                botas_coletadas += 1
            elif item.tipo == 'tempo':
                tempo_restante += 30
                relogios_coletados += 1
            
            itens_para_remover.append(item)
    
    for item in itens_para_remover:
        lista_de_itens.remove(item)


def atualizar_status_partida():
    """Verifica condições de vitória, derrota e atualiza o cronômetro."""
    global vitoria, derrota, tempo_restante, ultimo_evento_tempo
    
    if chaves_encontradas and porta_saida and personagem_rect.colliderect(porta_saida.rect):
        vitoria = True
    
    if tempo_restante <= 0:
        tempo_restante = 0
        derrota = True
    
    if pygame.time.get_ticks() - ultimo_evento_tempo >= 1000:
        tempo_restante -= 1
        ultimo_evento_tempo = pygame.time.get_ticks()


def desenhar_cena_jogo():
    """Desenha todos os elementos da cena do jogo (mapa, itens, jogador, HUD)."""
    tela.fill((0, 0, 0))
    
    camera_x = max(0, min(personagem_rect.centerx - largura_tela // 2, mapa_img_original.get_width() - largura_tela))
    camera_y = max(0, min(personagem_rect.centery - altura_tela // 2, mapa_img_original.get_height() - altura_tela))
    
    tela.blit(mapa_img_original, (-camera_x, -camera_y))
    
    for item in lista_de_itens:
        tela.blit(item.imagem, item.rect.move(-camera_x, -camera_y))

    if chaves_encontradas and porta_saida:
        tela.blit(porta_img, porta_saida.rect.move(-camera_x, -camera_y))

    tela.blit(personagem_img, personagem_rect.move(-camera_x, -camera_y))

    # Desenho do HUD
    hud_bg_color = (0, 0, 0, 150)
    textos_hud = [f"Chaves: {chaves_coletadas}/{total_chaves}",
                  f"Botas: {botas_coletadas}/{coletaveis_velocidade}",
                  f"Relógios: {relogios_coletados}/{coletaveis_tempo}"]
    for i, texto in enumerate(textos_hud):
        superficie = fonte_hud.render(texto, True, COR_AMARELA)
        fundo = pygame.Surface((superficie.get_width() + 10, superficie.get_height()), pygame.SRCALPHA)
        fundo.fill(hud_bg_color)
        tela.blit(fundo, (5, 10 + i * 35))
        tela.blit(superficie, (10, 10 + i * 35))
    
    minutos, segundos = divmod(int(tempo_restante), 60)
    cronometro_texto = f"{minutos:02d}:{segundos:02d}"
    superficie_cronometro = fonte_hud.render(cronometro_texto, True, (255, 0, 0))
    pos_cronometro = superficie_cronometro.get_rect(topright=(largura_tela - 10, 10))
    fundo_cronometro = pygame.Surface((pos_cronometro.width + 10, pos_cronometro.height), pygame.SRCALPHA)
    fundo_cronometro.fill(hud_bg_color)
    tela.blit(fundo_cronometro, fundo_cronometro.get_rect(topright=(largura_tela - 5, 10)))
    tela.blit(superficie_cronometro, pos_cronometro)
    
    if mensagem_chaves and pygame.time.get_ticks() - tempo_mensagem_inicio < duracao_mensagem:
        texto_msg = "Você tem as chaves! Encontre a saída!"
        desenhar_texto_com_contorno(texto_msg, fonte_mensagem_central, COR_AMARELA, (largura_tela / 2, 40))

    if vitoria: desenhar_tela_final("VOCÊ VENCEU!! :D", (255, 215, 0))
    elif derrota: desenhar_tela_final("Você perdeu... :(", (170, 0, 0))


def desenhar_tela_final(texto, cor):
    """Desenha uma camada escura sobre o jogo e exibe a mensagem de fim de jogo."""
    fundo_final = pygame.Surface((largura_tela, altura_tela), pygame.SRCALPHA)
    fundo_final.fill((0, 0, 0, 180))
    tela.blit(fundo_final, (0, 0))
    
    fonte_final = pygame.font.SysFont('Consolas', 100, bold=True)
    superficie_final = fonte_final.render(texto, True, cor)
    pos_final = superficie_final.get_rect(center=(largura_tela / 2, altura_tela / 2))
    tela.blit(superficie_final, pos_final)


def loop_jogo():
    """Orquestra todas as funções que rodam durante a partida."""
    if not vitoria and not derrota:
        processar_movimento_jogador()
        processar_coleta_itens()
        atualizar_status_partida()
    
    desenhar_cena_jogo()


# ==============================================================================
# LOOP PRINCIPAL DO PROGRAMA (O CORAÇÃO DO JOGO)
# ==============================================================================

def main():
    """Função principal que controla o fluxo do jogo, como o menu e a partida."""
    global dificuldade_selecionada
    
    estado_jogo = 'menu'
    running = True

    while running:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                running = False
            
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    if estado_jogo == 'jogando':
                        estado_jogo = 'menu'
                    else:
                        running = False
            
            if estado_jogo == 'menu' and evento.type == pygame.MOUSEBUTTONDOWN:
                rect_comecar, rect_sair, rect_facil, rect_medio, rect_dificil = desenhar_menu()
                
                if rect_facil.collidepoint(evento.pos): dificuldade_selecionada = 'facil'
                if rect_medio.collidepoint(evento.pos): dificuldade_selecionada = 'medio'
                if rect_dificil.collidepoint(evento.pos): dificuldade_selecionada = 'dificil'
                
                if rect_comecar.collidepoint(evento.pos):
                    iniciar_novo_jogo(dificuldade_selecionada)
                    estado_jogo = 'jogando'
                if rect_sair.collidepoint(evento.pos):
                    running = False

        if estado_jogo == 'menu':
            desenhar_menu()
        elif estado_jogo == 'jogando':
            loop_jogo()

        pygame.display.flip()
        relogio.tick(60)

    pygame.quit()
    sys.exit()


# Esta linha garante que a função main() só será chamada quando o script for executado diretamente
if __name__ == '__main__':
    main()