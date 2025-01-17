import pygame
import speech_recognition as sr
import random

pygame.init()
pygame.mixer.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Krucza Ślepota")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

recognizer = sr.Recognizer()
microphone = sr.Microphone()

fireball_sound = pygame.mixer.Sound("audio/coolaognia.wav")
wind_blast_sound = pygame.mixer.Sound("audio/wiater.mp3")
giant_rock_sound = pygame.mixer.Sound("audio/rocek.ogg")
fury_strike_sound = pygame.mixer.Sound("audio/PUNCH.mp3")
lightning_strike_sound = pygame.mixer.Sound("audio/pierun.mp3")
pygame.mixer.music.load("audio/bbg.ogg")
pygame.mixer.music.play(-1)  # -1 to nieskończona pętla
step_sound = pygame.mixer.Sound("audio/Tup.ogg")
wall_sound = pygame.mixer.Sound("audio/wall.mp3")
end_sound = pygame.mixer.Sound("audio/claps.ogg")
health_sound = pygame.mixer.Sound("audio/heart.mp3")

MAP_SIZE = 5
player_position = [2, 2]
player_health = 3
current_level = 0
quantity_of_levels = 3
stan = "intro"

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
        try:
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=10)
            command = recognizer.recognize_google(audio, language="pl-PL")
            print(f"Słyszę: {command}")
            return command.lower()
        except sr.WaitTimeoutError:
            print("Nie usłyszałem żadnej komendy. Spróbuj ponownie.")
            return None
        except sr.UnknownValueError:
            print("Nie rozumiem. Spróbuj ponownie.")
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
giant_rock = Spell("Skała", "Ziemia", 2, "skała", 1, giant_rock_sound)
fury_strike = Spell("Cios gniewu", "Fizyczne", 2, "cios gniewu", 1, fury_strike_sound)
lightning_strike = Spell("Błyskawica", "Elektryczność", 2, "błyskawica", 1, lightning_strike_sound)
escape_spell = Spell("Ucieczka", "Neutralne", float('inf'), "ucieczka", 0, None)


class Monster:
    def __init__(self, name, health, weakness, resist, damage, speed, enter_sound, dying_sound):
        self.name = name
        self.health = health
        self.max_health = health
        self.weakness = weakness
        self.resist = resist
        self.damage = damage
        self.speed = speed
        self.sound = pygame.mixer.Sound(enter_sound)
        self.dying = pygame.mixer.Sound(dying_sound)

    def play_sound(self):
        self.sound.play()

    def take_damage(self, amount, damage_type):
        if damage_type == self.weakness:
            amount *= 2
            print(f"{self.name} jest słaby na {damage_type}")
        elif damage_type == self.resist:
            amount = 0
            print(f"{self.name} jest odporny na {damage_type}")
            pygame.mixer.Sound("audio/nulbool.mp3").play()
            pygame.time.wait(2000)
        self.health -= amount
        if self.health > 0:
            print(f"{self.name} ma {self.health} hp.")
        else:
            print(f"{self.name} został pokonany!")
            self.dying.play()

    def reset_health(self):
        self.health = self.max_health


zombi = Monster("Zombi", 2, "Ogień", "Elektryczność", 1, 1, "audio/Zombi.wav", "audio/Bonk.mp3")
zombi2 = Monster("Zombi", 2, "Ogień", "Elektryczność", 1, 1, "audio/Zombi.wav", "audio/Bonk.mp3")
szlam = Monster("Szlam", 2, "Wiatr", "Fizyczne", 1, 1, "audio/szlamek.mp3", "audio/Bonk.mp3")
szlam2 = Monster("Szlam", 2, "Wiatr", "Fizyczne", 1, 1, "audio/szlamek.mp3", "audio/Bonk.mp3")
ognik = Monster("Ognik", 2, "Ziemia", "Wiatr", 1, 1, "audio/ognik.ogg", "audio/Bonk.mp3")
ognik2 = Monster("Ognik", 2, "Ziemia", "Wiatr", 1, 1, "audio/ognik.ogg", "audio/Bonk.mp3")
bandzior = Monster("Bandzior", 2, "Fizyczne", "Ziemia", 1, 1, "audio/bandzior.mp3", "audio/Bonk.mp3")
bandzior2 = Monster("Bandzior", 2, "Fizyczne", "Ziemia",1, 1, "audio/bandzior.mp3", "audio/Bonk.mp3")
latacz = Monster("Latacz", 2, "Elektryczność","Ogień", 1, 1, "audio/latacz.ogg", "audio/Bonk.mp3")
latacz2 = Monster("Latacz", 2, "Elektryczność", "Ogień",1, 1, "audio/latacz.ogg", "audio/Bonk.mp3")


def battle(monster, room, previous_position, player_position):
    pygame.mixer.Sound("audio/batcom.mp3").play()
    pygame.time.wait(2000)
    global player_health
    monster.play_sound()
    pygame.time.wait(2000)
    print(f"Walka z {monster.name}.")
    spells = [fireball, wind_blast, giant_rock, fury_strike, lightning_strike]

    while monster.health > 0:
        pygame.mixer.Sound("audio/whatatk.mp3").play()
        pygame.time.wait(1500)
        command = None
        while not command:
            command = recognize_command()
            if not command:
                continue

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
            elif "ucieczka" in command:
                return previous_position
            else:
                random_spell = random.choice(spells)
                random_spell.cast(monster)

            pygame.time.wait(1000)

        if monster.health <= 0:
            room.remove_monster()
            break

        player_health -= monster.damage
        print(f"{monster.name} atakuje masz {player_health} hp.")
        pygame.mixer.Sound("audio/bool.mp3").play()
        pygame.time.wait(1000)
        if player_health <= 0:
            print("Zostałeś pokonany!")
            pygame.quit()
            exit()

    return player_health, player_position


class Upgrade:
    def __init__(self, name, effect):
        self.name = name
        self.effect = effect

    def apply(self):
        self.effect()


def heal_player():
    global player_health
    player_health = min(player_health + 1, 3)
    pygame.mixer.Sound("audio/heal.mp3").play()
    pygame.time.wait(2200)


def restore_spells():
    global fireball, wind_blast, giant_rock, fury_strike, lightning_strike
    fireball.uses_left = 2
    wind_blast.uses_left = 2
    giant_rock.uses_left = 2
    fury_strike.uses_left = 2
    lightning_strike.uses_left = 2


def increase_spell_capacity():
    global fireball, wind_blast, giant_rock, fury_strike, lightning_strike
    fireball.uses_left += 1
    wind_blast.uses_left += 1
    giant_rock.uses_left += 1
    fury_strike.uses_left += 1
    lightning_strike.uses_left += 1
    print("Liczba użyć zaklęć została zwiększona o 1.")


upgrades = [
    Upgrade("Uleczenie", heal_player),
    Upgrade("Odnowienie zaklęć", restore_spells),
    Upgrade("Zwiększenie liczby zaklęć", increase_spell_capacity)
]


def find_upgrade():
    upgrade = random.choice(upgrades)
    print(f"Ulepszenie: {upgrade.name}!")
    upgrade.apply()


class Room:
    def __init__(self, has_monster=False, is_exit=False, has_upgrade=False):
        self.has_monster = has_monster
        self.monster = None
        self.is_exit = is_exit
        self.has_upgrade = has_upgrade

    def place_monster(self, monster):
        self.has_monster = True
        self.monster = monster

    def remove_monster(self):
        self.has_monster = False
        self.monster = None

    def place_upgrade(self):
        self.has_upgrade = True

    def enter(self):
        global current_level, quantity_of_levels
        if self.is_exit:
            if current_level < quantity_of_levels - 1:
                next_level()
            else:
                end_game()
        elif self.has_monster and self.monster:
            print(f"Znalazłeś {self.monster.name}!")
            battle(player_health, self.monster, self)
        elif self.has_upgrade:
            find_upgrade()
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
            selected_monster = random.choice(monsters)
            monsters.remove(selected_monster)
            dungeon_map[y][x].place_monster(selected_monster)
            placed_monsters += 1

    upgrade_x, upgrade_y = random.randint(0, map_size - 1), random.randint(0, map_size - 1)
    dungeon_map[upgrade_y][upgrade_x].place_upgrade()

    return dungeon_map


def move_player_on_map(command, player_pos, dungeon_map):
    global player_position
    x, y = player_pos
    previous_position = [x, y]

    if any(synonym in command for synonym in movement_synonyms["góra"]) and y > 0:
        y -= 1
    elif any(synonym in command for synonym in movement_synonyms["dół"]) and y < MAP_SIZE - 1:
        y += 1
    elif any(synonym in command for synonym in movement_synonyms["lewo"]) and x > 0:
        x -= 1
    elif any(synonym in command for synonym in movement_synonyms["prawo"]) and x < MAP_SIZE - 1:
        x += 1
    else:
        wall_sound.play()
        pygame.time.wait(3500)
        return [x, y]

    step_sound.play()
    new_room = dungeon_map[y][x]

    if new_room.has_monster and new_room.monster:
        if not battle(new_room.monster, new_room, previous_position, player_position):
            return previous_position
    else:
        new_room.enter()

    player_position = [x, y]
    return [x, y]


def next_level():
    global current_level, dungeon_map, player_position
    current_level += 1

    if current_level < quantity_of_levels:
        print(f"Poziom {current_level + 1}!")
        pygame.mixer.Sound("audio/down.mp3").play()
        pygame.time.wait(2000)
        for row in dungeon_map:
            for room in row:
                if room.has_monster and room.monster:
                    room.monster.reset_health()

        dungeon_map = generate_dungeon(MAP_SIZE, 5)
        player_position = [2, 2]
    else:
        end_game()


def end_game():
    end_sound.play()
    screen.fill(WHITE)
    pygame.display.flip()
    pygame.mixer.Sound("audio/outro.mp3").play()
    pygame.time.wait(11000)
    pygame.quit()
    exit()


running = True
dungeon_map = generate_dungeon(MAP_SIZE, quantity_of_levels)
while running:
    screen.fill(BLACK)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if stan == "intro":
        pygame.mixer.Sound("audio/pyt1.mp3").play()
        pygame.time.wait(1000)
        command = recognize_command()
        if not command:
            continue

        if "tak" in command:
            stan = "tutor"

        elif "nie" in command:
            pygame.mixer.Sound("audio/sprintro.mp3").play()
            pygame.time.wait(51000)
            stan = "tutor"

        else:
            continue

    if stan == "tutor":
        pygame.mixer.Sound("audio/pyt2.mp3").play()
        pygame.time.wait(1000)
        command = recognize_command()
        if not command:
            continue

        if "tak" in command:
            stan = "gra"

        elif "nie" in command:
            pygame.mixer.Sound("audio/tutor.mp3").play()
            pygame.time.wait(33000)
            stan = "gra"

        else:
            continue

    if stan == "gra":
        pygame.mixer.Sound("audio/ask.mp3").play()
        pygame.time.wait(1000)
        command = recognize_command()

        if not command:
            print("Nie rozpoznano komendy.")
            continue

        if command == "wyjdź":
            running = False

        elif "stan" in command:
            print(f"Zdrowie: {player_health}")
            for _ in range(player_health):
                health_sound.play()
                pygame.time.wait(1000)

        elif command:
            player_position = move_player_on_map(command, player_position, dungeon_map)
            print(f"Pozycja gracza: {player_position},{current_level}")

        else:
            print("Nieznana komenda.")

        pygame.display.flip()

    else:
        pygame.quit()

pygame.quit()
