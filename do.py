import json
import pathlib
import json

import click
from jinja2 import Environment, FileSystemLoader
from slugify import slugify


@click.group()
def main():
    """click"""
    pass



@click.command()
def pub():
    """ go through index, generate pages"""
    f = open('data/dakota.json')
    culture = json.load(f)
    constellations = culture['constellations']
    env = Environment(
        loader=FileSystemLoader('templates'),
    )
    const_data = []
    prev = 'index'
    for con in constellations:
        # create a page for each constellation 
        name = con['common_name']['native']
        filename = slugify(name)
        const_data.append({
                    "img" : con['image']['file'],
                    'name': name,
                    'trans': con['common_name']['english'],
                    'filename' : filename,
                    'prev': prev
                    })
        prev = filename
    
    for j in range(0,len(const_data)-1):
        const_data[j]['next'] = const_data[j+1]['filename']

    for const in const_data:
        with open(f'public/dakota/{const["filename"]}.html','w') as s:
            s.write(env.get_template('const.html')
                .render(const=const))
    with open(f'public/dakota/index.html','w') as i:
        i.write(env.get_template('index.html')
            .render(const_data=const_data, culture='Dakota'))


# generate pages
# put each on a separate page, provide a listing

main.add_command(pub)


if __name__ == "__main__":
    main()