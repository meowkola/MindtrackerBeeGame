import win32gui
import win32ui
from ctypes import windll
from PIL import Image
import pytesseract
import cv2
import pygame
import numpy as np
import time
import random

pytesseract.pytesseract.tesseract_cmd = r"tesseract.exe"

def concentration():
    hwnd = win32gui.FindWindow(None, 'Mind Tracker BCI 1.9.7')
    left, top, right, bot = win32gui.GetWindowRect(hwnd)
    w = right - left
    h = bot - top
    
    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
    saveDC.SelectObject(saveBitMap)
    
    result = windll.user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 0)
    
    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)
    
    im = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)
    
    if result == 1:
        im_cropped = im.crop((240, 695, 240 + 125, 700 + 60))
        
        # Convert to numpy array and preprocess
        opc = np.array(im_cropped)
        gray = cv2.cvtColor(opc, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        
        # Apply morphological transformations
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
        processed_image = cv2.dilate(cv2.erode(thresh, kernel), kernel)

        # Use optimized Tesseract config
        numbers = pytesseract.image_to_string(processed_image, config='--psm 6 -c tessedit_char_whitelist=0123456789')
        
        return numbers.strip()[:2]


pygame.init()
WIDTH, HEIGHT = 1280, 640
FPS = 30
frame = 0


font1 = pygame.font.Font(None, 35)
font2 = pygame.font.Font(None, 80)


score = 0


window = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

img_BG = pygame.image.load("sprites\game-background-vector-7.png")
img_bird = pygame.image.load("sprites\Remove-bg.ai_1733342123439.png")
img_honey = pygame.image.load("sprites\good.png")
img_stars = pygame.image.load("sprites\S001_nyknck.png")
img_bird_2 = pygame.image.load("sprites\SAwe.png")





pipes = []
bges = []
bges.append(pygame.Rect(0, 0, 1280, 640))

con_1 = int(concentration())
py, sy, ay = HEIGHT - (int(con_1) * HEIGHT / 100.05), 0, 0
player = pygame.Rect(WIDTH // 3, py, 100,100)
play = True

last_concentration_time = time.time()  # Время последнего вызова
concentration_interval = 1 / 2


start_time = pygame.time.get_ticks()


while play:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            play = False
    
    # движение BG
    for i in range(len(bges)-1,-1,-1):
        bg = bges[i]
        bg.x -= 3

        if bg.right < 0:
            bges.remove(bg)
        
        if bges[len(bges) - 1].right <= WIDTH:
            bges.append(pygame.Rect(bges[len(bges)-1].right, 0, 1280, 640))





    if len(pipes) == 0 or pipes[len(pipes)-1].x < WIDTH - 300 + random.randint(0, 50):
        pipes.append(pygame.Rect(WIDTH, 30 + random.randint(0, 200), 30, 30))

    for i in range(len(pipes)-1,-1,-1):
        pipe = pipes[i]
        pipe.x -= 5

        if pipe.right < 0:
            pipes.remove(pipe)

    # считывание концентрации
    current_time = time.time()
    if current_time - last_concentration_time >= concentration_interval:
        con = concentration()  # Вызываем функцию только если прошло достаточно времени
        last_concentration_time = current_time  
        if con.isdigit():
            if abs(int(con) - int(con_1)) < 5:
                sy = int(con_1)- int(con)
                # player.y = HEIGHT - (int(con) * (HEIGHT / 102))
                con_1 = int(con)
        # Обновляем время последнего вызова
    player.y += sy


    frame = (frame + 0.6) % 4


    elapsed_time = pygame.time.get_ticks() - start_time  # Время в миллисекундах

    # Преобразуем время в секунды для отображения
    seconds = elapsed_time / 1000

    if player.y < 0:
        player.y = 0 
    if player.y > HEIGHT - 100:
        player.y = HEIGHT - 100
    # # py +=sy
    # # sy = (old_con - con) * 2

    # old_con = con
    # player.y = py


    
    for pipe in pipes:
        if player.colliderect(pipe):
            score+=1
            pipes.remove(pipe)

            

    for bg in bges:
        window.blit(img_BG, bg)

    image = img_bird_2.subsurface(100 * int(frame), 0, 100, 100)
    
    window.blit(image, player)


    for pipe in pipes:
        window.blit(img_honey, pipe)
        

    text = font1.render('Коцентрация: ' + str(con_1), 1, pygame.Color('black'))
    text2 = font1.render('Очки: ' + str(score), 1, pygame.Color('black'))
    text3 = font1.render('Время: ' +  str(round(seconds)), 1, pygame.Color('black'))
    window.blit(text, (10, 10))
    window.blit(text2, (10, 45))
    window.blit(text3, (10,80))

    



    pygame.display.update()
    clock.tick(FPS)
pygame.quit()

