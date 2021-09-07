import requests
from bs4 import BeautifulSoup

def get_stock(page):
    page = requests.get(page)
    soup = BeautifulSoup(page.content, 'html.parser')
    name = soup.title.text.split('- IKEA')[0].strip()

    stockchecks = soup.find_all("div", class_="range-revamp-stockcheck__item")

    for stockcheck in stockchecks:
        indicator = stockcheck.find("span", class_="range-revamp-indicator")
        if indicator:
            if indicator.has_attr('class'):
                success = indicator['class'][-1].split('--')[-1] == 'success'
                break
    else:
        success = None 

    if success is None:
        print(f'{name} unknown stock')
    elif success:
        print(f'{name} got stock!')
    else:
        print(f'{name} no stock!')
    
    return name, success

if __name__ == '__main__':
    links = [
        'https://www.ikea.com/sg/en/p/stenared-dining-table-stone-effect-quartz-bamboo-60467887/',
        'https://www.ikea.com/sg/en/p/hemnes-coffee-table-white-stain-light-brown-10413496/',
        'https://www.ikea.com/sg/en/p/malm-chest-of-2-drawers-white-10354642/',
        'https://www.ikea.com/sg/en/p/kolbjoern-cabinet-in-outdoor-beige-50409299/',
        'https://www.ikea.com/sg/en/p/besta-tv-bench-with-doors-white-lappviken-white-s19299137/',
        'https://www.ikea.com/sg/en/p/havsen-sink-bowl-w-visible-front-white-s69253716/',
        ]

    for link in links:
        get_stock(page=link)