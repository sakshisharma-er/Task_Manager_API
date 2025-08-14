from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from .models import *
from .serializers import *
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


# ---------------- Task Views ---------------- #

class TaskListCreateView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(
        operation_summary="Get all tasks",
        operation_description="Retrieve a list of all tasks",
        responses={200: TaskSerializer(many=True)}
    )
    def get(self, request):
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Create a new task",
        operation_description="Add a new task to the database",
        request_body=TaskSerializer,
        responses={201: TaskSerializer}
    )
    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
from drf_yasg import openapi

jwt_auth = [{'Bearer': []}]  

class TaskDetailView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(
        operation_summary="Update a task",
        operation_description="Update task fields (partial updates allowed). Authentication required.",
        request_body=TaskSerializer,
        responses={200: TaskSerializer, 400: "Bad Request", 401: "Unauthorized"},
        security=jwt_auth  
    )
    def put(self, request, pk):
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)

        task = Task.objects.get(id=pk)
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="Delete a task",
        operation_description="Delete a task by ID. Only admin users can delete tasks.",
        responses={200: "Task deleted", 401: "Unauthorized", 403: "Forbidden"},
        security=jwt_auth  
    )
    def delete(self, request, pk):
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
        if not request.user.is_staff:
            return Response({"error": "Only admin users can delete tasks"}, status=status.HTTP_403_FORBIDDEN)

        task = Task.objects.get(pk=pk)
        task.delete()
        return Response(f"Task with ID {pk} deleted", status=status.HTTP_200_OK)



class TaskfilterbyCompletedView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(
        operation_summary="Filter tasks by completion status with pagination",
        operation_description="Provide `completed` as true/false/null, along with page_size and page_number.",
        responses={200: openapi.Response('Paginated tasks', TaskSerializer(many=True))}
    )
    def get(self, request, completed, page_size, page_number):
        try:
            page_size = int(page_size)
            page_number = int(page_number)
        except ValueError:
            return Response({"error": "page_size and page_number must be integers"}, status=status.HTTP_400_BAD_REQUEST)

        tasks = Task.objects.all().order_by('created_at')
        if completed.lower() != "null":
            tasks = tasks.filter(completed=completed.lower() in ['true', '1']).order_by('created_at')

        paginator = Paginator(tasks, page_size)


        paginator = Paginator(tasks, page_size)
        try:
            page_obj = paginator.page(page_number)
        except:
            return Response({"error": "Invalid page number"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = TaskSerializer(page_obj, many=True)
        return Response({
            "total_items": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": page_number,
            "page_size": page_size,
            "results": serializer.data
        }, status=status.HTTP_200_OK)


# ---------------- Authentication Views ---------------- #

class RegisterView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="User registration",
        operation_description="Register a new user",
        request_body=RegisterSerializer,
        responses={201: "User registered successfully", 400: "Bad Request"}
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="User login",
        operation_description="Provide username and password to receive JWT tokens",
        request_body=LoginSerializer,
        responses={200: "Login successful", 400: "Bad Request"}
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenRefreshView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Refresh JWT token",
        operation_description="Provide refresh token to get a new access token",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token')}
        ),
        responses={200: "New access token", 400: "Invalid or expired token"}
    )
    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh = RefreshToken(refresh_token)
            return Response({'access': str(refresh.access_token)}, status=status.HTTP_200_OK)
        except TokenError:
            return Response({"error": "Invalid or expired refresh token"}, status=status.HTTP_400_BAD_REQUEST)
