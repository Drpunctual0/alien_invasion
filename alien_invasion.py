import sys
from time import sleep

import pygame

from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien

class AlienInvasion:
    """Oyunu başlat ve davranışını yönetmek için genel bir sınıf"""

    def __init__(self):
        """Oyunu başlatın ve oyunun kaynaklarını oluşturun"""
        pygame.init()
        self.settings = Settings()

        self.screen = pygame.display.set_mode((self.settings.screen_width, self.settings.screen_height))
        # Full ekran
        # self.screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect(). width
        self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption("Alien Invasion")

        # Bir scoreboard ve oyun istatistiklerini saklamak için bir örnek oluştur 
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)


        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self._create_fleet()

        # Play düğmesini oluştur
        self.play_button = Button(self, "Play")
    
    def run_game(self):
        """Oyun için ana döngüyü başlat"""
        while True:
            self._check_events()

            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()

            self._update_screen()
    

    def _check_events(self):
        """Tuşa basma ve fare olaylarına yanıt ver"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)
    
    def _check_play_button(self, mouse_pos):
        """Oyuncu Play'e tıkladığında yeni oyuna başla"""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            # Oyun istatistiklerini resetle
            self.settings.initialize_dynamic_settings()
            self.stats.reset_stats()
            self.stats.game_active = True
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()

            # Geri kalan uzaylılar ve mermilerden kurtul
            self.aliens.empty()
            self.bullets.empty()

            # Yeni bir filo oluştur ve gemiyi merkeze yerleştir
            self._create_fleet()
            self.ship.center_ship()

            # Fare imlecini gizle
            pygame.mouse.set_visible(False)

    
    def _check_keydown_events(self, event):
        """Tuşa basmalara yanıt ver"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()
    
    def _check_keyup_events(self, event):
        """Tuşu serbest bırakmalara yanıt ver"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False
    
    def _fire_bullet(self):
        """Yeni bir mermi oluştur ve bu mermiyi mermi grubuna ekle"""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)    

    def _update_bullets(self):
        """Mermilerin konumunu güncelle ve mermilerden kurtul"""
        # Mermilerin konumunu güncelle
        self.bullets.update()

        # Kaybolan mermilerden kurtul
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):   
        """Mermi-uzaylı çarpışmasına yanıt ver"""
        #  Çarpışan mermi ve uzaylıları sil
        collisions = pygame.sprite.groupcollide(self.bullets, self.aliens, True, True)

        if collisions:
            
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * (len(aliens))
                  
            self.sb.prep_score()
            self.sb.check_high_score()

        if not self.aliens:
            # Var olan mermileri imha et ve yeni filo oluştur
            # self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

            # Seviyeyi arttır
            self.stats.level += 1
            self.sb.prep_level()

    def _update_aliens(self):
        """Filonun kenarda olup olmadığını kontrol et"""      
        """Daha sonra tüm uzaylıların konumunu güncelle"""
        
        self._check_fleet_edges()
        self.aliens.update()

        # Uzaylı gemi çarpışmalarına bak
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()
        
        # Ekranın eltına vuran uzaylıları ara
        self._check_aliens_bottom()

    def _check_aliens_bottom(self):
        """Herhangi bir uzaylının ekranın alt tarafına ulaşıp ulaşmadığını kontol et"""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # Buna gemiye çarpıldığında olduğu gibi muamele et
                self._ship_hit()
                break

    def _ship_hit(self):
        """Uzaylı tarafından vurulan gemiye yanıt ver"""
        if self.stats.ships_left > 0:
            # Ship_left i azalt ve scoreboard u güncelle
            self.stats.ships_left -= 1
            self.sb.prep_ships()

            # Geri kalan uzaylı ve mermilerden kurtul
            self.aliens.empty()
            self.bullets.empty()

            # Yeni bir filo oluştur ve gemiyi merkeze koy 
            self._create_fleet()
            self.ship.center_ship()
            
            # Durdur
            sleep(0.5)
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)

    def _create_fleet(self):
        """Uzaylı filosunu oluştur"""
        # Bir uzaylı oluştur ve bir satırdaki uzaylı sayısını bul
        # Her bir uzaylı arasındak, boşluk bir uzaylı genişliğine eşittir
        # Bir uzaylı oluştur
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_aliens_x = available_space_x // (2 * alien_width)

        # Ekrana sığan uzaylı satırları  sayısını belirle
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height - (3 * alien_height) - ship_height)
        number_rows = available_space_y // (2 * alien_height)

        # Tüm bir uzaylı filosunu oluştur
        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                self._create_alien(alien_number, row_number)        


    def _create_alien(self, alien_number, row_number):
        """Bir uzaylı oluştur ve satıra yerleştir"""
        alien = Alien(self)
        alien_width, alien_height  = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)

    def _check_fleet_edges(self):
        """Herhangi bir uzaylı bir kenara ulaştığında uygun bir şekilde yanıt ver"""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break
    
    def _change_fleet_direction(self):
        """Tüm bir filoyu düşür ve filonun yönünü değiştir"""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1


    def _update_screen(self):
        """Ekrandaki resimleri güncelle ve yeni ekrana dön"""
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()

        self.aliens.draw(self.screen)

        # Skor bilgisini çiz
        self.sb.show_score()

        # Oyun aktif değilse play düğmesini çiz
        if not self.stats.game_active:
            self.play_button.draw_button()
        
        pygame.display.flip()


if __name__ == '__main__':
    """Bir oyun örneği oluştur ve çalıştır"""
    ai = AlienInvasion()
    ai.run_game()