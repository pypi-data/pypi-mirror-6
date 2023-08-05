#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import base64
from . import templates
import imp


class Converter(object):

    def __init__(self, input_file=None):
        """ Create Converter instance

        :param input_file Will be loaded as a base
        :type str or unicode
        """
        self.files = {}
        self.template = templates.BasicTemplate()
        if input_file is not None and os.path.isfile(input_file):
            self.load_file(input_file)

    def load_file(self, input_file):
        """ Loads data array from file (result of this converter)

        Tries to import, load and replace files' data.
        It will overwirte previously added items with #add_file or #load_file.

        :param input_file
        :type str or unicode
        """
        pyimg = imp.load_source('image2py_taf', input_file)
        self.files = pyimg.data
        self.set_template(templates.templateByName(pyimg.template))

    def set_template(self, template):
        """ Sets template to be used when generating output

        :param template TEmplate instance
        :type instance of BasicTemplate
        """
        if isinstance(template, templates.BasicTemplate):
            self.template = template
        else:
            raise TypeError('converter#set_template:'
                            'Template must inherit from BasicTemplate')

    def save(self, filename=None):
        """ Generates output and saves to given file

        :param filename File name
        :type str or unicode
        """
        if filename is None:
            raise IOError('Converter#save: Undefined filename')
        cnt = self.output()
        with (open(filename, 'wb+')) as f:
            f.write(cnt.encode('utf-8'))

    def add_file(self, filename):
        """ Read and adds given file's content to data array
        that will be used to generate output

        :param filename File name to add
        :type str or unicode
        """
        with (open(filename, 'rb')) as f:
            data = f.read()
        # below won't handle the same name files
        # in different paths
        fname = os.path.basename(filename)
        self.files[fname] = base64.b64encode(data)

    def remove_file(self, filename):
        """ Removes item from data array associated with filename

        :param filename File name
        :type str to unicode
        """
        del self.files[os.path.basename(filename)]

    def output(self):
        """ Generates output from data array

        :returns Pythoned file
        :rtype str or unicode
        """
        if len(self.files) < 1:
            raise Exception('Converter#output: No files to convert')
        return self.template.render(self.files)
