import pygame

print("Iniciando o gerador de máscara de colisão AVANÇADO...")

# --- CONFIGURAÇÕES ---
FICHEIRO_MAPA_ORIGINAL = "mapa.jpg"
FICHEIRO_MASCARA_SAIDA = "mapa_colisao.png"
LIMIAR_VERDE = 30

# --- NOVA CONFIGURAÇÃO DE FECHAMENTO ---
# Para tapar pequenos "buracos" brancos nas paredes e solidificá-las.
# Um valor de 1 ou 2 é recomendado. Define como 0 para desativar.
NIVEL_FECHAMENTO = 2

# --- CONFIGURAÇÃO DE EROSÃO ---
# Para afinar as paredes e alargar os corredores (aplicado DEPOIS do fechamento).
# Define como 0 para não afinar as paredes. 1 ou 2 é um bom começo.
NIVEL_EROSAO = 1
# --------------------

pygame.init()

try:
    mapa_original = pygame.image.load(FICHEIRO_MAPA_ORIGINAL)
    print(f"Imagem '{FICHEIRO_MAPA_ORIGINAL}' carregada.")
except pygame.error as e:
    print(f"ERRO ao carregar '{FICHEIRO_MAPA_ORIGINAL}': {e}")
    exit()

largura, altura = mapa_original.get_size()
print(f"Dimensões: {largura}x{altura}.")

# --- PASSO 1: Gerar a máscara de colisão inicial ---
print("Passo 1: Gerando a máscara inicial...")
mascara_processada = pygame.Surface((largura, altura))
for x in range(largura):
    for y in range(altura):
        r, g, b, _ = mapa_original.get_at((x, y))
        if g > r + LIMIAR_VERDE and g > b + LIMIAR_VERDE:
            mascara_processada.set_at((x, y), (0, 0, 0)) # Preto (Parede)
        else:
            mascara_processada.set_at((x, y), (255, 255, 255)) # Branco (Caminho)

# --- PASSO 2: Aplicar a operação de "Fechamento" (Dilatação seguida de Erosão) ---
if NIVEL_FECHAMENTO > 0:
    print(f"Passo 2: Aplicando Fechamento (Nível {NIVEL_FECHAMENTO})...")
    
    # DILATAÇÃO ("Engordar" para tapar buracos)
    for i in range(NIVEL_FECHAMENTO):
        print(f"  - Passagem de Dilatação {i + 1}/{NIVEL_FECHAMENTO}...")
        mascara_temp = mascara_processada.copy()
        for x in range(1, largura - 1):
            for y in range(1, altura - 1):
                # Regra da Dilatação: um pixel vira preto se ele OU QUALQUER vizinho for preto.
                if mascara_processada.get_at((x,y)) == (0,0,0): continue # Já é preto
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        if mascara_processada.get_at((x + dx, y + dy)) == (0, 0, 0):
                            mascara_temp.set_at((x, y), (0, 0, 0))
                            break
                    else: continue
                    break
        mascara_processada = mascara_temp.copy()

    # EROSÃO (parte do Fechamento, para voltar ao tamanho original)
    for i in range(NIVEL_FECHAMENTO):
        print(f"  - Passagem de Erosão (Fechamento) {i + 1}/{NIVEL_FECHAMENTO}...")
        mascara_temp = mascara_processada.copy()
        for x in range(1, largura - 1):
            for y in range(1, altura - 1):
                # Regra da Erosão: um pixel só continua preto se TODOS os vizinhos forem pretos.
                if mascara_processada.get_at((x,y)) == (255,255,255): continue # Já é branco
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        if mascara_processada.get_at((x + dx, y + dy)) == (255, 255, 255):
                            mascara_temp.set_at((x, y), (255, 255, 255))
                            break
                    else: continue
                    break
        mascara_processada = mascara_temp.copy()

# --- PASSO 3: Aplicar a Erosão final para afinar as paredes ---
if NIVEL_EROSAO > 0:
    print(f"Passo 3: Aplicando Erosão final para afinar paredes (Nível {NIVEL_EROSAO})...")
    for i in range(NIVEL_EROSAO):
        # Reutiliza a mesma lógica de erosão da etapa anterior
        print(f"  - Passagem de Erosão (Afinamento) {i + 1}/{NIVEL_EROSAO}...")
        mascara_temp = mascara_processada.copy()
        for x in range(1, largura - 1):
            for y in range(1, altura - 1):
                if mascara_processada.get_at((x,y)) == (255,255,255): continue
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        if mascara_processada.get_at((x + dx, y + dy)) == (255, 255, 255):
                            mascara_temp.set_at((x, y), (255, 255, 255))
                            break
                    else: continue
                    break
        mascara_processada = mascara_temp.copy()

# --- PASSO 4: Salvar o resultado final ---
try:
    pygame.image.save(mascara_processada, FICHEIRO_MASCARA_SAIDA)
    print("-" * 30)
    print(f"SUCESSO! Máscara de colisão final guardada como '{FICHEIRO_MASCARA_SAIDA}'.")
    print("-" * 30)
except pygame.error as e:
    print(f"ERRO ao guardar a imagem: {e}")

pygame.quit()