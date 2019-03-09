import pygame
import pandas as pd
from os import path
from collections import defaultdict
from heapq import *
from pygame.locals import *
from math import ceil, sqrt

# Constantes:
ROOT_DIR = path.dirname(path.abspath(__file__)) # Diretório raiz do projeto.
COLOR_BLACK = (0,0,0)   # RGB da cor preta.
COLOR_WHITE = (255,255,255) # RGB da cor branca.
SCREEN_SIZE = (800, 600)    # Dimensões da janela.
FONT_SIZE = 11  # Tamanho da fonte.
DOT_RADIUS = 4  # Raio dos pontos do mapa.
LINE_WIDTH = 2  # Espessura das linhas de rota.

# Carrega a imagem do mapa.
vale_map_img = pygame.transform.scale(pygame.image.load(path.join(ROOT_DIR, 'mapa_vale.png')), SCREEN_SIZE)

pygame.init()   # Inicializa os módulos do pygame.
pygame.display.set_caption('Projeto Vale do Paraíba')   # Altera o título da janela.

screen = pygame.display.set_mode(SCREEN_SIZE)    # Altera as dimensões da janela.

sys_font = pygame.font.SysFont('Comic Sans MS', FONT_SIZE) # Carrega uma fonte específica do sistema para uso.
title_font = pygame.font.SysFont('Comic Sans MS', FONT_SIZE+10) # Carrega uma fonte específica do sistema para uso.
medium_font = pygame.font.SysFont('Comic Sans MS', FONT_SIZE+2)

# Classe que representa os dados que serão carregados do arquivo dist_vale.csv
class Node:
    # Construtor da classe.
    def __init__(self):
        self.name = None
        self.neighbours = set()
        self.distance = None

    # Retorna o nome do município.
    def get_name(self):
        return self.name

    # Altera o nome do município.
    def set_name(self, name):
        self.name = name

    # Retorna a distância do município para o seu vizinho.
    def get_distance(self):
        return self.distance

    # Altera a distância do município para o seu vizinho.
    def set_distance(self, distance):
        self.distance = distance

    # Retorna a lista de vizinhos do município.
    def get_neighbours(self):
        return self.neighbours

    # Adiciona um vizinho ao município.
    def add_neighbour(self, neighbour):
        self.neighbours.add(neighbour)

# Classe que representa os pontos de cada municipio no mapa.
class MapDot():
    # Construtor da classe.
    def __init__(self, name, pos):
        self.name = name
        self.pos = pos
        self.rect = Rect((pos[0], pos[1]), (DOT_RADIUS+2, DOT_RADIUS+2))

    # Retorna o nome do município.
    def get_name(self):
        return self.name

    # Retorna a posição do ponto no mapa.
    def get_pos(self):
        return self.pos

    # Retorna o retângulo de colisão do ponto.
    def get_rect(self):
        return self.rect

# Retorna um Node já existente na lista de nodes, caso contrário retorna None.
# Útil para evitar ligações redundantes entre municípios.
def already_exists(name, lst):
    for node in lst:
        if node.get_name() == name:
            return node
    return None

# Retorna o objeto de um ponto específico do mapa pelo nome do município.
def get_city_byname(cities, name):
    for city in cities:
        if city.get_name() == name:
            return city
    return None

# Algoritmo de Dijkstra para encontrar a rota mais curta entre dois municípios.
def dijkstra(edges, f, t):
    g = defaultdict(list)
    for l,r,c in edges:
        g[l].append((c,r))
    q, seen, mins = [(0,f,())], set(), {f: 0}
    while q:
        (cost,v1,path) = heappop(q)
        if v1 not in seen:
            seen.add(v1)
            path = (v1, path)
            if v1 == t: return (cost, path)
            for c, v2 in g.get(v1, ()):
                if v2 in seen: continue
                prev = mins.get(v2, None)
                next = cost + c
                if prev is None or next < prev:
                    mins[v2] = next
                    heappush(q, (next, v2, path))
    return float("inf")

# Início de Main.
if __name__ == "__main__":

    # Faz a leitura dos dados contidos no arquivo dist_vale.csv e cria uma tabela.
    data = pd.read_csv(path.join(ROOT_DIR, 'dist_vale.csv'), sep=',', encoding='utf-8')
    values = data.values    # Transforma os valores da tabela em uma matriz.

    # Varre a matriz e cria uma lista de Nodes.
    nodes = list()
    for i in range(len(values)):
        current_city = values[i][0]
        current_node = already_exists(current_city, nodes)
        if current_node:
            new_neighbour = Node()
            new_neighbour.set_name(values[i][1])
            new_neighbour.set_distance(values[i][2])
            current_node.add_neighbour(new_neighbour)
        else:
            new_node = Node()
            new_node.set_name(values[i][0])
            new_neighbour = Node()
            new_neighbour.set_name(values[i][1])
            new_neighbour.set_distance(values[i][2])
            new_node.add_neighbour(new_neighbour)
            nodes.append(new_node)

    # Varre a lista de Nodes e cria a lista de Vértices para uso no algoritmo de Dijkstra.
    edges = list()
    for node in nodes:
        for neighbour in node.get_neighbours():
            new_edge = (node.get_name(), neighbour.get_name(), neighbour.get_distance())
            edges.append(new_edge)

    # Faz a leitura das posições dos pontos no mapa, contidos no arquivo map_dots.csv
    map_data = pd.read_csv(path.join(ROOT_DIR, 'map_dots.csv'), sep=',', encoding='utf-8')
    map_values = map_data.values    # Transforma os dados em uma matriz.

    # Cria os MapDots que representam os pontos no mapa.
    map_cities = [MapDot(map_values[i][0], (map_values[i][1], map_values[i][2])) for i in range(len(map_values))]
    city_count = len(map_cities)

    route_path = None   # Variável do município atual.
    route_dist = None   # Variável da distância da rota atual.
    from_city = None    # Variável do município de origem.
    to_city = None      # Variável do município de destino.
    central_city = None  # Variável do município central.

    showing_center = False  # Determina se o município central será destacada no mapa.

    running = True  # Determina se o programa está ativo.
    while running:
        pygame.event.pump() # Atualiza os eventos do pygame.

        mouse_pos = pygame.mouse.get_pos()  # Atualiza a posição do ponteiro do mouse.
        mouse_rect = Rect((mouse_pos[0], mouse_pos[1]), (4, 4)) # Atualiza o retângulo de colisão do ponteiro do mouse.

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                # Algoritmo que determina a cidade central ao pressionar a tecla Espaço.
                elif event.key == pygame.K_SPACE:
                    if not showing_center:
                        smallest_sum = float('inf') # Menor soma começa como Infinito.
                        for i in range(city_count): # O valor de i representa o índice do município de origem.
                            s = 0   # A variável s armazena a soma das distâncias entre o município de origem e o município de destino.
                            for j in range(city_count): # O valor de j representa o índice do município de destino.
                                if (j == i):    # Pula para a próxima iteração caso o valor de i e j sejam iguais.
                                    continue
                                path = dijkstra(edges, map_cities[i].get_name(), map_cities[j].get_name()) # Determina a menor rota entre os dois municípios.
                                s += path[0]    # Soma a distância da nova rota na variável s.
                            if s < smallest_sum:    # Verifica se a distância da nova rota é a menor de todas.
                                smallest_sum = s
                                central_city = map_cities[i] # Armazena o novo município central.
                        print('Center City:', central_city.get_name())   # Imprime o nome do município central.
                        showing_center = True   # Ativa o destaque do município central.
                    else:
                        showing_center = False  # Desativa o destaque do município central.
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:   # Botão direito do mouse determina o município de origem do mapa.
                    for city in map_cities:
                        if city.get_rect().colliderect(mouse_rect): # Verifica se o retângulo do ponteiro colide com o retângulo do ponto no mapa.
                            from_city = city.get_name()
                elif event.button == 3: # Botão esquerdo do mouse determina o município de destino do mapa.
                    for city in map_cities:
                        if city.get_rect().colliderect(mouse_rect):
                            to_city = city.get_name()
                if from_city and to_city:   # Traça a rota entre os municípios escolhidos no mapa.
                    make_path = lambda tup: (*make_path(tup[1]), tup[0]) if tup else ()
                    path = dijkstra(edges, from_city, to_city)
                    route_dist = path[0]
                    route_path = make_path(path[1])
                    # Imprime a rota no console.
                    print('\nRota: {} ate {}\nDistancia: aprox. {} km.\nPercurso: {}\n'.format(from_city, to_city, ceil(route_dist), route_path))

        screen.fill(COLOR_WHITE)    # Preenche o fundo com a cor específica.
        screen.blit(vale_map_img, (0, 0))   # Desenha a imagem do mapa.

        for city in map_cities: # Varre a lista de municípios e os desenha no mapa.
            pygame.draw.circle(screen, COLOR_BLACK, city.get_pos(), DOT_RADIUS) # Desenha o ponto no mapa.
            name_text = medium_font.render(city.get_name(), True, COLOR_BLACK)    # Cria o texto do nome.
            screen.blit(name_text, (city.get_pos()[0]-len(city.get_name())*3, city.get_pos()[1]))   # Desenha o nome no mapa.

        if showing_center:  # Desenha as linhas que destacam o município central.
            for i in range(city_count):
                pygame.draw.line(screen, COLOR_BLACK, central_city.get_pos(), map_cities[i].get_pos(), LINE_WIDTH)
                title_text = title_font.render('Município Central: Município de {}.'.format(central_city.get_name()), True, COLOR_BLACK)
                screen.blit(title_text, (SCREEN_SIZE[0]/3 - 70, 0))
        elif route_path:    # Desenha as linhas da rota atual.
            for i in range(len(route_path)-1):
                pygame.draw.line(screen, COLOR_BLACK, get_city_byname(map_cities, route_path[i]).get_pos(), get_city_byname(map_cities, route_path[i+1]).get_pos(), LINE_WIDTH)
                title_text = title_font.render('Rota: {} até {}, Distância: aprox. {} km.'.format(from_city, to_city, ceil(route_dist)), True, COLOR_BLACK)
                screen.blit(title_text, (SCREEN_SIZE[0]/4 - 70, 0))


        pygame.display.flip()   # Atualiza a janela do programa.
