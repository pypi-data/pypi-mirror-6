import os, ConfigParser
import pkginfo

class BaseFinder(object):
    """
    Base finder for installed eggs
    """
    eggs = []
    
    def format_egg_row(self, name, version):
        return "{name}={version}".format(name=name, version=version)
    
    def render(self):
        return '\n'.join([self.format_egg_row(k,v) for k,v in self.eggs])

class BuildoutConfigFinder(BaseFinder):
    """
    Find installed eggs from the given buildout config
    
    WARNING: This implementation is not really working because it follows config 
             extends and the '+=' does not seem to be honored in option merging 
             with ConfigParser
    """
    def __init__(self, initial_config):
        self.initial_config = initial_config
            
    def get_configparser(self):
        """
        Configure a ConfigParser and return it
        """
        parser = ConfigParser.SafeConfigParser()
        # Preserve case options
        parser.optionxform = str
        
        return parser
        
    def crawl(self):
        """
        Crawl config file following the 'extend' option of 'Buildout' section
        """
        configs = self.recurse_config_finder(self.initial_config)
        configs.reverse()
        self.find_eggs(configs)
        
    def recurse_config_finder(self, config_path, paths=[]):
        """
        Recursively find all configs extends filepaths
        """
        print "config:", config_path
        paths.append(config_path)
        
        current_path, current_filename = os.path.split(config_path)
        print "* current_path:", current_path
        print "* current_filename:", current_filename
        
        # Read the file to find extend option
        parser = self.get_configparser()
        parser.read([config_path])
        
        # Following config extends if any
        try:
            config_extends = parser.get('buildout', 'extends')
        except ConfigParser.NoSectionError, ConfigParser.NoOptionError:
            pass
        else:
            config_extends = os.path.join(current_path, config_extends)
            if os.path.exists(config_extends):
                print "config_extends:", config_extends
                paths = self.recurse_config_finder(config_extends)
        
        return paths
    
    def find_eggs(self, configs):
        """
        configs is a list of config file that will be merged, this should be 
        in the right order
        """
        parser = self.get_configparser()
        # Read needed cfg files
        parser.read(configs)
        
        egg_list = parser.get('buildout', 'eggs')
        egg_list = egg_list.strip().splitlines()

        # Get versions for each defined egg in buildout
        for egg_name in egg_list:
            try:
                version_name = parser.get('versions', egg_name)
            #except ConfigParser.NoOptionError:
            except:
                version_name = "unknow"

            self.eggs.append( (egg_name, version_name) )
        return self.eggs


class PipFinder(BaseFinder):
    """
    TODO: ?
    
    Find installed eggs from PIP frozen file (like requirements.txt)
    """
    pass


class BuildoutEggdirFinder(BaseFinder):
    """
    Find installed eggs directly from Buildout egg directory
    
    This should get the installed eggs list (like the one generated within 
    django-instance script) and parse their "EGG-INFO/PKG-INFO" file to know 
    the name and the version.
    
    Note that this will not work for egg installed in develop mode.
    """
    def __init__(self, eggs_dir):
        self.eggs_dir = eggs_dir
            
    def crawl(self):
        """
        Crawl config file following the 'extend' option of 'Buildout' section
        """
        for item in os.listdir(self.eggs_dir):
            infos = pkginfo.Develop(os.path.join(self.eggs_dir, item))
            self.eggs.append( (infos.name, infos.version) )

# Testing
if __name__ == "__main__":
    #finder = BuildoutConfigFinder('../../../development.cfg')
    #finder.crawl()
    #print finder.render()

    finder = BuildoutEggdirFinder('../../../eggs')
    finder.crawl()
    print finder.render()
