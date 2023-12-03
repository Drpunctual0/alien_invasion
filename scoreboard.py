import pygame.font
from pygame.sprite import Group

from ship import Ship

class Scoreboard:
    """Skor verme bilgisini bildiren bir sınıf"""
    def __init__(self, ai_game):
        """Skor tutan niteliklere ilk değer ata"""
        self.ai_game = ai_game
        self.screen = ai_game.screen
        self.screen_rect = self.screen.get_rect()
        self.settings = ai_game.settings 
        self.stats = ai_game.stats

        # Skor verme bilgisi için yazı tipi ayarları
        self.text_color = (30, 30, 30)
        self.font = pygame.font.SysFont(None, 48)

        # başlangıç skor resmini ayarla
        self.prep_score()
        self.prep_high_score()
        self.prep_level()
        self.prep_ships()


    def prep_score(self):
        """Skoru işlenmiş bir resme dönüştür"""
        rounded_score = round(self.stats.score, -1)
        score_str = "{:,}".format(rounded_score)
        self.score_image = self.font.render(score_str, True, self.text_color, self.settings.bg_color)

        # Skoru ekranın sağ alt köşesinde görüntüle
        self.score_rect = self.score_image.get_rect()
        self.score_rect.right = self.screen_rect.right - 20
        self.score_rect.top = 20

    def prep_level(self):
        """Seviyeyi işlenmiş bir resme dönüştür"""
        level_str = str(self.stats.level)
        self.level_image = self.font.render(level_str, True, self.text_color, self.settings.bg_color)

        # Seviyeyi skorun altına yerleştir
        self.level_rect = self.level_image.get_rect()
        self.level_rect.right = self.score_rect.right
        self.level_rect.top = self.score_rect.bottom + 10

    def prep_ships(self):
        """Kaç gemi kaldığını göster"""
        self.ships = Group()

        for ship_number in range(self.stats.ships_left):
            ship = Ship(self.ai_game)
            ship.rect.x = 10 + ship_number * ship.rect.width
            ship.rect.y = 10
            self.ships.add(ship)


    def prep_high_score(self):
        """Yüksek skoru işlenmiş bir resme dönüştür"""
        high_score = round(self.stats.high_score, -1)
        high_score_str = "{:,}".format(high_score)
        self.high_score_image = self.font.render(high_score_str, True, self.text_color, self.settings.bg_color)

        # Yüksek skoru ekranın üst kısmında merkeze yerleştir
        self.high_score_rect = self.high_score_image.get_rect()
        self.high_score_rect.centerx = self.screen_rect.centerx
        self.high_score_rect.top = self.score_rect.top

    def check_high_score(self):
        """Yeni bir yüksek skor olup olmadığını görmek için denetle"""
        if self.stats.score > self.stats.high_score:
            self.stats.high_score = self.stats.score
            self.prep_high_score()

    def show_score(self):
        """Skorları, seviyeyi ve gemileri ekrana çiz"""
        self.screen.blit(self.score_image, self.score_rect)
        self.screen.blit(self.high_score_image, self.high_score_rect)
        self.screen.blit(self.level_image, self.level_rect)
        self.ships.draw(self.screen)