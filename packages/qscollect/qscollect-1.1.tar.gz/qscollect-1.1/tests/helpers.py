import lxml.etree as ET
import os.path as path
import zipfile

DIR = path.abspath(path.join(
    path.dirname(__file__),
    "..",
    "test_data"
))

def data_file(*str):
    return path.join(DIR, *str)

def get_content_tree_from_zip(zip_path):
    data_file = zipfile.ZipFile(zip_path)
    content_file = data_file.open("contents.xml")
    xml_data = ET.parse(content_file)
    return xml_data.getroot()
