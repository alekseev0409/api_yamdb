from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from users.models import User


class Category(models.Model):
    name = models.CharField(max_length=128,
                            default=None)
    slug = models.SlugField(max_length=128,
                            unique=True)

    class Meta:
        ordering = ['id']

    def __str__(self) -> str:
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=128,
                            default=None)
    slug = models.SlugField(max_length=128,
                            unique=True)

    class Meta:
        ordering = ['id']

    def __str__(self) -> str:
        return self.name


class Title(models.Model):
    name = models.CharField(
                            max_length=128,)
    year = models.IntegerField()
    description = models.TextField(
        max_length=256,
        blank=True,
        null=True
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
    )
    category = models.ForeignKey(
        Category,
        null=True,
        on_delete=models.SET_NULL,
        related_name='titles',
    )

    class Meta:
        ordering = ['id']

    def __str__(self) -> str:
        return self.name


class Review(models.Model):
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    pub_date = models.DateTimeField(auto_now_add=True)
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    score = models.IntegerField(validators=[MinValueValidator(1),
                                MaxValueValidator(10)])

    class Meta:
        ordering = ('-pub_date',)
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_relationships'
            ),
        ]

    def __str__(self) -> str:
        return self.text


class Comment(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True)

    class Meta:
        ordering = ['id']
