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


# #StudentLookupByPhone

# def normalize_phone(raw: str) -> str:
#     """
#     Basit normalize: baştaki '+' hariç tüm boşluk, tire, parantez vb. temizlenir.
#     Eğer DB'de + ülke koduyla saklıyorsan, bu fonksiyonu aynı formatı üretecek şekilde ayarla.
#     strip() → Baştaki ve sondaki boşlukları siler.
#     Örn: " +90 532 123 45 67 " → "+90 532 123 45 67"
#     if raw.startswith("+"):
#         return "+" + re.sub(r"\D", "", raw[1:])
#     raw.startswith("+") → Eğer numara + ile başlıyorsa (ör: +90...).

#     raw[1:] → İlk karakteri (+) at, geri kalan kısmı al (örn: "90 532 123 45 67").
#     re.sub(r"\D", "", raw[1:]) → Regex ile rakam olmayan her şeyi sil.
#     \D = digit olmayan karakter.
#     Boşluk, tire, parantez vs. hepsi silinir.
#     Sonuç olarak başına tekrar "+" eklenir.
#     Örn: "+90 532-123-4567" → "+905321234567"
#     return re.sub(r"\D", "", raw)
#     Eğer numara + ile başlamıyorsa → doğrudan tüm rakam olmayan karakterleri sil.
#     Örn: "0532 123 45 67" → "05321234567"
#     Örn: "0 (532) 123-45-67" → "05321234567"
#     """
#     raw = raw.strip()
#     if raw.startswith("+"):
#         return "+" + re.sub(r"\D", "", raw[1:])
#     # Örn. yerel formatları + ülke koduna çevirmek istersen burada mantık ekleyebilirsin.
#     return re.sub(r"\D", "", raw)


# class StudentLookupByPhone(APIView):
#     """
#     GET /api/students/lookup?phone=+49...  (veya 0532..., 532..., vs.)
#     JSON:
#     - found: bool
#     - message: str
#     - student: {...} (found=True ise)
#     - enrolled: bool
#     - enrollments: [ { id, course:{id,name}, status, enrolled_at }, ... ]
#     """

#     def get(self, request, *args, **kwargs):
#         phone = request.query_params.get("phone")
#         if not phone:
#             return Response(
#                 {"detail": "Telefon nomeri ýazmadyňyz, nomer hökmanydyr!"},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         normalized = normalize_phone(phone)

#         try:
#             student = (
#                 Student.objects.select_related("branch")
#                 .get(phone=normalized)
#             )
#         except Student.DoesNotExist:
#             # İstersen 404 yerine 200 + found:false döndürüp UI'ı basitleştirebilirsin.
#             return Response(
#                 {
#                     "found": False,
#                     "message": "Bu nomerde registrasiya edilen okuwcy tapylmady",
#                     "phone": phone,
#                 },
#                 status=status.HTTP_200_OK,
#             )

#         enrollments_qs = (
#             Enrollment.objects
#             .filter(student=student)
#             .select_related("course")
#             .order_by("-enrolled_at")
#         )

#         student_data = StudentSerializer(student).data
#         enrollments_data = EnrollmentSerializer(enrollments_qs, many=True).data
#         enrolled = len(enrollments_data) > 0

#         return Response(
#             {
#                 "found": True,
#                 "message": "Okuwcy tapyldy we maglumatlary sergilendi."
#                 if enrolled
#                 else "Okuwcy tapyldy, emma hic hili kursa registrasiya edilmedik",
#                 "student": student_data,
#                 "enrolled": enrolled,
#                 "enrollments": enrollments_data,
#             },
#             status=status.HTTP_200_OK,
#         )




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


    
    
