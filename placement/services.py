# placement/services.py
from django.db.models import Count, Q
from courses.models import Course
from .models import PlacementChoice

def score_to_level(score: int, total: int) -> str:
    """Toplam kaç sorudan kaç doğruya göre CEFR bandı (oran bazlı)."""
    ratio = (score / max(total, 1)) * 100
    if ratio <= 20: return "A1"
    if ratio <= 40: return "A2"
    if ratio <= 60: return "B1"
    if ratio <= 80: return "B2"
    return "C1"

def evaluate_answers(answer_list):
    """
    answer_list: [{"q": <question_id>, "choice": <choice_id>}, ...]
    """
    correct = 0
    checked = 0
    choice_ids = [a.get("choice") for a in answer_list if a.get("choice")]
    if not choice_ids:
        return 0, 0
    correct_id_set = set(
        PlacementChoice.objects.filter(id__in=choice_ids, is_correct=True).values_list("id", flat=True)
    )
    for a in answer_list:
        cid = a.get("choice")
        if not cid:
            continue
        checked += 1
        if cid in correct_id_set:
            correct += 1
    return correct, checked

def recommend_courses(level: str, branch_id=None, limit=4):
    """
    İstersen sonuçla birlikte kurs önerisi döndür.
    Not: İngilizce dersleri hem 'English' hem 'İngilizce' olarak tutulabilir.
    """
    qs = Course.objects.filter(
        status__in=["OPEN","ONGOING"],
        is_active=True,
        subject__level=level
    ).filter(Q(subject__name__icontains="English") | Q(subject__name__icontains="İngilizce"))
    if branch_id:
        qs = qs.filter(branch_id=branch_id)
    return qs.order_by("start_date")[:limit]
