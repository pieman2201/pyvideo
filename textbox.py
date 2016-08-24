import pygame

# TextBox class for pygame by Ishan Kamat


class TextBox(object):
    def __init__(self, prompt, size, fontSize):
        self.text = prompt
        self.size = size
        self.string = ""
        self.fontSize = fontSize
        self.interval = 0
        self.startInput = 0

    def getBase(self):
        size = self.size
        text = self.text
        base = pygame.Surface((size[0], size[1]))
        textfont = pygame.font.SysFont("Courier", self.fontSize)
        pyText = textfont.render(text, True, (255, 255, 255))
        while pyText.get_width() > size[0] - 20:
            text = text[1:]
            textfont = pygame.font.SysFont("Courier", self.fontSize)
            pyText = textfont.render(text, True, (255, 255, 255))
        base.blit(pyText, (2, 0))
        self.startInput = 2 + pyText.get_width()
        textRect1 = pygame.Rect(0, 20, size[0], size[1])
        textRect2 = pygame.Rect(2, 22, size[0] - 4, size[1] - 4)
        pygame.draw.rect(base, (255, 255, 255), textRect1)
        pygame.draw.rect(base, (0, 0, 0), textRect2)
        return base

    def input(self):
        value = ""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise SystemExit
            elif event.type == pygame.KEYDOWN:
                self.interval = 14
                key = event.key
                if key == pygame.K_RETURN:
                    return self.string
                elif key == pygame.K_BACKSPACE:
                    self.string = self.string[:-1]
                else:
                    try:
                        value = chr(key)
                    except:
                        pass
        keys = pygame.key.get_pressed()
        if (keys[303] or keys[304]) and value != "":
            if value.upper() != value.lower():
                value = value.upper()
            elif value == ";":
                value = ":"
            else:
                value = chr(ord(value) + 16)
        elif keys[pygame.K_BACKSPACE]:
            if self.interval == 13:
                self.interval = 12
                self.string = self.string[:-1]
        else:
            pass
        self.string += value

    def getString(self):
        return self.string

    def getFilled(self):
        self.interval += 1
        self.interval %= 24
        fontSize = self.fontSize
        textfont = pygame.font.SysFont("Courier", fontSize)
        fillText = textfont.render(
            self.string + ("|" if self.interval > 12 else " "),
            True,
            (255, 255, 255)
        )
        maxLength = self.size[0] - self.startInput
        newString = self.string
        while fillText.get_width() > maxLength:
            newString = newString[1:]
            print(newString)
            fillText = textfont.render(
                newString + ("|" if self.interval > 12 else " "),
                True,
                (255, 255, 255)
            )
            print(fillText.get_width(), maxLength)
        newbase = self.getBase()
        newbase.blit(fillText, (self.startInput, 0))
        return newbase
