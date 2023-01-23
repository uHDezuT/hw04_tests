from django.forms import ModelForm, Textarea

from .models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['group', 'text', 'image']
        labels = {
            'group': 'Группа',
            'text': 'Текст',
            'image': 'Изображение',
        }
        help_texts = {
            'group': 'Название группы поста',
            'text': 'Текст поста',
            'image': 'Изображение поста',
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {'text': Textarea(attrs={"cols": 55, "rows": 2})}
        help_texts = {
            'text': 'Текст комментария',
        }
