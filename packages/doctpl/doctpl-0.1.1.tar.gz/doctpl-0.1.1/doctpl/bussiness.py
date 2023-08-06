from __future__ import unicode_literals

import os
import shutil


class _GLOBAL:
    DIR_PATH = os.path.expanduser('~/.doctpl')
    if not os.path.exists(DIR_PATH):
        os.mkdir(DIR_PATH)


class ToolSet(object):

    @property
    def dir_abs_path(self):
        return _GLOBAL.DIR_PATH

    @property
    def avaliable_templates(self):
        """
        return:
            dict of templates (file name, path) pairs.
        """

        template_abspath_mapping = {}
        for filename in os.listdir(self.dir_abs_path):
            file_path = os.path.join(self.dir_abs_path, filename)
            if os.path.isfile(file_path):
                template_abspath_mapping[filename] = file_path
        return template_abspath_mapping

    def make_copy(self, to_path, template_name):
        """
        parameters:
            to_path: target path entered in shell.
            template_name: file name of template.
        return:
            absolute path of target file.
        """

        template_path = self.avaliable_templates.get(template_name, None)
        target_path = os.path.abspath(to_path)

        if template_path is None:
            raise Exception("No Such Template: {}".format(template_name))
        if os.path.exists(target_path):
            raise Exception("{} Already Existed.".format(target_path))

        # symbolic link should not be use.
        shutil.copyfile(template_path, target_path)

        return target_path
