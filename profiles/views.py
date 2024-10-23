from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Profile
from .serializers import ProfileSerializer


class ProfileList(APIView):
    """
    API endpoint that allows users to retrieve a list of profiles.

    This class-based view handles GET requests to return all profile instances
    from the database. It uses the Profile model and ProfileSerializer to
    serialize the data and return it as a JSON response.

    Methods:
        get(request): Handles GET requests and returns a serialized list of
        Profile objects.
    Args:
        request (HttpRequest): The HTTP request object that contains metadata
        about the request.
    Returns:
        Response: A JSON response containing serialized data of all Profile
        instances.
    """
    def get(self, request):
        """
        Retrieves all profiles from the database and returns them in serialized
        form.
        This method queries the Profile model for all instances, serializes
        them using ProfileSerializer, and returns the serialized data in the
        response.

        Args:
            request (HttpRequest): The HTTP request object containing request
            data.
        Returns:
            Response: A JSON response with serialized data of all Profile
            objects.
        """
        profiles = Profile.objects.all()
        serializer = ProfileSerializer(profiles, many=True)
        return Response(serializer.data)


class ProfileDetail(APIView):
    def get_object(self, pk):
        try:
            profile = Profile.objects.get(pk=pk)
            return profile
        except Profile.DoesNotExist:
            raise Http404
    
    def get(self,request,pk):
        profile = self.get_object(pk)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)
    
