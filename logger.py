import yaml
import os
import datetime as dt

class Logger:
    def __init__(self, length, width, num_mines,  seed, file=None):
        self.file = file
        self.game_config = {}
        self.game_config['seed'] = seed
        self.game_config['length'] = length
        self.game_config['width'] = width
        self.game_config['num_mines'] = num_mines
        self.actions = []

    def log(self, action, x, y):
        self.actions.append((action, x, y))

    def write(self, agent, final_score):
        log_dir = os.path.join(os.getcwd(), "logs")
        if not self.file:
            file_name = "{}-{}_{}_{}.yml".format(agent, dt.datetime.now().strftime("%Y%d%m_%H%M%S"), self.game_config['seed'], final_score)
            self.file = os.path.join(log_dir, file_name)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        with open(self.file, 'w') as fh:
            yaml.dump({
                'config': self.game_config,
                'final_score': final_score,
                'actions': self.actions
            }, fh, indent=4, default_flow_style=False, width=1000)
