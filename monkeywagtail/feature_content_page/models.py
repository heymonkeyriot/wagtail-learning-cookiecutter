import collections

from django.db import models
from django.db.models import Count
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django import forms
from wagtail.wagtailcore.models import Orderable, Page
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailcore.fields import StreamField
from modelcluster.fields import ParentalKey
from wagtail.wagtailsearch import index
from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel,
    StreamFieldPanel,
    InlinePanel,
    MultiFieldPanel)
from wagtail.wagtailsnippets.edit_handlers import SnippetChooserPanel
from monkeywagtail.core.blocks import StandardBlock
from monkeywagtail.author.models import Author

FilterObject = collections.namedtuple('FilterObject', 'id, name, slug')


class ArtistFeaturePageRelationship(Orderable, models.Model):
    # http://www.tivix.com/blog/working-wagtail-i-want-my-m2ms/
    # This is the start of defining the m2m. The related name is the 'magic'
    # that Wagtail hooks to. The model name (artist) within the app (artist) is
    # a terrible naming convention that you should avoid. It's 'class.model'
    page = ParentalKey(
        'FeatureContentPage', related_name='feature_page_artist_relationship'
    )
    artist = models.ForeignKey(
        'artist.artist',
        related_name='artist_feature_page_relationship'
        # If a related name is set here you can use it on relations
        # otherwise you use the lowercase model name with `_set` e.g.
        # artistfeaturepagerelationship_set
        # c/f https://docs.djangoproject.com/en/1.10/topics/db/queries/#following-relationships-backward
    )
    panels = [
        # We need this for the inlinepanel on the Feature Content Page to grab hold of
        SnippetChooserPanel('artist')
    ]


class AuthorFeaturePageRelationship(Orderable, models.Model):
    # We get to define another m2m for authors since a page can have many authors
    # and authors can obviously have many pages. You will see that the modelname
    # and appname are once again identical because I'm not very good at this game!
    page = ParentalKey(
        'FeatureContentPage', related_name='feature_page_author_relationship'
    )
    author = models.ForeignKey(
        'author.author',
        related_name="author_feature_page_relationship"
    )
    panels = [
        # We need this for the inlinepanel on the Feature Content Page to grab hold of
        SnippetChooserPanel('author')
    ]


class GenreFeaturePageRelationship(Orderable, models.Model):
    page = ParentalKey(
        'FeatureContentPage', related_name='feature_page_genre_relationship'
    )
    genre = models.ForeignKey(
        'genre.GenreClass',
        related_name='genre_feature_page_relationship'
    )
    panels = [
        FieldPanel('genre')
    ]


class FeatureContentPage(Page):
    """
    This is a feature content page for all of your interviews, news etc.
    """

    # TODO This almost entirely duplicates StandardPage class. They should be
    # referencing something to reduce the duplication

    search_fields = Page.search_fields + [
        # Defining what fields the search catches
        index.SearchField('introduction'),
        index.SearchField('body'),
    ]

    date = models.DateField("Post date", help_text='blah')

    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Image to be used where this feature content is listed'
    )

    # Page models mostly use generic Django fields. Here we're using a choice
    # field for how the images should be styled.
    # https://docs.djangoproject.com/en/1.10/ref/models/fields/#choices
    # You can reference core/blocks.py for how you can reference choices within
    # StreamField

    image_choices_list = (
            ('fit', 'Contained width'),
            ('expand', 'Expanded width'),
            ('full', 'Full width'),
            ('hide', 'Hidden (e.g. only display on listings)'),
        )

    image_choices = models.CharField(
        max_length=255,
        choices=image_choices_list,
        help_text='How you want the image to be displayed on the feature page'
    )

    # Note below that standard blocks use 'help_text' for supplementary text
    # rather than 'label' as with StreamField
    introduction = models.TextField(
        blank=True,
        help_text="Text to show at the top of the individual page")

    # Using CharField for little reason other than showing a different input
    # type Wagtail allows you to use any field type Django follows, so you can
    # use anything from
    # https://docs.djangoproject.com/en/1.9/ref/models/fields/#field-types
    listing_introduction = models.CharField(
        max_length=250,
        blank=True,
        help_text="Text shown on listing pages, if empty will show 'Introduction' field content")

    # Note below we're calling StreamField from another location. The
    # `StandardBlock` class is a shared asset across the site. It is defined in
    # core > blocks.py. It is just as 'correct' to define the StreamField
    # directly within the model, but this method aids consistency.
    body = StreamField(
        StandardBlock(),
        help_text="Blah blah blah",
        blank=True
        )

    content_panels = Page.content_panels + [
        # The content panels are displaying the components of content we defined
        # in the StandardPage class above. If you add something to the class and
        # want it to appear for the editor you have to define it here too
        # A full list of the panel types you can use is at
        # http://docs.wagtail.io/en/latest/reference/pages/panels.html
        # If you add a different type of panel ensure you've imported it from
        # wagtail.wagtailadmin.edit_handlers in the `From` statements at the top
        # of the model InlinePanel('artist_groups', label="Artist(s)"),
        # SnippetChooserPanel('artist'),
        FieldPanel('date'),
        MultiFieldPanel(
            [
                FieldPanel('introduction'),
                FieldPanel('listing_introduction'),
            ],
            heading="Introduction",
            classname="collapsible"
        ),
        MultiFieldPanel(
            [
                ImageChooserPanel('image'),
                FieldPanel('image_choices'),
            ],
            heading="Image details",
            classname="collapsible"
        ),
        StreamFieldPanel('body'),
        MultiFieldPanel(
            # This duplicates the album/models.py album classa.
            [
                InlinePanel(
                            'feature_page_genre_relationship',
                            label="Genre",
                            panels=None,
                            min_num=1,
                            max_num=3
                ),
            ],
            heading="Genres",
            classname="collapsible"
        ),
        InlinePanel('feature_page_artist_relationship', label="Artists"),
        InlinePanel(
            'feature_page_author_relationship',
            label="Authors",
            help_text='something'),
    ]

    @property
    def features_index(self):
        # I'm not convinced this is altogether necessary... but still we're
        # going from feature_content_page -> feature_index_page
        return self.get_ancestors().type(FeatureIndexPage).last()

    parent_page_types = [
        'feature_content_page.FeatureIndexPage'
        # app.model
    ]

    subpage_types = [
    ]

    # We're returning artists and authors to allow the template to grab the
    # related content. Note the fact we use the related name
    # `artist_feature_page_relationship` to grab them. In the template we'll use
    # a loop to grab them e.g. {% for artist in page.artists %}
    #
    # You don't need to place this at the end of the model, but conventionally
    # it makes sense to put it here
    def artists(self):
        artists = [
            n.artist for n in self.feature_page_artist_relationship.all()
        ]
        return artists

    def authors(self):
        authors = [
            n.author for n in self.feature_page_author_relationship.all()
        ]
        return authors

    def genres(self):
        genres = [
            n.genre for n in self.feature_page_genre_relationship.all()
        ]
        return genres

    def subgenres(self):
        subgenres = [
            n.subgenre for n in self.feature_page_subgenre_relationship.all()
        ]
        return subgenres


class FeatureIndexPage(Page):
    listing_introduction = models.TextField(
        help_text='Text to describe this section. Will appear on other pages that reference this feature section',
        blank=True
        )
    introduction = models.TextField(
        help_text='Text to describe this section. Will appear on the page',
        blank=True
        )
    body = StreamField(
        StandardBlock(),
        blank=True,
        help_text="No good reason to have this here, but in case there's a"
                  "feature section I can't think of"
        )

    search_fields = Page.search_fields + [
        index.SearchField('listing_introduction'),
        index.SearchField('body'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('listing_introduction'),
        FieldPanel('introduction'),
        StreamFieldPanel('body')
    ]

    parent_page_types = [
        'home.HomePage'
    ]

    # Defining what content type can sit under the parent
    subpage_types = [
        'FeatureContentPage'
    ]

    # @property
    # def features(self):
    #     """
    #     Return feature pages that will live under this index page.
    #     This is now redundant since we return our features via
    #     the `get_filtered_feature_pages` function below.
    #     """
    #     return FeatureContentPage.objects.live().descendant_of(self).order_by('-date')

    def filter_years(self):
        """
        Return a collection of years from the date field of feature pages beneath
        this page.
        """
        years = set()
        features = FeatureContentPage.objects.live().descendant_of(self)
        year_dates = features.dates('date', 'year', order='DESC')
        for date in year_dates:
            years.add(date.year)
        return sorted(years, reverse=True)

    def genres(self):
        """
        Return a list of genres from pages that have a relationship defined
        with a genre and are living beneath this page.
        """
        genres = set()

        for feature_content_page in FeatureContentPage.objects.live().descendant_of(self):
            feature_genres = [
                d.genre for d in
                feature_content_page.feature_page_genre_relationship.all()
            ]

            for genre in feature_genres:
                genres.add(FilterObject(
                    id=genre.id,
                    name=genre.title,
                    slug=genre.slug
                ))

        return sorted(genres, key=lambda d: d.name)

    def paginate(self, request, objects):
        page = request.GET.get('page')
        paginator = Paginator(objects, settings.DEFAULT_PER_PAGE)
        try:
            pages = paginator.page(page)
        except PageNotAnInteger:
            pages = paginator.page(1)
        except EmptyPage:
            pages = paginator.page(paginator.num_pages)
        return pages

    def get_filtered_feature_pages(self, request={}):
        """
        Return a filtered queryset of live feature pages that are decendants of
        this page.
        """
        features = FeatureContentPage.objects.live().descendant_of(self)
        # The first step is to create a `features` variable that we populate
        # with a query. This will return all feature_content_pages that are
        # live (e.g. not draft) and a descendant of this index page

        is_filtering = False
        # Second is to create a filter variable. By default it is set to false

        request_filters = {}
        for k, v in request.GET.items():
            request_filters[k] = (v)
        # Here the `=(v)` will accept any value and will trigger `is_filtering`
        # to be True in year and genre below if populated

        # filter by year
        year = request_filters.get('year', '')
        if year:
            is_filtering = True
            features = features.filter(date__year=year)
        # This appends the `features` variable with a filter. The filter in this
        # case being a the 'year', which we access via the double underscore
        # ('__') reverse lookup from the 'date' field.

        # filter by genre
        genre = request_filters.get('genre', '')
        if genre:
            is_filtering = True
            features = features.filter(
                feature_page_genre_relationship__genre__slug=genre
            )
        # We filter on genre__slug so that we can guarantee a response
        # that doesn't include spaces e.g. 'heavy-metal' rather than 'heavy
        #  metal' but it gives more useful information than genre__id

        sort_by = request_filters.get('sort_by', 'modified')
        if sort_by == 'date-asc':
            features = features.order_by('first_published_at')
        if sort_by == 'date-desc':
            features = features.order_by('-first_published_at')

        if not is_filtering:
            pass

        filters = {
            'year': year,
            'genre': genre,
            'sort_by': sort_by
        }

        return features, filters, is_filtering

    def get_context(self, request):
        """
        Overriding the context to get more control over what we return.
        See the section `SEPARATED CONTEXT & PAGINATION` at the end of
        this .py file for details on how it works.
        """
        context = super(FeatureIndexPage, self).get_context(request)

        # filters
        features, filters, is_filtering = self.get_filtered_feature_pages(request)

        # Pagination
        features = self.paginate(request, features)
        # (request, features) looks for the 'features' on line 392

        context['features'] = features

        context['filters'] = filters
        context['is_filtering'] = is_filtering

        return context

    # We use this property to allow the homepage to get the children of the
    # referenced index pages
    @property
    def children(self):
        return self.get_children().specific().live()

        # http://docs.wagtail.io/en/v1.2/topics/pages.html#customising-template-context

# SEPARATED CONTEXT & PAGINATION
#     def features(self):
#        return FeatureContentPage.objects.live().descendant_of(self).order_by('-first_published_at')
#        # We want to use `date` but think we need to define date within the filter?
#        #
#        # Previously self.get_children().specific().live().descendant_of(self).order_by('-first_published_at')
#        # Which I think is redundant since `get_children()` and `descendant_of(self)` are identical?
#
#    def paginate(self, request, *args):
#        page = request.GET.get('page')
#        paginator = Paginator(self.features, 2)  # Show 2 features per page
#        try:
#            pages = paginator.page(page)
#        except PageNotAnInteger:
#            pages = paginator.page(1)
#        except EmptyPage:
#            pages = paginator.page(paginator.num_pages)
#        return pages
#
#    def get_context(self, request):
#        """
#        Overriding the context to get more control over what we return.
#        """
#        context = super(FeatureIndexPage, self).get_context(request)
#
#        features = self.paginate(request, self.features)
#        # Right... I think I understand this
#        # the function `paginate` defines how the paginator should behave. We do
#        # this passing (I think) a local variable 'pages' through that is made
#        # available globally by the `paginate` function. On it's own it's inert.
#        # Calling `features = self.paginate will give you a sad white space where
#        # content should be. We need to make a request to the features function
#        # (where we define the queryset for the content we want returned) within
#        # paginate for anything to happen. We do this with
#        # features = self.paginate(request, self.features) e.g. give me all the
#        # features but wrap them with pagination.
#        #
#        # We need `self.` because we need to tell Python to go get them from
#        # FeatureIndexPage rather than from within the `get_context` function.
#        #
#        # Within paginate we add a third positional argument (that can be
#        # named whatever you want as far as I can tell, so have called it `*args` as
#        # that appears to be the convention) to enable `self.features` to be requested. Without it
#        # you'd get an error "paginate() takes 2 positional arguments but 3 were given"
#        #
#        #
#        # features_pagination = self.features(request)
#        # Without above we'll get an error local variable referenced before assignment.
#        # Unfortunately, with above we get the error
#        # 'PageQuerySet' object is not callable. Removing `(request)` removes the error
#
#        # pagination
#        # features_pagination = self.get_paginated(request, features_pagination)
#
#        context['features'] = features
#
#        return context
#
# Actually further conversation suggested I didn't understand. The `*args' isn't
# necessary. I can either pass 'features' in to the paginate method and access it
# there without need to use `self.` to get to the global
#
#
#
# MIXED CONTEXT & PAGINATION
# For reference below will work _and_ paginate
#
# The difficulty with this is that we're mixing pagination
# with context. It makes it quite difficult to follow the thread through
# as features and paginator have different attributes assigned before
# having features returned. It works fine, but isn't hugely extensible.
#
#    @property
#    def features(self):
#        return self.get_children().specific().live().descendant_of(self).order_by('-first_published_at')
#        # We want to use `date` but think we need to define date within the filter?
#
#    def get_context(self, request):
#        # http://docs.wagtail.io/en/v1.2/topics/pages.html#customising-template-context
#        # That convention can only be used on page models. Which is a pain.
#        page_number = request.GET.get('page')
#        paginator = Paginator(self.features, settings.DEFAULT_PER_PAGE)
#        try:
#            features = paginator.page(page_number)
#        except PageNotAnInteger:
#            features = paginator.page(1)
#        except EmptyPage:
#            features = paginator.page(paginator.num_pages)
#
#        context = super().get_context(request)
#        context.update(features=features)
#
#        return context
#
# AMENDED CONTEXT
# The absolute minimum required (if you want to override the context) is:
#
#    def get_context(self, request):
#        context = super(FeatureIndexPage, self).get_context(request)
#
#        # Add extra variables and return the updated context
#        context['features'] = FeatureContentPage.objects.live().descendant_of(self).order_by('-first_published_at')
#        return context
