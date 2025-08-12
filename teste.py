import pygame
import random

# ==============================================================================
# CLASSE DO ITEM (Juntamos tudo em um só arquivo)
# ==============================================================================
class Item(pygame.sprite.Sprite):
    """
    Representa um item coletável no jogo, como uma chave, bota ou relógio.
    """
    def __init__(self, x, y, tipo, imagem):
        super().__init__()
        self.tipo = tipo
        self.imagem = imagem
        self.rect = self.imagem.get_rect(center=(x, y))

# ==============================================================================
# INICIALIZAÇÃO E CONFIGURAÇÕES
# ==============================================================================
pygame.init()
pygame.font.init()

# Configurações da janela (tela cheia)
info = pygame.display.Info()
largura_tela = info.current_w
altura_tela = info.current_h
tela = pygame.display.set_mode((largura_tela, altura_tela))
pygame.display.set_caption("CIn Saída!")

# Configurações da fonte do HUD
fonte_hud = pygame.font.SysFont('Consolas', 30, bold=True)

# ==============================================================================
# CARREGAMENTO DE IMAGENS E DADOS
# ==============================================================================
print("Carregando imagens...")
# Certifique-se de que os nomes dos arquivos do mapa e da colisão estão corretos!
mapa_img = pygame.image.load("mapa.jpg").convert()
mapa_colisao_img = pygame.image.load("mapa_colisao.png").convert()
mapa_colisao_img.set_colorkey((255, 255, 255)) # Define o branco como transparente

personagem_img_original = pygame.image.load("perso.webp").convert_alpha()
personagem_img = pygame.transform.scale(personagem_img_original, (64, 64))

chave_img_original = pygame.image.load("chave.png").convert_alpha()
chave_img = pygame.transform.scale(chave_img_original, (32, 32))

porta_img_original = pygame.image.load("porta.png").convert_alpha()
porta_img = pygame.transform.scale(porta_img_original, (64, 64))

upgrade_velocidade_original = pygame.image.load("bota.png").convert_alpha()
velocidade_img = pygame.transform.scale(upgrade_velocidade_original, (32, 32))

upgrade_tempo_original = pygame.image.load("relogio.png").convert_alpha()
tempo_img = pygame.transform.scale(upgrade_tempo_original, (32, 32))
print("Imagens carregadas com sucesso!")

# Criação das máscaras de colisão para física baseada em pixels
paredes = pygame.mask.from_surface(mapa_colisao_img)
colisao_personagem = pygame.mask.from_surface(personagem_img)

# Variáveis e dados do jogo
total_chaves = 3
coletaveis_velocidade = 5
coletaveis_tempo = 4

chaves_coletadas = 0
botas_coletadas = 0
relogios_coletados = 0

chaves_encontradas = False
vitoria = False
derrota = False
lista_de_itens = []
porta_saida = None

# ==============================================================================
# GERAÇÃO ALEATÓRIA DE ITENS E PERSONAGEM
# ==============================================================================
largura_mapa = mapa_img.get_width()
altura_mapa = mapa_img.get_height()
posicoes_validas = [] # Lista para guardar todos os pontos onde os itens podem nascer

def mapear_posicoes_validas():
    """
    Varre o mapa e armazena coordenadas de CENTRO válidas.
    
    A grande mudança aqui: em vez de checar um único pixel, agora verificamos se
    a MÁSCARA INTEIRA do personagem caberia no local sem colidir. Isso garante
    que o personagem nunca nascerá "entalado" ou preso nas paredes.
    """
    print("Mapeando posições válidas e seguras para spawn...")
    passo = 24  # Podemos usar um passo um pouco maior, pois a área de verificação é maior.
    largura_personagem = personagem_img.get_width()
    altura_personagem = personagem_img.get_height()
    
    for x in range(0, largura_mapa, passo):
        for y in range(0, altura_mapa, passo):
            # A posição (x, y) do loop é um candidato a CENTRO.
            # Para usar a função 'overlap', precisamos da coordenada do canto superior esquerdo.
            pos_x_canto = x - largura_personagem // 2
            pos_y_canto = y - altura_personagem // 2

            # A MÁGICA ACONTECE AQUI:
            # Verificamos se a máscara do personagem, na posição candidata,
            # NÃO sobrepõe (retorna None) a máscara das paredes.
            if paredes.overlap(colisao_personagem, (pos_x_canto, pos_y_canto)) is None:
                # Se não há sobreposição, este é um local seguro!
                # Adicionamos a coordenada de CENTRO (x, y) à lista.
                posicoes_validas.append((x, y))
                
    print(f"Mapeamento concluído! {len(posicoes_validas)} posições seguras encontradas.")

# Executamos a função de mapeamento UMA VEZ no início do jogo.
mapear_posicoes_validas()

def encontrar_posicao_valida():
    """
    Retorna uma posição aleatória da lista de posições válidas pré-calculadas.
    Este método é instantâneo e garantido.
    """
    if not posicoes_validas:
        # Se, por algum motivo, nenhuma posição for encontrada, coloca o personagem no centro.
        print("AVISO: Nenhuma posição de spawn segura foi encontrada. Verifique o mapa de colisão.")
        return (largura_mapa // 2, altura_mapa // 2) 
    return random.choice(posicoes_validas)

# Configurações do personagem (FAZEMOS ISSO ANTES DOS ITENS)
print("\n--- GERANDO POSIÇÃO DO PERSONAGEM ---")
posicao_inicial_personagem = encontrar_posicao_valida()
posicoes_validas.remove(posicao_inicial_personagem)
personagem_rect = personagem_img.get_rect(center=posicao_inicial_personagem)
velocidade = 4
print(f"-> Personagem gerado na posição: {posicao_inicial_personagem}")
print("--- GERAÇÃO CONCLUÍDA ---\n")


# 1. Lista com todos os itens a serem gerados
itens_a_gerar = []
for _ in range(total_chaves):
    itens_a_gerar.append(('chave', chave_img))
for _ in range(coletaveis_velocidade):
    itens_a_gerar.append(('velocidade', velocidade_img))
for _ in range(coletaveis_tempo):
    itens_a_gerar.append(('tempo', tempo_img))

# 2. Embaralhar a lista para garantir aleatoriedade
random.shuffle(itens_a_gerar)

# 3. Gerar cada item e imprimir sua posição para depuração
print("\n--- INICIANDO GERAÇÃO DE ITENS ---")
for tipo_item, imagem_item in itens_a_gerar:
    x, y = encontrar_posicao_valida()
    posicoes_validas.remove((x, y))
    
    print(f"-> Gerado item '{tipo_item}' na posição: ({x}, {y})")
    novo_item = Item(x, y, tipo_item, imagem_item)
    lista_de_itens.append(novo_item)

# 4. Gerar a porta de saída
x_porta, y_porta = encontrar_posicao_valida()
posicoes_validas.remove((x_porta, y_porta))
print(f"-> Porta de saída gerada na posição: ({x_porta}, {y_porta})")
print("--- GERAÇÃO CONCLUÍDA ---\n")
porta_saida = Item(x_porta, y_porta, 'porta', porta_img)

# Variáveis de controle do jogo
mensagem_chaves = False
tempo_mensagem_inicio = 0
duracao_mensagem = 5000  # 5 segundos em milissegundos
tempo_restante = 480  # 8 minutos em segundos
relogio = pygame.time.Clock()
ultimo_evento_tempo = pygame.time.get_ticks()

# ==============================================================================
# LOOP PRINCIPAL DO JOGO
# ==============================================================================
running = True
while running:
    # --- Processamento de Eventos ---
    teclas = pygame.key.get_pressed()
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT or teclas[pygame.K_ESCAPE]:
            running = False

    # --- Lógica do Jogo (só roda se não houver vitória ou derrota) ---
    if not vitoria and not derrota:
        # Movimentação do personagem e checagem de colisão com paredes
        pos_anterior = personagem_rect.copy()
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            personagem_rect.x -= velocidade
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            personagem_rect.x += velocidade
        if teclas[pygame.K_UP] or teclas[pygame.K_w]:
            personagem_rect.y -= velocidade
        if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
            personagem_rect.y += velocidade
        
        # Se a nova posição colide com uma parede, volta para a anterior
        offset_colisao = (pos_anterior.x - personagem_rect.x, pos_anterior.y - personagem_rect.y)
        if paredes.overlap(colisao_personagem, (personagem_rect.x, personagem_rect.y)):
            personagem_rect = pos_anterior

        # Coleta de itens
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
                    velocidade *= 1.2
                    botas_coletadas += 1
                elif item.tipo == 'tempo':
                    tempo_restante += 30
                    relogios_coletados += 1
                itens_para_remover.append(item)
        
        # Remove os itens coletados da lista principal
        for item in itens_para_remover:
            lista_de_itens.remove(item)

        # Condição de vitória
        if chaves_encontradas and personagem_rect.colliderect(porta_saida.rect):
            vitoria = True

        # Atualização do cronômetro
        evento_atual_tempo = pygame.time.get_ticks()
        if evento_atual_tempo - ultimo_evento_tempo >= 1000:
            tempo_restante -= 1
            ultimo_evento_tempo = evento_atual_tempo
        
        # Condição de derrota
        if tempo_restante <= 0:
            tempo_restante = 0
            derrota = True

    # --- Lógica da Câmera ---
    camera_x = personagem_rect.centerx - largura_tela // 2
    camera_y = personagem_rect.centery - altura_tela // 2
    
    # Prende a câmera nos limites do mapa
    camera_x = max(0, min(camera_x, largura_mapa - largura_tela))
    camera_y = max(0, min(camera_y, altura_mapa - altura_tela))
        
    # --- Desenho na Tela ---
    tela.fill((0, 0, 0)) # Limpa a tela com preto
    
    # Desenha o mapa relativo à câmera
    tela.blit(mapa_img, (-camera_x, -camera_y))
    
    # Desenha os itens
    for item in lista_de_itens:
        tela.blit(item.imagem, item.rect.move(-camera_x, -camera_y))

    # Desenha a porta se as chaves foram encontradas
    if chaves_encontradas:
        tela.blit(porta_saida.imagem, porta_saida.rect.move(-camera_x, -camera_y))

    # Desenha o personagem
    tela.blit(personagem_img, personagem_rect.move(-camera_x, -camera_y))

    # --- HUD (Heads-Up Display) ---
    hud_font_color = (255, 255, 0)
    hud_bg_color = (0, 0, 0, 150) # Fundo preto semi-transparente

    # Contadores
    textos_hud = [
        f"Chaves: {chaves_coletadas}/{total_chaves}",
        f"Botas: {botas_coletadas}/{coletaveis_velocidade}",
        f"Relógios: {relogios_coletados}/{coletaveis_tempo}"
    ]
    for i, texto in enumerate(textos_hud):
        superficie = fonte_hud.render(texto, True, hud_font_color)
        fundo = pygame.Surface((superficie.get_width() + 10, superficie.get_height()), pygame.SRCALPHA)
        fundo.fill(hud_bg_color)
        tela.blit(fundo, (5, 10 + i * 35))
        tela.blit(superficie, (10, 10 + i * 35))

    # Cronômetro
    minutos = tempo_restante // 60
    segundos = tempo_restante % 60
    cronometro_texto = f"{minutos:02d}:{segundos:02d}"
    superficie_cronometro = fonte_hud.render(cronometro_texto, True, (255, 0, 0))
    pos_cronometro = superficie_cronometro.get_rect(topright=(largura_tela - 10, 10))
    fundo_cronometro = pygame.Surface((superficie_cronometro.get_width() + 10, superficie_cronometro.get_height()), pygame.SRCALPHA)
    fundo_cronometro.fill(hud_bg_color)
    tela.blit(fundo_cronometro, fundo_cronometro.get_rect(topright=(largura_tela - 5, 10)))
    tela.blit(superficie_cronometro, pos_cronometro)

    # Mensagem de "Encontre a saída!"
    if mensagem_chaves and pygame.time.get_ticks() - tempo_mensagem_inicio < duracao_mensagem:
        texto_msg = "Você tem as chaves! Encontre a saída!"
        fonte_msg = pygame.font.SysFont('Consolas', 40, bold=True)
        superficie_msg = fonte_msg.render(texto_msg, True, (255, 255, 255))
        pos_msg = superficie_msg.get_rect(centerx=largura_tela / 2, top=20)
        fundo_rect = pos_msg.inflate(20, 10)
        pygame.draw.rect(tela, (0, 0, 0, 180), fundo_rect, border_radius=8)
        tela.blit(superficie_msg, pos_msg)
            
    # --- Telas de Vitória ou Derrota ---
    def desenhar_tela_final(texto, cor):
        fundo_final = pygame.Surface((largura_ela, altura_tela), pygame.SRCALPHA)
        fundo_final.fill((0, 0, 0, 180))
        tela.blit(fundo_final, (0, 0))
        
        fonte_final = pygame.font.SysFont('Consolas', 100, bold=True)
        superficie_final = fonte_final.render(texto, True, cor)
        pos_final = superficie_final.get_rect(center=(largura_tela / 2, altura_tela / 2))
        tela.blit(superficie_final, pos_final)

    if vitoria:
        desenhar_tela_final("VOCÊ VENCEU!! :D", (255, 215, 0))
    elif derrota:
        desenhar_tela_final("Você perdeu... :(", (170, 0, 0))

    # --- Atualização Final ---
    pygame.display.flip()
    relogio.tick(60)

# ==============================================================================
# FINALIZAÇÃO
# ==============================================================================
pygame.quit()
print("\nJogo encerrado. Obrigado por jogar!")