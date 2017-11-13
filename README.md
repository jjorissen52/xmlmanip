

```python
from xmlmanip import XMLSchema, SearchableList
```


```python
string = """
<breakfast_menu>
<food tag="waffles">
    <name>Belgian Waffles</name>
    <price>$5.95</price>
    <description>
   Two of our famous Belgian Waffles with plenty of real maple syrup
   </description>
    <calories>650</calories>
</food>
<food tag="waffles">
    <name >Strawberry Belgian Waffles</name>
    <price>$7.95</price>
    <description>
    Light Belgian waffles covered with strawberries and whipped cream
    </description>
    <calories>900</calories>
</food>
<food tag="waffles">
    <name>Berry-Berry Belgian Waffles</name>
    <price>$8.95</price>
    <description>
    Belgian waffles covered with assorted fresh berries and whipped cream
    </description>
    <calories>900</calories>
</food>
<food tag="toast">
    <name>French Toast</name>
    <price>$4.50</price>
    <description>
    Thick slices made from our homemade sourdough bread
    </description>
    <calories>600</calories>
</food>
<food tag="classic">
    <name>Homestyle Breakfast</name>
    <price>$6.95</price>
    <description>
    Two eggs, bacon or sausage, toast, and our ever-popular hash browns
    </description>
    <calories>950</calories>
</food>
</breakfast_menu>
"""
```

You can import your XML string to convert it to a dict. (dict conversion handled by https://github.com/martinblech/xmltodict).


```python
schema = XMLSchema(string)
schema
```




    XMLSchema([('breakfast_menu',
                OrderedDict([('food',
                              [OrderedDict([('@tag', 'waffles'),
                                            ('name', 'Belgian Waffles'),
                                            ('price', '$5.95'),
                                            ('description',
                                             'Two of our famous Belgian Waffles with plenty of real maple syrup'),
                                            ('calories', '650')]),
                               OrderedDict([('@tag', 'waffles'),
                                            ('name', 'Strawberry Belgian Waffles'),
                                            ('price', '$7.95'),
                                            ('description',
                                             'Light Belgian waffles covered with strawberries and whipped cream'),
                                            ('calories', '900')]),
                               OrderedDict([('@tag', 'waffles'),
                                            ('name',
                                             'Berry-Berry Belgian Waffles'),
                                            ('price', '$8.95'),
                                            ('description',
                                             'Belgian waffles covered with assorted fresh berries and whipped cream'),
                                            ('calories', '900')]),
                               OrderedDict([('@tag', 'toast'),
                                            ('name', 'French Toast'),
                                            ('price', '$4.50'),
                                            ('description',
                                             'Thick slices made from our homemade sourdough bread'),
                                            ('calories', '600')]),
                               OrderedDict([('@tag', 'classic'),
                                            ('name', 'Homestyle Breakfast'),
                                            ('price', '$6.95'),
                                            ('description',
                                             'Two eggs, bacon or sausage, toast, and our ever-popular hash browns'),
                                            ('calories', '950')])])]))])



Use .search() to search for data of interest.


```python
schema.search(name="Homestyle Breakfast")
```




    [SchemaInnerDict([('@tag', 'classic'),
                      ('name', 'Homestyle Breakfast'),
                      ('price', '$6.95'),
                      ('description',
                       'Two eggs, bacon or sausage, toast, and our ever-popular hash browns'),
                      ('calories', '950')])]



The `SearchAbleList` class will also allow you to easily search through lists of dicts.


```python
example_list = [{"thing": 1, "other_thing": 2}, {"thing": 2, "other_thing": 2}]
searchable_list = SearchableList(example_list)
print(searchable_list.search(thing__ne=2)) # thing != 2
print(searchable_list.search(other_thing=2))
```

    [{'thing': 1, 'other_thing': 2}]
    [{'thing': 1, 'other_thing': 2}, {'thing': 2, 'other_thing': 2}]


Use .locate() if you are interested in the "path" to your data of interest and .retrieve() to get an object from its "path."


```python
schema.locate(name="Homestyle Breakfast")
```




    ['__breakfast_menu__food__4__name']




```python
schema.retrieve('__breakfast_menu__food__4__name')
```




    'Homestyle Breakfast'




```python
schema.retrieve('__breakfast_menu__food__4')
```




    SchemaInnerDict([('@tag', 'classic'),
                     ('name', 'Homestyle Breakfast'),
                     ('price', '$6.95'),
                     ('description',
                      'Two eggs, bacon or sausage, toast, and our ever-popular hash browns'),
                     ('calories', '950')])



You have access to all of the standard comparison methods.


```python
paths = schema.locate(name__contains="Waffles")
paths
```




    ['__breakfast_menu__food__0__name',
     '__breakfast_menu__food__1__name',
     '__breakfast_menu__food__2__name']




```python
schema.search(name__contains="Waffles")
```




    [SchemaInnerDict([('@tag', 'waffles'),
                      ('name', 'Belgian Waffles'),
                      ('price', '$5.95'),
                      ('description',
                       'Two of our famous Belgian Waffles with plenty of real maple syrup'),
                      ('calories', '650')]),
     SchemaInnerDict([('@tag', 'waffles'),
                      ('name', 'Berry-Berry Belgian Waffles'),
                      ('price', '$8.95'),
                      ('description',
                       'Belgian waffles covered with assorted fresh berries and whipped cream'),
                      ('calories', '900')]),
     SchemaInnerDict([('@tag', 'waffles'),
                      ('name', 'Strawberry Belgian Waffles'),
                      ('price', '$7.95'),
                      ('description',
                       'Light Belgian waffles covered with strawberries and whipped cream'),
                      ('calories', '900')])]




```python
schema.search(calories__lt="700")
```




    [SchemaInnerDict([('@tag', 'toast'),
                      ('name', 'French Toast'),
                      ('price', '$4.50'),
                      ('description',
                       'Thick slices made from our homemade sourdough bread'),
                      ('calories', '600')]),
     SchemaInnerDict([('@tag', 'waffles'),
                      ('name', 'Belgian Waffles'),
                      ('price', '$5.95'),
                      ('description',
                       'Two of our famous Belgian Waffles with plenty of real maple syrup'),
                      ('calories', '650')])]



##### Warning, all types are compared as strings, which may have undesirable results. 


```python
schema.search(calories__lt="700") == schema.search(calories__lt="70") 
```




    True



Some attributes cannot be accessed via keyword arguements, unfortunately.


```python
schema.search(@tag__ne="waffles")
```


      File "<ipython-input-13-da95e3095c41>", line 1
        schema.search(@tag__ne="waffles")
                      ^
    SyntaxError: invalid syntax



You will need to pass the desired attribute and comparison method as strings in this case.


```python
schema.search('@tag', 'waffles') # default comparison is __eq__
```




    [SchemaInnerDict([('@tag', 'waffles'),
                      ('name', 'Belgian Waffles'),
                      ('price', '$5.95'),
                      ('description',
                       'Two of our famous Belgian Waffles with plenty of real maple syrup'),
                      ('calories', '650')]),
     SchemaInnerDict([('@tag', 'waffles'),
                      ('name', 'Strawberry Belgian Waffles'),
                      ('price', '$7.95'),
                      ('description',
                       'Light Belgian waffles covered with strawberries and whipped cream'),
                      ('calories', '900')]),
     SchemaInnerDict([('@tag', 'waffles'),
                      ('name', 'Berry-Berry Belgian Waffles'),
                      ('price', '$8.95'),
                      ('description',
                       'Belgian waffles covered with assorted fresh berries and whipped cream'),
                      ('calories', '900')])]




```python
schema.search('@tag', 'waffles', comparison='ne')
```




    [SchemaInnerDict([('@tag', 'classic'),
                      ('name', 'Homestyle Breakfast'),
                      ('price', '$6.95'),
                      ('description',
                       'Two eggs, bacon or sausage, toast, and our ever-popular hash browns'),
                      ('calories', '950')]),
     SchemaInnerDict([('@tag', 'toast'),
                      ('name', 'French Toast'),
                      ('price', '$4.50'),
                      ('description',
                       'Thick slices made from our homemade sourdough bread'),
                      ('calories', '600')])]




```python

```
