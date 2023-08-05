from distutils.version import StrictVersion

__all__ = ["GraphViz"]


class GraphViz(object):
    """Some useful utilities related to Graphviz

    Get the version installed

        >>> from graphviz_tools import GraphViz
        >>> g = GraphViz()
        >>> g.get_version()

    """
    def __init__(self):
        pass

    def dot_in_path(self):
        """Is the dot executable found in the path ?

        :return: True if found, False otherwies
        """
        try:
            subprocess.Popen(["dot", "-V"])
        except OSError:
            return False
        return True

        
    def get_version(self):
        import subprocess
        t = subprocess.Popen(["dot", "-V"], shell=False, stderr=subprocess.PIPE)
        msg = t.stderr.read()
        version = msg.split("version")[1].strip()
        version = version.split(" ")[0]
        return version

    def is_striped_available(self):
        """Return true is the striped node style is available"""
        version = self.get_version()

        if StrictVersion(version) >= StrictVersion("2.30.0"):
            return True
        else:
            return False
