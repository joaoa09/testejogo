import pygame
import random

#inicialização do pygame
pygame.init()

#configurações da janela
info = pygame.display.Info()
largura_tela = info.current_w
altura_tela = info.current_h
tela = pygame.display.set_mode((largura_tela, altura_tela))
pygame.display.set_caption("Encontre a Saída!")

#configurações do HUD
cor_texto = (255, 255, 255)
pygame.font.init()
fonte_hud = pygame.font.SysFont('Consolas', 30, bold=True)

#classe para os itens
class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, tipo, imagem):
        super().__init__()
        self.tipo = tipo
        self.imagem = imagem
        self.rect = self.imagem.get_rect(center=(x, y))

#carregamento das imagens

mapa_img = pygame.image.load("mapa.jpg").convert()
mapa_colisao_img = pygame.image.load("mapa_colisao.png").convert()
mapa_colisao_img.set_colorkey((255, 255, 255))

personagem_img_original = pygame.image.load("perso.webp").convert_alpha()
personagem_img = pygame.transform.scale(personagem_img_original, (32, 32))

chave_img_original = pygame.image.load("chave.png").convert_alpha()
chave_img = pygame.transform.scale(chave_img_original, (32, 32))

porta_img_original = pygame.image.load("porta.png").convert_alpha()
porta_img = pygame.transform.scale(porta_img_original, (64, 64))

coletavel1_img_original = pygame.image.load("coletavel1.png").convert_alpha()
coletavel1_img = pygame.transform.scale(coletavel1_img_original, (32, 32))

 
#criação das máscaras
paredes = pygame.mask.from_surface(mapa_colisao_img)
colisao_personagem = pygame.mask.from_surface(personagem_img)

#variáveis do personagem e do mundo
personagem_rect = personagem_img.get_rect(center=(70, 70))
velocidade_base = 4
velocidade = velocidade_base

#variáveis de jogo e itens
chaves_coletadas = 0
numero_total_chaves = 3
jogo_vencido = False
jogo_finalizado = False
lista_de_itens = []
porta_saida = None

#variáveis para o buff de velocidade
buff_velocidade_ativo = False
tempo_buff_inicio = 0
duracao_buff_velocidade = 35000

#geração de itens
largura_mapa = mapa_img.get_width()
altura_mapa = mapa_img.get_height()

while len(lista_de_itens) < numero_total_chaves:
    x = random.randint(50, largura_mapa - 50)
    y = random.randint(50, altura_mapa - 50)
    if paredes.get_at((x, y)) == 0:
        nova_chave = Item(x, y, 'chave', chave_img)
        lista_de_itens.append(nova_chave)

item_spawnado = False
while not item_spawnado:
    x = random.randint(50, largura_mapa - 50)
    y = random.randint(50, altura_mapa - 50)
    if paredes.get_at((x, y)) == 0:
        novo_coletavel = Item(x, y, 'velocidade', coletavel1_img)
        lista_de_itens.append(novo_coletavel)
        item_spawnado = True

while porta_saida is None:
    x = random.randint(50, largura_mapa - 50)
    y = random.randint(50, altura_mapa - 50)
    if paredes.get_at((x, y)) == 0:
        porta_saida = Item(x, y, 'porta', porta_img)

# Variáveis para controlar a mensagem de vitória
exibir_mensagem_vitoria = False
tempo_mensagem_inicio = 0
duracao_mensagem = 5000 

# --- LOOP PRINCIPAL DO JOGO ---
a_executar = True
relogio = pygame.time.Clock()

while a_executar:
    teclas = pygame.key.get_pressed()

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT or teclas[pygame.K_ESCAPE]:
            a_executar = False

    if buff_velocidade_ativo:
        if pygame.time.get_ticks() - tempo_buff_inicio > duracao_buff_velocidade:
            velocidade = velocidade_base
            buff_velocidade_ativo = False

    if not jogo_finalizado:
        
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            personagem_rect.x -= velocidade
            if paredes.overlap(colisao_personagem, (personagem_rect.x, personagem_rect.y)):
                personagem_rect.x += velocidade

        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            personagem_rect.x += velocidade
            if paredes.overlap(colisao_personagem, (personagem_rect.x, personagem_rect.y)):
                personagem_rect.x -= velocidade
        
        if teclas[pygame.K_UP] or teclas[pygame.K_w]:
            personagem_rect.y -= velocidade
            if paredes.overlap(colisao_personagem, (personagem_rect.x, personagem_rect.y)):
                personagem_rect.y += velocidade
        
        if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
            personagem_rect.y += velocidade
            if paredes.overlap(colisao_personagem, (personagem_rect.x, personagem_rect.y)):
                personagem_rect.y -= velocidade
        
    # ### MODIFICADO ### --- Lógica de Coleta de Itens Reestruturada ---
    itens_para_remover = []
    for item in lista_de_itens:
        if personagem_rect.colliderect(item.rect):
            # A coleta de CHAVE só funciona se o jogador ainda NÃO coletou todas
            if item.tipo == 'chave' and not jogo_vencido:
                itens_para_remover.append(item)
                chaves_coletadas += 1
                if chaves_coletadas == numero_total_chaves:
                    jogo_vencido = True
                    exibir_mensagem_vitoria = True
                    tempo_mensagem_inicio = pygame.time.get_ticks()
            
            # A coleta de VELOCIDADE funciona a qualquer momento (antes de finalizar o jogo)
            elif item.tipo == 'velocidade' and not jogo_finalizado:
                itens_para_remover.append(item)
                velocidade = velocidade_base * 1.5
                buff_velocidade_ativo = True
                tempo_buff_inicio = pygame.time.get_ticks()
    
    # Remove da lista os itens que foram coletados neste frame
    for item in itens_para_remover:
        lista_de_itens.remove(item)


    if jogo_vencido and not jogo_finalizado:
        if personagem_rect.colliderect(porta_saida.rect):
            jogo_finalizado = True

    # --- LÓGICA DA CÂMARA ---
    camera_x = personagem_rect.centerx - largura_tela // 2
    camera_y = personagem_rect.centery - altura_tela // 2
    if camera_x < 0: camera_x = 0
    
    if camera_y < 0: camera_y = 0
    
    if camera_x > largura_mapa - largura_tela: camera_x = largura_mapa - largura_tela
    
    if camera_y > altura_mapa - altura_tela: camera_y = altura_mapa - altura_tela
        
    # --- ATUALIZAÇÃO DA TELA ---
    tela.blit(mapa_img, (-camera_x, -camera_y))
    
    for item in lista_de_itens:
        tela.blit(item.imagem, item.rect.move(-camera_x, -camera_y))

    if jogo_vencido and porta_saida:
        tela.blit(porta_saida.imagem, porta_saida.rect.move(-camera_x, -camera_y))

    tela.blit(personagem_img, personagem_rect.move(-camera_x, -camera_y))

    # --- Desenha a Interface (HUD) ---
    texto_hud = f"Chaves: {chaves_coletadas}"
    superficie_texto = fonte_hud.render(texto_hud, True, cor_texto, (0, 0, 0))
    pos_texto = (20, 20) 
    tela.blit(superficie_texto, pos_texto)

    if buff_velocidade_ativo:
        pos_icone = (20, 60)
        tela.blit(coletavel1_img, pos_icone)

        tempo_restante = (duracao_buff_velocidade - (pygame.time.get_ticks() - tempo_buff_inicio)) / 1000
        tempo_restante = max(0, tempo_restante)
        texto_buff = f"Velocidade extra: {tempo_restante:.1f}s"
        superficie_buff = fonte_hud.render(texto_buff, True, (173, 216, 230), (0,0,0))
        
        pos_texto_buff = (pos_icone[0] + coletavel1_img.get_width() + 10, pos_icone[1] + 4)
        tela.blit(superficie_buff, pos_texto_buff)

    if exibir_mensagem_vitoria:
        if pygame.time.get_ticks() - tempo_mensagem_inicio > duracao_mensagem:
            exibir_mensagem_vitoria = False

        else:
            texto_vitoria = "Você tem as chaves! Encontre a saída!"
            fonte_vitoria = pygame.font.SysFont('Consolas', 40, bold=True)
            superficie_vitoria = fonte_vitoria.render(texto_vitoria, True, (0, 0, 0))
            pos_vitoria = superficie_vitoria.get_rect(centerx=largura_tela / 2, top=20)
            fundo_rect = pos_vitoria.inflate(20, 10)
            pygame.draw.rect(tela, (255, 255, 255), fundo_rect, border_radius=5)
            tela.blit(superficie_vitoria, pos_vitoria)

    if jogo_finalizado:
        fundo_final = pygame.Surface((largura_tela, altura_tela), pygame.SRCALPHA)
        fundo_final.fill((0, 0, 0, 180))
        tela.blit(fundo_final, (0, 0))
        
        texto_final = "VOCÊ VENCEU!"
        fonte_final = pygame.font.SysFont('Consolas', 100, bold=True)
        superficie_final = fonte_final.render(texto_final, True, (255, 215, 0))
        pos_final = superficie_final.get_rect(center=(largura_tela / 2, altura_tela / 2))
        tela.blit(superficie_final, pos_final)

    pygame.display.flip()
    relogio.tick(60)

pygame.quit()