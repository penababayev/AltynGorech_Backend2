from .models import Teachers, ExamEvents
from .serializers import TeacherSerializer, ExamEventSerializer
from django.http import HttpResponse, JsonResponse
from rest_framework.parsers import JSONParser
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def teacher_list(request):
    if request.method == "GET":
        obj = Teachers.objects.all()
        serializer = TeacherSerializer(obj, many = True)
        return JsonResponse(serializer.data, safe=False)
    elif request.method == "POST":
        data = JSONParser().parse(request)
        serializer = TeacherSerializer(data = data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)
        
    return HttpResponse(status = 400)

@csrf_exempt
def teacher_detail(request, pk):
    try:
        obj = Teachers.objects.get(pk=pk)
    except Teachers.DoesNotExist:
        return HttpResponse(status=404)
    
    if request.method == 'GET':
        serializer = TeacherSerializer(obj)
        return JsonResponse(serializer.data)
    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = TeacherSerializer(obj, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)
    elif request.method == 'DELETE':
        obj.delete()
        return HttpResponse(status=204)



        