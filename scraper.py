import requests
from bs4 import BeautifulSoup


def get_section_urls(soup, section_name):
    header = soup.find(lambda tag: tag.name.startswith('h') and section_name.lower() in tag.text.lower())
    if not header:
        return {}
    table = header.find_next('table')
    if not table:
        return {}
    rows = table.select('tr')[1:]
    result = {
        'ts': [],
        'lar': [],
        'combined_mlar': [],
        'combined_mlar_with_header': []
    }
    for row in rows:
        cells = row.find_all('td')
        if len(cells) < 3:
            continue
        file_type = cells[0].text.strip().lower()
        link = cells[2].find('a')
        if not link:
            continue
        href = link.get('href').strip()
        if file_type == 'ts':
            result['ts'].append(href)
        elif file_type == 'lar':
            result['lar'].append(href)
        elif 'combined' in file_type and 'with header' in file_type:
            result['combined_mlar_with_header'].append(href)
        elif 'combined' in file_type:
            result['combined_mlar'].append(href)
    return result


def get_all_sections(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    sections = ['Public', 'Private', 'Archive']
    result = {}
    for section in sections:
        result[section.lower()] = get_section_urls(soup, section)
    return result


url = "https://<your-wiki-url>"
all_data = get_all_sections(url)

for section, files in all_data.items():
    print(f"\n{section.upper()} TS:")
    print('\n'.join(files['ts']))
    print(f"\n{section.upper()} LAR:")
    print('\n'.join(files['lar']))
    print(f"\n{section.upper()} COMBINED MLAR:")
    print('\n'.join(files['combined_mlar']))
    print(f"\n{section.upper()} COMBINED MLAR WITH HEADER:")
    print('\n'.join(files['combined_mlar_with_header']))
