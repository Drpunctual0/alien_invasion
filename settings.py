class Settings:
    """Uzaylı istilası için bütün ayarları saklayan sınıf"""

    def __init__(self):
        """Oyunun durağan ayarlarına ilk değer atayın"""
        # Ekran ayarları
        self.screen_width = 1200
        self.screen_height = 800
        self.bg_color = (230, 230, 230)

        # Gemi ayarları
        self.ship_limit = 3

        # Mermi ayarları
        self.bullet_width = 3
        self.bullet_height = 20
        self.bullet_color = (60,60,60)
        self.bullets_allowed = 10

        # Uzaylı ayarları
        self.fleet_drop_speed = 10

        # Oyunun ne kadar çabuk hızlandığı
        self.speedup_scale = 1.1

        # Uzaylı puan değerinin ne kadar çabuk arttığı 
        self.score_scale = 1.5

        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self):
        """Oyun boyunca değişen ayarlara ilk değer ata"""
        self.ship_speed = 1.0
        self.bullet_speed = 5.0
        self.alien_speed = 0.3

        # Filo yönü olarak 1 sağı, -1 solu temsil eder
        self.fleet_direction = 1

        # Skor verme
        self.alien_points = 50

    def increase_speed(self):
        """Hız ayarlarını ve uzaylı puan değerlerini arttır"""
        self.ship_speed *= self.speedup_scale
        self.bullet_speed *= self.speedup_scale
        self.alien_speed *= self.speedup_scale
        self.alien_points = int(self.alien_points * self.score_scale)