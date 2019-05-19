from django import forms


class VkRequestForm(forms.Form):
    CHOISE_OWNEWR_POST = [('all', 'Все посты'), ('owner', 'Посты владельца'), ('others', 'Только гостевые посты')]
    id_group = forms.CharField(label='ID Группы')
    count_posts = forms.IntegerField(label='Кол-во постов для анализа')
    filter_posts = forms.ChoiceField(label='От кого посты', widget=forms.RadioSelect, choices=CHOISE_OWNEWR_POST)
