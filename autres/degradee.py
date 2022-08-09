import json
import pygame


WIDTH, HEIGHT = 1280, 720
BLACK, WHITE, RED, BLUE, GREEN = "black", "white", "red", "blue", "green"


def get_default_file_data(rgb, res):
    return """
{
    "rgb": """ + str(rgb) + """,

    "res": """ + str(res) + """
}
    """


class Renderer:
    def __init__(self) -> None:
        pygame.init()

        # Init the path for the custom variables
        self.custom_path = "./custom.json"
        program_name = "DEGRADEE"

        # Init the variables
        self.init_variables()

        # Init the needed variables
        self.running = True
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(program_name)

        # Init the grid where all the colors will be stored
        self.grid = [[0] * (self.cells_y + 1) for i in range(self.cells_x + 1)]

        color = 0
        for x in range(self.cells_x):
            for y in range(self.cells_y):
                color += 1
                self.grid[x][y] = color

                if color >= self.color_fade:
                    color = 0
        
        self.init_colors()
 
    def custom_variables(self):
        # The side margins
        self.margine_x = 10
        self.margine_y = 10
        
        # The number of lines of the render
        self.fade_difference = -1

        # 0 -> vertical
        # 1 -> horizontal
        self.mode = 1
        
        if self.mode == 0: self.color_fade = self.resolution[1] + self.fade_difference
        #elif self.mode == 1: self.color_fade = (self.resolution[0] + self.fade_difference) * self.resolution[1]
        elif self.mode == 1: self.color_fade = self.resolution[0] + self.fade_difference

    def get_custom_variables(self):
        try:
            with open(self.custom_path, 'r') as file:
                infos = json.load(file)
            
            self.rgb = infos['rgb']
            self.resolution = infos['res']
            
        except:
            print("No parameters initialized, taking default grey")
            self.rgb = [100, 100, 100]
            self.resolution = [480, 360]

            filedata = get_default_file_data(self.rgb, self.resolution)

            with open(self.custom_path, 'w') as file:
                file.write(filedata)
        
        data = {
            'rgb': self.rgb,
            'res': self.resolution
        }
        
        return data

    def init_variables(self):
        # Init the custom variables
        custom = self.get_custom_variables()
        self.custom_variables()

        # Attribute each variable
        self.r = custom['rgb'][0]
        self.g = custom['rgb'][1]
        self.b = custom['rgb'][2]

        self.darkness_r = self.r / self.color_fade
        self.darkness_g = self.g / self.color_fade
        self.darkness_b = self.b / self.color_fade

        self.cells_x = custom['res'][0]
        self.cells_y = custom['res'][1]
    
    def init_colors(self):
        self.background_color = BLACK

        # The list that will store all the colors
        self.colors = []

        # Calculate all the different shades of colors
        for i in range(self.color_fade + 1):
            self.colors.append((self.r, self.g, self.b))

            # Make the colors darker
            self.r -= self.darkness_r
            self.g -= self.darkness_g
            self.b -= self.darkness_b
    
    def render(self):
        self.screen.fill(self.background_color)

        # Render the fade
        if self.mode == 0:
            for i in range(self.cells_x):
                for j in range(self.cells_y):
                    color = self.colors[self.grid[i][j]]
                    # Draw the pixel on the screen
                    position = (int(self.topleft(i, j)[0]), int(self.topleft(i, j)[1]))
                    size = (int((WIDTH - self.margine_x * 2) / self.cells_x + 1), int((HEIGHT - self.margine_y * 2) / self.cells_y + 1))
                    pygame.draw.rect(self.screen, color, (position[0], position[1], size[0], size[1]))
                    #pygame.Surface.set_at(self.screen, position, color)

                # Update the screen
                pygame.display.flip()
        else:
            for j in range(self.cells_y):
                for i in range(self.cells_x):
                    color = self.colors[self.grid[i][j]]
                    # Draw the pixel on the screen
                    position = (int(self.topleft(i, j)[0]), int(self.topleft(i, j)[1]))
                    size = (int((WIDTH - self.margine_x * 2) / self.cells_x + 1), int((HEIGHT - self.margine_y * 2) / self.cells_y + 1))
                    pygame.draw.rect(self.screen, color, (position[0], position[1], size[0], size[1]))
                    #pygame.Surface.set_at(self.screen, position, color)

                # Update the screen
                pygame.display.flip()
        
        print(f"The render is done with {self.cells_x * self.cells_y} points in total !")
    
    def run(self):
        self.clock = pygame.time.Clock()
        self.fps = 120

        self.ft = True

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    continue
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        continue
                    elif event.key == pygame.K_r:
                        self.ft = not self.ft

            # Render the fade if the function is running for the first time
            if self.ft:
                self.render()
                self.ft = False
            
            self.clock.tick(self.fps)
        
        pygame.quit()
    
    def topleft(self, i, j):
        return [(i / self.cells_x * (WIDTH - self.margine_x * 2) + self.margine_x), \
            (j / self.cells_y * (HEIGHT - self.margine_y * 2) + self.margine_y)]


if __name__ == '__main__':
    render = Renderer()
    render.run()

