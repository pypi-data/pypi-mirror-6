#-*- coding:utf-8 -*-


class BasicTemplate(object):

    def __init__(self):
        self._part_files = []
        self._part_imports = []
        self._part_func = []

    def part_files(self, files):
        self._part_files.append("data = {}")
        for name, data in files.items():
            self._part_files.append(
                self._prepare_file_var(name, data)
            )

    def _prepare_file_var(self, name, data):
        output = ["data['{!s}'] = \"\" ".format(name)]
        while data:
            part = data[:70]
            data = data[70:]
            output.append('    "{!s}" '.format(part))
        return "\\\n".join(output)

    def part_imports(self):
        self._part_imports.append("import base64")

    def part_functions(self):
        self._part_func = [
            "def get_data(name):\n    return data[name]",
            "def get_decoded(name):\n    return base64.b64decode(data[name])",
            "def list_files():\n    return list(data.keys())"
            ]

    def render(self, files):
        self.part_imports()
        self.part_functions()
        self.part_files(files)
        header = "# created with image2py\n" \
                 "template = '{!s}'".format(self.__class__.__name__)
        blocks = [header,
                  "\n".join(self._part_imports),
                  "\n\n".join(self._part_files),
                  "\n\n".join(self._part_func)]
        return "\n\n\n".join(blocks)

# Below are example templates for qt  toolkit


class QtTemplate(BasicTemplate):

    def part_imports(self):
        super(QtTemplate, self).part_imports()
        self._part_imports.append("""
try:
    from PySide.QtCore import QByteArray
    from PySide.QtGui import QIcon, QPixmap, QImage
except:
    from PyQt4.QtCore import QByteArray
    from PyQt4.QtGui import QIcon, QPixmap, QImage
""")

    def part_functions(self):
        super(QtTemplate, self).part_functions()
        self._part_func += [
            "def getAsQByteArray(n):\n    QByteArray.fromBase64(data[n])",
            "def getAsQPixmap(n):\n    p = QPixmap\n"
            "    p.loadFromData(getAsQByteArray(n))\n    return p",
            "def getAsQIcon(n):\n    return QIcon(getAsQPixmap(n))",
            "def getAsQImage(n):\n"
            "    return QImage.fromData(getAsQByteArray(n))"
        ]


class PySideTemplate(QtTemplate):

    def part_imports(self):
        BasicTemplate.part_imports(self)
        self._part_imports.append("""
from PySide.QtCore import QByteArray
from PySide.QtGui import QIcon, QPixmap, QImage
""")


class PyQtTemplate(BasicTemplate):

    def part_imports(self):
        BasicTemplate.part_imports(self)
        self._part_imports.append("""
from PyQt4.QtCore import QByteArray
from PyQt4.QtGui import QIcon, QPixmap, QImage
""")


lookup_map = {'basic': BasicTemplate,
              'qt': QtTemplate,
              'pyside': PySideTemplate,
              'pyqt': PyQtTemplate}


def templateByName(name):
    cname = name.strip().lower().replace('template', '')
    if cname not in lookup_map:
        raise Exception('Given template does not exist.')
    return lookup_map[cname]()
