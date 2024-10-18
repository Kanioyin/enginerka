import pygame
import speech_recognition as sr
import random

pygame.init()
pygame.mixer.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ślepy lochołaz")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

recognizer = sr.Recognizer()
microphone = sr.Microphone()

fireball_sound = pygame.mixer.Sound("audio/Bonk.mp3")
wind_blast_sound = pygame.mixer.Sound("audio/Bonk.mp3")
giant_rock_sound = pygame.mixer.Sound("audio/Bonk.mp3")
fury_strike_sound = pygame.mixer.Sound("audio/Bonk.mp3")
lightning_strike_sound = pygame.mixer.Sound("audio/Bonk.mp3")
pygame.mixer.music.load("audio/bbg.ogg")
pygame.mixer.music.play(-1)  # -1 to nieskończona pętla
step_sound = pygame.mixer.Sound("audio/Tup.ogg")
wall_sound = pygame.mixer.Sound("audio/Bonk.mp3")
end_sound = pygame.mixer.Sound("audio/claps.ogg")

MAP_SIZE = 5
player_position = [2, 2]
player_health = 3

movement_synonyms = {
    "góra": ["góra", "w górę", "na północ", "w górę mapy", "do góry"],
    "dół": ["dół", "w dół", "na południe", "na dół"],
    "lewo": ["lewo", "w lewo", "na lewo", "na zachód"],
    "prawo": ["prawo", "w prawo", "na prawo", "na wschód"]
}


def recognize_command():
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Słucham...")
        audio = recognizer.listen(source)
    try:
        command = recognizer.recognize_google(audio, language="pl-PL")
        print(f"Słyszę: {command}")
        return command.lower()
    except sr.UnknownValueError:
        print("Nie rozumiem.")
        return None
    except sr.RequestError:
        print("Błąd sieci.")
        return None


class Spell:
    def __init__(self, name, spell_type, uses_left, activation_command, damage, sound):
        self.name = name
        self.spell_type = spell_type
        self.uses_left = uses_left
        self.activation_command = activation_command
        self.damage = damage
        self.sound = sound

    def cast(self, target):
        if self.uses_left > 0:
            self.uses_left -= 1
            print(f"Rzucasz {self.name}! Pozostało {self.uses_left}.")
            self.sound.play()
            target.take_damage(self.damage, self.spell_type)
        else:
            print(f"Zaklęcie {self.name} nie ma już pozostałych użyć.")


fireball = Spell("Kula Ognia", "Ogień", 2, "kula ognia", 1, fireball_sound)
wind_blast = Spell("Podmuch Wiatru", "Wiatr", 2, "podmuch wiatru", 1, wind_blast_sound)
giant_rock = Spell("Wielki głaz", "Ziemia", 2, "skała", 1, giant_rock_sound)
fury_strike = Spell("Cios gniewu", "Fizyczne", 2, "cios gniewu", 1, fury_strike_sound)
lightning_strike = Spell("Błyskawica", "Elektryczność", 2, "błyskawica", 1, lightning_strike_sound)

class Monster:
    def __init__(self, name, health, weakness, damage, speed, sound_file):
        self.name = name
        self.health = health
        self.weakness = weakness
        self.damage = damage
        self.speed = speed
        self.sound = pygame.mixer.Sound(sound_file)

    def play_sound(self):
        self.sound.play()

    def take_damage(self, amount, damage_type):
        if damage_type == self.weakness:
            amount *= 2
            print(f"{self.name} jest słaby na {damage_type}")
        self.health -= amount
        if self.health > 0:
            print(f"{self.name} ma teraz {self.health} punktów zdrowia.")
        else:
            print(f"{self.name} został pokonany!")


zombi = Monster("Zombi", 2, "Ogień", 1, 1, "audio/Zombi.wav")
zombi2 = Monster("Zombi", 2, "Ogień", 1, 1, "audio/Zombi.wav")
szlam = Monster("Szlam", 2, "Wiatr", 1, 1, "audio/szlamek.mp3")
szlam2 = Monster("Szlam", 2, "Wiatr", 1, 1, "audio/szlamek.mp3")
ognik = Monster("Ognik",2,"Ziemia",1, 1, "audio/szlamek.mp3")
ognik2 = Monster("Ognik",2,"Ziemia",1, 1, "audio/szlamek.mp3")
bandzior = Monster("Bandzior", 2, "Fizyczne", 1, 1, "audio/bandzior.mp3")
bandzior2 = Monster("Bandzior", 2, "Fizyczne", 1, 1, "audio/bandzior.mp3")
latacz = Monster("Latacz", 2, "Elektryczność", 1, 1, "audio/latacz.mp3")
latacz2 = Monster("Latacz", 2, "Elektryczność", 1, 1, "audio/latacz.mp3")

def battle(ph, monster, room):
    monster.play_sound()
    print(f"PVP z {monster.name}.")
    while monster.health > 0:
        command = recognize_command()

        if "kula ognia" in command:
            fireball.cast(monster)
        elif "podmuch wiatru" in command:
            wind_blast.cast(monster)
        elif "skała" in command:
            giant_rock.cast(monster)
        elif "cios gniewu" in command:
            fury_strike.cast(monster)
        elif "błyskawica" in command:
            lightning_strike.cast(monster)
        else:
            print("Nieznane zaklęcie.")

        if monster.health <= 0:
            print(f"Pokonałeś {monster.name}!")
            room.remove_monster()
            break

        ph -= monster.damage
        print(f"{monster.name} atakuje i zadaje {monster.damage} obrażeń. Masz teraz {ph} punktów zdrowia.")

        if ph <= 0:
            print("Zostałeś pokonany!")
            pygame.quit()  # Wyłączenie gry
            exit()


class Room:
    def __init__(self, has_monster=False, is_exit=False):
        self.has_monster = has_monster
        self.monster = None
        self.is_exit = is_exit

    def place_monster(self, monster):
        self.has_monster = True
        self.monster = monster

    def remove_monster(self):
        self.has_monster = False
        self.monster = None

    def enter(self):
        if self.is_exit:
            end_sound.play()
            print("Koniec gry!")
            screen.fill(WHITE)
            font = pygame.font.SysFont(None, 55)
            end_text = font.render("Koniec gry!", True, BLACK)
            screen.blit(end_text, (SCREEN_WIDTH // 2 - end_text.get_width() // 2, SCREEN_HEIGHT // 2))
            pygame.display.flip()
            pygame.time.wait(2000)
            wait_for_exit()
        elif self.has_monster and self.monster:
            print(f"Znalazłeś {self.monster.name}!")
            battle(player_health, self.monster, self)
        else:
            print("Pokój jest pusty.")


def wait_for_exit():
    global running
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                waiting = False
            if event.type == pygame.KEYDOWN:
                running = False
                waiting = False


def generate_dungeon(map_size, num_monsters):
    dungeon_map = [[Room() for _ in range(map_size)] for _ in range(map_size)]

    exit_x, exit_y = random.randint(0, map_size - 1), random.randint(0, map_size - 1)
    dungeon_map[exit_y][exit_x].is_exit = True

    monsters = [zombi, zombi2, szlam, szlam2, ognik, ognik2, bandzior, bandzior2, latacz, latacz2]

    placed_monsters = 0
    while placed_monsters < num_monsters:
        x, y = random.randint(0, map_size - 1), random.randint(0, map_size - 1)

        if not dungeon_map[y][x].has_monster and not dungeon_map[y][x].is_exit:
            dungeon_map[y][x].place_monster(random.choice(monsters))
            placed_monsters += 1

    return dungeon_map


def move_player_on_map(command, player_pos, dungeon_map):
    x, y = player_pos

    if any(synonym in command for synonym in movement_synonyms["góra"]) and y > 0:
        y -= 1
        step_sound.play()
    elif any(synonym in command for synonym in movement_synonyms["dół"]) and y < MAP_SIZE - 1:
        y += 1
        step_sound.play()
    elif any(synonym in command for synonym in movement_synonyms["lewo"]) and x > 0:
        x -= 1
        step_sound.play()
    elif any(synonym in command for synonym in movement_synonyms["prawo"]) and x < MAP_SIZE - 1:
        x += 1
        step_sound.play()
    else:
        wall_sound.play()

    new_room = dungeon_map[y][x]
    new_room.enter()
    return [x, y]


dungeon_map = generate_dungeon(MAP_SIZE, 5)
running = True
while running:
    screen.fill(BLACK)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                print(f"Pozycja gracza: {player_position}")

                command = recognize_command()

                if command == "wyjdź":
                    running = False

                elif command:
                    player_position = move_player_on_map(command, player_position, dungeon_map)

                else:
                    print("Nieznana komenda.")

    pygame.display.flip()

pygame.quit()
