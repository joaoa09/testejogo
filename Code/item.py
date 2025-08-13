import pygame

class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, tipo, imagem):
        super().__init__()
        
        self.tipo = tipo
        self.imagem = imagem
        self.rect = self.imagem.get_rect(center=(x, y))