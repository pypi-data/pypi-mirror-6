import zipfile
import re

import lxml.etree as ET
import qscollect.collectors.omnifocus._omnientry as omnientry
import qscollect.collectors.omnifocus.helpers as h


FILENAME_RE = re.compile(r"(?P<start>\S{14})=(?P<end>\S{14})")


class OmniFocus(object):
    def __init__(self):
        self._context = {}
        self._tasks = {}

    def _add_entry(self, element):
        tag = h._NS_STRIP(element.tag)
        func = getattr(self, "_handle_{0}".format(tag), self._nop)
        func(element)

    @property
    def _id(self):
        """ Needed for compatibility with the "previous state" loading from the database and for testing """
        return ""

    def _feed_snapshop(self, tree):
        # print ET.tostring(tree, pretty_print=True)
        for element in tree:
            self._add_entry(element)

    def _feed_transactional(self, tree):
        for element in tree:
            if "op" not in element.attrib:
                self._add_entry(element)
            else:
                func = getattr(self, "_op_{0}".format(element.attrib["op"]), self._nop)
                func(element)

    @property
    def state(self):
        return {
            'contexts': dict(self.contexts),
            'tasks': dict(self.tasks)
        }

    def get_content_tree_from_zip(self, zip_path):
        data_file = zipfile.ZipFile(zip_path)
        content_file = data_file.open("contents.xml")
        xml_data = ET.parse(content_file)
        return xml_data.getroot()

    def feed(self, filename):
        matches = FILENAME_RE.search(filename)
        start, end = matches.groups()
        tree = self.get_content_tree_from_zip(filename)
        if start == "00000000000000":
            self._feed_snapshop(tree)
        else:
            self._feed_transactional(tree)

    def _nop(self, *args, **kargs):
        pass  # Do nothing for tags we don't understand


    def _entry(self, entry_type, element):
        id_ = element.attrib["id"]
        data = {}
        for e in element:
            data[h._NS_STRIP(e.tag)] = e
        entry = omnientry._OmniEntry(object_id=id_, entry_type=entry_type, **data)
        return id_, entry

    def _handle_context(self, element):
        id_, entry = self._entry("context", element)
        self._context[id_] = entry

    def _handle_task(self, element):
        id_, entry = self._entry("task", element)
        self._tasks[id_] = entry

    def _op_update(self, element):
        type_ = h._NS_STRIP(element.tag)
        id_ = element.attrib["id"]
        func = getattr(self, "_update_{0}".format(type_), self._nop)
        func(id_, element)

    def _update_task(self, id_, element):
        entry = self._tasks[id_]
        data = {}
        for e in element:
            data[h._NS_STRIP(e.tag)] = e

        entry.update(data)


    @property
    def tasks(self):
        return self._tasks

    @property
    def contexts(self):
        return self._context
