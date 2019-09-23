# coding=utf-8

import urllib.request, urllib.parse, urllib.error, os, configparser

def createConfig(path): #Создание стандартного конфиг файла

    config = configparser.ConfigParser()
    config.add_section("Settings")
    config.set("Settings", "acestreamserveradressport", "127.0.0.1:6878") #Адрес:Порт AceStream сервера
    config.set("Settings", "aceproxyserveradressport", "192.168.0.199:8000") #Адрес:Порт proxy сервера от Pepsik
    config.set("Settings", "outputfolder", "") #Адрес папки где будут создаваться плейлисты (если отсутствует то создастся)
    config.set("Settings", "createplaylistall", "0") #Создание плейлиста со всеми найдеными каналами (1 или 0)
    config.set("Settings", "playlistallfilename", "All.m3u") #Название файла плейлиста со всеми найдеными каналами
    config.set("Settings", "createfavorite", "1") #Создание плейлиста с избранными каналами
    config.set("Settings", "playlistfavoritefilename", "Favorite.m3u") #Название файла плейлиста с избранными каналами
    config.set("Settings", "createfavoriteproxy", "0") #Создание плейлиста с избранными каналами с использованием proxy сервера от Pepsik
    config.set("Settings", "playlistfavoriteproxyfilename", "Favorite_proxy.m3u") #Название файла плейлиста с избранными каналами с использованием proxy сервера от Pepsik
    config.set("Settings", "favoritechannels", "Discovery,Eurosport,Моя Планета") #Ключевые слова для подбора каналов в плейлист избранного (регистр имеет значение)
    
    with open(path, "w", encoding='utf-8') as config_file:
        config.write(config_file)

#####Работа с конфиг файлом#####

if not os.path.exists('settings.ini'):
        createConfig('settings.ini')

config = configparser.ConfigParser()
config.read('settings.ini', encoding='utf-8')
acestreamserveradressport = config.get("Settings", "acestreamserveradressport")
aceproxyserveradressport = config.get("Settings", "aceproxyserveradressport")
outputfolder = config.get("Settings", "outputfolder")
createplaylistall = config.get("Settings", "createplaylistall")
playlistallfilename = config.get("Settings", "playlistallfilename")
createfavorite = config.get("Settings", "createfavorite")
playlistfavoritefilename = config.get("Settings", "playlistfavoritefilename")
createfavoriteproxy = config.get("Settings", "createfavoriteproxy")
playlistfavoriteproxyfilename = config.get("Settings", "playlistfavoriteproxyfilename")
favoritechannales = config.get("Settings", "favoritechannels")
favoritechannales_split = favoritechannales.split(',')

################################

if outputfolder != '':
    if not os.path.exists(outputfolder):
        os.makedirs(outputfolder) #Проверка наличия и создание папки для плейлистов


#####Парсинг JSON-файла#########

url_ace_json = 'https://search.acestream.net/all?api_version=1.0&api_key=test_api_key'
ace_json = urllib.request.urlopen(url_ace_json).read().decode('unicode-escape', errors='ignore') #Долбаный юникод...
ace_json_str = str(ace_json)
ace_json_str_split = ace_json_str.split('},{')

k = 0 #Счетчик
name = [] #Список названий каналов
cat = [] #Список названий категорий каналов
infohash = [] #Список инфохешей каналов
number_of_favorite_channels = [] #Список порядковых номеров каналов отобраных в избранное 

for string in ace_json_str_split:
    name.append(string[string.find('"name":"'):string.find('","availability"')])
    name[k] = name[k][8:]
    cat.append(string[string.find('"categories":["'):string.find('","infohash"')])
    cat[k] = cat[k][15:]
    infohash.append(string[string.find('"infohash":"'):string.find('","name"')])
    infohash[k] = infohash[k][12:]
    if createfavorite == '1' or createfavoriteproxy == '1':
        for channel in favoritechannales_split:
            if name[k].find(channel) != -1:
                number_of_favorite_channels.append(k)
    k = k + 1                                                              

################################

#####Создание плейлистов########

if createplaylistall == '1':
    output = open(outputfolder + playlistallfilename, 'w', encoding='utf-8')
    output.write('#EXTM3U\n')
if createfavorite == '1':
    output_favorite = open(outputfolder + playlistfavoritefilename, 'w', encoding='utf-8')
    output_favorite.write('#EXT3U\n')

n = 0

while n != k:
    if createplaylistall == '1':
        output.write('#EXTINF:-1 group-title="' + cat[n] + ',' + name[n] + '\n' + 'http://' + acestreamserveradressport + '/ace/getstream?infohash=' + infohash[n] + '\n')
    if createfavorite == '1':
        for i in number_of_favorite_channels:
            if n == i:
                output_favorite.write('#EXTINF:-1 group-title="' + cat[n] + ',' + name[n] + '\n' + 'http://' + acestreamserveradressport + '/ace/getstream?infohash=' + infohash[n] + '\n')
            

    n = n + 1

#####Отдельно создание прокси плейлиста#####

if createfavoriteproxy == '1':
    content_id = []
    k = 0
    for n in number_of_favorite_channels:
        content_id_gen_url = 'http://' + acestreamserveradressport + '/server/api/?method=get_content_id&infohash=' + infohash[n]
        content_id.append(str(urllib.request.urlopen(content_id_gen_url).read())[29:])
        content_id[k] = content_id[k][:40]
        print(content_id[k])
        k = k + 1
        
    outputproxy = open(outputfolder + playlistfavoriteproxyfilename, 'w', encoding='utf-8')
    outputproxy.write('#EXTM3U\n')
    n = 0
    for id in content_id:
        outputproxy.write('#EXTINF:-1 group-title="' + cat[number_of_favorite_channels[n]] + ',' + name[number_of_favorite_channels[n]] + '\n' + 'http://' + aceproxyserveradressport + '/pid/' + str(id) + '/stream.mp4' + '\n')
        n = n + 1
    outputproxy.close()
	
############################################
	
if createplaylistall == '1':
    output.close()
if createfavorite == '1':
    output_favorite.close()
