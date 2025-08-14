import pygame

class Camera:
    def __init__(self, xo, yo, largura_tela, altura_tela, tela_jogo):
        self.x = xo
        self.y = yo
        self.altura_tela = altura_tela
        self.largura_tela = largura_tela
        self.tela_jogo = tela_jogo

    def ajustar_camera(self, retangulo_alvo, imagem_mapa, tela_jogo):
            
        self.x = max(0, min(retangulo_alvo.centerx - self.largura_tela // 2, imagem_mapa.get_width() - self.largura_tela))
        self.y = max(0, min(retangulo_alvo.centery - self.altura_tela // 2, imagem_mapa.get_height() - self.altura_tela))

        tela_jogo.blit(imagem_mapa, (-self.x, -self.y))