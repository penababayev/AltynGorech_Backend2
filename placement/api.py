# placement/api.py
import random, hashlib
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Q

from .models import PlacementQuestion, PlacementTestResult, PlacementChoice
from .serializers import PlacementQuestionOut
from .services import evaluate_answers, score_to_level, recommend_courses

VALID_SKILLS = {"grammar", "vocab", "reading", "listening"}

@api_view(["GET"])
@permission_classes([AllowAny])
def get_questions(request):
    """
    Public endpoint: rastgele aktif sorular.
    Query:
      - limit (default 20)
      - mix (comma): grammar,vocab,reading,listening
    Kriter: >=2 şık + >=1 doğru şık.
    """
    limit = int(request.GET.get("limit", 20))
    skills_raw = request.GET.get("mix", "grammar,vocab,reading").split(",")
    skills = [s.strip().lower() for s in skills_raw if s.strip()]
    valid = {"grammar","vocab","reading","listening"}
    skills = [s for s in skills if s in valid] or ["grammar","vocab","reading"]

    qs = (
        PlacementQuestion.objects
        .filter(is_active=True, skill__in=skills)
        .annotate(
            num_choices=Count("choices"),
            num_correct=Count("choices", filter=Q(choices__is_correct=True)),
        )
        .filter(num_choices__gte=2, num_correct__gte=1)
        .distinct()
    )

    # Fallback: sıkı filtrede soru yoksa, doğru-şık şartını esnet
    if not qs.exists():
        qs = (
            PlacementQuestion.objects
            .filter(is_active=True, skill__in=skills)
            .annotate(num_choices=Count("choices"))
            .filter(num_choices__gte=2)
            .distinct()
        )

    items = list(qs)
    random.shuffle(items)
    items = items[:limit]

    data = PlacementQuestionOut(items, many=True).data
    for q in data:
        random.shuffle(q["choices"])
    return Response({"questions": data})


@api_view(["POST"])
@permission_classes([AllowAny])
def submit(request):
    """
    Body:
    {
      "answers": [{"q": <question_id>, "choice": <choice_id>}, ...],
      "email": "optional@x.com",
      "branch_id": 1   # opsiyonel, kurs öneri filtresi
    }
    """
    payload = request.data or {}
    answers = payload.get("answers", [])
    email   = (payload.get("email") or "").strip()
    branch_id = payload.get("branch_id")

    if not isinstance(answers, list) or not answers:
        return Response({"detail": "answers list required"}, status=status.HTTP_400_BAD_REQUEST)

    # Puanla
    correct, checked = evaluate_answers(answers)
    level = score_to_level(correct, checked)

    # Beceri kırılımı
    q_ids = [a.get("q") for a in answers if a.get("q")]
    q_map = {q.id: q for q in PlacementQuestion.objects.filter(id__in=q_ids)}
    breakdown = {}
    # doğru seti
    correct_ids = set(PlacementChoice.objects.filter(
        id__in=[a.get("choice") for a in answers if a.get("choice")], is_correct=True
    ).values_list("id", flat=True))
    for a in answers:
        q = q_map.get(a.get("q"))
        if not q: continue
        k = q.skill
        breakdown.setdefault(k, {"correct":0, "total":0})
        breakdown[k]["total"] += 1
        if a.get("choice") in correct_ids:
            breakdown[k]["correct"] += 1

    # Kurs önerisi (opsiyonel)
    recos = recommend_courses(level=level, branch_id=branch_id)
    recos_out = [{
        "id": c.id,
        "title": str(c),
        "start_date": c.start_date,
        "branch": str(c.branch) if c.branch_id else "",
        "status": c.status
    } for c in recos]

    # Sonucu kaydet (lead/istatistik)
    ip = request.META.get("REMOTE_ADDR","")
    ip_hash = hashlib.sha256(ip.encode("utf-8")).hexdigest()[:24]
    res = PlacementTestResult.objects.create(
        email=email,
        total_score=correct,
        estimated_level=level,
        raw_payload={"answers": answers},
        ua=request.META.get("HTTP_USER_AGENT","")[:200],
        ip_hash=ip_hash,
        skill_breakdown=breakdown,
    )

    return Response({
        "score": correct,
        "total": checked,
        "level": level,
        "recommended_courses": recos_out,
        "result_id": res.id,
        "breakdown": breakdown,
    })


# Soru çek:
# GET /api/placement/questions?limit=10&mix=grammar,vocab,reading

# Cevap gönder:
# POST /api/placement/submit