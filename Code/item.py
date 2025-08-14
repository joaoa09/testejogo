import pygame

class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, tipo, imagem):
        super().__init__()
        
        self.tipo = tipo
        self.imagem = imagem
        self.rect = self.imagem.get_rect(center=(x, y))
        self.colisao = pygame.mask.from_surface(self.imagem)

    def inserir_item(self, tela, camera):
        tela.blit(self.imagem, self.rect.move(-camera.x, -camera.y))

    def item_coletado(self, lista_itens):
        lista_itens.remove(self)