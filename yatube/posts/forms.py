from django.forms import ModelForm

from .models import Post


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
