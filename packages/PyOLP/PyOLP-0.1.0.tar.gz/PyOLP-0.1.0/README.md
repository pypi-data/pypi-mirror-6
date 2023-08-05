PyOLP
=====

Python library implementing the Oregon Liquor Prices V1 API

## Examples

```python
>>> from PyOLP import PyOLP
>>> p = PyOLP()

# Get all the products that are 90 proof and are on sale
>>> for product in p.get_products(proof=90.0, on_sale=True):
...     print('{} ${}'.format(product.title, product.get_price().amount))
Bulleit 95 Rye $29.95
Bulleit Bourbon Frontier $29.95
C.m. Parrot Bay Coconut 90 $17.95
George Dickel #12 $19.95
Korbel Gold Reserve Vsop $16.95
Metaxa Ouzo $16.45

product = p.get_product('171')
>>> product.id
u'171'
>>> product.title
u'Canadian Rich & Rare'
>>> product.on_sale
False
>>> product.bottles_per_case
24

>>> store = p.get_store('243')
>>> store.id
u'243'
>>> store.name
u'Willamina Liquor'
>>> store.address
u'212 NE Main St, Willamina, OR 97396, USA'
>>>store.hours_raw
u'9-6 M-S; Closed Sunday'
```
## Credit

Special thanks to all the fantastic developers who worked on 
https://github.com/jacquev6/PyGithub. This library used many
idea from that that project including the overall architecture 
and parts of the code.
