import os
import sys
import subprocess
import setuptools
import shutil
import tempfile
import logging
from zc.buildout.download import Download
import zc
import zc.recipe.egg

DOWNLOAD_URL = "http://projects.unbit.it/downloads/uwsgi-{0}.tar.gz"


def str_to_bool(s):
    """
    Converts a string to a bool value; looks at the first character,
    if it's y(es), t(rue) or 1 returns True, otherwise, False.
    """
    if len(s) > 0:
        if s[0] in "yYtT1":
            return True
    return False


class UWSGI:
    """
    Buildout recipe downloading, compiling and configuring python paths for uWSGI.
    """

    def __init__(self, buildout, name, options):
        self.egg = zc.recipe.egg.Egg(buildout, options["recipe"], options)
        self.name = name
        self.buildout = buildout
        self.log = logging.getLogger(self.name)
        
        # Use the "download-cache" directory as cache, if present
        self.cache_dir = buildout["buildout"].get("download-cache")
        if self.cache_dir is not None:
            # If cache_dir isn't an absolute path, make it relative to buildout's directory
            self.cache_dir = os.path.join(buildout["buildout"]["directory"], self.cache_dir)
                    
        if "extra-paths" in options:
            options["pythonpath"] = options["extra-paths"]
        else:
            options.setdefault("extra-paths", options.get("pythonpath", ""))
        self.options = options

    def download_release(self):
        """
        Download uWSGI release based on "version" option and return path to downloaded file.
        """
        if self.cache_dir is not None:
            download = Download(cache=self.cache_dir)
        else:
            self.log.warning("not using a download cache for uwsgi")
            download = Download()
        download_url = self.options.get("download-url", DOWNLOAD_URL)
        download_path, is_temp = download(download_url.format(self.options.get("version", "latest")))
        return download_path

    def extract_release(self, download_path):
        """
        Extracts uWSGI package and returns path containing uwsgiconfig.py along with path to extraction root.
        """
        uwsgi_path = None
        extract_path = tempfile.mkdtemp("-uwsgi")
        setuptools.archive_util.unpack_archive(download_path, extract_path)
        for root, dirs, files in os.walk(extract_path):
            if "uwsgiconfig.py" in files:
                uwsgi_path = root
        return uwsgi_path, extract_path

    def build_uwsgi(self, uwsgi_path):
        """
        Build uWSGI and returns path to executable.
        """
        # Change dir to uwsgi_path for compile.
        current_path = os.getcwd()
        os.chdir(uwsgi_path)

        #
        # Set the environment
        # Call make
        #
        profile = self.options.get("profile", "default.ini")
        os.environ["UWSGI_PROFILE"] = profile
        os.environ["PYTHON_BIN"] = sys.executable

        subprocess.check_call(["make", "-f", "Makefile"])

        os.chdir(current_path)
        return os.path.join(uwsgi_path, "uwsgi")

    def copy_uwsgi_to_bin(self, uwsgi_executable_path):
        """
        Copy uWSGI executable to bin and return the resulting path.
        """
        bin_path = self.buildout["buildout"]["bin-directory"]
        shutil.copy(uwsgi_executable_path, bin_path)
        return os.path.join(bin_path, os.path.basename(uwsgi_executable_path))

    def get_extra_paths(self):

        # Add libraries found by a site .pth files to our extra-paths.
        if 'pth-files' in self.options:
            import site
            for pth_file in self.options['pth-files'].splitlines():
                pth_libs = site.addsitedir(pth_file, set())
                if not pth_libs:
                    self.log.warning(
                        'No site *.pth libraries found for pth_file=%s' % (
                        pth_file,))
                else:
                    self.log.info('Adding *.pth libraries=%s' % pth_libs)
                    self.options['extra-paths'] += '\n' + '\n'.join(pth_libs)

        # Add local extra-paths.
        return [p.replace('/', os.path.sep) for p in
                self.options['extra-paths'].splitlines() if p.strip()]

    def create_conf_xml(self):
        """
        Create xml file file with which to run uwsgi.
        """
        path = os.path.join(self.buildout["buildout"]["parts-directory"], self.name)
        try:
            os.mkdir(path)
        except OSError:
            pass

        xml_path = os.path.join(path, "uwsgi.xml")

        conf = ""
        for key, value in self.options.items():
            # Configuration items for the XML file are prefixed with "xml-"
            if key.startswith("xml-") and len(key) > 4:
                key = key[4:]
                if value.lower() == "true":
                    conf += "<%s/>\n" % key
                elif value and value.lower() != "false":
                    if "\n" in value:
                        for subvalue in value.split():
                            conf += "<%s>%s</%s>\n" % (key, subvalue, key)
                    else:
                        conf += "<%s>%s</%s>\n" % (key, value, key)

        requirements, ws = self.egg.working_set()

        # get list of paths to put into pythonpath
        #pythonpaths = zc.buildout.easy_install._get_path(ws, self.get_extra_paths())
        pythonpaths = ws.entries + self.get_extra_paths()

        # mungle basedir of pythonpath entries
        if 'pythonpath-eggs-directory' in self.options:
            source = self.options['eggs-directory']
            target = self.options['pythonpath-eggs-directory']
            pythonpaths = [path.replace(source, target) for path in pythonpaths]

        # generate pythonpath directives
        for path in pythonpaths:
            conf += "<pythonpath>%s</pythonpath>\n" % path

        with open(xml_path, "w") as f:
            f.write("<uwsgi>\n%s</uwsgi>" % conf)

        return xml_path

    def install(self):
        paths = []

        use_sys_binary = str_to_bool(self.options.get("use-system-binary", "false"))
        if not use_sys_binary:
            if not os.path.exists(os.path.join(self.buildout["buildout"]["bin-directory"], "uwsgi")):
                # Download uWSGI.
                download_path = self.download_release()

                # Extract uWSGI.
                uwsgi_path, extract_path = self.extract_release(download_path)

                # Build uWSGI.
                uwsgi_executable_path = self.build_uwsgi(uwsgi_path)

                # Copy uWSGI to bin.
                paths.append(self.copy_uwsgi_to_bin(uwsgi_executable_path))

                # Remove extracted uWSGI package.
                shutil.rmtree(extract_path)

        # Create uWSGI conf xml.
        paths.append(self.create_conf_xml())

        return paths

    def update(self):
        # Create uWSGI conf xml - the egg set might have changed even if
        # the uwsgi section is unchanged so it's safer to re-generate the xml
        self.create_conf_xml()
