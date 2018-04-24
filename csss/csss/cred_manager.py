def get_file_config(config_file):
    """
    Retrieves credentials and configurations from an available .yml file

    :param config_file: the file name of the .yml to retrieve configurations from

    :return: returns contents of .yml file
    """
    cfg_dir = os.getenv( 'INTEGRITY_CONFIG_DIR', None )
    if cfg_dir and os.path.isfile(os.path.join( cfg_dir , config_file)):
        with open((os.path.join( cfg_dir , config_file)), 'r') as cfg:
            return yaml.load(cfg)
    else:
        return ''

def get_env_config(env_var):
    """
    Retrieves credentials and configurations from the shell environment

    :param env_var: the environment variable to retrieve from

    :return: the value of the specified environment variable
    """
    if env_var in os.environ:
        return os.environ[env_var]
    else:
        return ''

class CSSSConfig():
#class to retrieve hcp-specific credentials and configurations

  def __init__(self):
    self.logger = logging.getLogger('CSSSConfig')

  def get_csss_config(self):

    csss_config = {
      'csss_user': '',
      'csss_client_id': '',
      'csss_client_secret': '',
      'csss_refresh_token': ''
    }

    csss_config['csss_user'] = self.get_csss_user()
    csss_config['csss_client_id'] = self.get_csss_client_id()
    csss_config['csss_client_secret'] = self.get_csss_client_secret()
    csss_config['csss_refresh_token'] = self.get_csss_refresh_token()

    return csss_config

  def get_csss_user(self):
    csss_user = ''
    csss_yml = get_file_config('csss-creds.yml')
    csss_user = get_env_config('CSSS_USER')
    if csss_user: self.logger.debug('Retrieved {} from {}'.format('csss_user', 'env'))
    if not csss_user and csss_yml:
      csss_user = csss_yml['csss_website']['user']
      if csss_user: self.logger.debug("Retrieved {} from {}".format('csss_user','csss-creds.yml'))
    return csss_user

  def get_csss_client_id(self):
    csss_client_id = ''
    csss_yml = get_file_config('csss-creds.yml')
    csss_client_id = get_env_config('csss_client_id')
    if csss_client_id: self.logger.debug('Retrieved {} from {}'.format('csss_client_id', 'env'))
    if not csss_client_id and csss_yml:
      csss_client_id = csss_yml['csss_website']['client_id']
      if csss_client_id: self.logger.debug('Retrieved {} from {}'.format('csss_client_id', 'csss-creds.yml'))
    return csss_client_id

  def get_csss_client_secret(self):
    csss_client_secret = ''
    csss__yml = get_file_config('csss-creds.yml')
    csss_client_secret = get_env_config('csss_client_secret')
    if csss_client_secret: self.logger.debug('Retrieved {} from {}'.format('csss_client_secret', 'env'))
    if not csss_client_secret and csss_yml:
      csss_client_secret = csss_yml['csss_website']['client_id']
      if csss_client_secret: self.logger.debug('Retrieved {} from {}'.format('csss_client_secret', 'csss-creds.yml'))
    return csss_client_secret

  def get_csss_refresh_token(self):
    csss_refresh_token = ''
    csss__yml = get_file_config('csss-creds.yml')
    csss_refresh_token = get_env_config('csss_refresh_token')
    if csss_refresh_token: self.logger.debug('Retrieved {} from {}'.format('csss_refresh_token', 'env'))
    if not csss_refresh_token and csss_yml:
      csss_refresh_token = csss_yml['csss_website']['client_id']
      if csss_refresh_token: self.logger.debug('Retrieved {} from {}'.format('csss_refresh_token', 'csss-creds.yml'))
    return csss_refresh_token