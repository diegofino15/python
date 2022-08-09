import pygame

pygame.font.init()
GUI_FONT = pygame.font.Font(None, 32)
DEBUG_COLOR = "black"
DEBUG_TEXT_COLOR = "white"
WIDTH, HEIGHT = 1280, 720
offset = 10


def debug(texts, font=GUI_FONT, side='center', y='center', offset_plus=(0, 0), color=DEBUG_TEXT_COLOR, bg=False, bg_color=DEBUG_COLOR) -> None:
    screen = pygame.display.get_surface()
    
    for index, label in enumerate(texts):
        text = font.render(label, True, color)
        text_rect = text.get_rect()
        height_text = text_rect.height
        width_text = text_rect.width

        if side == 'left': x_rect = offset + offset_plus[0]
        elif side == 'right': x_rect = WIDTH - width_text - offset * 3 + offset_plus[0]
        else: x_rect = WIDTH / 2 - width_text / 2 - offset + offset_plus[0]
        
        if y == 'top': y_rect = offset + (height_text + offset * 2) * index + offset_plus[1]
        elif y == 'bottom': y_rect = HEIGHT - offset - (height_text + offset * 2) * (index + 1) + offset_plus[1]
        else: 
            min_y_pos = HEIGHT / 2 - (len(texts) / 2 * height_text)
            y_rect = min_y_pos + (height_text + offset * 2) * index + offset_plus[1]

        x_text = x_rect + offset
        y_text = y_rect + offset
        
        if bg: pygame.draw.rect(screen, bg_color, (x_rect, y_rect, width_text + offset * 2, height_text + offset * 2))
        screen.blit(text, (x_text, y_text))

