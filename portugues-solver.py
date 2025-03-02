import os
import json
import requests

# Variables
CACHE_DIR = "pt_br_games_cache"
os.makedirs(CACHE_DIR, exist_ok=True)
# API_URL = "https://api.contexto.me/machado/en/top/"
# API_URL = "https://api.contexto.me/machado/es/top/"
API_URL = "https://api.contexto.me/machado/pt-br/top/"

# function : fetch & return game data
def fetch_game(game_id):
    url = f"{API_URL}{game_id}"
    cache_file = os.path.join(CACHE_DIR, f"{game_id}.json")

    if os.path.exists(cache_file):
        # print(f"Jogo {game_id} já existe no cache.")
        with open(cache_file, "r") as f:
            return game_id, json.load(f)

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()

            with open(cache_file, "w") as file:
                json.dump(data, file)

            print(f"Jogo {game_id} baixado e armazenado em cache.")
            return game_id, data
        else:
            print(f"Falha ao buscar o jogo {game_id}: Código de status HTTP {response.status_code}")
            return game_id, None 
    except Exception as e:
        print(f"Erro ao buscar o jogo {game_id}: {e}")
        return game_id, None

# function : find max game-id
def fetch_max_game_id():
    max_id = 1
    while True:
        _, game_data = fetch_game(max_id + 1)
        if game_data is None:
            break
        max_id += 1
    return max_id

# function : fetch all games' data
def fetch_all_games():
    max_game_id = fetch_max_game_id()
    print(f"Buscando todos os jogos até o ID do jogo {max_game_id}...")

    results = []
    for game_id in range(1, max_game_id + 1):
        results.append(fetch_game(game_id))

    return results

# function : scan for target word at target index in the specified game-id
def scan_word(games, target_word, target_index):
    target_word = target_word.lower()
    matches = []
    for game_id, game_data in games:
        if game_data and "words" in game_data:
            words = game_data["words"]

            if target_index < len(words) and words[target_index].lower() == target_word:
                top_word = words[0]
                matches.append((game_id, top_word, words))

    if matches:
        print(f"\nEncontrado '{target_word}' no índice {target_index} nos seguintes jogos:")
        for game_id, top_word, word_list in matches:
            print(f" - ID do jogo: {game_id}")
            print(f"   Palavra superior: '{top_word}'")
            print("   Lista de palavras:")

            first_50 = word_list[:50]
            for i in range(len(first_50)):
                print(f" {(i + 1)}: {first_50[i]}")

            remaining_words = word_list[50:]
            if remaining_words:
                print(" Palavras restantes:", remaining_words, "\n")
    else:
        print(f"\nNão foi possível encontrar '{target_word}' no índice {target_index} em nenhum jogo.")

    return matches

# subprocedure : scan for target word at target index in the specified game-id
def main():
    print("Começando a buscar jogos...")
    games = fetch_all_games()

    while True:
        user_input = input("Digite um ou mais pares de índice de palavras (exemplo: 'house 40 castle 50') ou digite 'exit' para sair: ")

        if user_input.lower() == "exit":
            print("Sair do programa. Adeus!")
            break

        words = user_input.strip().split()
        if len(words) < 2 or len(words) % 2 != 0:
            print("Entrada inválida, insira pares de índice de palavras como 'palavra1 40 palavra2 50'.")
            return

        pairs = []
        for i in range(0, len(words), 2):
            pairs.append((words[i], int(words[i + 1]) - 1))
        
        for word, index in pairs:
            matches = scan_word(games, word, index)
            if not matches:
                print(f"Não foram encontradas correspondências para '{word}' no índice {index}.")

if __name__ == "__main__":
    main()