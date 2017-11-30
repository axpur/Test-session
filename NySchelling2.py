import random

from mesa import Model, Agent
from mesa.time import RandomActivation
from mesa.space import SingleGrid
from mesa.datacollection import DataCollector


class SchellingAgent(Agent):
    '''
    Schelling segregation agent
    '''
    # Q: What is the purpose of _init_ exactly
    def __init__(self, pos, model, agent_type):
        '''
         Create a new Schelling agent.
         Args:
            unique_id: Unique identifier for the agent.
            x, y: Agent initial location.
            agent_type: Indicator for the agent's type (minority=1, majority=0)
        '''
        super().__init__(pos, model)
        self.pos = pos
        self.type = agent_type

    def step(self):

        similar = 0 #How many agents around me are similar to me. Initially zero. Done for each agent at every step.
        for neighbor in self.model.grid.neighbor_iter(self.pos):
            if neighbor.type == self.type:
                similar += 1

        # If unhappy, move:
        if similar < self.model.homophily:
            # Simplifies location adjustment
            self.model.grid.move_to_empty(self) #If not happy, move to empty cell.
        else:
            # Keep track of happy people
            self.model.happy += 1


class SchellingModel(Model):
    '''
    Model class for the Schelling segregation model.
    '''

    def __init__(self, height, width, density, minority_pc, homophily):
        '''
        '''
        # Setting up the Model
        self.height = height
        self.width = width
        self.density = density #percentage (empty houses)
        self.minority_pc = minority_pc #percentage minority in the city
        self.homophily = homophily #number of similar minded person that you want around you

        # Setting up the AGM simulation
        self.schedule = RandomActivation(self)

        # Setting up the grid, using inputs in the function, the torus function
        # seems to be related to how we treat edges, but not sure
        self.grid = SingleGrid(height, width, torus=True)

        # Setting the number of happy people to zero
        self.happy = 0

        self.datacollector = DataCollector(
            {"happy": lambda m: m.happy},  # Model-level count of happy agents
            # For testing purposes, agent's individual x and y
            {"x": lambda a: a.pos[0], "y": lambda a: a.pos[1]})

        self.running = True

        # Set up agents
        # We use a grid iterator that returns
        # the coordinates of a cell as well as
        # its contents. (coord_iter)
        for cell in self.grid.coord_iter():
            # For each cell coordinate apply if statements
            x = cell[1]
            y = cell[2]

            # First if statement: take a random number between 0 and 1
            # (random.random command) and check whether that value is
            # below the assigned density.

            # Second if statement: take a random number between 0 and 1
            # and assign the agent type based on the condition
            if random.random() < self.density:
                if random.random() < self.minority_pc:
                    agent_type = 1
                else:
                    agent_type = 0

                # Refer to the above function related to Agent attributes
                agent = SchellingAgent((x, y), self, agent_type)
                self.grid.position_agent(agent, (x, y))
                self.schedule.add(agent)

    def step(self):
        '''
        Run one step of the model. If All agents are happy, halt the model.
        '''
        self.happy = 0  # Reset counter of happy agents
        self.schedule.step()
        self.datacollector.collect(self)

        if self.happy == self.schedule.get_agent_count():
            self.running = False
