import os
import zipfile
import tempfile
import matplotlib.pyplot as plt


class PNGRenderer(object):
    def __init__(self, stub):
        self.stub = stub
        self.figures = []
        self.temp_dir = tempfile.mkdtemp()

    def save_page(self, out_name, figure=None):
        figure = figure if figure else plt.gcf()
        self.figures.append((figure, out_name))

    def render(self):
        with zipfile.ZipFile(self.stub + '.zip', 'w') as outfile:
            for figure, name in self.figures:
                temp_path = os.path.join(self.temp_dir, name)
                figure.savefig(temp_path)
                outfile.write(temp_path, os.path.basename(temp_path))

    savefig = save_page
