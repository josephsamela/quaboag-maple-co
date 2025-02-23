import qrcode
import qrcode.image.svg

from openpyxl import load_workbook
from datetime import datetime
from collections import defaultdict
from jinja2 import Environment, FileSystemLoader

def main():

    # Load data
    workbook = load_workbook('data.xlsx')
    trees = load_data(workbook, 'trees')
    yields = load_data(workbook, 'yields')

    # Load templates
    environment = Environment(loader=FileSystemLoader("templates/"))
    
    environment.filters['format_date'] = format_date
    environment.filters['format_latitude'] = format_latitude
    environment.filters['format_longitude'] = format_longitude

    template_tree = environment.get_template("tree.html")
    template_inventory = environment.get_template("inventory.html")

    # Iterate over trees
    for tree in trees:

        # Generate tree webpage
        page = template_tree.render(
            tree=tree,
            yields=get_yields(yields, tree)
        )
        render_page(
            page, 
            filename=f"site/tree/{tree['id']}.html"
        )

        # Generate tree QR code
        img = qrcode.make(
            data=f'samela.io/quaboag-maple-co/tree/{tree["id"]}',
            image_factory=qrcode.image.svg.SvgPathImage,
            border=0
        )
        img.save(f'site/assets/qr/{tree["id"]}.svg')

    # Render inventory page
    page = template_inventory.render(trees=trees)
    render_page(page, "site/index.html")


def render_page(page, filename):
    with open(filename, mode="w", encoding="utf-8") as message:
        message.write(page)
        print(f"... wrote {filename}")

def get_yields(yields, tree):
    data = []
    for y in yields:
        if y['tree'] == tree['id']:
            data.append(y)
    return data

def load_data(workbook, worksheet):
    first = True
    headers = None
    data = []
    for i, row in enumerate(workbook[worksheet].iter_rows(values_only=True)):
        if first:
            headers = row
            first = False
        else:
            rowdict = dict()
            for i, header in enumerate(headers):
                if header in ['id', 'tree']:
                    rowdict[header] = f"{row[i]:02}"
                else:
                    rowdict[header] = row[i]
            data.append(rowdict)
    return data

def format_date(date):
    if isinstance(date, datetime):
        return date.strftime('%b %-d, %Y')
    else:
        return date

def format_latitude(coordinate):
    degrees, minute, second = decdeg2dms(coordinate)
    
    
    if degrees < 0:
        direction = 'S'
    else:
        direction = 'N'

    return f'{round(abs(degrees))}°{round(minute)}\'{round(second)}" {direction}'

def format_longitude(coordinate):
    degrees, minute, second = decdeg2dms(coordinate)
    
    if degrees < 0:
        direction = 'W'
    else:
        direction = 'E'

    return f'{round(abs(degrees))}°{round(minute)}\'{round(second)}" {direction}'

def decdeg2dms(dd):
   is_positive = dd >= 0
   dd = abs(dd)
   minutes,seconds = divmod(dd*3600,60)
   degrees,minutes = divmod(minutes,60)
   degrees = degrees if is_positive else -degrees
   return (degrees,minutes,seconds)

if __name__ == '__main__':
    main()
