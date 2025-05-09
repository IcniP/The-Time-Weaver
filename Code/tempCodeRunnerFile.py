    self.map_w = tmx_map.width * TILE_SIZE
        self.map_h = tmx_map.height * TILE_SIZE

        # Load ground tiles
        for x, y, image in tmx_map.get_layer_by_name('ground').tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, (self.all_sprites, self.collision_sprites))

        # Load pit collisions
        for obj in tmx_map.get_layer_by_name('pits'):
            surf = pygame.Surface((obj.width, obj.height), pygame.SRCALPHA)
            CollisionSprite((obj.x, obj.y), surf, self.collision_sprites)

        # Load patrol zones from 'zones' layer
        self.patrol_zones = [
            pygame.Rect(obj.x, obj.y, obj.width, obj.height)
            for obj in tmx_map.get_layer_by_name('zones')
        ]

        # Load entity markers
        player_pos = None
        entity_markers = list(tmx_map.get_layer_by_name('entities'))

        # First pass: find player marker
        for marker in entity_markers:
            if marker.name == 'Player':
                player_pos = (marker.x, marker.y)
                break

        if player_pos:
            self.player = Player(player_pos, self.all_sprites, self.collision_sprites)

        # Second pass: spawn enemies/bosses
        for marker in entity_markers:
            name = marker.name
            pos = (marker.x, marker.y)

            if name in ['sword', 'axe']:
                enemy = Humanoid(name.capitalize(), pos, self.all_sprites, self.collision_sprites)
                for zone in self.patrol_zones:
                    if zone.collidepoint(*pos):
                        enemy.patrol_bounds(zone)
                        break

            elif name == 'spear':
                Humanoid('Spear', pos, self.all_sprites, self.collision_sprites)

            elif name == 'Cervus':
                self.cervus = Cervus(pos, self.all_sprites, self.player)

            elif name == 'Noliictu':
                self.noliictu = Noliictu(pos, self.all_sprites, self.player)