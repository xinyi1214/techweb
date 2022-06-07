 #!/bin/env python

'''
Auteur : Xinyi Shen (copyright)
Date : 26 avril 2021

La commande pour lancer le script : streamlit run app.py
Utilisation:
C'est une application streamlit. Il y a deux partie: la première partie est une recherche d'hôtels par les pays.
La deuxième partie est un exemple pour un dictionnaire des langues peu dotées.
'''

import requests
from bs4 import BeautifulSoup
import re
import streamlit as st
from unidecode import unidecode
import pandas as pd
import matplotlib.pyplot as plt
from selenium import webdriver
import time

#La preimère partie

#pré-requis: un pays
#résultat : une partie d'urls de toutes les hôtels de ce pays

def getHotelName(country):
	countryName = country.lower()
	countryName = unidecode(countryName) #normalise les noms de pays
	url = "https://www.nh-hotels.fr/hotels/" + countryName #crée l'url pour accéder la page
	header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',} #passing header info in request
	response = requests.get(url, headers = header) #récupere les infos de l'url
	soup = BeautifulSoup(response.content, 'html.parser') #parse la page html
	hotels = [] 

	#le boucle pour trouver tous les urls de chaque hôtel de ce pays dans la page html
	for eachHotel in soup.find_all("div", class_="block-body"):
		for all_a in eachHotel.find_all("a"): 
			hotelUrl = all_a.get("href") 
			hotels.append(hotelUrl)

	return hotels

#résultat: Les informations utilis des hôtels que le client cherche

def getData():
	info = [] #initialisation d'une liste de dictionnaire pour stocker tous les information de l'hôtels de ce pays
	hotels = getHotelName(country)

	#Pour tous les hôtels dans la liste hotels, on récupére les informations (nom hôtel, eco-friendly ?, étoiles et l'url) puis on stock dans la liste info
	for hotel in hotels:
		url = "https://www.nh-hotels.fr"+hotel
		header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',} #passing header info in request
		response = requests.get(url, headers = header)
		soup = BeautifulSoup(response.content, 'html.parser')		
		#scraping the info
	
   		#hotel name
		title = soup.find('title').contents[0].split("|")[0] #prend le premier élément "title" et récupere le nom de l'hôtel et le pays
		hotel= title

		#eco-friendly ?
		#cherche la présence de l'image eco-friendly dans l'élement "color-primary"
		color_primary = soup.find(id = "services") 

		if color_primary.select_one('img[alt="Eco-friendly"]'):
			ecofriendly = "Oui"
		else:
			ecofriendly =  "Non"

		#étoiles
		#cherche la classe "stars" et compte les étoiles
		stars = soup.find(class_='stars')
		star = len(stars.select('span'))
					
		#url
		plusinfo = url

		#crée un dictionnaire de tous les informations de l'hôtel et ajoute ce dictionnaire à la liste info
		info.append({"Hôtel": hotel, "Eco-friendly": ecofriendly, "Étoiles" : star, "Plus d'informations" : plusinfo})
		#fin boucle

	info = pd.DataFrame(info) #prépare l'affchiage des informations sous la forme graphique avec pandas

	leninfo = len(info) #compte les hôtels dans ce pays
	eco_stars = info[(info[u"Eco-friendly"] == "Oui") &(info[u"Étoiles"] > 3)] #trouve les hôtels qui sont à la fois eco-friendly et plus de trois étoiles
	avec = len(eco_stars) #compte les hôtels eco-friendly et plus de 3 étoiles
	sans = leninfo - avec #compte les hôtels qui sont pas eco-friendly ou moin de 3 étoiles

	return avec, sans, info

#La deuxième partie

#pré-requis: un mot en yemba
#résultat : les informations de ce mot et ses traductions en français

def find_item(word):
	#id_mots : enregistre tous les mots qui vont être extraité comme les valeurs et tous les id des mots sur le page html
	id_mots = {"ad964222-efbb-48a5-bb23-ae9fd606ecdb" : "a","796760e0-1557-4ad0-8daa-139c3c4391f7":"á", "6c97a20b-f271-4f8e-912e-3bfe2db1a494" : "alá pū", "93ecdcd3-c570-4891-94ac-e4c7d449a7bc" : "alēm"}
	#option : afin de scraper le site sans ouvrir le navigateur
	option = webdriver.ChromeOptions() 
	option.add_argument("headless")
	#commence à scraper le site
	driver = webdriver.Chrome(chrome_options=option)
	driver.get("https://ntealan.net")

	time.sleep(2) #wait the page to load

	#close the little window
	try:
		windows = driver.find_element_by_class_name("modal-bottom")
		windows_button = windows.find_element_by_tag_name("button")
		windows_button.click() 
	except:
		pass

	#find the items
	time.sleep(3) #wait the page to load
	#parcourir les éléments dans la page html avec plusieurs méthodes différents afin de trouver les informations pertinnat
	flex_container = driver.find_element_by_class_name("flex-container")
	bar = flex_container.find_element_by_tag_name("app-bar-left")
	barleft = bar.find_element_by_class_name("barLeft")
	listeUL = barleft.find_element_by_xpath("div/div/div/ul")

	for key, value in id_mots.items():
		if word == value: #si le mot cherché par le client est identique que celui dans le dictionnaire
			item = listeUL.find_element_by_id(key) #on recherche le même id dans la page html
			item.click() #entre dans la page d'article
			time.sleep(3) #attend la page active
			main = driver.find_element_by_class_name("main")
			app_central = main.find_element_by_xpath("div/div/div/app-central")
			contenu = app_central.find_element_by_class_name("contenu")
			div= contenu.find_element_by_xpath("div[1]/div[1]/div[1]")
			article = div.find_element_by_class_name("article")
			entry = article.find_element_by_xpath("div[1]")

			#variant
			variant = entry.find_element_by_class_name("variant")
			radical = variant.find_element_by_class_name("radical").text
			forme = variant.find_element_by_class_name("forme").text
			type_ = variant.find_element_by_class_name("type").text

			#category
			category = article.find_element_by_class_name("category")
			cat_part = category.find_element_by_class_name("cat_part").text

			#translation
			translation = article.find_element_by_class_name("translation")
			group_equiv = translation.find_element_by_class_name("group_equiv")
			number = group_equiv.find_element_by_class_name("number").text		
			equivalent = translation.find_elements_by_class_name("equivalent")
			traduction = [] #initialise une liste afin d'ajouter toutes les traductions
			for item in equivalent:			
				traduction.append(item.text)
			lang = translation.find_element_by_class_name("lang").text
			
			#crée un dictionnaire et ajoute tous les informations dedans
			dic = {"radical": radical, "forme":forme, "type":type_, "pos":cat_part, "traduction en français":traduction }
	driver.close()
	return dic	

#Création de l'app

st.markdown("""
	<style>
	body{
	background:#F8FEFE
	}
	</style>
	""", unsafe_allow_html=True) #change la couleur du backgroud 

#crée un sidebar pour faire une petite présentation de cette application et ajoute un choix entre deux pages
st.sidebar.header("À propos")
st.sidebar.write("Cette application vous propose deux options.")
st.sidebar.write("La première, les hôtels Eco-friendly de l'Hotel Group.")
st.sidebar.write("La deuxième, un dictionaire des langues peu-dotées.")
st.sidebar.write("")
status = st.sidebar.radio("Quelle page voulez-vous voir ?", ("Hôtels Eco-friendly", "Dictionaire des langues peu-dotées"))
st.sidebar.write("")
st.sidebar.subheader("Auteur:")
st.sidebar.write("Xinyi Shen")

#commence à créer la première page
if status =="Hôtels Eco-friendly":
	st.title("Hôtels Eco-friendly")
	st.subheader("Dans cette page, nous proposons les hôtels Eco-friendly de l'Hotel Group pour faciliter votre voyage.")
	st.text("")
	st.info("Vous pouvez chosir le pays dans lequel vous voulez voyager, nous rechercherons pour vous les informations pertinentes puis nous vous affichons dans un graphique les hôtels Eco-friendly et les hôtels non Eco-friendly.")
	st.text("")
	#ajoute le module de recherche
	country = st.text_input("Pays dans lequel vous voulez voyager (en français)")
	if country != '':
		try:
			avec, sans, info = getData()
			st.subheader("Tous les hôtels dans ce pays:")
			st.table(info) #insére le tableau qu'on a crée par pandas
			st.text("")
			plt.bar(["Hôtels non Eco-friendly", "Hôtels Eco-friendly"], [sans, avec])
			st.subheader("Nous comparons les hôtels qui ont plus de 3 étoiles:")
			st.set_option('deprecation.showPyplotGlobalUse', False)
			st.pyplot() #ajoute la graphique

		except:
			st.error("Désolé, l'Hotel Group ne propose pas d'hôtels dans ce pays. ")

#commence à créer la deuxième page
else:
	if status == "Dictionaire des langues peu-dotées":
		st.title("Dictionaire des langues peu-dotées")
		st.text("")
		st.info('En 2007, le cabinet de recherche Computer Industry Almanac1 estimait le nombre d’ordinateurs personnels en circulation dans le monde a un milliard de machines, soit un ordinateur pour 6,6 personnes en moyenne. Ce chiffre est accompagné de tendances qui montrent que la progression de l’informatisation des foyers diminue légèrement dans les pays dits développés, et augmente très fortement depuis quelques années dans les pays en voie de développement, nouveaux moteurs de la croissance de ce march´e. Dès lors, le développement rapide de technologies de traitement numérique du langage, dans les langues de ces pays, est un enjeu essentiel. (Thomas Pellegrini. Transcription automatique de langues peu dotées. Informatique [cs]. Université Paris Sud - Paris XI, 2008. Français. fftel-00619657f)')

		st.write("Dans ce cas, nous introduisons un dictionaire en ligne qui présente les langues peu-dotées, par exemple, yemba, swahili, yangben, etc.")
		st.text("")
		st.write("Pour vous montrer ce dictionaire, nous extrayons quelques exemples en yemba.")
		st.text("")
		#crée un choix pour représente les articles qui sont extrait
		word = st.selectbox("Vous voulez chosir quel mot yemba ?",("a", "á", "alá pū", "alēm"))
		if word != '':
			try:
				dic = find_item(word)
				for key, value in dic.items():
					st.info(
						'''
						{} : {}
	 					'''.format(key, value)
	 					) #affiche le dictionnare
			except:
				st.error("Erreur de connexion. L'accès au siteweb du dictionaire étant difficile, il est normal de devoir reessayer plusieurs fois pour avoir un résultat. Merci de reessayer.")
		st.write("")
		st.text("Pour plus d'informations:" )
		st.markdown(
    """<a href="https://ntealan.net">https://ntealan.net</a>""", unsafe_allow_html=True,
) #affiche l'url du site original