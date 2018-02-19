from rest_framework import serializers
from todolist.models import TodoList
from django.contrib.auth.models import User



class TodoListSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    highlight = serializers.HyperlinkedIdentityField(view_name='todolist-highlight', format='html')

    class Meta:
        model = TodoList
        fields = ('created', 'highlight', 'title','text','owner')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    todos = serializers.HyperlinkedRelatedField(queryset=TodoList.objects.all(), view_name='todolist-detail', many=True)

    class Meta:
        model = User
        fields = ('url', 'username', 'todos')
