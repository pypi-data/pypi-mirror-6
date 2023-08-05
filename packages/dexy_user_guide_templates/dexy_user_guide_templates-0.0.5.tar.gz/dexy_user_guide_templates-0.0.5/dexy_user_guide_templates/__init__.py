from dexy.template import Template
import os

parent_dir = os.path.dirname(__file__)
template_file = os.path.join(parent_dir, "templates.yaml")
Template.register_plugins_from_yaml_file(template_file)
