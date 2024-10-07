import pygame
import speech_recognition as sr
import random

pygame.init()
pygame.mixer.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Szczyl w lochu")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

recognizer = sr.Recognizer()
microphone = sr.Microphone()

# muza
fireball_sound = pygame.mixer.Sound("audio/Bonk.mp3")
wind_blast_sound = pygame.mixer.Sound("audio/Bonk.mp3")
pygame.mixer.music.load("audio/bbg.ogg")
pygame.mixer.music.play(-1)  # -1 to lup do infinita
step_sound = pygame.mixer.Sound("audio/Tup.ogg")
wall_sound = pygame.mixer.Sound("audio/Bonk.mp3")

# niepodległosć
MAP_SIZE = 5
player_position = [2, 2]
player_health = 30


def recognize_command():
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Słucham...")
        audio = recognizer.listen(source)
    try:
        command = recognizer.recognize_google(audio, language="pl-PL")
        print(f"Słysze: {command}")
        return command.lower()
    except sr.UnknownValueError:
        print("Ja nie panimaju")
        return None
    except sr.RequestError:
        print("No necig?")
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


fireball = Spell("Kula Ognia", "Ogień", 3, "kula ognia", 10, fireball_sound)
wind_blast = Spell("Podmuch Wiatru", "Wiatr", 5, "podmuch wiatru", 7, wind_blast_sound)


def activate_spell(command):
    if fireball.activation_command in command:
        fireball.cast()
    elif wind_blast.activation_command in command:
        wind_blast.cast()
    else:
        print("Nieznane zaklęcie.")


class Monster:
    def __init__(self, name, health, weakness, damage, speed):
        self.name = name
        self.health = health
        self.weakness = weakness
        self.damage = damage
        self.speed = speed

    def take_damage(self, amount, damage_type):
        if damage_type == self.weakness:
            amount *= 2
            print(f"{self.name} jest słaby na {damage_type}")
        self.health -= amount
        if self.health > 0:
            print(f"{self.name} ma teraz {self.health} punktów zdrowia.")
        else:
            print(f"{self.name} został pokonany!")


zombi = Monster("Zombi", 10, "Ogień", 3, 1)
szlam = Monster("Szlam", 8, "Wiatr", 2, 2)


def battle(ph, monster, room):
    print(f"Rozpoczyna się walka! Zmierzasz się z {monster.name}.")
    while monster.health > 0:
        print(f"{monster.name} ma {monster.health} punktów zdrowia.")
        command = recognize_command()

        if "kula ognia" in command:
            fireball.cast(monster)
        elif "podmuch wiatru" in command:
            wind_blast.cast(monster)
        else:
            print("Nieznane zaklęcie.")

        if monster.health <= 0:
            print(f"Pokonałeś {monster.name}!")
            room.remove_monster()
            break

        ph -= monster.damage
        print(f"{monster.name} atakuje i zadaje {monster.damage} obrażeń. Masz teraz {player_health} punktów zdrowia.")

        if ph <= 0:
            print("Zostałeś pokonany!")
            break


movement_synonyms = {
    "góra": ["góra", "w górę", "na północ", "w górę mapy", "do góry"],
    "dół": ["dół", "w dół", "na południe", "na dół"],
    "lewo": ["lewo", "w lewo", "na lewo", "na zachód"],
    "prawo": ["prawo", "w prawo", "na prawo", "na wschód"]
}


def move_player_on_map(command, player_pos, dungeon_map):
    x, y = player_pos

    if any(synonym in command for synonym in movement_synonyms["góra"]) and x > 0:
        x -= 1
        step_sound.play()
    elif any(synonym in command for synonym in movement_synonyms["dół"]) and x < 4:
        x += 1
        step_sound.play()
    elif any(synonym in command for synonym in movement_synonyms["lewo"]) and y > 0:
        y -= 1
        step_sound.play()
    elif any(synonym in command for synonym in movement_synonyms["prawo"]) and y < 4:
        y += 1
        step_sound.play()
    else:
        wall_sound.play()

    new_room = dungeon_map[x][y]
    new_room.enter()
    return (x, y)


class Room:
    def __init__(self, has_monster=False):
        self.has_monster = has_monster
        self.monster = None

    def place_monster(self, monster):
        self.has_monster = True
        self.monster = monster

    def remove_monster(self):
        self.has_monster = False
        self.monster = None

    def enter(self):
        if self.has_monster and self.monster:
            print(f"Znalazłeś {self.monster.name}!")
            battle(player_health, self.monster, self)
        else:
            print("Pokój jest pusty.")


def generate_dungeon():
    dungeon_map = [[Room() for _ in range(5)] for _ in range(5)]
    monsters = [Monster("Zombi", 10, "Ogień", 3, 1),
                Monster("Szlam", 8, "Wiatr", 2, 2)]

    for _ in range(5):
        x, y = random.randint(0, 4), random.randint(0, 4)
        if not dungeon_map[x][y].has_monster:
            dungeon_map[x][y].place_monster(random.choice(monsters))
    return dungeon_map


dungeon_map = generate_dungeon()
running = True
while running:
    screen.fill(WHITE)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                print(f"Pozycja gracza: {player_position}")

                command = recognize_command()

                if command:
                    player_position = move_player_on_map(command, player_position, dungeon_map)
                elif command == "exit":
                    running = False
                else:
                    print("Nieznana komenda.")

    pygame.display.flip()

pygame.quit()
