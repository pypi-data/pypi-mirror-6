# -*- coding: utf-8 -*-
import os.path

def sphinx_theme_path():
    """Use this method in conf.py

        html_theme = 'nostrain'
        import nostrain
        html_theme_path = [nostrain.sphinx_theme_path()]
    """
    root = os.path.dirname(__file__)
    return os.path.join(root, 'sphinx')
