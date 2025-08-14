import pygame
import random
import sys
from personagem import Personagem
from item import Item
from camera import Camera
from pygame import mixer

pygame.init()
pygame.font.init()

#Criando a Janela de Jogo

info = pygame.display.Info()
largura_tela = info.current_w
altura_tela = info.current_h
tela = pygame.display.set_mode((largura_tela, altura_tela))

pygame.display.set_caption("CIn Saída!")
relogio = pygame.time.Clock()

#Cores & Fontes

COR_BRANCA = (255, 255, 255)
COR_AMARELA = (255, 255, 0)
COR_VERMELHO = (255 ,0, 0)
COR_VERDE = (0, 150, 0)
COR_LARANJA = (255, 100, 0)
COR_TITULO = (220, 230, 255)

fonte_titulo = pygame.font.SysFont('Consolas', 100, bold=True)
fonte_menu = pygame.font.SysFont('dejavuserif', 65, bold=True)
fonte_dificuldade = pygame.font.SysFont('Times New Roman', 45, bold=True)
fonte_hud = pygame.font.SysFont('Consolas', 30, bold=True)
fonte_mensagem_central = pygame.font.SysFont('Consolas', 40, bold=True)

mapa_img_original = pygame.image.load("Imagens/mapa.jpg").convert()
mapa_colisao_img = pygame.image.load("Imagens/mapa_colisao.png").convert()
mapa_colisao_img.set_colorkey((255, 255, 255))

chave_img = pygame.transform.scale(pygame.image.load("Imagens/chave.png").convert_alpha(), (96, 96))
porta_img = pygame.transform.scale(pygame.image.load("Imagens/porta.png").convert_alpha(), (128, 128))
velocidade_img = pygame.transform.scale(pygame.image.load("Imagens/bota.png").convert_alpha(), (96, 96))
tempo_img = pygame.transform.scale(pygame.image.load("Imagens/relogio.png").convert_alpha(), (96, 96))

escala_blur = 0.05

mapa_pequeno = pygame.transform.smoothscale(mapa_img_original, (int(largura_tela * escala_blur), int(altura_tela * escala_blur)))

mapa_fundo_blur = pygame.transform.scale(mapa_pequeno, (largura_tela, altura_tela))

paredes = pygame.mask.from_surface(mapa_colisao_img)

#Variáveis
largura_mapa, altura_mapa = mapa_img_original.get_size()

tempo_restante = 0
ultima_marcacao_temporal = 0

vitoria = False
derrota = False

total_chaves = 3
total_velocidade = 5
total_tempo = 4
chaves_coletadas = 0
botas_coletadas = 0
relogios_coletados = 0
chaves_encontradas = False
lista_de_itens = []
porta_saida = None

musica_tocou = False
tocar_musica = True

mensagem_chaves = False
tempo_msg = 0
duracao_mensagem = 5000

dificuldade_selecionada = 'medio'

protagonista = Personagem(pygame.image.load("Imagens/perso.png"), paredes, (largura_mapa, altura_mapa), 0)

camera = Camera(protagonista.x, protagonista.y, largura_tela, altura_tela, tela)

camera.ajustar_camera(protagonista.rect, mapa_img_original, tela)

def fazendo_txt(texto, fonte, cor_texto, centro_pos):

    texto_surf_principal = fonte.render(texto, True, cor_texto)
    rect_principal = texto_surf_principal.get_rect(center=centro_pos)
    tela.blit(texto_surf_principal, rect_principal)

def desenhar_tela_final(texto, cor):
    fundo_final = pygame.Surface((largura_tela, altura_tela), pygame.SRCALPHA)
    fundo_final.fill((0, 0, 0, 180))
    tela.blit(fundo_final, (0, 0))
    
    fonte_final = pygame.font.SysFont('Consolas', 50, bold=True)
    superficie_final = fonte_final.render(texto, True, cor)
    pos_final = superficie_final.get_rect(center=(largura_tela / 2, altura_tela / 2))
    tela.blit(superficie_final, pos_final)        

estado_jogo = 'menu'
running = True

while running:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            running = False
        
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                if estado_jogo == 'jogando':
                    protagonista.velocidade = 0
                    protagonista.x, protagonista.y = random.randint(0, largura_mapa), random.randint(0, altura_mapa)

                    estado_jogo = 'menu'

                else:
                    running = False
        
        if estado_jogo == 'menu' and evento.type == pygame.MOUSEBUTTONDOWN:
            tela.blit(mapa_fundo_blur, (0, 0))

            fazendo_txt("CIn Saída!", fonte_titulo, COR_TITULO, (largura_tela / 2, altura_tela * 0.25))
            fazendo_txt("Dificuldade", fonte_dificuldade, COR_BRANCA, (largura_tela / 2, altura_tela * 0.45))
            
            mouse_pos = pygame.mouse.get_pos()
            
            pos_y_dificuldade = altura_tela * 0.55
            espacamento_dificuldade = 200
            rect_facil = fonte_dificuldade.render("Calouro", True, COR_BRANCA).get_rect(center=(largura_tela/2 - espacamento_dificuldade, pos_y_dificuldade))
            rect_medio = fonte_dificuldade.render("Veterano", True, COR_BRANCA).get_rect(center=(largura_tela/2, pos_y_dificuldade))
            rect_dificil = fonte_dificuldade.render("Pós", True, COR_BRANCA).get_rect(center=(largura_tela/2 + 160, pos_y_dificuldade))
            
            cor_facil = COR_VERDE if dificuldade_selecionada == 'facil' else COR_BRANCA
            cor_medio = COR_LARANJA if dificuldade_selecionada == 'medio' else COR_BRANCA
            cor_dificil = COR_VERMELHO if dificuldade_selecionada == 'dificil' else COR_BRANCA
            
            fazendo_txt("Calouro", fonte_dificuldade, cor_facil, rect_facil.center)
            fazendo_txt("Veterano", fonte_dificuldade, cor_medio, rect_medio.center)
            fazendo_txt("Pós", fonte_dificuldade, cor_dificil, rect_dificil.center)

            pos_y_botoes = altura_tela * 0.75
            hitbox_comecar = fonte_menu.render("Pular a catraca", True, COR_BRANCA).get_rect(center=(largura_tela / 2, pos_y_botoes))
            cor_comecar = COR_AMARELA if hitbox_comecar.collidepoint(mouse_pos) else COR_BRANCA
            fazendo_txt("Pular a catraca", fonte_menu, cor_comecar, hitbox_comecar.center)
            
            rect_sair = fonte_menu.render("Trancar curso", True, COR_BRANCA).get_rect(center=(largura_tela / 2, pos_y_botoes + 90))
            cor_sair = COR_AMARELA if rect_sair.collidepoint(mouse_pos) else COR_BRANCA
            fazendo_txt("Trancar curso", fonte_menu, cor_sair, rect_sair.center)

            if rect_facil.collidepoint(evento.pos): 
                dificuldade_selecionada = 'facil'

            if rect_medio.collidepoint(evento.pos): 
                dificuldade_selecionada = 'medio'
            
            if rect_dificil.collidepoint(evento.pos):
                dificuldade_selecionada = 'dificil'
            
            if hitbox_comecar.collidepoint(evento.pos):
                
                botas_coletadas=0
                relogios_coletados=0
                chaves_coletadas=0


                chaves_encontradas=False
                vitoria = False
                derrota = False
                
                lista_de_itens = []
                
                if dificuldade_selecionada == 'facil': 
                    tempo_restante = 480
                elif dificuldade_selecionada == 'medio': 
                    tempo_restante = 360
                elif dificuldade_selecionada == 'dificil':
                    tempo_restante = 240
                
                ultima_marcacao_temporal = pygame.time.get_ticks()
                mensagem_chaves= False 
                tempo_msg = 0
                
                itens_a_gerar = []
                for _ in range(total_chaves):
                    itens_a_gerar.append(('chave', chave_img))
                for _ in range(total_velocidade):
                    itens_a_gerar.append(('velocidade', velocidade_img))
                for _ in range(total_tempo):
                    itens_a_gerar.append(('tempo', tempo_img))
                
                random.shuffle(itens_a_gerar)

                for tipo, img in itens_a_gerar:
                    x, y = random.randint(0, largura_mapa), random.randint(0, altura_mapa)
                    while paredes.overlap(protagonista.colisao, (x, y)):
                        x, y = random.randint(0, largura_mapa), random.randint(0, altura_mapa)
                    
                    lista_de_itens.append(Item(x, y, tipo, img))

                x, y = random.randint(0, largura_mapa), random.randint(0, altura_mapa)
                while paredes.overlap(protagonista.colisao, (x, y)):
                    x, y = random.randint(0, largura_mapa), random.randint(0, altura_mapa)
                porta_saida = Item(x, y, 'porta', porta_img)
                estado_jogo = 'jogando'
                protagonista.velocidade = 5
            
            if rect_sair.collidepoint(evento.pos):
                running = False

    if estado_jogo == 'menu':
        if tocar_musica:
            mixer.music.load("Musica/musicatopzera.ogg")
            mixer.music.play(-1)
            tocar_musica = False

        tela.blit(mapa_fundo_blur, (0, 0))

        fazendo_txt("CIn Saída!", fonte_titulo, COR_TITULO, (largura_tela / 2, altura_tela * 0.25))
        fazendo_txt("Dificuldade", fonte_dificuldade, COR_BRANCA, (largura_tela / 2, altura_tela * 0.45))
        
        mouse_pos = pygame.mouse.get_pos()
        
        pos_y_dificuldade = altura_tela * 0.55
        espacamento_dificuldade = 200
        rect_facil = fonte_dificuldade.render("Calouro", True, COR_BRANCA).get_rect(center=(largura_tela/2 - espacamento_dificuldade, pos_y_dificuldade))
        rect_medio = fonte_dificuldade.render("Veterano", True, COR_BRANCA).get_rect(center=(largura_tela/2, pos_y_dificuldade))
        rect_dificil = fonte_dificuldade.render("Pós", True, COR_BRANCA).get_rect(center=(largura_tela/2 + 160, pos_y_dificuldade))
        
        cor_facil = COR_VERDE if dificuldade_selecionada == 'facil' else COR_BRANCA
        cor_medio = COR_LARANJA if dificuldade_selecionada == 'medio' else COR_BRANCA
        cor_dificil = COR_VERMELHO if dificuldade_selecionada == 'dificil' else COR_BRANCA
        
        fazendo_txt("Calouro", fonte_dificuldade, cor_facil, rect_facil.center)
        fazendo_txt("Veterano", fonte_dificuldade, cor_medio, rect_medio.center)
        fazendo_txt("Pós", fonte_dificuldade, cor_dificil, rect_dificil.center)

        pos_y_botoes = altura_tela * 0.75
        hitbox_comecar = fonte_menu.render("Pular a catraca", True, COR_BRANCA).get_rect(center=(largura_tela / 2, pos_y_botoes))
        cor_comecar = COR_AMARELA if hitbox_comecar.collidepoint(mouse_pos) else COR_BRANCA
        fazendo_txt("Pular a catraca", fonte_menu, cor_comecar, hitbox_comecar.center)
        
        rect_sair = fonte_menu.render("Trancar curso", True, COR_BRANCA).get_rect(center=(largura_tela / 2, pos_y_botoes + 90))
        cor_sair = COR_AMARELA if rect_sair.collidepoint(mouse_pos) else COR_BRANCA
        fazendo_txt("Trancar curso", fonte_menu, cor_sair, rect_sair.center)
    
    elif estado_jogo == 'jogando':
        if not vitoria and not derrota:

            pos_anterior = protagonista.rect.copy()
            teclas = pygame.key.get_pressed()

            if teclas[pygame.K_LEFT] or teclas[pygame.K_a]: 
                protagonista.rect.x -= protagonista.velocidade

            if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]: 
                protagonista.rect.x += protagonista.velocidade

            if teclas[pygame.K_UP] or teclas[pygame.K_w]:
                protagonista.rect.y -= protagonista.velocidade

            if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
                protagonista.rect.y += protagonista.velocidade
            
            if paredes.overlap(protagonista.colisao, (protagonista.rect.x, protagonista.rect.y)):
                protagonista.rect = pos_anterior

            for item in lista_de_itens:
                if protagonista.rect.colliderect(item.rect):
                    if item.tipo == 'chave':
                        chaves_coletadas += 1
                        if chaves_coletadas == total_chaves:
                            chaves_encontradas = True
                            mensagem_chaves = True
                            tempo_msg = pygame.time.get_ticks()
                    elif item.tipo == 'velocidade':
                        protagonista.velocidade *= 1.2
                        botas_coletadas += 1
                    elif item.tipo == 'tempo':
                        tempo_restante += 30
                        relogios_coletados += 1
                    
                    item.item_coletado(lista_de_itens)

        else:
            if vitoria:
                desenhar_tela_final("Parabéns, você graduou :)", (255, 215, 0))
                if not musica_tocou:
                    mixer.music.stop()
                    mixer.music.load("Musica/ganhou.ogg")
                    mixer.music.play()
                    musica_tocou = True

            elif derrota:
                tempo_restante = 0
                if not musica_tocou:
                    mixer.music.stop()
                    mixer.music.load("Musica/perdeu.ogg")
                    mixer.music.play()
                    musica_tocou = True

            tocar_musica = True

        if pygame.time.get_ticks() - ultima_marcacao_temporal >= 1000:
            tempo_restante -= 1
            ultima_marcacao_temporal = pygame.time.get_ticks()
            
        tela.fill((0, 0, 0))

        camera.ajustar_camera(protagonista.rect, mapa_img_original, tela)

        for item in lista_de_itens:
            item.inserir_item(tela, camera)

        if chaves_encontradas and porta_saida:
            tela.blit(porta_img, porta_saida.rect.move(-camera.x, -camera.y))
            if protagonista.colisao.overlap(porta_saida.colisao, (protagonista.rect.x - porta_saida.rect.x, protagonista.rect.y - porta_saida.rect.y)):
                vitoria = True

        tela.blit(protagonista.sprite, protagonista.rect.move(-camera.x, -camera.y))

        hud_fundo_cor = (0, 0, 0, 150)
        textos_hud = [f"Chaves: {chaves_coletadas}/{total_chaves}", f"Botas: {botas_coletadas}/{total_velocidade}", f"Relógios: {relogios_coletados}/{total_tempo}"]
        
        for i, texto in enumerate(textos_hud):
            superficie_texto = fonte_hud.render(texto, True, COR_AMARELA)
            fundo_texto = pygame.Surface((superficie_texto.get_width() + 10, superficie_texto.get_height()), pygame.SRCALPHA)
            fundo_texto.fill(hud_fundo_cor)
            tela.blit(fundo_texto, (5, 10 + i * 35))
            tela.blit(superficie_texto, (10, 10 + i * 35))
            
        if tempo_restante>0:
            minutos = tempo_restante // 60
            segundos = tempo_restante % 60
            cronometro_texto = f"{minutos:02d}:{segundos:02d}"
            superficie_cronometro = fonte_hud.render(cronometro_texto, True, (255, 0, 0))
            
            pos_cronometro = superficie_cronometro.get_rect(topright=(largura_tela - 10, 10))
            
            fundo_cronometro = pygame.Surface((pos_cronometro.width + 10, pos_cronometro.height), pygame.SRCALPHA)
            fundo_cronometro.fill(hud_fundo_cor)
            tela.blit(fundo_cronometro, fundo_cronometro.get_rect(topright=(largura_tela - 5, 10)))
            tela.blit(superficie_cronometro, pos_cronometro)
        else:
            derrota = True
        
        if mensagem_chaves and pygame.time.get_ticks() - ultima_marcacao_temporal < duracao_mensagem:
            texto_msg = "Você tem as chaves! A porta da formatura te aguarda"
            fazendo_txt(texto_msg, fonte_mensagem_central, COR_AMARELA, (largura_tela / 2, 40))

        if vitoria:
            desenhar_tela_final("Parabéns, você graduou :)", (255, 215, 0))

        elif derrota:
            desenhar_tela_final("Eita, demorou demais, você foi jubilado! :(", (170, 0, 0))

    pygame.display.flip()
    relogio.tick(60)

pygame.quit()
sys.exit()