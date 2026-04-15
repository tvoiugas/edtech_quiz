from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='💻')
    color = models.CharField(max_length=20, default='#6366f1')
    difficulty_label = models.CharField(max_length=50, default='Mixed')

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def str(self):
        return self.name

    def get_question_count(self):
        return self.questions.count()


class Question(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    explanation = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def str(self):
        return f"{self.category.name}: {self.text[:60]}"


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def str(self):
        return f"{'✓' if self.is_correct else '✗'} {self.text[:40]}"


class QuizSession(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_sessions')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    total_questions = models.PositiveIntegerField(default=0)
    correct_answers = models.PositiveIntegerField(default=0)
    time_spent_seconds = models.PositiveIntegerField(default=0)
    score_percent = models.FloatField(default=0)

    class Meta:
        ordering = ['-started_at']

    def str(self):
        return f"{self.user.username} - {self.category.name} ({self.status})"

    def calculate_score(self):
        if self.total_questions > 0:
            self.score_percent = round((self.correct_answers / self.total_questions) * 100, 1)
        return self.score_percent

    def get_grade(self):
        score = self.score_percent
        if score >= 90:
            return 'S', '#10b981', 'Отлично!'
        elif score >= 75:
            return 'A', '#6366f1', 'Хорошо!'
        elif score >= 60:
            return 'B', '#f59e0b', 'Неплохо'
        elif score >= 40:
            return 'C', '#f97316', 'Слабо'
        else:
            return 'D', '#ef4444', 'Нужно учиться!'

    def get_time_display(self):
        minutes = self.time_spent_seconds // 60
        seconds = self.time_spent_seconds % 60
        if minutes > 0:
            return f"{minutes}м {seconds}с"
        return f"{seconds}с"


class UserAnswer(models.Model):
    session = models.ForeignKey(QuizSession, on_delete=models.CASCADE, related_name='user_answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.ForeignKey(Answer, on_delete=models.CASCADE, null=True, blank=True)
    is_correct = models.BooleanField(default=False)
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['session', 'question']


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar_color = models.CharField(max_length=20, default='#6366f1')
    bio = models.TextField(blank=True, max_length=200)
    github_url = models.URLField(blank=True)
    total_quizzes = models.PositiveIntegerField(default=0)
    total_correct = models.PositiveIntegerField(default=0)
    total_questions = models.PositiveIntegerField(default=0)
    best_score = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def str(self):
        return f"Profile: {self.user.username}"

    def get_avg_score(self):
        if self.total_questions > 0:
            return round((self.total_correct / self.total_questions) * 100, 1)
        return 0

    def get_level(self):
        quizzes = self.total_quizzes
        if quizzes >= 50:
            return 'Expert', '⚡️'
        elif quizzes >= 20:
            return 'Advanced', '🔥'
        elif quizzes >= 10:
            return 'Intermediate', '💡'
        elif quizzes >= 3:
            return 'Beginner', '🌱'
        return 'Новичок', '🐣'

