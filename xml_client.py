import xml.etree.cElementTree as ET


a = ET.Element('CompleteMultipartUpload')
b = ET.SubElement(a, 'Part')
ET.SubElement(b, 'PartNumber').text="1"
ET.SubElement(b, 'Etag').text="tag"


c = ET.SubElement(a, 'Part')
ET.SubElement(c, 'PartNumber').text="2"
ET.SubElement(c, 'Etag').text="tag2"
# root = ET.Element("CompleteMultipartUpload")
# # doc = ET.SubElement(root, "Part")
#
# doc=ET.SubElement(root, "Part").text = "1"
# ET.SubElement(doc, "PartNumber").text = "2"
# #
# # ET.SubElement(root, "Part").text = "2"
# #
# # ET.SubElement(doc, "PartNumber").text = "2"
#
# # tree = ET.ElementTree(root)
ET.dump(a)

# CompleteMultipartUpload

