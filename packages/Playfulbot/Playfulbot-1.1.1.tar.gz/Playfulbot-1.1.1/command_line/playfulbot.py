#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# 2014 Alex Silva <alexsilvaf28 at gmail.com>

import httplib, urllib, urllib2, mechanize, argparse
from bs4 import BeautifulSoup
from colorama import Fore

def main():
	red_ini = Fore.RED
	red_end = Fore.RESET
	green_ini = Fore.GREEN
	green_end = Fore.RESET
	cyan_ini = Fore.CYAN
	cyan_end = Fore.RESET

	argument_parser = argparse.ArgumentParser(description="Autoapuestas en " +
	"Playfulbet")
	argument_parser.add_argument("-m", "--tasamin", help="Realizar apuestas " +
	"menores (cantidad de coins establecidas con [coins_min](200 por defecto)) " +
	" a tasas inferiores o iguales a 1.2. Esta opción solo se activa si se " +
	"apuesta 800 o más coins.", action="store_true")
	argument_parser.add_argument("user", help="Usuario de Playfulbet")
	argument_parser.add_argument("password", help="Contraseña de Playfulbet")
	argument_parser.add_argument("coins", nargs="?", default="200",
	help="Numero de monedas a apostar. Por defecto 200", type=int)
	argument_parser.add_argument("coins_min", nargs="?", default="200",
	help="Numero de monedas a apostar a las tasas inferiores a 1.2 " +
	"(incluidas). Por defecto 200", type=int)
	args = argument_parser.parse_args()

	tasa_min_arg = args.tasamin
	user_arg = args.user
	password_arg = args.password
	coins_arg = args.coins
	coins_min_arg = args.coins_min


	# Create Form
	form_data = {
		"user[login]": user_arg,
		"user[password]": password_arg
	}

	try:
		mbrowser = mechanize.Browser()
		mbrowser.set_handle_robots(False)
		mbrowser.set_handle_equiv(False)
		mbrowser.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; \
		Linux i686; es-ES; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
		mbrowser.open("http://playfulbet.com/")
		mbrowser.select_form(nr=0)
		for key in form_data:
			mbrowser.form[key] = form_data[key]
		mainpage_loggedin = mbrowser.submit()
		
		parser_mainpage = BeautifulSoup(mbrowser.follow_link(url_regex="/usuarios"))
		promo = parser_mainpage.findAll("a", {"href": "/promociones"})
		connected = len(promo) > 1

		if connected:
			try:
				# Obtener numero de coins
				coins = parser_mainpage.findAll("b", {"class": "active-coins"})
				played_coins = parser_mainpage.findAll("b", {"class": "played"})

				if len(coins) == 0 or len(played_coins) == 0:
					raise Exception(red_ini + ">> Conexion con servidor cancelada" + red_end)

				coins = coins[0].string
				played_coins = played_coins[0].string 

				print
				print "Tienes:"
				print green_ini + "- " + coins + " coins disponibles" + green_end
				print red_ini + "- " + played_coins + " coins jugadas" + red_end
				print
				
				coins = coins.replace(".", "")

				key_response = raw_input("Desea continuar la apuesta [s/n]: ")
				if key_response.lower() == "s" or key_response == "" or int(coins) < 200:
					pass
				else:
					raise KeyboardInterrupt

				bet_num = 0
				bet_max = 0
				bet_min = 0

				# Numero de apuestas
				if int(coins_arg > 800) and tasa_min_arg:
					bet_max = int(coins) // int(coins_arg)
					bet_min = (int(coins) - bet_max * int(coins_arg)) // int(coins_min_arg)
					bet_num = bet_max + bet_min

					print
					print cyan_ini + "Se realizarán", bet_max, "apuestas de " + \
					str(coins_arg) + " coins y", bet_min, "apuestas de " + \
					str(coins_min_arg) + " coins" + cyan_end
					print
				else:
					bet_num = int(coins) // int(coins_arg)


					print
					print cyan_ini + "Se realizarán", bet_num, "apuestas de " + str(coins_arg) + \
					" coins" + cyan_end
					print

				if bet_num > 0:
					print "Apuestas:"

				if bet_num > 0:
					mbrowser.follow_link(url_regex="/eventos")

				# Bucle de paginas
				page_num = 1
				while page_num < 7 and bet_num > 0:
					# Bucle de eventos
					link_url = ""
					links = []
					
					for link in mbrowser.links(text_regex="Juega"):
						links.append(link)

					i = 0
					errors = 0
					while i < len(links) and bet_num > 0:
						link = links[i]
						# Para que no se repitan obtener solo los eventos que no se han jugado
						if link.attrs[1][1] == "btn--action" and link_url != link.url and link.text != "Juega otra vez":
							link_url = link.url
							mbrowser.follow_link(link)
							parser_eventpage = BeautifulSoup(mbrowser.response().read())
							# Buscar el porcentaje
							options = parser_eventpage.findAll("label", {"data-match": "match-bet"})
							# Si la página está caida
							if len(options) < 1:
								errors += 1
							else:
								i += 1
								# Bucle de obtención del menor
								min = 100.0
								min_option = ""
								for option in options:
									value = float(option.string)
									if value < min:
										min = value
										min_option = option['for']
								# Rellenar formulario de apuesta
								mbrowser.select_form(nr=2)
								mbrowser.form["option_id"] = [min_option.split("_")[-1]]
								if coins_arg > 800 and min <= 1.2 and bet_min > 0 and tasa_min_arg:
									mbrowser.form["points"] = str(coins_min_arg)
									bet_done = mbrowser.submit()
									parser_eventpage = BeautifulSoup(bet_done.read())
									advice = parser_eventpage.findAll("div", {"id": "flash"})
									print "Tasa:", str(min), ", apuesta:", coins_min_arg, "-", str(advice[0]).split("\">")[1].split("</")[0]
									mbrowser.follow_link(text_regex="Jugar")
									# Se disminuye el contador de apuestas
									bet_min -= 1
									bet_num -= 1
								elif coins_arg > 800 and min > 1.2 and bet_max > 0 and tasa_min_arg:
									mbrowser.form["points"] = str(coins_arg)
									bet_done = mbrowser.submit()
									parser_eventpage = BeautifulSoup(bet_done.read())
									advice = parser_eventpage.findAll("div", {"id": "flash"})
									print "Tasa:", str(min), ", apuesta:", coins_arg, "-", str(advice[0]).split("\">")[1].split("</")[0]
									mbrowser.follow_link(text_regex="Jugar")
									# Se disminuye el contador de apuestas
									bet_max -= 1
									bet_num -= 1
								else:
									mbrowser.form["points"] = str(coins_arg)
									bet_done = mbrowser.submit()
									parser_eventpage = BeautifulSoup(bet_done.read())
									advice = parser_eventpage.findAll("div", {"id": "flash"})
									print "Tasa:", str(min), ", apuesta:", coins_arg, "-", str(advice[0]).split("\">")[1].split("</")[0]
									mbrowser.follow_link(text_regex="Jugar")
									# Se disminuye el contador de apuestas
									bet_num -= 1
							if errors == 5:
								i += 1
						else:
							i += 1
					# Siguiente página
					page_num += 1
					mbrowser.follow_link(url_regex="/eventos\?page=" + str(page_num))
			except KeyboardInterrupt, k:
				print red_ini + ">> Se ha cancelado la apuesta" + red_end
			except mechanize.URLError, e:
				print red_ini + ">> Conexion con servidor cancelada" + red_end
			except Exception, e:
				print e
		else:
			print red_ini + ">> Datos de login incorrectos" + red_end
	except mechanize.URLError, e:
		print red_ini + ">> Error de conexion" + red_end
	except KeyboardInterrupt, e:
		print red_ini + ">> Apuesta interrumpida por el usuario" + red_end



if __name__ == '__main__':
	main()
