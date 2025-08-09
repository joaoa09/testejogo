import pygame

# 1. Inicialização do Pygame
pygame.init()

# 2. Configurações da Janela
largura_tela = 1680
altura_tela = 960
tela = pygame.display.set_mode((largura_tela, altura_tela))
pygame.display.set_caption("Jogo com Colisão - Corrigido")

# 3. Carregamento das Imagens
try:
    mapa_img = pygame.image.load("mapa.jpg").convert()
    mapa_colisao_img = pygame.image.load("mapa_colisao.png").convert()

    # --- CORREÇÃO CRÍTICA ADICIONADA AQUI ---
    # Define a cor branca (255, 255, 255) como "transparente" para esta imagem.
    # Isto garante que a máscara de colisão seja criada APENAS com os pixeis pretos (paredes).
    mapa_colisao_img.set_colorkey((255, 255, 255))

except pygame.error as e:
    print(f"Erro ao carregar imagens: {e}")
    pygame.quit()
    exit()

try:
    personagem_img = pygame.image.load("perso.webp").convert_alpha()
    novo_tamanho = (32, 32)
    personagem_img = pygame.transform.scale(personagem_img, novo_tamanho)
except pygame.error as e:
    print(f"Erro ao carregar imagem do personagem: {e}")
    pygame.quit()
    exit()

# Agora, a criação das máscaras vai funcionar como esperado
mapa_mask = pygame.mask.from_surface(mapa_colisao_img)
personagem_mask = pygame.mask.from_surface(personagem_img)

# 4. Variáveis do Personagem e do Mundo
personagem_rect = personagem_img.get_rect(center=(70, 70))
velocidade = 4 # Diminuí para testar em corredores apertados

a_executar = True
relogio = pygame.time.Clock()

# --- LOOP PRINCIPAL DO JOGO ---
while a_executar:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            a_executar = False

    # --- LÓGICA DE MOVIMENTO E COLISÃO (EIXO POR EIXO) ---
    teclas = pygame.key.get_pressed()
    
    if teclas[pygame.K_LEFT]:
        personagem_rect.x -= velocidade
        if mapa_mask.overlap(personagem_mask, (personagem_rect.left, personagem_rect.top)):
            personagem_rect.x += velocidade
    if teclas[pygame.K_RIGHT]:
        personagem_rect.x += velocidade
        if mapa_mask.overlap(personagem_mask, (personagem_rect.left, personagem_rect.top)):
            personagem_rect.x -= velocidade

    if teclas[pygame.K_UP]:
        personagem_rect.y -= velocidade
        if mapa_mask.overlap(personagem_mask, (personagem_rect.left, personagem_rect.top)):
            personagem_rect.y += velocidade
    if teclas[pygame.K_DOWN]:
        personagem_rect.y += velocidade
        if mapa_mask.overlap(personagem_mask, (personagem_rect.left, personagem_rect.top)):
            personagem_rect.y -= velocidade

    # --- LÓGICA DA CÂMARA (continua igual) ---
    camera_x = personagem_rect.centerx - largura_tela // 2
    camera_y = personagem_rect.centery - altura_tela // 2

    if camera_x < 0: camera_x = 0
    if camera_y < 0: camera_y = 0
    if camera_x > mapa_img.get_width() - largura_tela: camera_x = mapa_img.get_width() - largura_tela
    if camera_y > mapa_img.get_height() - altura_tela: camera_y = mapa_img.get_height() - altura_tela
        
    # --- ATUALIZAÇÃO DA TELA ---
    tela.blit(mapa_img, (-camera_x, -camera_y))
    tela.blit(personagem_img, personagem_rect.move(-camera_x, -camera_y))

    pygame.display.flip()
    relogio.tick(60)

pygame.quit()