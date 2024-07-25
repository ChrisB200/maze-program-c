import pygame


class Sidebar:
    def __init__(self, transform: tuple, size: tuple):
        self.transform = pygame.math.Vector2(transform)
        self.size = size
        self.elements = []
        self.visible = True
        self.active = True

    def add_element(self, *elements):
        for element in elements:
            self.elements.append(element)
            element.parent = self

    def remove_element(self, *elements):
        for element in elements:
            element.parent = None
            self.elements.remove(element)

    def set_visible(self, state: bool):
        self.visible = state
        for element in self.elements:
            element.visible = state

    def set_active(self, state: bool):
        self.active = state
        for element in self.elements:
            element.active = state

    def check_hover(self):
        for element in self.elements:
            if element.isHover:
                return element
        return None

    def update(self):
        for element in self.elements:
            element.update()

    def event_handler(self, event):
        for element in sorted(self.elements, key=lambda element: element.layer):
            element.event_handler(event)

    def draw(self, surface):
        for element in sorted(self.elements, key=lambda element: element.layer):
            element.draw(surface)


class Element:
    def __init__(self, transform: tuple, size: list, callback=None):
        self.local_transform = pygame.math.Vector2(transform)
        self.size = size
        self.visible = True
        self.active = True
        self.surf = pygame.Surface(size)
        self.isHover = False
        self.callback = callback
        self.parent = None
        self.layer = 0

    def change_layer(self, layer):
        self.layer = layer

    @property
    def transform(self):
        return (
            self.local_transform + self.parent.transform
            if self.parent
            else self.local_transform
        )

    def get_rect(self):
        return pygame.Rect(
            self.transform.x, self.transform.y, self.size[0], self.size[1]
        )

    def draw(self, surface):
        surface.blit(self.surf, self.transform)

    def check_hover(self):
        if self.get_rect().collidepoint(pygame.mouse.get_pos()) and self.active:
            self.isHover = True
        else:
            self.isHover = False

    def update(self):
        self.check_hover()

    def event_handler(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.isHover:
                self.callback if self.callback else None


class Text(Element):
    def __init__(
        self, transform: tuple, text: str, font, colour=(0, 0, 0), callback=None
    ):
        super().__init__(transform, [0, 0], callback)
        self.text = text
        self.font = font
        self.colour = colour
        self.antialias = True
        self.update_surf()

    def update_surf(self):
        self.surf = self.font.render(
            str(self.text), self.antialias, self.colour, (255, 0, 0)
        )
        self.size[0] = self.surf.get_width()
        self.size[1] = self.surf.get_height()

    def change_aliasing(self, state):
        self.antialias = state
        self.update_surf()

    def change_text(self, text):
        self.text = text
        self.update_surf()

    def change_colour(self, colour):
        self.colour = colour
        self.update_surf()


class Button(Text):
    def __init__(
        self,
        transform: tuple,
        size,
        text,
        font,
        bg=(255, 255, 255),
        colour=(0, 0, 0),
        callback=None,
    ):
        self.bg = bg
        super().__init__(transform, text, font, colour, callback=callback)
        self.padding = {"top": 0, "right": 0, "bottom": 0, "left": 0}

    def update_surf(self):
        self.surf = self.font.render(
            str(self.text), self.antialias, self.colour, self.bg
        )
        self.size[0] = self.surf.get_width()
        self.size[1] = self.surf.get_height()
