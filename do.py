import json
import pathlib
import json
import os

import click
from jinja2 import Environment, FileSystemLoader
from slugify import slugify
import requests

@click.group()
def main():
    """click"""
    pass



@click.command()
def pub():
    cultures = [
        {"name":"Dakota","slug":"dakota"},
        {"name":"Arabic","slug":"arabic"},
        {"name":"Aztec","slug":"aztec"},
        {"name":"Belarusian","slug":"belarusian"},
        {"name":"Boorong","slug":"boorong"},
        {"name":"Chinese","slug":"chinese_contemporary"},
        {"name":"Hawaiian","slug":"hawaiian_starlines"},
        {"name":"Inuit","slug":"inuit"},
        {"name":"Kamilaroi","slug":"kamilaroi"},
        {"name":"Macedonian","slug":"macedonian"},
        {"name":"Maori","slug":"maori"},
        {"name":"Northern andes","slug":"northern_andes"},
        {"name":"Ojibwe","slug":"ojibwe"},
        {"name":"Romanian","slug":"romanian"},
        {"name":"Western","slug":"western"},
    ]
    for culture in cultures:
        data_path = f'data/{culture["slug"]}.json'
        if os.path.isfile(data_path):
            f = open(data_path)
        else:
            r = requests.get(
                f'https://raw.githubusercontent.com/Stellarium/stellarium-skycultures/master/{culture["slug"]}/index.json'
                , allow_redirects=True)
            f = open(data_path,'wb')
            f.write(r.content)
            f = open(data_path,'r')

        culture_data = json.load(f)
        f.close()
        os.makedirs(f'public/{culture["slug"]}',exist_ok=True)
        constellations = culture_data['constellations']
        env = Environment(
            loader=FileSystemLoader('templates'),
        )
        const_data = []
        prev = 'index'
        for con in constellations:
            image = con.get('image','none')
            if image == 'none':
                continue
            # create a page for each constellation
            native = con['common_name'].get('native','none')
            name = con['common_name'].get('english')
            pronounce = con['common_name'].get('pronounce',name)
            if native == 'none':
                trans = pronounce
            else:
                trans = name
                name = native
            filename = slugify(name)
            const_data.append({
                        "img" : image['file'],
                        'name': name,
                        'trans': trans,
                        'filename' : filename,
                        'prev': prev,
                        'next': 'index'
                        })
            prev = filename
        
        for j in range(0,len(const_data)-1):
            const_data[j]['next'] = const_data[j+1]['filename']
        # const_data[len(const_data)]['next'] = 'index'

        for const in const_data:
            with open(f'public/{culture["slug"]}/{const["filename"]}.html','w') as s:
                s.write(env.get_template('const.html')
                    .render(const=const, culture=culture))
        
        with open(f'public/{culture["slug"]}/index.html','w') as i:
            i.write(env.get_template('cindex.html')
                .render(const_data=const_data, culture=culture))

    with open(f'public/index.html','w') as ei:
        ei.write(env.get_template('index.html')
            .render(cultures=cultures))


# generate pages
# put each on a separate page, provide a listing

main.add_command(pub)


if __name__ == "__main__":
    main()