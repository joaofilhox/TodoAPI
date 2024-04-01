import csv
import io
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.request import Request
from .models import Task
from .serializers import TaskSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from rest_framework.parsers import MultiPartParser, FormParser

class TaskView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: TaskSerializer(many=True)},
        summary="List tasks",
        description="Returns a list of all tasks."
    )
    def get(self, request: Request) -> Response:
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=TaskSerializer,
        responses={201: TaskSerializer()},
        summary="Create task",
        description="Creates a new task."
    )
    
    def post(self, request: Request) -> Response:
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class TaskUpdateDeleteView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        request=TaskSerializer,
        responses={200: TaskSerializer()},
        summary="Update task",
        description="Updates an existing task."
    )
    def put(self, request: Request, pk: int) -> Response:
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = TaskSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    

    @extend_schema(
        responses={204: "No content", 404: "Task not found", 500: "Failed to delete task"},
        summary="Delete task",
        description="Deletes an existing task."
    )
    def delete(self, request: Request, pk: int) -> Response:
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        try:
            task.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class ImportTasksView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        request={"type": "file"},
        responses={201: "Tasks imported successfully", 400: "Bad request"},
        summary="Import tasks",
        description="Imports tasks from a CSV or Excel file. Upload a file with fields 'Title', 'Description', and 'Status'."
    )
    def post(self, request):
        file = request.FILES.get('file')
    
        if not file:
            return Response({'error': 'No file uploaded'}, status=status.HTTP_400_BAD_REQUEST)

        if file.content_type not in ['text/csv', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']:
            return Response({'error': 'Unsupported file format'}, status=status.HTTP_400_BAD_REQUEST)

        tasks_data = self.parse_csv(file)

        user = request.user
        if not user.is_authenticated:
            return Response({'error': 'User not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)

        errors = []
        successes = 0
        
        for task_data in tasks_data:
            serializer = TaskSerializer(data=task_data)
            if serializer.is_valid():
                serializer.save(owner=request.user)
                successes += 1
            else:
                errors.append(serializer.errors)

        if successes > 0:
            return Response({'message': f'{successes} task(s) imported successfully'},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'No tasks imported', 'details': errors},
                            status=status.HTTP_400_BAD_REQUEST)
            

    def parse_csv(self, file):

        tasks_data = []
        file_text = io.TextIOWrapper(file, encoding='utf-8')  

        csv_reader = csv.DictReader(file_text)
        for row in csv_reader:
            
            task = {
                'title': row.get('title', ''),
                'description': row.get('description', ''),
                'status': row.get('status', '')
            }
            
            tasks_data.append(task)
        return tasks_data