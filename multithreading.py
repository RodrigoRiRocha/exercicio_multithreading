import requests
import time
import csv
import concurrent.futures

# ============================================================
# CONFIGURAÇÃO
# Obtenha sua chave gratuita em: https://www.themoviedb.org/settings/api
# ============================================================
API_KEY = '42f4ab21b98538807ec02a0ed743af6b'

BASE_URL    = 'https://api.themoviedb.org/3'
MAX_THREADS = 10

# ============================================================
# FUNÇÕES
# ============================================================

def fetch_movie_details(movie):
    """
    Recebe um dicionário com dados básicos de um filme (vindos da lista popular)
    e busca os detalhes completos via API do TMDB.
    Retorna uma lista [título, ano, nota, sinopse] ou None se falhar.
    """
    try:
        movie_id = movie['id']
        url = f'{BASE_URL}/movie/{movie_id}?api_key={API_KEY}&language=en-US'

        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            print(f'[AVISO] Falha ao buscar filme id={movie_id}: status {response.status_code}')
            return None

        data = response.json()

        title  = data.get('title')
        year   = data.get('release_date', '')[:4]
        rating = data.get('vote_average')
        plot   = data.get('overview')

        if all([title, year, rating, plot]):
            print(f'{title} ({year}) - Nota: {rating}')
            return [title, year, rating, plot]

        return None

    except Exception as e:
        print(f'[AVISO] Erro ao buscar filme id={movie.get("id")}: {e}')
        return None


def fetch_popular_movies():
    """
    Busca as primeiras 5 páginas de filmes populares do TMDB (aprox. 100 filmes).
    Retorna uma lista de dicionários com dados básicos de cada filme.
    """
    movies = []
    for page in range(1, 6):
        url = f'{BASE_URL}/movie/popular?api_key={API_KEY}&language=en-US&page={page}'
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f'[ERRO] Falha ao buscar página {page}: status {response.status_code}')
            break
        movies.extend(response.json().get('results', []))
    return movies


def main():
    if not API_KEY or len(API_KEY) < 10:
        print('[ERRO] Insira sua chave de API do TMDB na variável API_KEY.')
        print('       Obtenha gratuitamente em: https://www.themoviedb.org/settings/api')
        return

    start_time = time.time()

    print('[INFO] Buscando lista de filmes populares...')
    movies = fetch_popular_movies()
    print(f'[INFO] {len(movies)} filmes encontrados. Iniciando extração com {MAX_THREADS} threads...\n')

    results = []

    # Multithreading: busca os detalhes de todos os filmes em paralelo
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = executor.map(fetch_movie_details, movies)
        for result in futures:
            if result:
                results.append(result)

    # Salva os resultados em CSV
    with open('movies.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['Title', 'Year', 'Rating', 'Plot'])
        writer.writerows(results)

    end_time = time.time()
    print(f'\n[INFO] {len(results)} filmes salvos em movies.csv')
    print(f'[INFO] Tempo total: {end_time - start_time:.2f}s')


if __name__ == '__main__':
    main()