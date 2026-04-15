import json
import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Category, Question, Answer, QuizSession, UserAnswer, UserProfile


def home(request):
    categories = Category.objects.all()
    if request.user.is_authenticated:
        recent_sessions = QuizSession.objects.filter(
            user=request.user, status='completed'
        ).select_related('category')[:3]
    else:
        recent_sessions = []
    return render(request, 'quiz/home.html', {
        'categories': categories,
        'recent_sessions': recent_sessions,
    })


@login_required
def dashboard(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    sessions = QuizSession.objects.filter(user=request.user, status='completed').select_related('category')
    
    # Stats per category
    category_stats = {}
    for session in sessions:
        cat = session.category.name
        if cat not in category_stats:
            category_stats[cat] = {'count': 0, 'total_score': 0, 'icon': session.category.icon, 'color': session.category.color}
        category_stats[cat]['count'] += 1
        category_stats[cat]['total_score'] += session.score_percent
    
    for cat in category_stats:
        category_stats[cat]['avg_score'] = round(
            category_stats[cat]['total_score'] / category_stats[cat]['count'], 1
        )

    recent_sessions = sessions[:10]
    level, level_icon = profile.get_level()
    
    return render(request, 'quiz/dashboard.html', {
        'profile': profile,
        'sessions': recent_sessions,
        'category_stats': category_stats,
        'level': level,
        'level_icon': level_icon,
        'avg_score': profile.get_avg_score(),
    })

@login_required
def start_quiz(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    questions = list(Question.objects.filter(category=category).prefetch_related('answers'))
    
    if not questions:
        messages.error(request, 'В этой категории пока нет вопросов.')
        return redirect('home')
    
    random.shuffle(questions)
    questions = questions[:10]
    
    session = QuizSession.objects.create(
        user=request.user,
        category=category,
        total_questions=len(questions),
    )
    
    request.session[f'quiz_{session.id}_questions'] = [q.id for q in questions]
    request.session[f'quiz_{session.id}_current'] = 0
    request.session[f'quiz_{session.id}_start_time'] = timezone.now().isoformat()
    
    return redirect('quiz_question', session_id=session.id, question_num=1)


@login_required
def quiz_question(request, session_id, question_num):
    session = get_object_or_404(QuizSession, id=session_id, user=request.user)
    
    if session.status != 'in_progress':
        return redirect('quiz_result', session_id=session.id)
    
    question_ids = request.session.get(f'quiz_{session_id}_questions', [])
    if not question_ids:
        return redirect('home')
    
    if question_num < 1 or question_num > len(question_ids):
        return redirect('quiz_result', session_id=session.id)
    
    question_id = question_ids[question_num - 1]
    question = get_object_or_404(Question, id=question_id)
    answers = list(question.answers.all())
    random.shuffle(answers)
    
    return render(request, 'quiz/question.html', {
        'session': session,
        'question': question,
        'answers': answers,
        'question_num': question_num,
        'total_questions': len(question_ids),
        'progress_percent': round(((question_num - 1) / len(question_ids)) * 100),
    })


@login_required
@require_POST
def submit_answer(request, session_id):
    session = get_object_or_404(QuizSession, id=session_id, user=request.user)
    
    if session.status != 'in_progress':
        return JsonResponse({'error': 'Session not active'}, status=400)
    
    data = json.loads(request.body)
    answer_id = data.get('answer_id')
    question_id = data.get('question_id')
    question_num = data.get('question_num', 1)
    
    question = get_object_or_404(Question, id=question_id)
    answer = get_object_or_404(Answer, id=answer_id, question=question)
    correct_answer = question.answers.filter(is_correct=True).first()
    
    is_correct = answer.is_correct
    
    UserAnswer.objects.get_or_create(
        session=session,
        question=question,
        defaults={'selected_answer': answer, 'is_correct': is_correct}
    )
    
    question_ids = request.session.get(f'quiz_{session_id}_questions', [])
    next_num = question_num + 1
    is_last = next_num > len(question_ids)
    
    if is_last:
        # Complete session
        correct_count = UserAnswer.objects.filter(session=session, is_correct=True).count()
        session.correct_answers = correct_count
        session.status = 'completed'
        session.completed_at = timezone.now()
        
        start_time_str = request.session.get(f'quiz_{session_id}_start_time')
        if start_time_str:
            from datetime import datetime, timezone as dt_tz
            start_time = datetime.fromisoformat(start_time_str)
            elapsed = (timezone.now() - start_time).total_seconds()
            session.time_spent_seconds = int(elapsed)
        
        session.calculate_score()
        session.save()
        
        # Update profile
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        profile.total_quizzes += 1
        profile.total_questions += session.total_questions
        profile.total_correct += session.correct_answers
        if session.score_percent > profile.best_score:
            profile.best_score = session.score_percent
        profile.save()

    return JsonResponse({
        'is_correct': is_correct,
        'correct_answer_id': correct_answer.id if correct_answer else None,
        'explanation': question.explanation,
        'is_last': is_last,
        'next_url': f'/quiz/result/{session_id}/' if is_last else f'/quiz/{session_id}/question/{next_num}/',
    })

@login_required
def quiz_result(request, session_id):
    session = get_object_or_404(QuizSession, id=session_id, user=request.user)
    user_answers = UserAnswer.objects.filter(session=session).select_related(
        'question', 'selected_answer', 'question__category'
    ).prefetch_related('question__answers')
    
    grade, grade_color, grade_label = session.get_grade()
    
    return render(request, 'quiz/result.html', {
        'session': session,
        'user_answers': user_answers,
        'grade': grade,
        'grade_color': grade_color,
        'grade_label': grade_label,
    })

@login_required
def leaderboard(request):
    from django.db.models import Count, Avg
    top_users = UserProfile.objects.select_related('user').order_by('-best_score', '-total_quizzes')[:20]
    return render(request, 'quiz/leaderboard.html', {'top_users': top_users})
