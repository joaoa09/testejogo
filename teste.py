import pygame

# 1. Inicialização do Pygame
pygame.init()

# 2. Configurações da Janela (A nossa "Câmara")
largura_tela = 1680
altura_tela = 720
tela = pygame.display.set_mode((largura_tela, altura_tela))
pygame.display.set_caption("Câmara a Seguir o Personagem")

# 3. Carregamento das Imagens
# Carrega a imagem de fundo (o mapa) no seu tamanho original
try:
    mapa_img = pygame.image.load("mapa.jpg").convert()
except pygame.error as e:
    print(f"Erro ao carregar a imagem 'mapa.jpg': {e}")
    pygame.quit()
    exit()

# Carrega a imagem do personagem
try:
    # Garante que estás a usar um formato compatível como .png
    personagem_img = pygame.image.load("perso.webp").convert_alpha()

    # --- LÓGICA DE REDIMENSIONAMENTO ADICIONADA AQUI ---
    # Define o novo tamanho desejado (largura, altura) em pixels.
    novo_tamanho = (64, 64)  # <--- É AQUI QUE TU ADAPTAS O TAMANHO!
    
    # Redimensiona a imagem para o novo tamanho
    personagem_img = pygame.transform.scale(personagem_img, novo_tamanho)

except pygame.error as e:
    print(f"Erro ao carregar a imagem 'perso.webp': {e}")
    pygame.quit()
    exit()

# 4. Variáveis do Personagem e do Mundo
# O rect do personagem agora representa a sua posição no MUNDO (no mapa grande)
personagem_rect = personagem_img.get_rect(center=(mapa_img.get_width() // 2, mapa_img.get_height() // 2))
velocidade = 10 

# Variável para controlar o loop principal do jogo
a_executar = True
relogio = pygame.time.Clock()

# --- LOOP PRINCIPAL DO JOGO ---
while a_executar:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            a_executar = False

    # --- Lógica de Movimento do Personagem (em relação ao mundo) ---
    teclas = pygame.key.get_pressed()
    
    if teclas[pygame.K_LEFT]:
        personagem_rect.x -= velocidade
    if teclas[pygame.K_RIGHT]:
        personagem_rect.x += velocidade
    if teclas[pygame.K_UP]:
        personagem_rect.y -= velocidade
    if teclas[pygame.K_DOWN]:
        personagem_rect.y += velocidade

    # --- Lógica de Limites (em relação às bordas do MAPA) ---
    if personagem_rect.left < 0:
        personagem_rect.left = 0
    if personagem_rect.right > mapa_img.get_width():
        personagem_rect.right = mapa_img.get_width()
    if personagem_rect.top < 0:
        personagem_rect.top = 0
    if personagem_rect.bottom > mapa_img.get_height():
        personagem_rect.bottom = mapa_img.get_height()

    # --- LÓGICA DA CÂMARA ---
    camera_x = personagem_rect.centerx - largura_tela // 2
    camera_y = personagem_rect.centery - altura_tela // 2

    if camera_x < 0:
        camera_x = 0
    if camera_y < 0:
        camera_y = 0
    if camera_x > mapa_img.get_width() - largura_tela:
        camera_x = mapa_img.get_width() - largura_tela
    if camera_y > mapa_img.get_height() - altura_tela:
        camera_y = mapa_img.get_height() - altura_tela
        
    # --- Atualização da Tela ---
    tela.blit(mapa_img, (-camera_x, -camera_y))
    tela.blit(personagem_img, personagem_rect.move(-camera_x, -camera_y))

    pygame.display.flip()
    
    relogio.tick(60)

pygame.quit()