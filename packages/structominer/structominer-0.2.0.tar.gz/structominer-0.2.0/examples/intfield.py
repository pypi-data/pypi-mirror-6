from structominer import Document, IntField

html = """
<div><span>Foo</span></div>
"""

class MyDoc(Document):
    thing = IntField('//span')


mydoc = MyDoc(html)

print mydoc['thing']
