import pygame, time

class NotifyBar(object):
    def __init__(self, fontSize):
        self.fontSize = fontSize
        self.notifications = []
        self.params = {}
        self.number = 0

    def addNotification(self, text, duration):
        self.notifications.append(self.number)
        self.params[self.number] = (time.time() * 1000, duration, text)
        self.number += 1

    def cleanNotifications(self):
        for notification in self.notifications:
            values = self.params[notification]
            if time.time() * 1000 > values[0] + values[1]:
                del self.params[notification]
                self.notifications.remove(notification)

    def getBar(self):
        self.cleanNotifications()
        if len(self.notifications) > 0:
            notification = self.notifications[-1]
            notification = self.params[notification][2]
            textfont = pygame.font.SysFont("Courier", self.fontSize)
            notipy = textfont.render(notification, True, (255, 255, 255))
            return notipy
        else:
            return pygame.Surface((0,0))