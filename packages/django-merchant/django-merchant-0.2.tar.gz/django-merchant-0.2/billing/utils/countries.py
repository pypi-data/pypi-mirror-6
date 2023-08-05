# -*- coding: utf-8 -*-
# vim:tabstop=4:expandtab:sw=4:softtabstop=4
from django.utils.translation import ugettext_lazy as _

# List taken from http://www.iso.org/iso/english_country_names_and_code_elements
COUNTRY_CODE = {
    "AFGHANISTAN": "AF",
    "ÅLAND ISLANDS": "AX",
    "ALBANIA": "AL",
    "ALGERIA": "DZ",
    "AMERICAN SAMOA": "AS",
    "ANDORRA": "AD",
    "ANGOLA": "AO",
    "ANGUILLA": "AI",
    "ANTARCTICA": "AQ",
    "ANTIGUA AND BARBUDA": "AG",
    "ARGENTINA": "AR",
    "ARMENIA": "AM",
    "ARUBA": "AW",
    "AUSTRALIA": "AU",
    "AUSTRIA": "AT",
    "AZERBAIJAN": "AZ",
    "BAHAMAS": "BS",
    "BAHRAIN": "BH",
    "BANGLADESH": "BD",
    "BARBADOS": "BB",
    "BELARUS": "BY",
    "BELGIUM": "BE",
    "BELIZE": "BZ",
    "BENIN": "BJ",
    "BERMUDA": "BM",
    "BHUTAN": "BT",
    "BOLIVIA, PLURINATIONAL STATE OF": "BO",
    "BOSNIA AND HERZEGOVINA": "BA",
    "BOTSWANA": "BW",
    "BOUVET ISLAND": "BV",
    "BRAZIL": "BR",
    "BRITISH INDIAN OCEAN TERRITORY": "IO",
    "BRUNEI DARUSSALAM": "BN",
    "BULGARIA": "BG",
    "BURKINA FASO": "BF",
    "BURUNDI": "BI",
    "CAMBODIA": "KH",
    "CAMEROON": "CM",
    "CANADA": "CA",
    "CAPE VERDE": "CV",
    "CAYMAN ISLANDS": "KY",
    "CENTRAL AFRICAN REPUBLIC": "CF",
    "CHAD": "TD",
    "CHILE": "CL",
    "CHINA": "CN",
    "CHRISTMAS ISLAND": "CX",
    "COCOS (KEELING) ISLANDS": "CC",
    "COLOMBIA": "CO",
    "COMOROS": "KM",
    "CONGO": "CG",
    "CONGO, THE DEMOCRATIC REPUBLIC OF THE": "CD",
    "COOK ISLANDS": "CK",
    "COSTA RICA": "CR",
    "CÔTE D'IVOIRE": "CI",
    "CROATIA": "HR",
    "CUBA": "CU",
    "CYPRUS": "CY",
    "CZECH REPUBLIC": "CZ",
    "DENMARK": "DK",
    "DJIBOUTI": "DJ",
    "DOMINICA": "DM",
    "DOMINICAN REPUBLIC": "DO",
    "ECUADOR": "EC",
    "EGYPT": "EG",
    "EL SALVADOR": "SV",
    "EQUATORIAL GUINEA": "GQ",
    "ERITREA": "ER",
    "ESTONIA": "EE",
    "ETHIOPIA": "ET",
    "FALKLAND ISLANDS (MALVINAS)": "FK",
    "FAROE ISLANDS": "FO",
    "FIJI": "FJ",
    "FINLAND": "FI",
    "FRANCE": "FR",
    "FRENCH GUIANA": "GF",
    "FRENCH POLYNESIA": "PF",
    "FRENCH SOUTHERN TERRITORIES": "TF",
    "GABON": "GA",
    "GAMBIA": "GM",
    "GEORGIA": "GE",
    "GERMANY": "DE",
    "GHANA": "GH",
    "GIBRALTAR": "GI",
    "GREECE": "GR",
    "GREENLAND": "GL",
    "GRENADA": "GD",
    "GUADELOUPE": "GP",
    "GUAM": "GU",
    "GUATEMALA": "GT",
    "GUERNSEY": "GG",
    "GUINEA": "GN",
    "GUINEA-BISSAU": "GW",
    "GUYANA": "GY",
    "HAITI": "HT",
    "HEARD ISLAND AND MCDONALD ISLANDS": "HM",
    "HOLY SEE (VATICAN CITY STATE)": "VA",
    "HONDURAS": "HN",
    "HONG KONG": "HK",
    "HUNGARY": "HU",
    "ICELAND": "IS",
    "INDIA": "IN",
    "INDONESIA": "ID",
    "IRAN, ISLAMIC REPUBLIC OF": "IR",
    "IRAQ": "IQ",
    "IRELAND": "IE",
    "ISLE OF MAN": "IM",
    "ISRAEL": "IL",
    "ITALY": "IT",
    "JAMAICA": "JM",
    "JAPAN": "JP",
    "JERSEY": "JE",
    "JORDAN": "JO",
    "KAZAKHSTAN": "KZ",
    "KENYA": "KE",
    "KIRIBATI": "KI",
    "KOREA, DEMOCRATIC PEOPLE'S REPUBLIC OF": "KP",
    "KOREA, REPUBLIC OF": "KR",
    "KUWAIT": "KW",
    "KYRGYZSTAN": "KG",
    "LAO PEOPLE'S DEMOCRATIC REPUBLIC": "LA",
    "LATVIA": "LV",
    "LEBANON": "LB",
    "LESOTHO": "LS",
    "LIBERIA": "LR",
    "LIBYAN ARAB JAMAHIRIYA": "LY",
    "LIECHTENSTEIN": "LI",
    "LITHUANIA": "LT",
    "LUXEMBOURG": "LU",
    "MACAO": "MO",
    "MACEDONIA, THE FORMER YUGOSLAV REPUBLIC OF": "MK",
    "MADAGASCAR": "MG",
    "MALAWI": "MW",
    "MALAYSIA": "MY",
    "MALDIVES": "MV",
    "MALI": "ML",
    "MALTA": "MT",
    "MARSHALL ISLANDS": "MH",
    "MARTINIQUE": "MQ",
    "MAURITANIA": "MR",
    "MAURITIUS": "MU",
    "MAYOTTE": "YT",
    "MEXICO": "MX",
    "MICRONESIA, FEDERATED STATES OF": "FM",
    "MOLDOVA, REPUBLIC OF": "MD",
    "MONACO": "MC",
    "MONGOLIA": "MN",
    "MONTENEGRO": "ME",
    "MONTSERRAT": "MS",
    "MOROCCO": "MA",
    "MOZAMBIQUE": "MZ",
    "MYANMAR": "MM",
    "NAMIBIA": "NA",
    "NAURU": "NR",
    "NEPAL": "NP",
    "NETHERLANDS": "NL",
    "NETHERLANDS ANTILLES": "AN",
    "NEW CALEDONIA": "NC",
    "NEW ZEALAND": "NZ",
    "NICARAGUA": "NI",
    "NIGER": "NE",
    "NIGERIA": "NG",
    "NIUE": "NU",
    "NORFOLK ISLAND": "NF",
    "NORTHERN MARIANA ISLANDS": "MP",
    "NORWAY": "NO",
    "OMAN": "OM",
    "PAKISTAN": "PK",
    "PALAU": "PW",
    "PALESTINIAN TERRITORY, OCCUPIED": "PS",
    "PANAMA": "PA",
    "PAPUA NEW GUINEA": "PG",
    "PARAGUAY": "PY",
    "PERU": "PE",
    "PHILIPPINES": "PH",
    "PITCAIRN": "PN",
    "POLAND": "PL",
    "PORTUGAL": "PT",
    "PUERTO RICO": "PR",
    "QATAR": "QA",
    "RÉUNION": "RE",
    "ROMANIA": "RO",
    "RUSSIAN FEDERATION": "RU",
    "RWANDA": "RW",
    "SAINT BARTHÉLEMY": "BL",
    "SAINT HELENA, ASCENSION AND TRISTAN DA CUNHA": "SH",
    "SAINT KITTS AND NEVIS": "KN",
    "SAINT LUCIA": "LC",
    "SAINT MARTIN": "MF",
    "SAINT PIERRE AND MIQUELON": "PM",
    "SAINT VINCENT AND THE GRENADINES": "VC",
    "SAMOA": "WS",
    "SAN MARINO": "SM",
    "SAO TOME AND PRINCIPE": "ST",
    "SAUDI ARABIA": "SA",
    "SENEGAL": "SN",
    "SERBIA": "RS",
    "SEYCHELLES": "SC",
    "SIERRA LEONE": "SL",
    "SINGAPORE": "SG",
    "SLOVAKIA": "SK",
    "SLOVENIA": "SI",
    "SOLOMON ISLANDS": "SB",
    "SOMALIA": "SO",
    "SOUTH AFRICA": "ZA",
    "SOUTH GEORGIA AND THE SOUTH SANDWICH ISLANDS": "GS",
    "SPAIN": "ES",
    "SRI LANKA": "LK",
    "SUDAN": "SD",
    "SURINAME": "SR",
    "SVALBARD AND JAN MAYEN": "SJ",
    "SWAZILAND": "SZ",
    "SWEDEN": "SE",
    "SWITZERLAND": "CH",
    "SYRIAN ARAB REPUBLIC": "SY",
    "TAIWAN, PROVINCE OF CHINA": "TW",
    "TAJIKISTAN": "TJ",
    "TANZANIA, UNITED REPUBLIC OF": "TZ",
    "THAILAND": "TH",
    "TIMOR-LESTE": "TL",
    "TOGO": "TG",
    "TOKELAU": "TK",
    "TONGA": "TO",
    "TRINIDAD AND TOBAGO": "TT",
    "TUNISIA": "TN",
    "TURKEY": "TR",
    "TURKMENISTAN": "TM",
    "TURKS AND CAICOS ISLANDS": "TC",
    "TUVALU": "TV",
    "UGANDA": "UG",
    "UKRAINE": "UA",
    "UNITED ARAB EMIRATES": "AE",
    "UNITED KINGDOM": "GB",
    "UNITED STATES": "US",
    "UNITED STATES MINOR OUTLYING ISLANDS": "UM",
    "URUGUAY": "UY",
    "UZBEKISTAN": "UZ",
    "VANUATU": "VU",
    "VENEZUELA, BOLIVARIAN REPUBLIC OF": "VE",
    "VIET NAM": "VN",
    "VIRGIN ISLANDS, BRITISH": "VG",
    "VIRGIN ISLANDS, U.S": "VI",
    "WALLIS AND FUTUNA": "WF",
    "WESTERN SAHARA": "EH",
    "YEMEN": "YE",
    "ZAMBIA": "ZM",
    "ZIMBABWE": "ZW",
}

#List taken from https://bitbucket.org/smileychris/django-countries/
# Nicely titled (and translatable) country names.
COUNTRIES = (
    ('AF', _(u'Afghanistan')),
    ('AX', _(u'\xc5land Islands')),
    ('AL', _(u'Albania')),
    ('DZ', _(u'Algeria')),
    ('AS', _(u'American Samoa')),
    ('AD', _(u'Andorra')),
    ('AO', _(u'Angola')),
    ('AI', _(u'Anguilla')),
    ('AQ', _(u'Antarctica')),
    ('AG', _(u'Antigua and Barbuda')),
    ('AR', _(u'Argentina')),
    ('AM', _(u'Armenia')),
    ('AW', _(u'Aruba')),
    ('AU', _(u'Australia')),
    ('AT', _(u'Austria')),
    ('AZ', _(u'Azerbaijan')),
    ('BS', _(u'Bahamas')),
    ('BH', _(u'Bahrain')),
    ('BD', _(u'Bangladesh')),
    ('BB', _(u'Barbados')),
    ('BY', _(u'Belarus')),
    ('BE', _(u'Belgium')),
    ('BZ', _(u'Belize')),
    ('BJ', _(u'Benin')),
    ('BM', _(u'Bermuda')),
    ('BT', _(u'Bhutan')),
    ('BO', _(u'Bolivia, Plurinational State of')),
    ('BQ', _(u'Bonaire, Sint Eustatius and Saba')),
    ('BA', _(u'Bosnia and Herzegovina')),
    ('BW', _(u'Botswana')),
    ('BV', _(u'Bouvet Island')),
    ('BR', _(u'Brazil')),
    ('IO', _(u'British Indian Ocean Territory')),
    ('BN', _(u'Brunei Darussalam')),
    ('BG', _(u'Bulgaria')),
    ('BF', _(u'Burkina Faso')),
    ('BI', _(u'Burundi')),
    ('KH', _(u'Cambodia')),
    ('CM', _(u'Cameroon')),
    ('CA', _(u'Canada')),
    ('CV', _(u'Cape Verde')),
    ('KY', _(u'Cayman Islands')),
    ('CF', _(u'Central African Republic')),
    ('TD', _(u'Chad')),
    ('CL', _(u'Chile')),
    ('CN', _(u'China')),
    ('CX', _(u'Christmas Island')),
    ('CC', _(u'Cocos (Keeling) Islands')),
    ('CO', _(u'Colombia')),
    ('KM', _(u'Comoros')),
    ('CG', _(u'Congo')),
    ('CD', _(u'Congo, The Democratic Republic of the')),
    ('CK', _(u'Cook Islands')),
    ('CR', _(u'Costa Rica')),
    ('CI', _(u"C\xf4te D'ivoire")),
    ('HR', _(u'Croatia')),
    ('CU', _(u'Cuba')),
    ('CW', _(u'Cura\xe7ao')),
    ('CY', _(u'Cyprus')),
    ('CZ', _(u'Czech Republic')),
    ('DK', _(u'Denmark')),
    ('DJ', _(u'Djibouti')),
    ('DM', _(u'Dominica')),
    ('DO', _(u'Dominican Republic')),
    ('EC', _(u'Ecuador')),
    ('EG', _(u'Egypt')),
    ('SV', _(u'El Salvador')),
    ('GQ', _(u'Equatorial Guinea')),
    ('ER', _(u'Eritrea')),
    ('EE', _(u'Estonia')),
    ('ET', _(u'Ethiopia')),
    ('FK', _(u'Falkland Islands (Malvinas)')),
    ('FO', _(u'Faroe Islands')),
    ('FJ', _(u'Fiji')),
    ('FI', _(u'Finland')),
    ('FR', _(u'France')),
    ('GF', _(u'French Guiana')),
    ('PF', _(u'French Polynesia')),
    ('TF', _(u'French Southern Territories')),
    ('GA', _(u'Gabon')),
    ('GM', _(u'Gambia')),
    ('GE', _(u'Georgia')),
    ('DE', _(u'Germany')),
    ('GH', _(u'Ghana')),
    ('GI', _(u'Gibraltar')),
    ('GR', _(u'Greece')),
    ('GL', _(u'Greenland')),
    ('GD', _(u'Grenada')),
    ('GP', _(u'Guadeloupe')),
    ('GU', _(u'Guam')),
    ('GT', _(u'Guatemala')),
    ('GG', _(u'Guernsey')),
    ('GN', _(u'Guinea')),
    ('GW', _(u'Guinea-bissau')),
    ('GY', _(u'Guyana')),
    ('HT', _(u'Haiti')),
    ('HM', _(u'Heard Island and McDonald Islands')),
    ('VA', _(u'Holy See (Vatican City State)')),
    ('HN', _(u'Honduras')),
    ('HK', _(u'Hong Kong')),
    ('HU', _(u'Hungary')),
    ('IS', _(u'Iceland')),
    ('IN', _(u'India')),
    ('ID', _(u'Indonesia')),
    ('IR', _(u'Iran, Islamic Republic of')),
    ('IQ', _(u'Iraq')),
    ('IE', _(u'Ireland')),
    ('IM', _(u'Isle of Man')),
    ('IL', _(u'Israel')),
    ('IT', _(u'Italy')),
    ('JM', _(u'Jamaica')),
    ('JP', _(u'Japan')),
    ('JE', _(u'Jersey')),
    ('JO', _(u'Jordan')),
    ('KZ', _(u'Kazakhstan')),
    ('KE', _(u'Kenya')),
    ('KI', _(u'Kiribati')),
    ('KP', _(u"Korea, Democratic People's Republic of")),
    ('KR', _(u'Korea, Republic of')),
    ('KW', _(u'Kuwait')),
    ('KG', _(u'Kyrgyzstan')),
    ('LA', _(u"Lao People's Democratic Republic")),
    ('LV', _(u'Latvia')),
    ('LB', _(u'Lebanon')),
    ('LS', _(u'Lesotho')),
    ('LR', _(u'Liberia')),
    ('LY', _(u'Libyan Arab Jamahiriya')),
    ('LI', _(u'Liechtenstein')),
    ('LT', _(u'Lithuania')),
    ('LU', _(u'Luxembourg')),
    ('MO', _(u'Macao')),
    ('MK', _(u'Macedonia, The Former Yugoslav Republic of')),
    ('MG', _(u'Madagascar')),
    ('MW', _(u'Malawi')),
    ('MY', _(u'Malaysia')),
    ('MV', _(u'Maldives')),
    ('ML', _(u'Mali')),
    ('MT', _(u'Malta')),
    ('MH', _(u'Marshall Islands')),
    ('MQ', _(u'Martinique')),
    ('MR', _(u'Mauritania')),
    ('MU', _(u'Mauritius')),
    ('YT', _(u'Mayotte')),
    ('MX', _(u'Mexico')),
    ('FM', _(u'Micronesia, Federated States of')),
    ('MD', _(u'Moldova, Republic of')),
    ('MC', _(u'Monaco')),
    ('MN', _(u'Mongolia')),
    ('ME', _(u'Montenegro')),
    ('MS', _(u'Montserrat')),
    ('MA', _(u'Morocco')),
    ('MZ', _(u'Mozambique')),
    ('MM', _(u'Myanmar')),
    ('NA', _(u'Namibia')),
    ('NR', _(u'Nauru')),
    ('NP', _(u'Nepal')),
    ('NL', _(u'Netherlands')),
    ('NC', _(u'New Caledonia')),
    ('NZ', _(u'New Zealand')),
    ('NI', _(u'Nicaragua')),
    ('NE', _(u'Niger')),
    ('NG', _(u'Nigeria')),
    ('NU', _(u'Niue')),
    ('NF', _(u'Norfolk Island')),
    ('MP', _(u'Northern Mariana Islands')),
    ('NO', _(u'Norway')),
    ('OM', _(u'Oman')),
    ('PK', _(u'Pakistan')),
    ('PW', _(u'Palau')),
    ('PS', _(u'Palestinian Territory, Occupied')),
    ('PA', _(u'Panama')),
    ('PG', _(u'Papua New Guinea')),
    ('PY', _(u'Paraguay')),
    ('PE', _(u'Peru')),
    ('PH', _(u'Philippines')),
    ('PN', _(u'Pitcairn')),
    ('PL', _(u'Poland')),
    ('PT', _(u'Portugal')),
    ('PR', _(u'Puerto Rico')),
    ('QA', _(u'Qatar')),
    ('RE', _(u'R\xe9union')),
    ('RO', _(u'Romania')),
    ('RU', _(u'Russian Federation')),
    ('RW', _(u'Rwanda')),
    ('BL', _(u'Saint Barth\xe9lemy')),
    ('SH', _(u'Saint Helena, Ascension and Tristan Da Cunha')),
    ('KN', _(u'Saint Kitts and Nevis')),
    ('LC', _(u'Saint Lucia')),
    ('MF', _(u'Saint Martin (French Part)')),
    ('PM', _(u'Saint Pierre and Miquelon')),
    ('VC', _(u'Saint Vincent and the Grenadines')),
    ('WS', _(u'Samoa')),
    ('SM', _(u'San Marino')),
    ('ST', _(u'Sao Tome and Principe')),
    ('SA', _(u'Saudi Arabia')),
    ('SN', _(u'Senegal')),
    ('RS', _(u'Serbia')),
    ('SC', _(u'Seychelles')),
    ('SL', _(u'Sierra Leone')),
    ('SG', _(u'Singapore')),
    ('SX', _(u'Sint Maarten (Dutch Part)')),
    ('SK', _(u'Slovakia')),
    ('SI', _(u'Slovenia')),
    ('SB', _(u'Solomon Islands')),
    ('SO', _(u'Somalia')),
    ('ZA', _(u'South Africa')),
    ('GS', _(u'South Georgia and the South Sandwich Islands')),
    ('SS', _(u'South Sudan')),
    ('ES', _(u'Spain')),
    ('LK', _(u'Sri Lanka')),
    ('SD', _(u'Sudan')),
    ('SR', _(u'Suriname')),
    ('SJ', _(u'Svalbard and Jan Mayen')),
    ('SZ', _(u'Swaziland')),
    ('SE', _(u'Sweden')),
    ('CH', _(u'Switzerland')),
    ('SY', _(u'Syrian Arab Republic')),
    ('TW', _(u'Taiwan, Province of China')),
    ('TJ', _(u'Tajikistan')),
    ('TZ', _(u'Tanzania, United Republic of')),
    ('TH', _(u'Thailand')),
    ('TL', _(u'Timor-leste')),
    ('TG', _(u'Togo')),
    ('TK', _(u'Tokelau')),
    ('TO', _(u'Tonga')),
    ('TT', _(u'Trinidad and Tobago')),
    ('TN', _(u'Tunisia')),
    ('TR', _(u'Turkey')),
    ('TM', _(u'Turkmenistan')),
    ('TC', _(u'Turks and Caicos Islands')),
    ('TV', _(u'Tuvalu')),
    ('UG', _(u'Uganda')),
    ('UA', _(u'Ukraine')),
    ('AE', _(u'United Arab Emirates')),
    ('GB', _(u'United Kingdom')),
    ('US', _(u'United States')),
    ('UM', _(u'United States Minor Outlying Islands')),
    ('UY', _(u'Uruguay')),
    ('UZ', _(u'Uzbekistan')),
    ('VU', _(u'Vanuatu')),
    ('VE', _(u'Venezuela, Bolivarian Republic of')),
    ('VN', _(u'Viet Nam')),
    ('VG', _(u'Virgin Islands, British')),
    ('VI', _(u'Virgin Islands, U.S.')),
    ('WF', _(u'Wallis and Futuna')),
    ('EH', _(u'Western Sahara')),
    ('YE', _(u'Yemen')),
    ('ZM', _(u'Zambia')),
    ('ZW', _(u'Zimbabwe')),
)