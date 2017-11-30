import yaml

class Logger:
    def __init__(self, file=None):
        self.file = file
        self.actions = []

    def log(self, action, x, y):
        print("{}: {}, {}".format(action, x, y))
        self.actions.append((action, x, y))

    def write(self, seed, final_score):
        if not self.file:
            file_name = "{}_{}_{}.yml".format(dt.datetime.now().strftime("%Y%d%m_%H%M%S"), seed, final_score)
            self.file = os.path.join(os.getcwd(), "logs", file_name)
        yaml.dump({
            'seed': seed,
            'final_score': final_score,
            'actions': self.actions
        }, self.file, indent=4, default_flow_style=False, width=1000)
