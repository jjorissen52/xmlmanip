

```python
from xmlmanip import XMLSchema
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
```


```python
print(schema)
```

    {
      "breakfast_menu": {
        "food": [
          {
            "@tag": "waffles",
            "name": "Belgian Waffles",
            "price": "$5.95",
            "description": "Two of our famous Belgian Waffles with plenty of real maple syrup",
            "calories": "650"
          },
          {
            "@tag": "waffles",
            "name": "Strawberry Belgian Waffles",
            "price": "$7.95",
            "description": "Light Belgian waffles covered with strawberries and whipped cream",
            "calories": "900"
          },
          {
            "@tag": "waffles",
            "name": "Berry-Berry Belgian Waffles",
            "price": "$8.95",
            "description": "Belgian waffles covered with assorted fresh berries and whipped cream",
            "calories": "900"
          },
          {
            "@tag": "toast",
            "name": "French Toast",
            "price": "$4.50",
            "description": "Thick slices made from our homemade sourdough bread",
            "calories": "600"
          },
          {
            "@tag": "classic",
            "name": "Homestyle Breakfast",
            "price": "$6.95",
            "description": "Two eggs, bacon or sausage, toast, and our ever-popular hash browns",
            "calories": "950"
          }
        ]
      }
    }


Use .locate() and .retrieve() to find and retrieve your data of interest.


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
[schema.retrieve(path) for path in paths]
```




    ['Belgian Waffles',
     'Strawberry Belgian Waffles',
     'Berry-Berry Belgian Waffles']




```python
paths = schema.locate(calories__lt="700") 
```


```python
[schema.retrieve(path) for path in paths]
```




    ['650', '600']



##### Warning, all types are compared as strings, which may have undesirable results. A fix for this problem is coming.


```python
schema.locate(calories__lt="700") == schema.locate(calories__lt="70") 
```




    True



Some attributes cannot be accessed via keyword arguements, unfortunately.


```python
schema.retrieve(@tag__ne="waffles")
```


      File "<ipython-input-21-c070fc7f6462>", line 1
        schema.retrieve(@tag__ne="waffles")
                        ^
    SyntaxError: invalid syntax



You will need to pass the desired attribute and comparison method as strings in this case.


```python
schema.locate('@tag', 'waffles') # default comparison is __eq__
```




    ['__breakfast_menu__food__0__@tag',
     '__breakfast_menu__food__1__@tag',
     '__breakfast_menu__food__2__@tag']




```python
schema.locate('@tag', 'waffles', comparison='ne')
```




    ['__breakfast_menu__food__3__@tag', '__breakfast_menu__food__4__@tag']



That's it so far.