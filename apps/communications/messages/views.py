from rest_framework import generics, permissions
from .models import Room, Message
from .serializers import RoomSerializer, MessageSerializer
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from .permissions import IsRoomParticipant

# Create your views here.
from django.contrib.auth import get_user_model
User = get_user_model()

class RoomListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        rooms = Room.objects.filter(user1=request.user) | Room.objects.filter(user2=request.user)
        serializer = RoomSerializer(rooms, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        user_id = request.data.get('user_id')
        try:
            other_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValidationError("User does not exist.")
        if other_user == request.user:
            raise ValidationError("Cannot create a room with yourself.")
        room, created = Room.objects.get_or_create(
            user1=min(request.user, other_user, key=lambda u: u.id),
            user2=max(request.user, other_user, key=lambda u: u.id)
        )
        serializer = RoomSerializer(room)
        return Response(serializer.data)


class MessageListCreateView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsRoomParticipant]

    def get_queryset(self):
        room_id = self.kwargs['room_id']
        room = Room.objects.get(id=room_id)
        self.check_object_permissions(self.request, room)
        return room.messages.all().order_by('timestamp')

    def perform_create(self, serializer):
        room = Room.objects.get(id=self.kwargs['room_id'])
        self.check_object_permissions(self.request, room)
        serializer.save(sender=self.request.user, room=room)
