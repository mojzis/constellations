import json
import pathlib
import json
import os

import click
from jinja2 import Environment, FileSystemLoader
from slugify import slugify
import requests

from PIL import Image, UnidentifiedImageError

PUBLIC_DIR = 'public'
THUMB_DIR = f'{PUBLIC_DIR}/thumbs'
IMG_DIR = f'{PUBLIC_DIR}/img'
THUMB_EXT = 'webp'
IMG_EXT = 'webp'
THUMB_SIZE = 70

REPO_URL = 'https://raw.githubusercontent.com/Stellarium/stellarium-skycultures/master'

@click.group()
def main():
    """click"""
    pass

def create_thumbnail(culture, orig_file_name, file_name):
    # todo: check extension
    thumb_file = f'{THUMB_DIR}/{culture}/{file_name}.{THUMB_EXT}'
    img_file = f'{IMG_DIR}/{culture}/{file_name}.{IMG_EXT}'
    # check if thumb exists
    if os.path.isfile(thumb_file):
        return
    else:
        if not os.path.isfile(img_file):
            # https://github.com/Stellarium/stellarium-skycultures/blob/master/
            # arabic/illustrations/Bearer-of-the-Demons-Head.webp?raw=true
            r = requests.get(
                f'{REPO_URL}/{culture}/{orig_file_name}?raw=true'
                , allow_redirects=True)
            # TODO: fail if r 404
            i = open(img_file,'wb')
            i.write(r.content)

        try:
            src_img = Image.open(img_file)
            src_img.thumbnail((THUMB_SIZE,THUMB_SIZE))
            src_img.save(thumb_file)
        except UnidentifiedImageError as e:
            print(e)


def get_culture_data(culture):
    data_path = f'data/{culture["slug"]}.json'
    if os.path.isfile(data_path):
        f = open(data_path)
    else:
        r = requests.get(
            f'https://raw.githubusercontent.com/Stellarium/stellarium-skycultures/master/{culture["slug"]}/index.json'
            , allow_redirects=True)
        f = open(data_path, 'wb')
        f.write(r.content)
        # this looks totally broken, is there a better way ? (r.content is binary)
        f = open(data_path, 'r')

    culture_data = json.load(f)
    f.close()
    return culture_data

def prepare_folders(culture):
    os.makedirs(f'public/{culture["slug"]}', exist_ok=True)
    os.makedirs(f'{THUMB_DIR}/{culture["slug"]}', exist_ok=True)
    os.makedirs(f'{IMG_DIR}/{culture["slug"]}', exist_ok=True)


@click.command()
def pub():
    cultures = [
        {"name":"Arabic (Al-Sufi)","slug":"arabic_al-sufi"},
        {"name":"Aztec","slug":"aztec"},
        {"name":"Belarusian","slug":"belarusian"},
        {"name":"Boorong","slug":"boorong"},
        {"name":"Chinese","slug":"chinese_contemporary"},
        {"name":"Dakota","slug":"dakota"},
        {"name":"Hawaiian","slug":"hawaiian_starlines"},
        {"name":"Inuit","slug":"inuit"},
        {"name":"Kamilaroi","slug":"kamilaroi"},
        {"name":"Macedonian","slug":"macedonian"},
        {"name":"Maori","slug":"maori"},
        {"name":"Northern andes","slug":"northern_andes"},
        {"name":"Ojibwe","slug":"ojibwe"},
        {"name":"Romanian","slug":"romanian"},
        {"name":"Sami","slug":"sami"},
        {"name":"Western","slug":"western"},
    ]
    for culture in cultures:
        print(f"Processing {culture['name']}")
        culture_data = get_culture_data(culture)
        constellations = culture_data['constellations']
        env = Environment(
            loader=FileSystemLoader('templates'),
        )
        const_data = []
        prev = 'index'
        for con in constellations:
            image = con.get('image','none')
            # for now we only create a page when a constellation has an image
            if image == 'none':
                continue
            img_path = image['file']
            img_filename = pathlib.Path(img_path).stem
            create_thumbnail(culture["slug"], img_path, img_filename)
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
                        "img" : img_path,
                        'thumb_filename': f'{img_filename}.{THUMB_EXT}',
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

        # assign a thumb from the first constellation
        culture['thumb_filename'] = const_data[0]['thumb_filename']

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
