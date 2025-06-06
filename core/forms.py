from django import forms
from .models import Review, Master

class ReviewForm(forms.ModelForm):
    """
    Форма для создания нового отзыва
    """
    # Переопределяем поле master для лучшего стиля
    master = forms.ModelChoiceField(
        queryset=Master.objects.filter(is_active=True),
        label="Мастер",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_master',
        }),
        empty_label="Выберите мастера"
    )
    
    # Переопределяем поле рейтинга, но скроем его в шаблоне и заменим на звездочки
    rating = forms.IntegerField(
        min_value=1, 
        max_value=5,
        label="Оценка",
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'id': 'rating',
            'style': 'display: none;',  # Скрываем поле, использоваться будут звезды
        })
    )
    
    class Meta:
        model = Review
        fields = ['client_name', 'text', 'rating', 'master', 'photo']
        widgets = {
            'client_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ваше имя'
            }),
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Напишите ваш отзыв...',
                'rows': 4
            }),
            'photo': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }
        labels = {
            'client_name': 'Ваше имя',
            'text': 'Текст отзыва',
            'photo': 'Фотография (необязательно)',
        }
        help_texts = {
            'text': 'Поделитесь своими впечатлениями о нашем мастере',
            'photo': 'Вы можете приложить фотографию результата работы мастера',
        }