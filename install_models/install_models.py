#!/usr/bin/python
# -*- coding: utf-8 -*-

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

# This script installs Stanford CoreNLP models into a convenient location of the
# OS it is invoked on.
#
# Since CoreNLP uses a version scheme for downloads different from the actual
# version (date) and checksum checks should be included for validating fresh and
# skipping existing downloads, the specification takes place in the file
# `versions` in the source root. `versions` maps versions to download URLs for
# model/language identifier and checksums.

import os
import plac
import urwid
import json
import hashlib
import logging
import urllib

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('corenlp-install-models.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

version_default = "3.7.0"
version_path_default = os.path.realpath(os.path.join(__file__, os.path.pardir, "corenlp-install-models-versions"))

@plac.annotations(version=("The version to download and install", "option"),
        versions_path=("A file containing mapping between versions, model/language identifiers and checksums", "option"))
def install_models(version=version_default,
        versions_path=version_path_default):
    logger.debug("version: %s" % (version,))

    if os.name == "posix" or os.name == "mac":
        home = os.path.expanduser("~")
    elif os.name == "nt":
        # Windows
        home = os.path.expanduser("~home") # see https://docs.python.org/2/library/os.path.html#os.path.expanduser for an explanation
    else:
        raise RuntimeError("The operating system '%s' isn't supported, can't proceed" % (os.name,))

    location_unprivileged = os.path.join(home, "CoreNLP-models-%s" % (version,))
    if os.name == "posix":
        location_privileged = "/usr/share/lib/corenlp-models-%s/" % (version,)
    elif os.name == "nt":
        # Windows
        location_privileged = "C:\\Program Files\\CoreNLP-models-%s\\" % (version,)
            # no better idea where to put a jar on Windows
    elif os.name == "mac":
        location_privileged = "/Library/CoreNLP-models-%s" % (version,)
            # no better idea where to put a jar on Mac, using `/Library/Java/Extensions` is discouraged<ref>http://stackoverflow.com/questions/12842063/where-to-install-jar-files-on-os-x-so-other-java-applications-will-find-them</ref>
    else:
        raise RuntimeError("The operating system '%s' isn't supported, can't proceed" % (os.name,))

    versions_file = open(versions_path, "r")
    versions_file_content = versions_file.read()
    versions_obj = json.loads(versions_file_content)
    models = versions_obj.keys()

    model_check_boxes = []
    for model in models:
        model_check_box = urwid.CheckBox(label=model, state=False)
        model_check_box.model = model
        model_check_boxes.append(model_check_box)
    group = []
    radio_button_unprivileged = urwid.RadioButton(group=group, label="unprivileged location (%s)" % (location_unprivileged,), state=True, on_state_change=None)
    radio_button_privileged = urwid.RadioButton(group=group, label="privileged location (%s)" % (location_privileged,), state=False, on_state_change=None)

    def install(arg):
        if radio_button_unprivileged.state == True:
            assert radio_button_privileged.state == False
            location = location_unprivileged
        else:
            assert radio_button_unprivileged.state == False
            location = location_privileged
        logger.debug("selected location: %s" % (location,))
        selected_models = []
        for model_check_box in model_check_boxes:
            if model_check_box.state == True:
                selected_models.append(model_check_box.model)
        logger.info("selected models: %s" % (selected_models,))
        for selected_model in selected_models:
            if not versions_obj[selected_model][version]:
                raise ValueError("version %s not specified for model '%s' in versions file '%s'" % (version, selected_model, versions_path,))
        for selected_model in selected_models:
            url = versions_obj[selected_model][version]["url"]
            url_split = url.split("/")
            file_target = url_split[len(url_split)-1]
            file_target_path = os.path.join(location, file_target)
            md5 = versions_obj[selected_model][version]["md5"]
            while True:
                if os.path.exists(file_target_path):
                    logger.info("validating MD5 checksum of existing file '%s'" % (file_target_path,))
                    file_target_md5 = hashlib.md5(open(file_target_path, "rb").read()).hexdigest()
                    logger.info("MD5 checksum for target file '%s' is %s" % (file_target_path, file_target_md5,))
                    if file_target_md5 == md5:
                        logger.info("MD5 checksums for file '%s' match" % (file_target_path,))
                        break
                    else:
                        logger.warn("MD5 checksum of existing file '%s' doesn't match %s, downloading new file again" % (file_target_path, md5,))
                # download
                #widgets = ['Test: ', Percentage(), ' ', Bar(marker=RotatingMarker()), ' ', ETA(), ' ', FileTransferSpeed()]
                #pbar = ProgressBar(widgets=widgets)

                #def dlProgress(count, blockSize, totalSize):
                #    if pbar.maxval is None:
                #        pbar.maxval = totalSize
                #        pbar.start()

                #    pbar.update(min(count*blockSize, totalSize))

                logger.info("started download from '%s'" % (url,))
                file_target_parent_path = os.path.dirname(file_target_path)
                if not os.path.exists(file_target_parent_path):
                    os.makedirs(file_target_parent_path)
                if not os.path.exists(file_target_path):
                    open(file_target_path, 'a').close() # touch file_target_path because urllib.urlretrieve fails in case it doesn't exist
                urllib.urlretrieve(url, file_target_path)#, reporthook=dlProgress)
                #pbar.finish()
                logger.info("finished download from '%s'" % (url,))
        logger.info("finished all installations")
        exit()

    versions_file_text = urwid.Text("Choose versions file")
    model_text = urwid.Text("Choose the model(s) to install")
    location_text = urwid.Text("Choose CoreNLP models installation mode")
    versions_file_edit = urwid.Edit(caption="Versions file path: ", edit_text=versions_path, multiline=False, align='left', wrap='space', allow_tab=False, edit_pos=None, layout=None, mask=None)
    install_button = urwid.Button("Install", on_press=install)
    def exit_handler(arg):
        exit()
    cancel_button = urwid.Button("Cancel", on_press=exit_handler)

    listbox_content = [versions_file_text,
            versions_file_edit,
            model_text] \
            +model_check_boxes \
            +[location_text,
            radio_button_unprivileged,
            radio_button_privileged,
            install_button,
            cancel_button]
    listbox = urwid.ListBox(urwid.SimpleListWalker(listbox_content))
    loop = urwid.MainLoop(listbox,
            unhandled_input=unhandled)
    loop.run()

def unhandled(key):
    if key == 'f8':
        exit()

def exit():
    raise urwid.ExitMainLoop()

if __name__ == "__main__":
    plac.call(install_models)
