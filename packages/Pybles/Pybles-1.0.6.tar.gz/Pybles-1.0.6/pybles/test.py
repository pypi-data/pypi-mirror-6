import pybles

a = pybles.Pyble(header_color='STRONG_RED', header_background_color='BG_WHITE')

a.add_column('Nombre')
a.add_column('Apellido')
a.add_line(['Guido', 'Accardo'])
a.add_line(['Delfina', 'Baravalle'])
a.add_line(['Teo', 'Baravalle'])
a.add_line(['Liliana', 'Chiavassa'])
a.add_line(['A', 'B'])
a.add_line(['A', 'B'])
a.add_line(['A', 'B'])
a.add_line(['A', 'B'])
a.show_table()

a.set_color(True)

a.show_table()
