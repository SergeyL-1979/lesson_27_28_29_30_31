from datetime import date

import pytest

from tests.factories import VacancyFactory
# === первый вариант теста =======
from vacancies.models import Vacancy
from vacancies.serializers import VacancyListSerializer


@pytest.mark.django_db
# ==== Тестирования одной записи ====
# def test_vacancy_list(client, vacancy):
# ==== Тестирование нескольких записей ====
def test_vacancy_list(client):
    vacancies = VacancyFactory.create_batch(10)

    # === первый вариант теста =======
    # vacancy = Vacancy.objects.create(
    #     slug="123",
    #     text="123"
    # )

    expected_response = {
        "count": 10,
        "next": None,
        "previous": None,
        "results": VacancyListSerializer(vacancies, many=True).data
        # "results": [{
        #     "id": vacancy.pk,
        #     "text": "test text",
        #     "slug": "test",
        #     "status": "draft",
        #     "created": date.today().strftime("%Y-%m-%d"),
        #     "username": "testuser",
        #     "skills": [],
        # }]
    }

    response = client.get("/vacancy/")

    assert response.status_code == 200
    assert response.data == expected_response

