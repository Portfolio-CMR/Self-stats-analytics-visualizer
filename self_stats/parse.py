import html5lib
import lxml.etree as ET
import requests
import io  # Import the io module

def preprocess_html_to_xml(html_content):
    # Parse the HTML with html5lib, which handles malformed HTML well
    document = html5lib.parse(html_content, namespaceHTMLElements=False)
    # Serialize the parsed HTML back to a well-formed XML string, now keeping as bytes
    return html5lib.serialize(document, encoding='utf-8')

def parse_html(file_path):
    # Read and preprocess the HTML file
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    xml_content = preprocess_html_to_xml(html_content)

    # Convert the XML content bytes to a file-like object
    xml_file = io.BytesIO(xml_content)

    # Now parse the well-formed XML content
    context = ET.iterparse(xml_file, events=("end",), tag="div")
    data = {'search_text': None, 'date': None, 'coordinates': None}

    for event, elem in context:
        if 'content-cell mdl-cell mdl-cell--6-col mdl-typography--body-1' in elem.get('class', ''):
            # Extract the search text and date
            data['search_text'] = elem.xpath(".//a/text()")[0].strip()
            data['date'] = elem.xpath(".//text()")[-1].strip()
        elif 'content-cell mdl-cell mdl-cell--12-col mdl-typography--caption' in elem.get('class', ''):
            # Extract the location coordinates from the link
            link = elem.xpath(".//a[contains(@href, 'maps')]/@href")[0]
            params = requests.utils.urlparse(link).query
            for param in params.split('&'):
                if 'center' in param:
                    data['coordinates'] = param.split('=')[1]
                    break

        # Clear the element to save memory
        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]

    return data

# Specify the file path here
file_path = 'data/.01_activity.html'
result = parse_html(file_path)
print(result)
