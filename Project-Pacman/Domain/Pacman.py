import pygame
import pytmx
import sys
import random
import os
import pygame.mixer
from Protagonista import Protagonista
from Perseguidor import Perseguidor
from Botao import Botao
from Coletaveis import Coletaveis
from Buff_velocidade import Buff_velocidade
from Monitor import Monitor
from Spawn import SpawnManager
from Matriz import maze
from Labirinto import Labirinto

# Constantes
LARGURA = 1296
ALTURA = 720
TAMANHO_CELULA = 24
PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
AZUL = (0, 0, 255)
VERMELHO = (255, 0, 0)
AMARELO = (255, 255, 0)
# Inicialização do Pygame
pygame.init()
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Pacman")
#inicalizar o som
pygame.mixer.init()

#CARREGAR a musica
pygame.mixer.music.load('imagens\music.mp3')
pygame.mixer.music.set_volume(0.05)
pygame.mixer.music.play(-1)

# Carregar o fundo do menu com caminho relativo para 'imagens'
FUNDO_MENU = pygame.image.load(os.path.join(os.path.dirname(
    __file__), "..", "..", "imagens", "fundo_menu.jpg"))
FUNDO_MENU = pygame.transform.scale(FUNDO_MENU, (LARGURA, ALTURA))

FUNDO_VITORIA = pygame.image.load(os.path.join(os.path.dirname(
    __file__), "..", "..", "imagens", "fundo_vitoria.png"))
FUNDO_VITORIA = pygame.transform.scale(FUNDO_VITORIA, (LARGURA, ALTURA))

FUNDO_DERROTA = pygame.image.load(os.path.join(os.path.dirname(
    __file__), "..", "..", "imagens", "fundo_derrota.png"))
FUNDO_DERROTA = pygame.transform.scale(FUNDO_DERROTA, (LARGURA, ALTURA))

# Função para carregar a fonte personalizada


def carregar_fonte(tamanho):
    fonte_path = os.path.join(os.path.dirname(
        __file__), "..", "..", "imagens", "PressStart2P-Regular.ttf")
    return pygame.font.Font(fonte_path, tamanho)


# Instanciar o labirinto (sem carregar o mapa ainda)
labirinto = Labirinto()

# Função para encontrar posição inicial


def encontrar_posicao_inicial():
    return (LARGURA // 2) +10, (ALTURA // 2) +10  # (648, 360)

# Função para desenhar contador de moedas


def desenhar_contador_moedas(tela, pontuacao):
    fonte = carregar_fonte(24)  # Usa a fonte personalizada
    texto = fonte.render(f"Caneta: {pontuacao}", True, AMARELO)
    tela.blit(texto, (35, 30))

def desenhar_contador_monitores(tela, vida):
    fonte = carregar_fonte(24)  # Usa a fonte personalizada
    texto = fonte.render(f"Vida: {vida}", True, AMARELO)
    tela.blit(texto, (35, 70))

def desenhar_contador_livros(tela, pontuacao_livros):
    fonte = carregar_fonte(24)  # Usa a fonte personalizada
    texto = fonte.render(f"Livros: {pontuacao_livros}", True, AMARELO)
    tela.blit(texto, (35, 120))
# Loop principal do jogo


def jogo_principal():
    vida = 3
    velocidade_buff_ativa = False
    # Carregar o mapa aqui, dentro da função
    labirinto.carregar_mapa()

    pos_x, pos_y = encontrar_posicao_inicial()
    jogador = Protagonista(pos_x, pos_y)
    vida = 3
    spawner = SpawnManager()
    matriz = maze
    moedas = Coletaveis.criar_moedas_na_matriz(matriz, TAMANHO_CELULA, spawner)
    monitores = Monitor.criar_monitores_na_matriz(matriz, TAMANHO_CELULA, spawner)
    total_moedas = len(moedas)

    inimigo = Perseguidor(170, 200)

    # Construção das paredes
    paredes = []
    for camada in labirinto.dados_tmx.layers:
        if isinstance(camada, pytmx.TiledTileLayer):
            if "colisão" in camada.name.lower():
                for y in range(camada.height):
                    for x in range(camada.width):
                        if camada.data[y][x] != 0:
                            paredes.append(pygame.Rect(
                                x * TAMANHO_CELULA,
                                y * TAMANHO_CELULA,
                                TAMANHO_CELULA,
                                TAMANHO_CELULA
                            ))
    print(f"Total de paredes carregadas: {len(paredes)}")
    pontuacao_monitores = 0
    pontuacao_livros = 0
    pontuacao = 0
    relogio = pygame.time.Clock()

    itens_especiais = []
    powerups = []
    powerup_ativo = False
    tempo_powerup = 0

    rodando = True
    vitoria = False
    while rodando:
        if pontuacao >= 175:
            rodando = False
            vitoria = True
            tela_resultado(vitoria)
            continue

        if inimigo.verificar_colisao(jogador):
            vida -= 1
            if vida <= 0:
                rodando = False
                tela_resultado(vitoria)
            else:
                jogador.x, jogador.y = encontrar_posicao_inicial()
                jogador.anim_frame = 0
                jogador.direction = "baixo"
                inimigo.x, inimigo.y = 170, 200
                inimigo.anim_frame = 0
                inimigo.direction = "baixo"

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
                pygame.quit()
                sys.exit()

        teclas = pygame.key.get_pressed()
        jogador.mover(teclas, paredes)
        jogador.limitar_bordas(LARGURA, ALTURA)
        inimigo.perseguir(jogador.x, jogador.y, paredes, LARGURA, ALTURA)

        for moeda in moedas[:]:
            if moeda.verificar_colisao(jogador):
                pontuacao += 1
                moedas.remove(moeda)

        for item in itens_especiais[:]:
            if item.verificar_colisao(jogador):
                itens_especiais.remove(item)
                pontuacao_livros +=1

        for monitor in monitores[:]:  # Copia da lista para remover enquanto itera
            if abs(jogador.x - monitor.x) < 32 and abs(jogador.y - monitor.y) < 32:
                vida += 1  # Aumenta uma vida
                monitores.remove(monitor)
                pontuacao_monitores += 1

        if not powerup_ativo and len(powerups)==0:
            buff_spawnado = spawner.tentar_spawn_buff(
                    moedas, monitores, powerups, powerup_ativo, buff_aplicado=Buff_velocidade)

        if buff_spawnado:
            powerup_ativo = True


        # Desenho na tela
        tela.fill(PRETO)  # Limpa a tela primeiro
        labirinto.desenhar(tela)

        for moeda in moedas:
            moeda.desenhar(tela)
        for item in itens_especiais:
            item.desenhar(tela)
        for monitor in monitores:
            monitor.desenhar(tela)
        for powerup in powerups[:]:
            powerup.desenhar(tela)
            if powerup.verificar_colisao(jogador):
                powerups.remove(powerup)
                powerup_ativo = True
                tempo_powerup = pygame.time.get_ticks()
                jogador.velocidade *= 2  # Dobra a velocidade
                velocidade_buff_ativa = True  # Novo flag
                pontuacao_livros += 1
         # Verifica se o powerup expirou (5 segundos)
        if powerup_ativo and (pygame.time.get_ticks() - tempo_powerup > 5000):
            powerup_ativo = False
            if velocidade_buff_ativa:
                jogador.velocidade //= 2  # Restaura a velocidade
                velocidade_buff_ativa = False

        jogador.modelo_personagem(tela)
        inimigo.desenhar(tela)

        # Desenha o contador por último para garantir visibilidade
        desenhar_contador_moedas(tela, pontuacao)
        desenhar_contador_monitores(tela, vida)
        desenhar_contador_livros(tela, pontuacao_livros)
        pygame.display.flip()
        relogio.tick(60)

# Menu principal


def menu_principal():
    ativo = True
    while ativo:
        tela.blit(FUNDO_MENU, (0, 0))
        pos_mouse = pygame.mouse.get_pos()

        # Títulos do menu com fonte personalizada
        fonte_titulo = carregar_fonte(50)
        fonte_subtitulo = carregar_fonte(20)
        fonte_botao = carregar_fonte(16)

        titulo = fonte_titulo.render("da Saga Emanoel:", True, (182, 143, 64))
        subtitulo = fonte_subtitulo.render(
            "O Labirinto Discreto", True, (182, 143, 64))

        botao_jogar = Botao(
            pos=(LARGURA // 2, 250),
            text_input="JOGAR",
            font=fonte_botao,
            base_color=BRANCO,
            hovering_color=AZUL
        )

        botao_sair = Botao(
            pos=(LARGURA // 2, 325),
            text_input="SAIR",
            font=fonte_botao,
            base_color=BRANCO,
            hovering_color=AZUL
        )

        tela.blit(titulo, titulo.get_rect(center=(LARGURA // 2 + 4, 110)))
        tela.blit(subtitulo, subtitulo.get_rect(
            center=(LARGURA // 2 + 4, 160)))

        for botao in [botao_jogar, botao_sair]:
            botao.mudar_cor(pos_mouse)
            botao.update_tela(tela)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ativo = False
                pygame.quit()
                sys.exit()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if botao_jogar.checar_clique(pos_mouse):
                    ativo = False
                    jogo_principal()
                elif botao_sair.checar_clique(pos_mouse):
                    ativo = False
                    pygame.quit()
                    sys.exit()

        pygame.display.update()


def tela_resultado(vitoria):

    # Transição de tela para os resultados
    fade_img = pygame.Surface((LARGURA, ALTURA)).convert_alpha()
    fade = fade_img.get_rect()
    fade_img.fill(PRETO)
    fade_alpha = 255

    ativo = True
    while ativo:

        fade_alpha -= 10
        fade_img.set_alpha(fade_alpha)
        if vitoria:
            tela.blit(FUNDO_VITORIA, (0, 0))
            pos_mouse = pygame.mouse.get_pos()

            fonte_titulo = carregar_fonte(50)
            fonte_subtitulo = carregar_fonte(20)
            fonte_botao = carregar_fonte(16)

            titulo = fonte_titulo.render(
                "VOCÊ CONSEGUIU!", True, (182, 143, 64))
            subtitulo = fonte_subtitulo.render(
                "De primeira! Agora é estudar para cálculo.", True, (182, 143, 64))

            botao_jogar = Botao(
                pos=(LARGURA // 2 - 10, 200),
                text_input="JOGAR NOVAMENTE",
                font=fonte_botao,
                base_color=BRANCO,
                hovering_color=AZUL
            )

            botao_sair = Botao(
                pos=(LARGURA // 2 - 10, 250),
                text_input="APROVEITAR AS FÉRIAS",
                font=fonte_botao,
                base_color=BRANCO,
                hovering_color=AZUL
            )

            tela.blit(titulo, titulo.get_rect(center=(LARGURA // 2 + 4, 100)))
            tela.blit(subtitulo, subtitulo.get_rect(
                center=(LARGURA // 2 + 4, 150)))

        else:
            tela.blit(FUNDO_DERROTA, (0, 0))
            pos_mouse = pygame.mouse.get_pos()

            # Títulos do menu com fonte personalizada
            fonte_titulo = carregar_fonte(35)
            fonte_subtitulo = carregar_fonte(15)
            fonte_botao = carregar_fonte(15)

            titulo = fonte_titulo.render(
                "VOCÊ FOI PEGO!", True, (182, 143, 64))
            subtitulo = fonte_subtitulo.render(
                "Devia ter estudado mais.", True, (182, 143, 64))

            botao_jogar = Botao(
                pos=(LARGURA // 2, 150),
                text_input="TENTAR NOVAMENTE",
                font=fonte_botao,
                base_color=BRANCO,
                hovering_color=AZUL
            )

            botao_sair = Botao(
                pos=(LARGURA // 2, 200),
                text_input="SAIR",
                font=fonte_botao,
                base_color=BRANCO,
                hovering_color=AZUL
            )

            tela.blit(titulo, titulo.get_rect(center=(LARGURA // 2 + 4, 85)))
            tela.blit(subtitulo, subtitulo.get_rect(
                center=(LARGURA // 2 + 4, 115)))
        tela.blit(fade_img, fade)

        for botao in [botao_jogar, botao_sair]:
            botao.mudar_cor(pos_mouse)
            botao.update_tela(tela)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ativo = False
                pygame.quit()
                sys.exit()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if botao_jogar.checar_clique(pos_mouse):
                    ativo = False
                    jogo_principal()
                elif botao_sair.checar_clique(pos_mouse):
                    ativo = False
                    pygame.quit()
                    sys.exit()

        pygame.display.update()


if __name__ == "__main__":
    menu_principal()
    pygame.quit()
    sys.exit()
