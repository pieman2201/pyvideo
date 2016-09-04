#!/usr/bin/python3

import pygame
from sys import argv
from textbox import TextBox
from notify import NotifyBar
import os

pygame.init()
path = argv[1]
clock = pygame.time.Clock()
frame_counter = 1
try:
    vpath = path
    p = os.popen("ffmpeg -i " + path + " -r 24 $filename%d.bmp")
    p.read()
    image = pygame.image.load("1.bmp")
    width = image.get_width()
    height = image.get_height()
    print("Image loaded")
except pygame.error:
    print("Editing new image")
    width = int(input("Width: "))
    height = int(input("Height: "))
    image = pygame.Surface((width, height))

if width > 1120:
    width = 1120
if height > 630:
    height = 630

s = pygame.display.set_mode((width, height))
s.blit(image, (0, 0))
pygame.display.set_caption(argv[1])
update = pygame.display.update

penColor = pygame.Color(255, 0, 0)
zoomLevel = 1.0

offset = [0, 0]

undoStack = []
redoStack = []


def getZoomed(surface, scale):
    width = float(surface.get_width()) * scale
    height = float(surface.get_height()) * scale
    return pygame.transform.scale(surface, (int(width), int(height)))
oldPos = (0, 0)
arrows = 0
radius = 1
movepr = 10
crop = False
notifics = NotifyBar(12)


def parseHex(hexStr):
    # assume rrggbb
    r = int(hexStr[0:2], 16)
    g = int(hexStr[2:4], 16)
    b = int(hexStr[4:6], 16)
    return r, g, b


def getRectFromPoints(point1, point2):
    p1x, p1y = point1
    p2x, p2y = point2

    if p2x < p1x:
        left = p2x
    else:
        left = p1x
    if p2y < p1y:
        top = p2y
    else:
        top = p1y
    width = abs(p1x - p2x)
    height = abs(p1y - p2y)
    left = int(left * zoomLevel)
    top = int(top * zoomLevel)
    width = int(width * zoomLevel)
    height = int(height * zoomLevel)

    return pygame.Rect(left, top, width, height)
step = 0
paused = False


def incStep(val=1.0):
    global step
    step += val
    step = step % 12

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            raise SystemExit
        elif event.type == pygame.VIDEORESIZE:
            size = event.dict['size']
            width, height = size
            s = pygame.display.set_mode(size)
        elif event.type == pygame.KEYDOWN:
            key = event.key
            if key == pygame.K_EQUALS:  # plus sign on equals key
                zoomLevel += 0.25
                notifics.addNotification("zoom: " + str(zoomLevel * 100) + "%",
                                         500)
                # print(zoomLevel)
            elif key == pygame.K_MINUS:
                zoomLevel -= 0.25
                if zoomLevel <= 0:
                    zoomLevel = 0.25
                notifics.addNotification("zoom: " + str(zoomLevel * 100) + "%",
                                         500)
                # print(zoomLevel)
            elif key == pygame.K_SPACE:
                paused = not paused
            elif key == pygame.K_UP:
                offset[1] += movepr * zoomLevel
            elif key == pygame.K_DOWN:
                offset[1] -= movepr * zoomLevel
            elif key == pygame.K_LEFT:
                offset[0] += movepr * zoomLevel
            elif key == pygame.K_RIGHT:
                offset[0] -= movepr * zoomLevel
            elif key == pygame.K_c:
                done = False
                colorInput = TextBox("hex: ", (width, 16), 12)
                while not done:
                    hexColor = colorInput.input()
                    if hexColor is not None:
                        R, G, B = parseHex(hexColor)
                        done = True
                    filled = colorInput.getFilled()
                    s.blit(filled, (0, height - filled.get_height()))
                    update()
                    clock.tick(24)
                penColor = pygame.Color(R, G, B)
            elif key == pygame.K_r:
                radInput = TextBox("radius: ", (width, 16), 12)
                done = False
                while not done:
                    radSize = radInput.input()
                    if radSize is not None:
                        radius = int(radSize)
                        done = True
                    filled = radInput.getFilled()
                    s.blit(filled, (0, height - filled.get_height()))
                    update()
                    clock.tick(24)
            elif key == pygame.K_k:
                crop = not crop
                notifics.addNotification("crop: " + ("on" if crop else "off"),
                                         2000)
            elif key == pygame.K_t:
                done = False
                textInput = TextBox("text: ", (width, 16), 12)
                while not done:
                    text = textInput.input()
                    if text is not None:
                        done = True
                    filled = textInput.getFilled()
                    s.blit(filled, (0, height - filled.get_height()))
                    update()
                    clock.tick(24)
                sizeInput = TextBox("size: ", (width, 16), 12)
                done = False
                while not done:
                    size = sizeInput.input()
                    if size is not None:
                        size = int(size)
                        done = True
                    filled = sizeInput.getFilled()
                    s.blit(filled, (0, height - filled.get_height()))
                    update()
                    clock.tick(24)
                hexInput = TextBox("hex: ", (width, 16), 12)
                done = False
                while not done:
                    color = hexInput.input()
                    if color is not None:
                        color = parseHex(color)
                        done = True
                    filled = hexInput.getFilled()
                    s.blit(filled, (0, height - filled.get_height()))
                    update()
                    clock.tick(24)
                notifics.addNotification("location", 10)
                notificsBar = notifics.getBar()

                textfont = pygame.font.SysFont("Courier", size)
                renderedText = textfont.render(text, True, color)

                undoStack.append(image.copy())
                done = False
                while not done:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            raise SystemExit
                    mousePos = pygame.mouse.get_pos()
                    boundsRect = pygame.Rect(mousePos[0], mousePos[1], 0, 0)
                    boundsRect.width = renderedText.get_width() * zoomLevel
                    boundsRect.height = renderedText.get_height() * zoomLevel
                    s.fill((0, 0, 0))
                    s.blit(getZoomed(image, zoomLevel), offset)
                    s.blit(notificsBar, (1, height - notificsBar.get_height()))
                    pygame.draw.rect(s, (255, 255, 255), boundsRect, 2)
                    if pygame.mouse.get_pressed()[0]:
                        done = True
                    update()
                    incStep()
                    clock.tick(24)
                mousePos = (
                    int(float(mousePos[0] - offset[0]) / zoomLevel),
                    int(float(mousePos[1] - offset[1]) / zoomLevel)
                )
                oldPos = mousePos
                image.blit(renderedText, mousePos)
                notifics.addNotification("text added", 750)
            elif key == pygame.K_z:
                if len(undoStack) > 0:
                    redoStack.append(image.copy())
                    image = undoStack.pop()
                    notifics.addNotification("undone", 1000)
                else:
                    notifics.addNotification("nothing to undo", 1000)
            elif key == pygame.K_y:
                if len(redoStack) > 0:
                    undoStack.append(image.copy())
                    image = redoStack.pop()
                    notifics.addNotification("redone", 1000)
                else:
                    notifics.addNotification("nothing to redo", 1000)
            elif key == pygame.K_f:
                undoStack.append(image.copy())
                image = pygame.transform.flip(image, False, True)
                notifics.addNotification("flipped", 500)
            elif key == pygame.K_ESCAPE:
                saveInput = TextBox("save as \"" + path + "\"? [y/n/c]: ",
                                    (width, 16), 12)
                done = False
                while not done:
                    response = saveInput.input()
                    if response is not None:
                        done = True
                    filled = saveInput.getFilled()
                    s.blit(filled, (0, height - filled.get_height()))
                    update()
                    clock.tick(24)
                print("done")
                if response == "y":
                    pygame.image.save(image, path)
                    print("saved")
                elif response == "n":
                    if "\\" in path:
                        while "\\" != path[-1]:
                            path = path[:-1]
                    saveInput = TextBox("save as: ", (width, 16), 12)
                    done = False
                    saveInput.string = path
                    while not done:
                        pathResponse = saveInput.input()
                        if pathResponse is not None:
                            done = True
                        filled = saveInput.getFilled()
                        s.blit(filled, (0, height - filled.get_height()))
                        update()
                        clock.tick(24)
                    pygame.image.save(image, pathResponse)
                    print("saved")
                else:
                    raise SystemExit
                raise SystemExit
    keys = pygame.key.get_pressed()
    if (keys[pygame.K_UP] or keys[pygame.K_DOWN] or keys[pygame.K_RIGHT]
            or keys[pygame.K_LEFT]):
        arrows += 1
    else:
        arrows = 0
    if arrows > 24:
        arrows -= 1
        if keys[pygame.K_UP]:
            offset[1] += movepr * zoomLevel
        if keys[pygame.K_DOWN]:
            offset[1] -= movepr * zoomLevel
        if keys[pygame.K_LEFT]:
            offset[0] += movepr * zoomLevel
        if keys[pygame.K_RIGHT]:
            offset[0] -= movepr * zoomLevel
    mousePos = pygame.mouse.get_pos()
    mousePos = (
        int(float(mousePos[0] - offset[0]) / zoomLevel),
        int(float(mousePos[1] - offset[1]) / zoomLevel)
    )
    if pygame.mouse.get_pressed()[0]:
        undoStack.append(image.copy())
        if crop:
            if mousePos == oldPos:
                undoStack.pop()
            else:
                baseImage = getZoomed(image, zoomLevel)
                startPos = mousePos
                while pygame.mouse.get_pressed()[0]:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            raise SystemExit
                    mousePos = pygame.mouse.get_pos()
                    mousePos = (
                        int(float(mousePos[0] - offset[0]) / zoomLevel),
                        int(float(mousePos[1] - offset[1]) / zoomLevel)
                    )
                    cropRect = getRectFromPoints(startPos, mousePos)
                    rectColor = (255, 255, 255)
                    if int(step) % 2:
                        rectColor = (0, 0, 0)
                    pygame.draw.rect(baseImage, rectColor, cropRect, 2)
                    s.blit(baseImage, offset)
                    update()
                    incStep(0.5)
                    clock.tick(24)
                    baseImage = getZoomed(image, zoomLevel)

                realWidth = round(
                    float(cropRect.width + (offset[0] * 0)) / zoomLevel
                )
                realHeight = round(
                    float(cropRect.height + (offset[1] * 0)) / zoomLevel
                )
                newImage = pygame.Surface((realWidth, realHeight))

                realTop = round(float(cropRect.top) / zoomLevel)
                realLeft = round(float(cropRect.left) / zoomLevel)

                realCropRect = pygame.Rect(
                    realLeft,
                    realTop,
                    realWidth,
                    realHeight
                )
                newImage.blit(image, (0, 0), area=realCropRect)

                cropPrompt = TextBox("crop? [y/n]: ", (width, 16), 12)
                done = False
                while not done:
                    response = cropPrompt.input()
                    if response is not None:
                        done = True
                    filled = cropPrompt.getFilled()
                    s.blit(filled, (0, height - filled.get_height()))
                    update()
                    incStep()
                    clock.tick(24)
                if response == "y":
                    image = newImage
                    width = image.get_width()
                    height = image.get_height()
                    if width > 1120:
                        width = 1120
                    if height > 630:
                        height = 630
                    s = pygame.display.set_mode((width, height))
                    notifics.addNotification("cropped", 750)
                    zoomLevel = 1.0
                    offset = [0, 0]
                else:
                    notifics.addNotification("canceled", 1500)
        else:
            if mousePos == oldPos:
                image.set_at(mousePos, penColor)
            else:
                while pygame.mouse.get_pressed()[0]:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            raise SystemExit
                    mousePos = pygame.mouse.get_pos()
                    mousePos = (
                        int(float(mousePos[0] - offset[0]) / zoomLevel),
                        int(float(mousePos[1] - offset[1]) / zoomLevel)
                    )
                    pygame.draw.line(image, penColor, oldPos, mousePos, radius)
                    s.fill((0, 0, 0))
                    zoomedImage = getZoomed(image, zoomLevel)
                    s.blit(zoomedImage, offset)
                    update()
                    oldPos = mousePos
                    incStep()
                    clock.tick(60)
    s.fill((0, 0, 0))
    zoomedImage = getZoomed(image, zoomLevel)
    s.blit(zoomedImage, offset)
    notificsBar = notifics.getBar()
    s.blit(notificsBar, (1, height - notificsBar.get_height()))
    update()
    oldPos = mousePos
    incStep()
    clock.tick(24)
    if not paused:
        frame_counter += 1
        try:
            pygame.image.save(image, str(frame_counter-1) + ".bmp")
            image = pygame.image.load(str(frame_counter) + ".bmp")
        except:
            p = os.popen(
                "ffmpeg -i $filename%d.bmp -y -r 24 " + path + ".out.mpg"
            )
            p.read()
            frame_counter -= 1
            while frame_counter > 0:
                p = os.popen("rm " + str(frame_counter) + ".bmp")
                p.read()
                frame_counter -= 1
            raise SystemExit
