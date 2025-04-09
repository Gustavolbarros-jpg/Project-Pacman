import pygame
import sys
from Protagonista import Protagonista 
from Coletaveis import *
from Perseguidor import Perseguidor
from Labirinto import LABIRINTO
import random
from Spawn import SpawnManager

pygame.init()

# Configurações
LARGURA_CELULA = 30  
LARGURA = len(LABIRINTO[0]) * LARGURA_CELULA
ALTURA = len(LABIRINTO) * LARGURA_CELULA
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Pac-Man")

# Cores
PRETO = (0, 0, 0)
AZUL = (0, 0, 255)
BRANCO = (255, 255, 255)

# Inicialização do jogador
def encontrar_posicao_inicial():
    for y in range(len(LABIRINTO)):
        for x in range(len(LABIRINTO[y])):
            if LABIRINTO[y][x] == 2:
                return x * LARGURA_CELULA + LARGURA_CELULA // 2, y * LARGURA_CELULA + LARGURA_CELULA // 2
    return LARGURA // 2, ALTURA // 2  

player_x, player_y = encontrar_posicao_inicial()
player = Protagonista(player_x, player_y)

vidas = 3
posicao_inicial_x, posicao_inicial_y = player_x, player_y

# Inicialização do perseguidor
perseguidor = Perseguidor(170, 200)  # Agora é um único objeto, não uma lista

# Criação das paredes
paredes = []
for y in range(len(LABIRINTO)):
    for x in range(len(LABIRINTO[y])):
        if LABIRINTO[y][x] == 1:  
            paredes.append(pygame.Rect(
                x * LARGURA_CELULA,
                y * LARGURA_CELULA,
                LARGURA_CELULA,
                LARGURA_CELULA
            ))

# Criação das moedas
moedas = []
monitores = []
spawn_manager = SpawnManager()
buff_velocidade = []
buffonmap = False

for y in range(len(LABIRINTO)):
    for x in range(len(LABIRINTO[y])):
        pos_x = x * LARGURA_CELULA + LARGURA_CELULA // 2
        pos_y = y * LARGURA_CELULA + LARGURA_CELULA // 2
        
        if LABIRINTO[y][x] == 2:
            moedas.append(Coletaveis(pos_x, pos_y))
            spawn_manager.adicionar_local_moeda(pos_x, pos_y)  # x,y correto
        elif LABIRINTO[y][x] == 3:
            monitores.append(Monitor(pos_x, pos_y))
            spawn_manager.adicionar_local_monitor(pos_x, pos_y)  # x,y correto
            
pontos = 0
relogio = pygame.time.Clock()
cacada = True

jogador_direcao = (0, 0)  

while cacada:
    if perseguidor.verificar_colisao(player):
        vidas -= 1
        #cacada = False
        
        if vidas > 0:
            # Volta para posição inicial
            player.x, player.y = posicao_inicial_x, posicao_inicial_y
            perseguidor.x, perseguidor.y = 170, 200  # Reseta posição do perseguidor
            
            # Mostra mensagem de vida perdida
            fonte = pygame.font.SysFont(None, 36)
            texto_vida = fonte.render(f"Vidas restantes: {vidas}", True, (255, 0, 0))
            tela.blit(texto_vida, (10, 10))
            pygame.display.flip()
            pygame.time.wait(1000)  # Pequena pausa para feedback
        else:
            # Game Over
            tela.fill(PRETO)
            fonte = pygame.font.SysFont(None, 72)
            texto = fonte.render("GAME OVER", True, (255, 0, 0))
            tela.blit(texto, (LARGURA//2 - texto.get_width()//2, ALTURA//2 - texto.get_height()//2))
            
            fonte = pygame.font.SysFont(None, 36)
            texto_pontos = fonte.render(f"Pontuação final: {pontos}", True, BRANCO)
            tela.blit(texto_pontos, (LARGURA//2 - texto_pontos.get_width()//2, ALTURA//2 + 50))
            
            pygame.display.flip()
            pygame.time.wait(3000)
            cacada = False

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            cacada = False

  
    teclas = pygame.key.get_pressed()
    if teclas[pygame.K_LEFT]:
        jogador_direcao = (-1, 0)
    elif teclas[pygame.K_RIGHT]:
        jogador_direcao = (1, 0)
    elif teclas[pygame.K_UP]:
        jogador_direcao = (0, -1)
    elif teclas[pygame.K_DOWN]:
        jogador_direcao = (0, 1)

    player.mover(teclas, paredes)
    player.limitar_bordas(LARGURA, ALTURA)

    perseguidor.perseguir(player.x, player.y, paredes,LARGURA,ALTURA)

 
    for moeda in moedas[:]:  
        if moeda.verificar_colisao(player):
            pontos += 10
            moedas.remove(moeda)

    for monitor in monitores[:]:
        if monitor.verificar_colisao(player):
            monitores.remove(monitor)
    
    chance = random.random()
    if chance < 0.3 and not buffonmap:  # 30% de chance
        spawn_manager.tentar_spawn_buff(moedas, monitores, buff_velocidade, buffonmap)


    # Renderização
    tela.fill(PRETO)

    # Desenhar paredes
    for parede in paredes:
        pygame.draw.rect(tela, AZUL, parede)

    # Desenhar moedas
    for moeda in moedas:
        moeda.desenhar(tela)

    if len(buff_velocidade) == 1:
        for buff in buff_velocidade[:]:
            buff.desenhar(tela)
            buffonmap = True

    for buff in buff_velocidade[:]:
        if buff.verificar_colisao(player):
            buff_velocidade.remove(buff)
            buffonmap = False


    for monitor in monitores:
        monitor.desenhar(tela)

    
    # Desenhar jogador
    player.modelo_personagem(tela)

    # Desenhar perseguidor (corrigido o nome do método)
    perseguidor.desenhar(tela)  # Era "desennhar" no seu código original

    pygame.display.flip()
    relogio.tick(60)

pygame.quit()
sys.exit()