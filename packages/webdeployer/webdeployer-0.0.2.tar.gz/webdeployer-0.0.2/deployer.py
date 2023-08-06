from fabric.api import cd, with_settings
from fabric.colors import blue
from fabric.decorators import with_settings
from fabric.auth import get_password
class Deployer(object):
  def __init__(self):
    self.client_name = "Techpro_and_services"
    self.project_name = "website"
    self.path = "/projects/clients/techpro_and_services"
    self.flavor = "django"

  def __setup(self):
    """
    Setup create the necesary directories to deploy
    """
    pass

  def generate_configs(self):
    pass

  def deploy(self, setup=False):
    pass