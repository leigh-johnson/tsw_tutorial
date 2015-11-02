## UNIT TEST DATA ##
@cherrypy.expose
def build_data(self):

    body_1 = Body(
        text="Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec qu"
        )
    body_2 = Body(
        text="Es gibt im Moment in diese Mannschaft, oh, einige Spieler vergessen ihnen Profi was sie sind. Ich lese nicht sehr viele Zeitungen, aber ich habe gehört viele Situationen. Erstens: wir haben nicht offe"
        )
    body_3 = Body(
        text="En se réveillant un matin après des rêves agités, Gregor Samsa se retrouva, dans son lit, métamorphosé en un monstrueux insecte. Il était sur le dos, un dos aussi dur qu’une carapace, et, en relevant."
        )        
    img_1 = Img(
        src='http://placehold.it/350x200&text=img_1',
        title='Placeholder img 1')
    img_2 = Img(
        src='http://placehold.it/350x200&text=img_2',
        title='Placeholder img 2')
    img_3 = Img(
        src='http://placehold.it/350x200&text=img_3',
        title='Placeholder img 3')
    article_1 = Article(
        title_en='Hero image',
        description_en='Hero image description',
        order=30,
        layout='image-hero',
        )
    article_2 = Article(
        title_en='Image asides',
        description_en='How to move',
        order=20,
        layout='image-aside',
        )
    article_3 = Article(
        title_en='Full-width video',
        description_en='Full-width video',
        order=10,
        layout='video',
        )
    category_1 = Category(
        title_en="Image layouts",
        description_en="Layouts with images",
        order=10,
        )
    category_2 = Category(
        title_en="Video layouts",
        description_en="How to make friends",
        order=20,
        )
    category_3 = Category(
        title_en="Dungeons",
        description_en="How to dungeon",
        order=30,
        )   
    article_1.imgs.append(img_1)
    article_2.imgs.append(img_2)


    article_2.imgs.append(img_3)

    article_1.body_en.append(body_1)
    article_1.body_fr.append(body_2)
    article_1.body_de.append(body_3)

    article_2.body_en.append(body_1)
    article_2.body_fr.append(body_2)
    article_2.body_de.append(body_3)

    article_3.body_en.append(body_1)
    article_3.body_fr.append(body_2)
    article_3.body_de.append(body_3)

    category_1.body_en.append(body_1)
    category_1.body_fr.append(body_2)
    category_1.body_de.append(body_3)

    category_2.body_en.append(body_1)
    category_2.body_fr.append(body_2)
    category_2.body_de.append(body_3)

    category_3.body_en.append(body_1)
    category_3.body_fr.append(body_2)
    category_3.body_de.append(body_3)

    category_1.articles.append(article_1)
    category_1.articles.append(article_2)
    category_2.articles.append(article_3)
    category_1.imgs.append(img_1)
    category_2.imgs.append(img_2)
    category_3.imgs.append(img_3)

    result = cherrypy.request.db.add_all([article_1, article_2, article_3, category_1, category_2, category_3, img_1, img_2, img_3])
    return result