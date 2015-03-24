#!/usr/bin/env python2.7

import cv2
import urllib
import numpy as np
import png
import pdb
import StringIO
import sys
from PIL import Image


class DroneSimulator(object):
    """
    """
    def __init__(self, gui):
        self.new()
        if gui:
            self.wsg = self.create_gui()
            self.wsg.run()
        else:
            print('Welcome to the wumpus world.')

    def start(self):
        while True:
            pass

    def new(self):
        """ Creates a new simulation.
        """
        self.wumpus = Wumpus()
        self.agent  = Agent()
        self.gold   = Gold()
        self.pits   = Pits()

        self.time = 0
        self.last_action = 'None'

        if self.pits.contains_pit(self.gold.location):
            self.gold.in_pit = True

    def action(self):
        """ Performs one action time-step.
        """
        # Make sure the agent is alive to perform an action.
        if not self.agent.health:
            return

        # Get the current percepts of the agent.
        breeze  = self.pits.contains_breeze(self.agent.location)
        stench  = self.wumpus.contains_stench(self.agent.location)
        bump    = self.agent.bump
        scream  = self.wumpus.scream
        glitter = self.gold.location == self.agent.location

        # Update the agent.
        # wwagent.update([breeze, stench, bump, scream, glitter])

        # Get the action from the 'intelligent' agent.
        # self.last_action = wwagent.action()

        self.last_action = 'MOVE'
        if self.last_action == 'ROTATE_LEFT':
            self.agent.orientation = (self.agent.orientation + 1) % 4
        elif self.last_action == 'ROTATE_RIGHT':
            self.agent.orientation = (self.agent.orientation - 1) % 4
        elif self.last_action == 'MOVE':
            # Update the agents location.
            (i, j) = self.agent.location
            self.agent.bump = False
            if self.agent.orientation == 2:
                if i - 1 > 0:
                    self.agent.location = (i - 1, j)
                else:
                    self.agent.bump = True
            elif self.agent.orientation == 3:
                if j - 1 > 0:
                    self.agent.location = (i, j - 1)
                else:
                    self.agent.bump = True
            elif self.agent.orientation == 1:
                if j + 1 <= 4:
                    self.agent.location = (i, j + 1)
                else:
                    self.agent.bump = True
            elif self.agent.orientation == 0:
                if i + 1 <= 4:
                    self.agent.location = (i + 1, j)
                else:
                    self.agent.bump = True

            # Check to see if the agent has died.
            if self.pits.contains_pit(self.agent.location) or self.wumpus.location == self.agent.location:
                self.agent.health = False
                self.location = (None, None)

        elif self.last_action == 'GRAB':
            if self.gold.location == self.agent.location:
                self.gold.grabbed = True
        elif self.last_action == 'SHOOT':
            self.agent.arrow = False
        elif self.last_action == 'CLIMB':
            pass

        # Check to see if the agent has fallen in the pit.

        # Update the simulator.
        self.time = self.time + 1

    def fow(self):
        """ Turns off fog of war.
        """
        pass

    def quit(self):
        sys.exit(0)

    def create_gui(self):
        """ Factory method that builds the wumpus simulator gui and passes the
            wumpus simulator to it.
        """
        return WumpusSimulator.WumpusSimulatorGUI(self)

    class WumpusSimulatorGUI(threading.Thread):
        """ GUI for the wumpus simulator.
        """
        def __init__(self, sim):
            threading.Thread.__init__(self)
            self.sim = sim
            self.root = tk.Tk()
            self.fog = True
            if self.root:
                self.root.wm_title("Wumpus World Simulator")
                self.sim_frame = tk.Frame(self.root)     # Frame containing sim
                self.info_frame = tk.Frame(self.root)    # Frame for labels
                self.button_frame = tk.Frame(self.root)  # Frame for buttons
                self.create_world()

        def create_world(self):
            """ Creates the Wumpus world.

                Contains a 4 x 4 grid of the Wumpus world along with a few buttons.
                and labels. The button on the bottom left starts a new simulation.
                The bottom middle mutton performs one percept-action time-step. The
                bottom right button toggles the fog of war. Additionally, below
                each button is a label. Bellow the new simulation button, is a
                description of the performance score of the agent. Below the action
                button is the turn number of the game. Below the fog of war
                button is the current thought of the agent.
            """
            # Image of the world.
            self.world = Image.new('RGB', (4*100, 4*100), 'white')

            # Create the layout of the frames.
            self.sim_frame.pack(side=tk.TOP)
            self.info_frame.pack(side=tk.BOTTOM)
            self.button_frame.pack(side=tk.BOTTOM)

            # Create the layout of the info labels.
            self.health_label = tk.Label(self.info_frame, width=12, text='Health: 1')
            self.time_label = tk.Label(self.info_frame, width=12, text='Time-step: 0')
            self.action_label = tk.Label(self.info_frame, width=18, text='Last action: None')
            self.score_label = tk.Label(self.info_frame, width=12, text='Score: 0')

            self.health_label.grid(row=0, column=0)
            self.time_label.grid(row=0, column=1)
            self.action_label.grid(row=0, column=2)
            self.score_label.grid(row=0, column=3)

            # Create the layout of the buttons.
            new_button = tk.Button(self.button_frame, text='New Simulation', command=self.new)
            action_button = tk.Button(self.button_frame, text='Action', command=self.action)
            fog_button = tk.Button(self.button_frame, text='Fog of War', command=self.fow)

            new_button.grid(row=0, column=0)
            action_button.grid(row=0, column=1)
            fog_button.grid(row=0, column=2)

            # Load the images for the world.
            image_grid         = Image.open('./images/grid.png')
            image_agent_right  = Image.open('./images/agent_right.png')
            image_agent_left   = Image.open('./images/agent_left.png')
            image_agent_up     = Image.open('./images/agent_up.png')
            image_agent_down   = Image.open('./images/agent_down.png')
            image_arrow        = Image.open('./images/arrow.png')
            image_wumpus_alive = Image.open('./images/wumpus_alive.png')
            image_wumpus_dead  = Image.open('./images/wumpus_dead.png')
            image_pit          = Image.open('./images/pit.png')
            image_gold         = Image.open('./images/gold.png')
            image_glitter      = Image.open('./images/glitter.png')
            image_stench       = Image.open('./images/stench.png')
            image_scream       = Image.open('./images/stench.png')
            image_wind         = Image.open('./images/wind.png')
            image_bump         = Image.open('./images/bump.png')

            # Image primitives.
            self.prim_grid         = image_grid.resize((100, 100), Image.NEAREST)
            self.prim_agent_left   = image_agent_left.resize((100, 100), Image.NEAREST)
            self.prim_agent_right  = image_agent_right.resize((100, 100), Image.NEAREST)
            self.prim_agent_up     = image_agent_up.resize((100, 100), Image.NEAREST)
            self.prim_agent_down   = image_agent_down.resize((100, 100), Image.NEAREST)
            self.prim_arrow        = image_arrow.resize((100, 100), Image.NEAREST)
            self.prim_wumpus_alive = image_wumpus_alive.resize((100, 100), Image.NEAREST)
            self.prim_wumpus_dead  = image_wumpus_dead.resize((100, 100), Image.NEAREST)
            self.prim_pit          = image_pit.resize((100, 100), Image.NEAREST)
            self.prim_gold         = image_gold.resize((100, 100), Image.NEAREST)
            self.prim_glitter      = image_glitter.resize((100, 100), Image.NEAREST)
            self.prim_scream       = image_scream.resize((100, 100), Image.NEAREST)
            self.prim_stench       = image_stench.resize((100, 100), Image.NEAREST)
            self.prim_wind         = image_wind.resize((100, 100), Image.NEAREST)
            self.prim_bump         = image_bump.resize((100, 100), Image.NEAREST)

            photo_world = ImageTk.PhotoImage(self.world)
            self.world_label = tk.Label(self.sim_frame, image=photo_world)
            self.world_label.image = photo_world

            # self.world_label.bind('<Configure>', self.resize)
            self.world_label.pack()
            self.update_world()

        def resize(self, event):
            new_width = event.width
            new_height = event.height
            resized_world = self.world.resize((new_width, new_height))
            photo_resized_world = ImageTk.PhotoImage(resized_world)
            self.world_label.configure(image=photo_resized_world)

        def update_world(self):
            """ Update the world, by blending together the image primitives for
                each cell.
            """
            # The image displayed on the screen.
            self.world = Image.new('RGBA', (4*100, 4*100), 'white')

            self.update_grid()
            self.update_agent()
            self.update_gold()
            self.update_pits()
            self.update_wumpus()
            self.update_percepts()

            # Return the final photo of the updated world.
            photo_world = ImageTk.PhotoImage(self.world)
            self.world_label.config(image=photo_world)
            self.world_label.image = photo_world

        def update_cell(self, location, prim_comb, blend=False):
            """ Updates a given cell with the primitive combination where the
                coordinates refer to the reference (1, 1) at the bottom left
                of the grid.
            """
            try:
                # Map to the python image coordinates.
                (i, j) = location
                y = (400 - j*100)
                x = (i - 1)*100
                box = (x, y, x + 100, y + 100)
            except ValueError:
                raise ValueError
            if not blend:
                self.world.paste(prim_comb, box)
            else:
                temp = self.world.crop(box)
                mask = temp.convert('L')
                mask = mask.point(lambda x: 0 if x < 250 else 255, 'L')
                temp.paste(prim_comb, (0, 0), mask)
                self.world.paste(temp, box)

        def update_grid(self):
            """ Updates the grey grid of each cell.
            """
            for i in range(1, 5):
                for j in range(1, 5):
                    self.update_cell((i, j), self.prim_grid)

        def update_agent(self):
            """ Updates the agent in the world.
            """
            if self.sim.agent.health:
                if self.sim.agent.orientation == 0:
                    self.update_cell(self.sim.agent.location, self.prim_agent_right, blend=True)
                if self.sim.agent.orientation == 1:
                    self.update_cell(self.sim.agent.location, self.prim_agent_up, blend=True)
                if self.sim.agent.orientation == 2:
                    self.update_cell(self.sim.agent.location, self.prim_agent_left, blend=True)
                if self.sim.agent.orientation == 3:
                    self.update_cell(self.sim.agent.location, self.prim_agent_down, blend=True)

                if self.sim.agent.arrow:
                    self.update_cell(self.sim.agent.location, self.prim_arrow, blend=True)

        def update_wumpus(self):
            """ Updates the wumpus in the world.
            """
            if self.sim.wumpus.health:
                self.update_cell(self.sim.wumpus.location, self.prim_wumpus_alive, blend=True)
            else:
                self.update_cell(self.sim.wumpus.location, self.prim_wumpus_dead, blend=True)

        def update_gold(self):
            """ Updates the gold in the world.
            """
            if not self.sim.gold.in_pit and not self.sim.gold.grabbed:
                self.update_cell(self.sim.gold.location, self.prim_gold, blend=True)

        def update_pits(self):
            """ Updates the pits in the world.
            """
            for pit in self.sim.pits.pits:
                    self.update_cell(pit.location, self.prim_pit, blend=True)

        def update_breezes(self):
            # Update breezes.
            for breeze in self.sim.pits.breezes:
                if breeze.location == self.sim.agent.location or not self.fog:
                    self.update_cell(breeze.location, self.prim_wind, blend=True)
                    breeze.known = True

        def update_stenches(self):
            # Update stenches.
            for stench in self.sim.wumpus.stenches:
                if stench.location == self.sim.agent.location or not self.fog:
                    self.update_cell(stench.location, self.prim_stench, blend=True)

        def update_glitter(self):
            # Update glitter.
            if (self.sim.gold.location == self.sim.agent.location or not self.fog) and not self.sim.gold.in_pit:
                self.update_cell(self.sim.gold.location, self.prim_glitter, blend=True)

        def update_scream(self):
            # Update scream
            if self.sim.wumpus.scream:
                for (i, j) in itertools.product(range(1, 5), range(1, 5)):
                    self.update_cell((i, j), self.prim_scream, blend=True)

        def update_bump(self):
            # Update bump.
            if self.sim.agent.bump:
                self.update_cell(self.sim.agent.location, self.prim_bump, blend=True)

        def update_percepts(self):
            """ Updates the percepts of the agent in the current state.
            """
            self.update_breezes()
            self.update_stenches()
            self.update_glitter()
            self.update_scream()
            self.update_bump()

        def run(self):
            self.root.mainloop()
            self.sim.quit()

        def new(self):
            self.sim.new()
            self.update_world()
            self.update_info()

        def action(self):
            self.sim.action()
            self.update_world()
            self.update_info()

        def update_info(self):
            # Update agents health.
            health_text = 'Health: %i' % self.sim.agent.health
            self.health_label.configure(text=health_text)

            # Update the current time-step.
            time_text = 'Time-step: %i' % self.sim.time
            self.time_label.configure(text=time_text)

            # Update the last action.
            action_text = 'Last action: %s' % self.sim.last_action
            self.action_label.configure(text=action_text)

        def fow(self):
            self.fog = not self.fog
            if self.fog:
                print('Making fog of war true.')
            else:
                print('Making fog of war false.')

            # Update the world.
            self.update_world()



# This works (tested) with raspberry pi and camera module but it should work with parrot too.
def main():
    while True:
        try:
            # Parrot seems to change IP: 192.168.1.(1,2,3).
            image = url_to_image('http://192.168.1.2:8080')
            cv2.imshow('opencv parrot test', image)
            k = cv2.waitKey(0)
            if k == 27:         # wait for ESC key to exit
                cv2.destroyAllWindows()
            elif k == ord('s'):  # wait for 's' key to save and exit
                cv2.imwrite('messigray.png', image)
                cv2.destroyAllWindows()
        except KeyboardInterrupt:
            cv2.destroyAllWindows()
            sys.exit(0)


# METHOD #1: OpenCV, NumPy, and urllib
def url_to_image(url):
        # download the image, convert it to a NumPy array, and then read
        # it into OpenCV format
        resp = urllib.urlopen(url)
        image = np.asarray(bytearray(resp.read()), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        return image


def get_stream_raspi():
    # Code credit: Petr Kout'
    # http://petrkout.com/electronics/low-latency-0-4-s-video-streaming-from-raspberry-pi-mjpeg-streamer-opencv/

    stream = urllib.urlopen('http://192.168.1.2:8080')
    r.read()
    ss = ''
    while True:
        ss += stream.read(1024)
        a = ss.find('\xff\xd8')
        b = ss.find('\xff\xd9')
        if a != -1 and b != -1:
            jpg = ss[a:b + 2]
            ss = ss[b + 2:]
            i = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.CV_LOAD_IMAGE_COLOR)
            cv2.imshow('opencv image server raspi test', i)
            if cv2.waitKey(1) == 27:
                exit(0)

if __name__ == '__main__':
    main()
