# Author:       Andrew Laing
# Email:        parisianconnections@gmail.com
# Last Updated: 17/02/2019
# Description:  Used to implement buttons for PyGame.
# Changes:      Refactored and comments added.
# ToDo:         write setter and getter functions.

import pygame
pygame.init()

# Set the border width for the button
BORDERWIDTH = 5

# Set up the default colours
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

BG_NORMAL_COL = (255, 100, 100)
FG_NORMAL_COL = (255, 155, 155)

BG_MOUSEOVER_COL = (210, 0, 0)
FG_MOUSEOVER_COL = (255, 62, 62)

BG_PRESSED_COL = (133, 60, 164)
FG_PRESSED_COL = (164, 92, 196)



class Button:
    """ Used to implement simple buttons for PyGame.

    Attributes:
        bg: A PyGame rectangle for the button's background.
        bg_colour: The button's current background colour.
        border_width: The width of the button's border.
        btn_bg_colour: The background colour of the button.
        btn_bg_mouseover_colour: The mouseover colour of the button.
        btn_bg_pressed_colour: The colour of the button when it is pressed.
        btn_fg_colour: The foreground colour of the button.
        btn_fg_mouseover_colour: The foreground mouseover colour of the button.
        btn_fg_pressed_colour: The foreground colour of the button when it is pressed.
        btn_txt_colour: The colour of the button text.
        btn_txt_mouseover_colour: The mouseover colour of the button text.
        btn_txt_pressed_colour: The colour of the button text when the button is pressed.
        caption: The button text.
        fg: A PyGame rectangle for the button's foreground.
        fg_colour: The button's current foreground colour.
        over_button: True if the cursor is over the button, otherwise False.
        pressed: True if the button is being pressed, otherwise False.
        text: A text object to hold the button caption.
        textFont: The font used to display the button caption.
        txt_colour: The button's current text colour.
        txt_left: The position for the left edge of the text.
        txt_top: The position for the top edge of the text.
    """

    def __init__(self, caption, bg_attributes, txt_position, font, fontsize):
        """ Initialises ButtonClass with a caption, button background attributes,
            a position for the text, and button background attributes.

        :param caption: A text string cation for the button.
        :param bg_attributes: A tuple containing the position and size attributes
                              for the button' background rectangle.
                              (Pixels from left-hand edge, width in pixels,
                               Pixels from top edge, height in pixels)
        :param txt_position: A tuple containing the top-left position of the buttons caption.
                              (Pixels from left-hand edge, Pixels from top edge)
        :param font: The font used to display the button caption.
        :param fontsize: The caption's font size.
        """
        self.border_width = BORDERWIDTH
        self.initialiseColours()
        self.initialiseButtonRects(bg_attributes)
        self.initialiseCaption(caption, txt_position, font, fontsize)
        self.over_button = False
        self.pressed = False


    def initialiseButtonRects(self, bg_attributes):
        """ Initialises the PyGame rectangles used to make the button.

        :param bg_attributes: A tuple containing the position and size attributes
                              for the button's background rectangle.
                              (Pixels from left-hand edge, width in pixels,
                               Pixels from top edge, height in pixels)
        """
        self.bg = pygame.Rect(bg_attributes[0], bg_attributes[1], bg_attributes[2], bg_attributes[3])
        self.fg = pygame.Rect(bg_attributes[0]+self.border_width,
                              bg_attributes[1]+self.border_width,
                              bg_attributes[2]-(self.border_width*2),
                              bg_attributes[3]-(self.border_width*2))


    def initialiseCaption(self, caption, txt_position, font, fontsize):
        """ Initialises the PyGame text object used to hold the button caption.

        :param caption: A text string cation for the button.
        :param txt_position: A tuple containing the top-left position of the buttons caption.
                              (Pixels from left-hand edge, Pixels from top edge)
        :param font: The font used to display the button caption.
        :param fontsize: The caption's font size.
        """
        self.caption = caption
        self.textFont = pygame.font.Font(font, fontsize)
        self.text = self.textFont.render(self.caption, True, self.txt_colour)
        self.txt_left = txt_position[0]
        self.txt_top = txt_position[1]


    def initialiseColours(self):
        """ Initialises the default colours used on the button. """
        self.btn_bg_colour = BG_NORMAL_COL
        self.btn_fg_colour = FG_NORMAL_COL

        self.btn_bg_mouseover_colour = BG_MOUSEOVER_COL
        self.btn_fg_mouseover_colour = FG_MOUSEOVER_COL

        self.btn_bg_pressed_colour = BG_PRESSED_COL
        self.btn_fg_pressed_colour = FG_PRESSED_COL

        self.btn_txt_colour = WHITE
        self.btn_txt_mouseover_colour = BLACK
        self.btn_txt_pressed_colour = WHITE

        self.bg_colour = self.btn_bg_colour
        self.fg_colour = self.btn_fg_colour
        self.txt_colour = self.btn_txt_colour


    def is_collision(self, mousePosition):
        """ Detects whether the mouse is over the button.

        :param mousePosition: A PyGame mouse position.
        :return: True if the mouse is over the button, otherwise false.
        """
        return self.bg.collidepoint(mousePosition)


    def is_over_button(self):
        """ Returns the state of the over_button variable.

        :return: True if the mouse is over the button, otherwise false.
        """
        return self.over_button


    def is_pressed(self):
        """ Returns the state of the pressed variable.

        :return: True if the button is being pressed, otherwise false.
        """
        return self.pressed


    def button_was_pressed(self, event):
        """ Detects whether the button is being pressed.
            If yes, it will update the button press state variables.

        :param event: A PyGame event object.
        :return: True if the button is being pressed, otherwise false.
        """
        button_was_pressed = False

        # deal with a button mouseover
        if self.is_collision(pygame.mouse.get_pos()):
            if not self.is_over_button():
                self.set_over_button()

            # detect and deal with the user pressing the button
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not self.is_pressed():
                    self.set_pressed()
                    button_was_pressed = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.is_over_button():
                    self.set_over_button()
        else:
            if self.is_over_button():
                self.set_over_button()

        return button_was_pressed


    def set_over_button(self):
        """ Used to update the over_button state variables, and button
            colours each time the user mouses over, or off the button.
        """
        if self.is_pressed():
            self.pressed = False

        self.over_button = not self.over_button

        # set the colours used to render the button
        if self.over_button:
            self.bg_colour = self.btn_bg_mouseover_colour
            self.fg_colour = self.btn_fg_mouseover_colour
            self.txt_colour = self.btn_txt_mouseover_colour
        else:
            self.bg_colour = self.btn_bg_colour
            self.fg_colour = self.btn_fg_colour
            self.txt_colour = self.btn_txt_colour

        # Rerender the button text
        self.text = self.textFont.render(self.caption, True, self.txt_colour)


    def set_pressed(self):
        """ Used to update the button pressed state variables and button
            colours each time the user presses or releases the button.
        """
        self.pressed = not self.pressed

        # set the colours used to render the button
        if self.pressed:
            self.bg_colour = self.btn_bg_pressed_colour
            self.fg_colour = self.btn_fg_pressed_colour
            self.txt_colour = self.btn_txt_pressed_colour
        else:
            self.bg_colour = self.btn_bg_colour
            self.fg_colour = self.btn_fg_colour
            self.txt_colour = self.btn_txt_colour

        # Rerender the button text
        self.text = self.textFont.render(self.caption, True, self.txt_colour)


    # draw the button upon a surface
    def render(self, surface):
        """ Blits the button onto a PyGame surface object.

        :param surface: A PyGame surface object.
        """
        pygame.draw.rect(surface, self.bg_colour, self.bg, 0)
        pygame.draw.rect(surface, self.fg_colour, self.fg, 0)
        surface.blit(self.text, (self.txt_left, self.txt_top))
