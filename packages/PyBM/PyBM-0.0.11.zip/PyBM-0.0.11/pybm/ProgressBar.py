import pygame

class ProgressBar():
    def __init__(self, screen, x, y, barwidth, barheight, name, font, queue_position=None):
        self.screen = screen
        self.color = (102, 170, 255)
        self.bgcolor = (0, 0, 0)
        self.txt_color = (255, 255, 255)
        self.x = x
        self.y = y
        self.width = barwidth
        self.height = barheight
        self.font = font
        self.textsize = self.font.size(name)
        self.text = self.font.render(name, True, self.txt_color)
        self.barspace = pygame.Surface((self.width, self.height))
        self.bar = pygame.Surface((self.width, self.height))
        self.queue_position = queue_position

    def update(self, percent):
        if percent > 100:
            percent = 100
        if percent < 0:
            percent = 0
        #pygame.draw.rect(self.bar, self.color, (0, 0, self.width, self.height), 2)
        #self.bar = pygame.Surface(((percent*self.width)/100, self.height))
        #fill_gradient(self.bar, self.color, ERROR)
        pygame.draw.rect(self.bar, self.color, (0, 0, (percent*self.width)/100, self.height), 0)
        self.barspace.blit(self.bar, ((0, 0)))
        self.barspace.blit(self.text, ((self.width/2)-(self.textsize[0]/2), (self.height/2)-(self.textsize[1]/2)))
        if not self.queue_position is None:
            self.queue_textsize = self.font.size(str(self.queue_position))
            self.queue_text = self.font.render(str(self.queue_position), True, self.txt_color)
            # self.barspace.blit(self.queue_text, (20, (self.height/2)-(self.textsize[1]/2)))
            self.barspace.blit(self.queue_text, (self.width-self.queue_textsize[0], 0))
        self.screen.blit(self.barspace, (self.x, self.y))

    def set_color(self, color):
        self.color = color

    def set_alpha(self, alpha):
        self.bar.set_alpha(alpha)