codes = {"bold": "\x02",
         "color": "\x03",
         "italic": "\x09",
         "strikethrough": "\x13",
         "reset": "\x0f",
         "underline": "\x15",
         "underline2": "\x1f",
         "reverse": "\x16"}

colors = {"white": "0",
          "black": "1",
          "dark_blue": "2",
          "green": "3",
          "red": "4",
          "dark_red": "5",
          "dark_violet": "6",
          "orange": "7",
          "yellow": "8",
          "light_green": "9",
          "cyan": "10",
          "light_cyan": "11",
          "blue": "12",
          "violet": "13",
          "dark_grey": "14",
          "light_grey": "15"}

def style(text, style):
	return codes[style]+text+codes[style]

def color(text, fgcolor, bgcolor=None):
	if fgcolor in colors and bgcolor in colors:
		colorstring = colors[fgcolor]+","+colors[bgcolor]
		return codes['color']+colorstring+text+codes['color']
	else:
		return codes['color']+colors[fgcolor]+text+codes['color']
