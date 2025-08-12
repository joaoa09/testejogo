import pygame
import random
from item import Item

#inicialização do pygame
pygame.init()

#configurações da janela
info = pygame.display.Info()
largura_tela = info.current_w
altura_tela = info.current_h
tela = pygame.display.set_mode((largura_tela, altura_tela))
pygame.display.set_caption("CIn Saída!")

#configurações do HUD
cor_texto = (255, 255, 255)
pygame.font.init()
fonte_hud = pygame.font.SysFont('Consolas', 30, bold=True)

#processamento das imagens

mapa_img = pygame.image.load("mapa.jpg").convert()
mapa_colisao_img = pygame.image.load("mapa_colisao.png").convert()
mapa_colisao_img.set_colorkey((255, 255, 255))

personagem_img_original = pygame.image.load("perso.webp").convert_alpha()
personagem_img = pygame.transform.scale(personagem_img_original, (32, 32))

chave_img_original = pygame.image.load("chave.png").convert_alpha()
chave_img = pygame.transform.scale(chave_img_original, (32, 32))

porta_img_original = pygame.image.load("porta.png").convert_alpha()
porta_img = pygame.transform.scale(porta_img_original, (64, 64))

upgrade_velocidade_original = pygame.image.load("bota.png").convert_alpha()
velocidade_img = pygame.transform.scale(upgrade_velocidade_original, (32, 32))

upgrade_tempo_original = pygame.image.load("relogio.png").convert_alpha()
tempo_img = pygame.transform.scale(upgrade_tempo_original, (32, 32))

#criação das máscaras
paredes = pygame.mask.from_surface(mapa_colisao_img)
colisao_personagem = pygame.mask.from_surface(personagem_img)

#dados das chaves
total_chaves = 3
chaves_coletadas = int()

#dados do aumento de velocidade
coletaveis_velocidade = 5
botas_coletadas = int()

#dados do aumento de tempo
coletaveis_tempo = 4
relogios_coletados = int()

chaves_encontradas = False
vitoria = derrota = False
lista_de_itens = []
porta_saida = None

#geração de itens
largura_mapa = mapa_img.get_width()
altura_mapa = mapa_img.get_height()

for _ in range(total_chaves):
    x = random.randint(50, largura_mapa - 50)
    y = random.randint(50, altura_mapa - 50)
    while paredes.get_at((x, y)) != 0:
        x = random.randint(50, largura_mapa - 50)
        y = random.randint(50, altura_mapa - 50)
        nova_chave = Item(x, y, 'chave', chave_img)
        lista_de_itens.append(nova_chave)

for _ in range(coletaveis_velocidade):
    x = random.randint(50, largura_mapa - 50)
    y = random.randint(50, altura_mapa - 50)
    while paredes.get_at((x, y)) != 0:
        x = random.randint(50, largura_mapa - 50)
        y = random.randint(50, altura_mapa - 50)
        novo_coletavel = Item(x, y, 'velocidade', velocidade_img)
        lista_de_itens.append(novo_coletavel)
    
for _ in range(coletaveis_tempo):
    x = random.randint(50, largura_mapa - 50)
    y = random.randint(50, altura_mapa - 50)
    while paredes.get_at((x, y)) != 0:
        x = random.randint(50, largura_mapa - 50)
        y = random.randint(50, altura_mapa - 50)
        novo_coletavel = Item(x, y, 'tempo', tempo_img)
        lista_de_itens.append(novo_coletavel)

while porta_saida is None:
    x = random.randint(50, largura_mapa - 50)
    y = random.randint(50, altura_mapa - 50)
    if paredes.get_at((x, y)) == 0:
        porta_saida = Item(x, y, 'porta', porta_img)

personagem_rect = personagem_img.get_rect(center=(70, 70))
velocidade = 4


#variaveis de chaves_encontradas
mensagem_chaves = False
tempo_mensagem_inicio = int()
duracao_mensagem = 5000

running = True

menu = True

tempo_restante = 480 #tempo total = 8min = 480s
relogio = pygame.time.Clock()
#variavel auxiliar para ajudar a cronometrar o tempo
ultimo_evento_tempo = pygame.time.get_ticks()

while running:
    teclas = pygame.key.get_pressed()

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT or teclas[pygame.K_ESCAPE]:
            running = False

    if not vitoria and not derrota:
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
        
    #coleta de itens
    itens_para_remover = []
    for item in lista_de_itens:
        if personagem_rect.colliderect(item.rect):
            #chave
            if item.tipo == 'chave':
                itens_para_remover.append(item)
                chaves_coletadas += 1
                if chaves_coletadas == total_chaves:
                    chaves_encontradas = True
                    mensagem_chaves = True
                    tempo_mensagem_inicio = pygame.time.get_ticks()
            
            #velocidade
            elif item.tipo == 'velocidade':
                itens_para_remover.append(item)
                velocidade = velocidade * 1.25
                botas_coletadas +=1
            
            #tempo
            elif item.tipo == 'tempo':
                itens_para_remover.append(item)
                tempo_restante += 30
                relogios_coletados += 1
    
    #remove os itens coletados
    for item in itens_para_remover:
        lista_de_itens.remove(item)

    if chaves_encontradas and (not vitoria or not derrota):
        if personagem_rect.colliderect(porta_saida.rect):
            vitoria = True

    #camera (agrupar como classe depois)
    camera_x = personagem_rect.centerx - largura_tela // 2
    camera_y = personagem_rect.centery - altura_tela // 2
    
    if camera_x < 0: 
        camera_x = 0
    
    if camera_x > largura_mapa - largura_tela:
        camera_x = largura_mapa - largura_tela


    if camera_y < 0:
        camera_y = 0

    if camera_y > altura_mapa - altura_tela:
        camera_y = altura_mapa - altura_tela
        
    tela.blit(mapa_img, (-camera_x, -camera_y))
    
    for item in lista_de_itens:
        tela.blit(item.imagem, item.rect.move(-camera_x, -camera_y))

    if chaves_encontradas:
        tela.blit(porta_saida.imagem, porta_saida.rect.move(-camera_x, -camera_y))

    tela.blit(personagem_img, personagem_rect.move(-camera_x, -camera_y))

    #relogio
    evento_atual_tempo = pygame.time.get_ticks()

    #se tiver passado 1000ms = 1s
    if evento_atual_tempo - ultimo_evento_tempo > 1000 and not (vitoria or derrota):
        tempo_restante -= 1
        ultimo_evento_tempo += 1000 #reinicia a contagem dos segundos

    #se o tempo tiver acabado:
    if tempo_restante < 0:
        tempo_restante = 0
        derrota = True

    #contador
    contador_chaves = f"Chaves: {chaves_coletadas}"
    superficie_chaves = fonte_hud.render(contador_chaves, True, (255, 255, 0), (0, 0, 0))
    pos_contador_chaves = (0, 0)

    contador_botas = f"Botas: {botas_coletadas}"
    superficie_botas = fonte_hud.render(contador_botas, True, (255, 255, 0), (0, 0, 0))
    pos_contador_botas = (0, 40)

    contador_relogio = f"Relógios: {relogios_coletados}"
    superficie_relogio = fonte_hud.render(contador_relogio, True, (255, 255, 0), (0, 0, 0))
    pos_contador_relogio = (0, 80)

    minutos_restantes = tempo_restante // 60
    segundos_restantes = tempo_restante % 60
    cronometro = f"0{minutos_restantes} : 0{segundos_restantes}" if minutos_restantes < 10 and segundos_restantes < 10 else f"{minutos_restantes} : 0{segundos_restantes}" if minutos_restantes>=10 else f"0{minutos_restantes} : {segundos_restantes}" if segundos_restantes >=10 else f"{minutos_restantes} : {segundos_restantes}"
    superficie_cronometro = fonte_hud.render(cronometro, True, (255, 0, 0), (0, 0, 0))
    pos_cronometro = (largura_tela - 117, 0)

    tela.blit(superficie_chaves, pos_contador_chaves)
    tela.blit(superficie_botas, pos_contador_botas)
    tela.blit(superficie_relogio, pos_contador_relogio)
    tela.blit(superficie_cronometro, pos_cronometro)

    if mensagem_chaves:
        if pygame.time.get_ticks() - tempo_mensagem_inicio > duracao_mensagem:
            mensagem_chaves = False

        else:
            texto_chaves_encontradas = "Você tem as chaves! Encontre a saída!"
            fonte_chaves_encontradas = pygame.font.SysFont('Consolas', 40, bold=True)
            superficie_chaves_encontradas = fonte_chaves_encontradas.render(texto_chaves_encontradas, True, (0, 0, 0))
            pos_chaves_encontradas = superficie_chaves_encontradas.get_rect(centerx=largura_tela / 2, top=20)
            fundo_rect = pos_chaves_encontradas.inflate(20, 10)
            pygame.draw.rect(tela, (255, 255, 255), fundo_rect, border_radius=5)
            tela.blit(superficie_chaves_encontradas, pos_chaves_encontradas)

    if vitoria:
        fundo_final = pygame.Surface((largura_tela, altura_tela), pygame.SRCALPHA)
        fundo_final.fill((0, 0, 0, 180))
        tela.blit(fundo_final, (0, 0))
        
        texto_final = "VOCÊ VENCEU!! :D"
        fonte_final = pygame.font.SysFont('Consolas', 100, bold=True)
        superficie_final = fonte_final.render(texto_final, True, (255, 215, 0))
        pos_final = superficie_final.get_rect(center=(largura_tela / 2, altura_tela / 2))
        tela.blit(superficie_final, pos_final)

    elif derrota:
        fundo_final = pygame.Surface((largura_tela, altura_tela), pygame.SRCALPHA)
        fundo_final.fill((0, 0, 0, 180))
        tela.blit(fundo_final, (0, 0))
        
        texto_final = "Você perdeu... :("
        fonte_final = pygame.font.SysFont('Consolas', 100, bold=True)
        superficie_final = fonte_final.render(texto_final, True, (127, 0, 0))
        pos_final = superficie_final.get_rect(center=(largura_tela / 2, altura_tela / 2))
        tela.blit(superficie_final, pos_final)

    pygame.display.flip()
    relogio.tick(60)

pygame.quit()