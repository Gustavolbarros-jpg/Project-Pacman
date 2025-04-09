import pygame
import math
from collections import deque
import heapq

class Perseguidor:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocidade = 2
        self.raio = 9  
        self.cor = (255, 0, 0)
        self.direcao = [0, 0]
        self.caminho = []  # Lista de nós para seguir
        self.grid_size = 30  # Tamanho da célula do grid (ajuste conforme seu labirinto)
        self.ultima_atualizacao_caminho = 0
        self.intervalo_atualizacao_caminho = 500  # Atualiza caminho a cada 1 segundo
        self.resetar_tempo()
        self.velocidade_atual = self.velocidade
        self.fator_velocidade = 0.05
        self.velocidade_max = 2

    def resetar_tempo(self):
        self.tempo_inicial = pygame.time.get_ticks()

    def get_tempo_decorrido(self):
        return (pygame.time.get_ticks() - self.tempo_inicial)/ 1000
    
    def get_velocidade_atual(self):

        tempo_decorrido = self.get_tempo_decorrido()
        velocidade_acumulada =  self.velocidade_atual + (self.fator_velocidade * tempo_decorrido)
        return min(velocidade_acumulada, self.velocidade_max)
        
    def desenhar(self, tela):
        pygame.draw.circle(tela, self.cor, (int(self.x), int(self.y)), self.raio)
        
        # Debug: desenhar o caminho calculado
        for node in self.caminho:
            pygame.draw.rect(tela, (255, 255, 0), 
                           (node[0] * self.grid_size, node[1] * self.grid_size, 
                            self.grid_size, self.grid_size), 1)
    
    def posicao_no_grid(self, x, y):
        """Converte coordenadas para posição no grid"""
        return (int(x // self.grid_size), int(y // self.grid_size))
    
    def construir_grid(self, paredes, largura, altura):
        """Cria uma representação em grid do labirinto"""
        cols = largura // self.grid_size
        rows = altura // self.grid_size
        grid = [[0 for _ in range(cols)] for _ in range(rows)]
        
        for parede in paredes:
            x_start = int(parede.x // self.grid_size)
            y_start = int(parede.y // self.grid_size)
            x_end = int((parede.x + parede.width) // self.grid_size)
            y_end = int((parede.y + parede.height) // self.grid_size)
            
            for y in range(y_start, y_end):
                for x in range(x_start, x_end):
                    if 0 <= y < rows and 0 <= x < cols:
                        grid[y][x] = 1  # 1 representa parede
        return grid
    
    def a_star(self, inicio, objetivo, grid):
        """Implementação do algoritmo A* para encontrar caminho"""
        linhas = len(grid)
        cols = len(grid[0]) if linhas > 0 else 0
        
        # Heurística (distância de Manhattan)
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])
        
        # Vizinhos (cima, baixo, esquerda, direita)
        vizinhos = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        
        open_set = []
        heapq.heappush(open_set, (0, inicio))
        veio_de = {}
        g_score = {inicio: 0}
        f_score = {inicio: heuristic(inicio, objetivo)}
        
        open_set_hash = {inicio}
        
        while open_set:
            atual = heapq.heappop(open_set)[1]
            open_set_hash.remove(atual)
            
            if atual == objetivo:
                # Reconstrói o caminho
                caminho = []
                while atual in veio_de:
                    caminho.append(atual)
                    atual = veio_de[atual]
                caminho.reverse()
                return caminho
                
            for dx, dy in vizinhos:
                vizinho = (atual[0] + dx, atual[1] + dy)
                
                # Verifica se está dentro do grid
                if 0 <= vizinho[0] < cols and 0 <= vizinho[1] < linhas:
                    # Verifica se não é parede
                    if grid[vizinho[1]][vizinho[0]] == 1:
                        continue
                        
                    tentative_g_score = g_score[atual] + 1
                    
                    if vizinho not in g_score or tentative_g_score < g_score[vizinho]:
                        veio_de[vizinho] = atual
                        g_score[vizinho] = tentative_g_score
                        f_score[vizinho] = tentative_g_score + heuristic(vizinho, objetivo)
                        if vizinho not in open_set_hash:
                            heapq.heappush(open_set, (f_score[vizinho], vizinho))
                            open_set_hash.add(vizinho)
        
        return []  # Se não encontrar caminho
    
    def atualizar_caminho(self, player_x, player_y, paredes, largura, altura):
        agora = pygame.time.get_ticks()
        if agora - self.ultima_atualizacao_caminho > self.intervalo_atualizacao_caminho:
            self.ultima_atualizacao_caminho = agora
            
            inicio = self.posicao_no_grid(self.x, self.y)
            objetivo = self.posicao_no_grid(player_x, player_y)
            
            grid = self.construir_grid(paredes, largura, altura)
            self.caminho = self.a_star(inicio, objetivo, grid)
    
    def seguir_caminho(self):
        if not self.caminho:
            return [0, 0]
            
        node_x, node_y = self.caminho[0]
        centro_node_x = node_x * self.grid_size + self.grid_size // 2
        centro_node_y = node_y * self.grid_size + self.grid_size // 2
        
        dx = centro_node_x - self.x
        dy = centro_node_y - self.y
        distancia = math.sqrt(dx*dx + dy*dy)
        
        if distancia < 5:  # Se estiver perto o suficiente do nó
            self.caminho.pop(0)  # Passa para o próximo nó
            return self.seguir_caminho()
        
        # Normaliza a direção
        if distancia > 0:
            return [dx/distancia, dy/distancia]
        return [0, 0]
    
    def perseguir(self, player_x, player_y, paredes, largura, altura):
        self.atualizar_caminho(player_x, player_y, paredes, largura, altura)
        self.direcao = self.seguir_caminho()
        
        # Movimentação
        self.veleocidade_atual = self.get_velocidade_atual()
        novo_x = self.x + self.direcao[0] * self.veleocidade_atual
        novo_y = self.y + self.direcao[1] * self.veleocidade_atual
        
        # Verificação de colisão simplificada (o pathfinding já evita paredes)
        self.x = novo_x
        self.y = novo_y
    
    def verificar_colisao(self, player):
        distancia = math.sqrt((self.x - player.x)**2 + (self.y - player.y)**2)
        return distancia < (self.raio + player.raio)