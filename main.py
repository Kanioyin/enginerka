import sys
import pygame
import speech_recognition as sr

pygame.init()
pygame.mixer.init()
screen_width, screen_height = (700, 400)
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('State of slow decay')
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
bg_music = pygame.mixer.Sound('audio/bbg.ogg')
bg_music.play(loops=-1)
locations = ["Mill","Start","Center",]

recognizer = sr.Recognizer()

def recognize_speech_from_mic(recognizer, microphone):
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        print('Ready to listen...')
        audio = recognizer.listen(source)

    try:
        print('Recognizing...')
        response = recognizer.recognize_google(audio)
        print(f'You said: {response}')
        if response == "exit" or response == "quit":
            pygame.quit()
            sys.exit()

        return response
    except sr.UnknownValueError:
        print('Sorry, speech was unintelligible. Try again.')
        return None
    except sr.RequestError:
        print('Sorry, the speech service is down.')
        return None

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:  #spacja
                text = recognize_speech_from_mic(recognizer, sr.Microphone())
                if text == "quit":
                    running = False

                if text:
                    screen.fill(BLACK)
                    font = pygame.font.SysFont(None, 48)
                    text_surface = font.render(text, True, WHITE)
                    text_rect = text_surface.get_rect(center=(screen_width/2, screen_height/2))
                    screen.blit(text_surface, text_rect)

    pygame.display.flip()

pygame.quit()
sys.exit()