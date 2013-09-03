""" A model is a set of animations. """

import animation
import json

def load(dirname, fps):
    """ Load a model from a standard directory layout. """
    descr = json.loads(open(dirname + '/model.json').read())
    model = {}
    for key, value in descr['animations'].items():
        model[key] = animation.load(dirname, fps, value)
    return model
