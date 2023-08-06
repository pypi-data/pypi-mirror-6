# -*- coding: utf-8 -*-
# :Progetto:  metapensiero.sqlalchemy.proxy -- nssjson glue
# :Creato:    gio 04 dic 2008 13:56:51 CET
# :Autore:    Lele Gaifax <lele@nautilus.homeip.net>
# :Licenza:   GNU General Public License version 3 or later
#

import decimal
from nssjson import JSONDecoder, JSONEncoder


JSONDateFormat = 'Y-m-d'
JSONTimeFormat = 'H:i:s'
JSONTimestampFormat = 'Y-m-d\\TH:i:s'


py2json = JSONEncoder(separators=(',', ':'),
                      use_decimal=True,
                      iso_datetime=True).encode

json2py = JSONDecoder(parse_float=decimal.Decimal,
                      iso_datetime=True).decode
