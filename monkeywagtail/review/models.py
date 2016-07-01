from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.fields import StreamField
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtailsearch import index
from wagtail.wagtailadmin.edit_handlers import FieldPanel, StreamFieldPanel, InlinePanel
from wagtail.wagtailsnippets.edit_handlers import SnippetChooserPanel
from modelcluster.fields import ParentalKey
from monkeywagtail.core.blocks import StandardBlock


# Artist
class ReviewArtistRelationship(models.Model):
    ArtistRelationship = ParentalKey(
        'ReviewPage',
        related_name='review_artist_relationship'
    )
    artist_name = models.ForeignKey(
        'artist.Artist',
        #app.class
        related_name="+",
        help_text='The artist who made the album being reviewed'
    )
    panels = [
        SnippetChooserPanel('artist_name')
    ]


# Album
class ReviewAlbumRelationship(models.Model):
    AlbumRelationship = ParentalKey(
        'ReviewPage',
        related_name='review_album_relationship'
    )
    album_name = models.ForeignKey(
        'album.Album',
        #app.class
        related_name="+",
        help_text='The album being reviewed'
    )
    panels = [
        SnippetChooserPanel('album_name')
    ]


# Ugh, and the authors
class ReviewAuthorRelationship(models.Model):
    authorRelationship = ParentalKey(
        'ReviewPage',
        related_name='review_author_relationship'
    )
    author_name = models.ForeignKey(
        'author.Author',
        #app.class
        related_name="+",
        help_text='The author who wrote this'
    )
    panels = [
        SnippetChooserPanel('author_name')
    ]


class ReviewPage(Page):
    """
    This is a page for an album review
    """

    search_fields = Page.search_fields + (
        # Defining what fields the search catches
        index.SearchField('introduction'),
        index.SearchField('body'),
    )

    date = models.DateField("Post date")

    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Image to be used where this review is listed'
    )

    # Note the integerfield can't just have a max_value and min_value assigned, but needs to import the
    # validators from django. It frankly feels silly to do that, but that's what you have to do!
    rating = models.IntegerField("Album rating", validators=[MinValueValidator(0), MaxValueValidator(5)], help_text="Your rating needs to be between 0 - 5")

    # Note below that standard blocks use 'help_text' for supplementary text rather than 'label' as with StreamField
    introduction = models.TextField(blank=True, help_text="Text to show at the review page")

    # Using CharField for little reason other than showing a different input type
    # Wagtail allows you to use any field type Django follows, so you can use anything from
    # https://docs.djangoproject.com/en/1.9/ref/models/fields/#field-types
    listing_introduction = models.CharField(max_length=250, blank=True, help_text="Text shown on review, and other, listing pages, if empty will show 'Introduction' field content")

    # Note below we're calling StreamField from another location. The `StandardBlock` class is a shared
    # asset across the site. It is defined in core > blocks.py. It is just as 'correct' to define
    # the StreamField directly within the model, but this method aids consistency.
    body = StreamField(StandardBlock(), blank=True)

    @property
    def artist_in_editor(self):
        artist_in_editor = [
            n.artist for n in self.review_artist_relationship.all()
        ]
        return artist_in_editor

    @property
    def album_in_editor(self):
        album_in_editor = [
            n.album for n in self.review_album_relationship.all()
        ]
        return album_in_editor

    @property
    def author_in_editor(self):
        author_in_editor = [
            n.author for n in self.review_author_relationship.all()
        ]
        return author_in_editor

    def get_context(self, request):
        # This is display view - I think - though I'm less show about what it's *actually* doing
        context = super(ReviewPage, self).get_context(request)
        context['children'] = Page.objects.live().in_menu().child_of(self)
        return context

    content_panels = Page.content_panels + [
        # The content panels are displaying the components of content we defined in the StandardPage class above
        # If you add something to the class and want it to appear for the editor you have to define it here too
        # A full list of the panel types you can use is at http://docs.wagtail.io/en/latest/reference/pages/panels.html
        # If you add a different type of panel ensure you've imported it from wagtail.wagtailadmin.edit_handlers in
        # in the `From` statements at the top of the model
        InlinePanel('review_album_relationship', label="Album", panels=None, min_num=1, max_num=1),
        InlinePanel('review_artist_relationship', label="Arist", panels=None, min_num=1),
        ImageChooserPanel('image'),
        FieldPanel('date'),
        FieldPanel('rating'),
        FieldPanel('introduction'),
        FieldPanel('listing_introduction'),
        StreamFieldPanel('body'),
        InlinePanel('review_author_relationship', label="Author", panels=None, min_num=1)
    ]

    parent_page_types = [
        'ReviewIndexPage'
    ]


class ReviewIndexPage(Page):
    listing_introduction = models.TextField(help_text='Text to describe this section. Will appear on other pages that reference this feature section', blank=True)
    introduction = models.TextField(help_text='Text to describe this section. Will appear on the page', blank=True)

    search_fields = Page.search_fields + (
        index.SearchField('listing_introduction'),
    )

    content_panels = Page.content_panels + [
        FieldPanel('listing_introduction'),
        FieldPanel('introduction')
    ]

    parent_page_types = [
        'home.HomePage'
    ]

    # Defining what content type can sit under the parent
    subpage_types = [
        'ReviewPage'
    ]

## Index page context to return content
## This works, but doens't paginate
    def get_context(self, request):
        context = super(ReviewIndexPage, self).get_context(request)
        context['reviews'] = ReviewPage.objects.descendant_of(self).live().order_by('-date')
        return context

# Below is how we get children of reviews (i.e a review) on to the homepage
    @property
    def children(self):
        return self.get_children().specific().live()