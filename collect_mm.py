"""
Collecting russian mass media in file mass_media.txt
"""
import bs4
import requests
st = requests.get(
    'https://infoselection.ru/infokatalog/novosti-smi/smi/item/249-20-samykh-poseshchaemykh-novostnykh-resursov-runeta')

soup = bs4.BeautifulSoup(st.content, 'html.parser')
res = soup.find_all('tbody')
li = []
s = 0
while s < 3:
    dd = res[s].find_all('a')
    for i in dd:
        li.append(i['href'])
    s += 1
li = set(li)
li = list(li)
li.sort()
print(len(li), li)
with open('mass_media.txt', 'w') as file:
    for step in li:
        file.write(step + '*\n')
