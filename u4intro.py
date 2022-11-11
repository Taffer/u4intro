#! /usr/bin/env python3
''' Simulate the Ultima IV: Quest of the Avatar intro.

By Chris Herborth (https://github.com/Taffer)
MIT license, see LICENSE.md for details.
'''

import pygame
import pygame.gfxdraw
import pygame_recorder  # https://github.com/tdrmk/pygame_recorder
import time
import sys

SCREEN_TITLE = 'Not Ultima IV'

SCREEN_WIDTH = 320  # 320x240, state of the art in 1985-ish...
SCREEN_HEIGHT = 240

BLACK = pygame.Color('black')
WHITE = pygame.Color('white')

TARGET_FPS = 30
RECORDING = True

# https://wiki.ultimacodex.com/wiki/Ultima_IV_internal_formats#TITLE.EXE
U4INTRO = 'Ultima4/TITLE.EXE'
U4_BEASTIE_OFFSET = 0x7380
U4_DAEMON_WIDTH = 56
U4_DRAGON_WIDTH = 48
U4_BEASTIE_HEIGHT = 32
U4_SIG_OFFSET = 0x746e


class Demo:
    def __init__(self, screen, record=False):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.sig_length = 1
        self.beastie_frame = 0
        self.beastie_ticks = 0

        if record:
            self.recorder = pygame_recorder.ScreenRecorder(SCREEN_WIDTH, SCREEN_HEIGHT, TARGET_FPS)
        else:
            self.recorder = None

        self.intro_bytes = open(U4INTRO, 'rb').read()

        # Animation frames for the top-left and top-right beasties. There are
        # 18 available frames. 184 frames interleaved in the animation data.
        #
        # The frames are 56x32 starting at 0,0 for the daemon and 176,0 for
        # the dragon. The dragon is 48x32.
        self.beastie = pygame.image.load('Ultima4_LZW_Animate.png').convert_alpha()
        self.daemon_frames = []
        self.dragon_frames = []
        daemon_x = 0
        dragon_x = 176
        y = 0
        beastie_rect = self.beastie.get_rect()
        for i in range(18):
            rect = pygame.Rect(daemon_x, y, U4_DAEMON_WIDTH, U4_BEASTIE_HEIGHT)
            self.daemon_frames.append(rect)

            rect = pygame.Rect(dragon_x, y, U4_DRAGON_WIDTH, U4_BEASTIE_HEIGHT)
            self.dragon_frames.append(rect)

            y += U4_BEASTIE_HEIGHT
            if y + U4_BEASTIE_HEIGHT > beastie_rect.height:
                daemon_x += U4_DAEMON_WIDTH
                dragon_x += U4_DRAGON_WIDTH
                y = 0

        self.daemon_ani = []
        self.dragon_ani = []
        for i in range(0, 184, 2):
            self.daemon_ani.append(int(self.intro_bytes[U4_BEASTIE_OFFSET + i]))
            self.dragon_ani.append(int(self.intro_bytes[U4_BEASTIE_OFFSET + i + 1]))

        # Signature is 266 x,y co-ordinates.
        self.signature = []
        for i in range(0, 532, 2):
            # Y co-ords are upside down due to DOS screen buffers growing up
            # from the bottom.
            xy = (int(self.intro_bytes[U4_SIG_OFFSET + i]), int(SCREEN_HEIGHT - self.intro_bytes[U4_SIG_OFFSET + i + 1]))
            self.signature.append(xy)

    def draw(self):
        self.screen.fill(BLACK)

        for i in range(self.sig_length):
            (x, y) = self.signature[i]
            pygame.gfxdraw.pixel(self.screen, x, y, WHITE)

        # Draw daemon, top-left.
        rect = pygame.Rect(0, 0, U4_DAEMON_WIDTH, U4_BEASTIE_HEIGHT)
        self.screen.blit(self.beastie, rect, self.daemon_frames[self.daemon_ani[self.beastie_frame]])

        # Draw dragon, top-right.
        rect = pygame.Rect(SCREEN_WIDTH - U4_DRAGON_WIDTH, 0, U4_DRAGON_WIDTH, U4_BEASTIE_HEIGHT)
        self.screen.blit(self.beastie, rect, self.dragon_frames[self.dragon_ani[self.beastie_frame]])

        self.beastie_ticks += 1
        if self.beastie_ticks % 10 == 0:
            self.beastie_frame += 1
            if self.beastie_frame >= len(self.daemon_ani):
                self.beastie_frame = 0

    def update(self):
        self.sig_length += 1
        if self.sig_length > len(self.signature):
            self.sig_length = 1

            if self.recorder:
                pygame.event.post(pygame.event.Event(pygame.QUIT, {}))

        if self.recorder:
            self.recorder.capture_frame(self.screen)

        self.clock.tick(TARGET_FPS)


def main():
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(SCREEN_TITLE)

    demo = Demo(screen, RECORDING)

    playing = True

    while playing:
        demo.draw()
        pygame.display.flip()

        demo.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                playing = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                playing = False

    if demo.recorder:
        demo.recorder.end_recording()

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
