"""Contains functions for calculating dissociation rates
"""
__author__ = 'George Oblapenko'
__license__ = "GPL"
__maintainer__ = "George Oblapenko"
__email__ = "kunstmord@kunstmord.com"
__status__ = "Production"


class OmegaError(Exception):
    def __init__(self, model_name, l, r):
        self.model_name = model_name
        self.l = l
        self.r = r

    def __str__(self):
        return 'Cannot calculate Omega (' + str(self.l) + ',' + str(self.r) + ')-integral for the ' + self.model_name\
               + ' interaction model - no approximation data found'


class ProbError(Exception):
    def __init__(self, process_name, delta, delta_name):
        self.process_name = process_name
        self.delta = delta
        self.delta_name = delta_name

    def __str__(self):
        return 'Cannot calculate probability for the following process: ' + self.process_name + ' (for delta '\
               + self.delta_name + '=' + str(self.delta) + ')'
    

class NoDataError(Exception):
    def __init__(self, partner1, partner2, process_name, file_name):
        self.partner1 = partner1
        self.partner2 = partner2
        self.process_name = process_name
        self.file_name = file_name

    def __str__(self):
        return 'Cannot find data for ' + self.process_name + ' for the following particles: ' + self.partner1\
               + ', ' + self.partner2 + ' (in file ' + self.file_name + ')'