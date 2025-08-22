# from .models import *
# from .serializers import *
# import re
# from django.http import HttpResponse, JsonResponse
# from rest_framework.parsers import JSONParser
# from django.views.decorators.csrf import csrf_exempt
# from rest_framework.decorators import api_view
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from django.db.models import Prefetch





# #Function based API ------******--------
# # @csrf_exempt
# # def teacher_list(request):
# #     if request.method == "GET":
# #         obj = Teachers.objects.all()
# #         serializer = TeacherSerializer(obj, many = True)
# #         return JsonResponse(serializer.data, safe=False)
# #     elif request.method == "POST":
# #         data = JSONParser().parse(request)
# #         serializer = TeacherSerializer(data = data)
# #         if serializer.is_valid():
# #             serializer.save()
# #             return JsonResponse(serializer.data)
# #         return JsonResponse(serializer.errors, status=400)
        
# #     return HttpResponse(status = 400)

# # @csrf_exempt
# # def teacher_detail(request, pk):
#     # try:
#     #     obj = Teachers.objects.get(pk=pk)
#     # except Teachers.DoesNotExist:
#     #     return HttpResponse(status=404)
    
#     # if request.method == 'GET':
#     #     serializer = TeacherSerializer(obj)
#     #     return JsonResponse(serializer.data)
#     # elif request.method == 'PUT':
#     #     data = JSONParser().parse(request)
#     #     serializer = TeacherSerializer(obj, data=data)
#     #     if serializer.is_valid():
#     #         serializer.save()
#     #         return JsonResponse(serializer.data)
#     #     return JsonResponse(serializer.errors, status=400)
#     # elif request.method == 'DELETE':
#     #     obj.delete()
#     #     return HttpResponse(status=204)
# #Function based API ------******--------



# @api_view(["GET", "POST"])
# def teacher_list(request):
#     if request.method == "GET":
#         obj = Teachers.objects.all()
#         serializer = TeacherSerializer(obj, many = True)
#         return Response(serializer.data)
#     elif request.method == "POST":
#         # data = JSONParser().parse(request)
#         serializer = TeacherSerializer(data = request.data) #aslynda json parseri cagyryp data=data edilyadi emma @api_view komegi bilen sadalasdy
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
#     return Response(status = status.HTTP_400_BAD_REQUEST)


# @api_view(['GET','PUT', 'DELETE'])
# def teacher_detail(request, pk):
#     try:
#         obj = Teachers.objects.get(pk=pk)
#     except Teachers.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)
    
#     if request.method == 'GET':
#         serializer = TeacherSerializer(obj)
#         return Response(serializer.data)
#     elif request.method == 'PUT':
#         # data = JSONParser().parse(request)
#         serializer = TeacherSerializer(obj, data = request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#     elif request.method == 'DELETE':
#         obj.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


# #News
# @api_view(['GET'])
# def news_list(request):
#     if request.method == 'GET':
#         obj = News.objects.all()
#         serializer = NewsSerializer(obj, many=True)
#         return Response(serializer.data)
#     return Response(status=status.HTTP_400_BAD_REQUEST)

# # @api_view(['DELETE'])
# # def delete_image(request, pk):
# #     try:
# #         obj = News.objects.get(pk=pk)
# #     except News.DoesNotExist:
# #         return Response (status=status.HTTP_404_NOT_FOUND)
# #     if request.method == 'DELETE':
# #         obj.delete()
# #         return Response(status=status.HTTP_204_NO_CONTENT)


# #Activity
# @api_view(['GET'])
# def activity_list(request):
#     if request.method == 'GET':
#         obj = Activity.objects.all()
#         serializer = ActivitySerializer(obj, many=True)
#         return Response(serializer.data)
#     return Response(status=status.HTTP_400_BAD_REQUEST)

    
# #Videos
# @api_view(['GET'])
# def video_list(request):
#     if request.method == 'GET':
#         obj = Video.objects.all()
#         serializer = VideoSerializer(obj, many=True)
#         return Response(serializer.data)
#     return Response(status=status.HTTP_400_BAD_REQUEST)

# #Adress
# @api_view(['GET'])
# def adress_list(request):
#     if request.method == 'GET':
#         obj = Adress.objects.all()
#         serializer = AdressSerializer(obj, many=True)
#         return Response(serializer.data)
#     return Response(status=status.HTTP_400_BAD_REQUEST)

# #Course Items
# # @api_view(['GET'])
# # def course_list(request, pk):
# #     try:
# #         obj = Course.objects.get(pk=pk)
# #     except Course.DoesNotExist:
# #         return Response(status=status.HTTP_404_NOT_FOUND)
# #     if request.method == 'GET':
# #         item = obj.items.all()
# #         serializer = CourseItemSerializer(item, many=True)
# #         return Response(serializer.data)


# #Certificates
# # @api_view(['GET'])
# # def certificate_by_phone_list(request, phone_number):
# #     try:
# #         customer = Certificate.objects.get(phone_num=phone_number)
# #     except Certificate.DoesNotExist:
# #         return Response(status=status.HTTP_404_NOT_FOUND)
# #     if request.method == 'GET':
# #         serializer = CertificateSerializer(customer)
# #         return Response(serializer.data)





# # @api_view(['GET'])
# # def certificate_by_phone_list(request, phone_number):
# #     try:
# #         customer = Student.objects.get(phone=phone_number)
# #     except Student.DoesNotExist:
# #         return Response(status=status.HTTP_404_NOT_FOUND)
# #     if request.method == 'GET':
# #         serializer = StudentSerializer(customer)
# #         return Response(serializer.data)


# #Profesyonel bir dershane veritabani


    
    
