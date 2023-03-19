import json

from django.conf import settings
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count, Avg
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from vacancies.models import Vacancy, Skill


def hello(request):
    return HttpResponse("Hy")

# @method_decorator(csrf_exempt, name='dispatch') # отключаем проверку csrf
class VacancyListView(ListView):
    model = Vacancy

    def get(self, request, *args, **kwargs):
        super().get(request, *args, **kwargs)
        # vacancies = Vacancy.objects.all()

        search_text = request.GET.get("text", None)
        if search_text:
            # vacancies = vacancies.filter(text=search_text)
            self.object_list = self.object_list.filter(text=search_text)

        # ==== сортировка по алфавиту ====
        # self.object_list = self.object_list.order_by("text")

        ## Join
        # По умолчанию Django не делает join, поэтому если вы знаете, что будете обращаться к колонкам связанной модели, необходимо самостоятельно вызвать метод `select_related`, в который передать список моделей.
        # Так же, Django умеет заранее запрашивать данные из моделей со связью m2m, для этого необходимо вызвать метод `prefetch_related`
        #  Например вот так мы с вами в уроке подтягивали для вакансии данные об авторе и скилах:
        self.object_list = self.object_list.select_related('user').prefetch_related('skills').order_by("text")

        # # ============ ПАГИНАЦИЯ В РУЧНУЮ =================
        # # 1 - 0:10
        # # 2- 10:20
        # # 3- 20:30
        # total_page = self.object_list.count()
        # page_number = int(request.GET.get("page", 1))
        # offset = (page_number - 1) * settings.TOTAL_ON_PAGE
        # if (page_number - 1) * settings.TOTAL_ON_PAGE < total_page:
        #     self.object_list = self.object_list[offset:offset + settings.TOTAL_ON_PAGE]
        # else:
        #     self.object_list = self.object_list[offset:offset + total_page]

        # ========= ПАГИНАЦИЯ С ПОМОЩЬЮ DJANGO ===============
        paginator = Paginator(self.object_list, settings.TOTAL_ON_PAGE)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        vacancies = []
        for vacancy in page_obj:
            vacancies.append({
                "id": vacancy.id,
                "text": vacancy.text,
                "slug": vacancy.slug,
                "status": vacancy.status,
                "created": vacancy.created,
                "user": vacancy.user.username,
                # "skills": list(vacancy.skills.all().values_list("name", flat=True)),
                "skills": list(map(str, vacancy.skills.all())),
            })

        response = {
            "items": vacancies,
            "num_pages": paginator.num_pages,
            "total": paginator.count,
        }

        return JsonResponse(response, safe=False)

class VacancyDetailView(DetailView):
    model = Vacancy

    def get(self, request, *args, **kwargs):
        vacancy = self.get_object()

        return JsonResponse({
            "id": vacancy.id,
            "text": vacancy.text,
            "slug": vacancy.slug,
            "status": vacancy.status,
            "created": vacancy.created,
            "user": vacancy.user_id,
        })


@method_decorator(csrf_exempt, name='dispatch') # отключаем проверку csrf
class VacancyCreateView(CreateView):
    model = Vacancy
    fields = ["user", "text", "slug", "status", "created", "skills"]

    def post(self, request, *args, **kwargs):
        vacancy_data = json.loads(request.body)

        vacancy = Vacancy.objects.create(
            # user_id=vacancy_data["user_id"],
            slug=vacancy_data["slug"],
            text=vacancy_data["text"],
            status = vacancy_data["status"],
        )

        vacancy.user = get_object_or_404(User, pk=vacancy_data["user_id"])

        # vacancy.text = vacancy_data["text"]
        # vacancy.slug = vacancy_data["slug"]
        # vacancy.status = vacancy_data["status"]
        # vacancy.created = vacancy_data["created"]
        # vacancy.skills = vacancy_data["skills"]
        # vacancy.save()
        for skill in vacancy_data["skills"]:
            # ===== Меняем TRY на следующий код ниже =====
            # try:
            #     skill_obj = Skill.objects.get(name=skill)
            # except Skill.DoesNotExist:
            #     skill_obj = Skill.objects.create(name=skill)
            # ==============================================
            skill_obj, created = Skill.objects.get_or_create(
                name=skill,
                defaults = {
                    "is_active": True,
                })
            vacancy.skills.add(skill_obj)
        vacancy.save()

        return JsonResponse({
            "id": vacancy.id,
            "text": vacancy.text,
            "slug": vacancy.slug,
            "status": vacancy.status,
            "created": vacancy.created,
            "user": vacancy.user_id,
            "skills": list(map(str, vacancy.skills.all())),
        })


@method_decorator(csrf_exempt, name='dispatch')  # отключаем проверку csrf
class VacancyUpdateView(UpdateView):
    model = Vacancy
    fields = ["text", "slug", "status", "skills"]

    def patch(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)

        vacancy_data = json.loads(request.body)

        self.object.slug=vacancy_data["slug"]
        self.object.text=vacancy_data["text"]
        self.object.status=vacancy_data["status"]

        for skill in vacancy_data["skills"]:
            try:
                skill_obj = Skill.objects.get(name=skill)
            except Skill.DoesNotExist:
                return JsonResponse({"error": "Skill not found!"}, status=404)
            self.object.skills.add(skill_obj)

        self.object.save()

        return JsonResponse({
            "id": self.object.id,
            "text": self.object.text,
            "slug": self.object.slug,
            "status": self.object.status,
            "created": self.object.created,
            "user": self.object.user_id,
            "skills": list(self.object.skills.all().values_list("name", flat=True)),
        })


@method_decorator(csrf_exempt, name='dispatch') # отключаем проверку csrf
class VacancyDeleteView(DeleteView):
    model = Vacancy
    success_url = '/'

    def delete(self, request, *args, **kwargs):
        super().delete(request, *args, **kwargs)

        return JsonResponse({"status": "ok"}, status=200)


class UserVacancyDetailView(View):
    def get(self, request):
        # annotate - создает дополнительную колонку куда кладет результат агрегирующей функции(Count, Sum)
        user_qs = User.objects.annotate(vacancies=Count('vacancy'))

        paginator = Paginator(user_qs, settings.TOTAL_ON_PAGE)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        users = []
        for user in page_obj:
            users.append({
                "id": user.id,
                "name": user.username,
                "vacancies": user.vacancies,
            })

        response = {
            "items": users,
            "total": paginator.count,
            "num_page": paginator.num_pages,
            "avg": user_qs.aggregate(avg=Avg('vacancies'))['avg']
        }

        return JsonResponse(response, )


# # ===== КОД НАПИСАН ЧЕРЕЗ ФУНКЦИИ БЕЗ ПРИМЕНЕНИЯ ООП =====
# @csrf_exempt # отключение проверки сертификации токенов
# def index(request):
#     if request.method == "GET":
#         vacancies = Vacancy.objects.all()
#
#         search_text = request.GET.get("text", None)
#         if search_text:
#             vacancies = vacancies.filter(text=search_text)
#
#         response = []
#         for vacancy in vacancies:
#             response.append({
#                 "id": vacancy.id,
#                 "text": vacancy.text,
#             })
#
#         return JsonResponse(response, safe=False)
#     elif request.method == "POST":
#         vacancy_data = json.loads(request.body)
#         vacancy = Vacancy()
#         vacancy.text = vacancy_data["text"]
#         vacancy.save()
#         return JsonResponse({
#             "id": vacancy.pk,
#             "text": vacancy.text,
#         })
#
#
# def get(request, vacancy_id):
#     if request.method == "GET":
#         try:
#             vacancy = Vacancy.objects.get(pk=vacancy_id)
#         except Vacancy.DoesNotExist:
#             return JsonResponse({"error": "Not found"}, status=404)
#
#         return JsonResponse({
#             "id": vacancy.id,
#             "text": vacancy.text,
#         })
