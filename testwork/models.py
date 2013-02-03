# -*- encoding: utf-8 -*-

import yaml
from utils import make_dynamic_model
from django.conf import settings


dynamic_conf = open(settings.PROJECT_ROOT+'/model_config.yaml', 'r')
models = yaml.load(dynamic_conf)
for key, val in models.items():
    # Make model Class
    make_dynamic_model(key, val)

