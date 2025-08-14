import pygame
import random

class Personagem:
    def __init__(self, sprite_fora_escala, colisao_mapa, dimensoes_mapa, velocidade): #dimensoes_mapa = (largura, altura)
        self.sprite = pygame.transform.scale(sprite_fora_escala, (70, 70))
        
        self.colisao = pygame.mask.from_surface(self.sprite)

        self.x, self.y = random.randint(0, dimensoes_mapa[0]), random.randint(0, dimensoes_mapa[1])

        while colisao_mapa.overlap(self.colisao, (self.x, self.y)):
            self.x, self.y = random.randint(0, dimensoes_mapa[0]), random.randint(0, dimensoes_mapa[1])
            
        self.rect = self.sprite.get_rect(topleft=(self.x, self.y))

        self.velocidade = velocidade