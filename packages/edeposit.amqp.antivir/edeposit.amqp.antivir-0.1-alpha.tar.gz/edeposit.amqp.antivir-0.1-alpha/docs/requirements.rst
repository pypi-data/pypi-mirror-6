Požadavky na modul a jeho omezení
----------------------------------------------------------------------------------------------------

Požadavky na funkci modulu
...................................................

Požadavky které jsou kladeny na funkci systému.

#. modul kontroluje, zda soubor obsahuje nějaké viry
#. modul umí soubor přijmout přímo ve zprávě jako stream
#. modul umí soubor přijmout jako cestu na souborovém systému
#. modul odesílá informaci o výsledku do nastavené exchange v RabbitMQ
#. modul je konfigurovatelný (viz :ref:`configuration`)
#. modul je šířen jako balíček na http://pypi.python.org (viz :ref:`installation`)
#. modul poskytuje metodu pro odeslání žádosti ke kontrole
#. modul poskytuje metodu pro převod dat z RabbitMQ do
   požadované výstupní struktury (viz. :ref:`usage`)

Omezení systému
............................

#. modul se připojuje k **RabbitMQ**
#. modul je napsaný v jazyce **Python**
