import os
import json
import requests

# Variables
CACHE_DIR = "en_games_cache"
os.makedirs(CACHE_DIR, exist_ok=True)
API_URL = "https://api.contexto.me/machado/en/top/"
# API_URL = "https://api.contexto.me/machado/es/top/"
# API_URL = "https://api.contexto.me/machado/pt-br/top/"

# function : fetch & return game data
def fetch_game(game_id):
    url = f"{API_URL}{game_id}"
    cache_file = os.path.join(CACHE_DIR, f"{game_id}.json")

    if os.path.exists(cache_file):
        # print(f"Game {game_id} already exists in cache.")
        with open(cache_file, "r") as f:
            return game_id, json.load(f)

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()

            with open(cache_file, "w") as file:
                json.dump(data, file)

            print(f"Game {game_id} downloaded and cached.")
            return game_id, data
        else:
            print(f"Failed to fetch game {game_id}: HTTP Status Code {response.status_code}")
            return game_id, None 
    except Exception as e:
        print(f"Error fetching game {game_id}: {e}")
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
    print(f"Fetching all games up to Game ID {max_game_id}...")

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
        print(f"\nFound '{target_word}' at index {target_index} in the following games:")
        for game_id, top_word, word_list in matches:
            print(f" - Game ID: {game_id}")
            print(f"   Top Word: '{top_word}'")
            print("   Word List:")

            first_50 = word_list[:50]
            for i in range(len(first_50)):
                print(f" {(i + 1)}: {first_50[i]}")

            remaining_words = word_list[50:]
            if remaining_words:
                print(" Remaining Words:", remaining_words, "\n")
    else:
        print(f"\nCould not find '{target_word}' at index {target_index} in any game.")

    return matches

# subprocedure : scan for target word at target index in the specified game-id
def main():
    print("Starting to fetch games...")
    games = fetch_all_games()

    while True:
        user_input = input("Enter one or more word-index pairs (example: 'house 40 castle 50') or type 'exit' to quit: ")

        if user_input.lower() == "exit":
            print("Exiting the program. Goodbye!")
            break

        words = user_input.strip().split()
        if len(words) < 2 or len(words) % 2 != 0:
            print("Invalid input, please enter word-index pairs like 'word1 40 word2 50'.")
            return

        pairs = []
        for i in range(0, len(words), 2):
            pairs.append((words[i], int(words[i + 1]) - 1))
        
        for word, index in pairs:
            matches = scan_word(games, word, index)
            if not matches:
                print(f"No matches found for '{word}' at index {index}.")

if __name__ == "__main__":
    main()