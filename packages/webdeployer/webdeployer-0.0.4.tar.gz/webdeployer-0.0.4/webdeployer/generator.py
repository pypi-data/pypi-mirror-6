from pkg_resources import resource_string
import os
class Generator(object):
  def __init__(self, generate=None):
    pass

  def config_parser(self, global_first=False):
    if global_first:
      eval(open(self.global_path).read())

    eval(open('webdeployer-config.py'))

  def __open_template(self, template_name):
    template_contents = resource_string('generators', template_name)
    return template_contents

  def __template_parser(self, template_name, settings=None):
    from jinja2 import Environment
    return Environment().from_string(self.__open_template(template_name)).render(settings=settings)

  def __generate_template(self, template_name, settings=None):
    self.__template_parser(template_name, settings=None)
    return self.__template_parser(template_name, settings)

  def __save_template(self, data, location='current_dir',file_name=None):
    if location != 'current_dir':
      print 'not current Dir'

    # Simpy change the extension  (tpl) of the template into .conf
    file_name = str(file_name.replace(".tpl", ".conf"))
    tpl_file = os.path.join(os.curdir, 'webdeployer-config', file_name)
    # if the directory does not exist make it
    if not os.path.exists(tpl_file):
      try:
        os.makedirs(os.path.dirname(tpl_file))
      except:
        print 'errror' # TODO: catch error
    # This should be the absolute project directory ? and then inside that dir webdeployer_folder ???
      try:
        with open(tpl_file, 'w+') as config_writer:
          config_writer.write(data)
      except:
        print 'error' # TODO: catch error!

  def __make_config(self, template_name, settings):
    output = self.__template_parser(template_name, settings)
    self.__save_template(output, file_name=template_name)
    return True

  def generate_nginx(self, settings=None):
    return self.__make_config('nginx.tpl', settings)

  def generate_gunicorn(self, settings=None):
    return self.__make_config('gunicorn.tpl', settings)

  def generate_supervisord(self, settings=None):
    return self.__make_config('supervisord.tpl', settings)

  def generate_config(self, settings=None):
    return self.__make_config('project-config.tpl', settings)