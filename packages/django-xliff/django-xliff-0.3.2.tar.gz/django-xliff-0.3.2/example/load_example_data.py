import datetime
from simpleapp.models import Category, Author, Article

sports = Category.objects.create(name="Sports")
music = Category.objects.create(name="Music")
op_ed = Category.objects.create(name="Op-Ed")

joe = Author.objects.create(name="Joe")
jane = Author.objects.create(name="Jane")

a1 = Article(
    author=jane,
    headline="Poker has no place on ESPN",
    pub_date=datetime.datetime(2006, 6, 16, 11, 00)
)
a1.save()
a1.categories = [sports, op_ed]

a2 = Article(
    author=joe,
    headline="Time to reform copyright",
    pub_date=datetime.datetime(2006, 6, 16, 13, 00, 11, 345)
)
a2.save()

a2.categories = [music, op_ed]
