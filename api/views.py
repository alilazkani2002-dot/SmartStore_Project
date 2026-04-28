from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
import pandas as pd
import numpy as np
import random
from pathlib import Path

# =========================
# تحميل ملفات Excel مرة واحدة فقط
# =========================

BASE_DIR = Path(__file__).resolve().parent.parent

products_df = pd.read_excel(BASE_DIR / "products.xlsx")
ratings_df = pd.read_excel(BASE_DIR / "ratings.xlsx")
users_df = pd.read_excel(BASE_DIR / "users.xlsx")
behavior_df = pd.read_excel(BASE_DIR / "behavior.xlsx")


# =========================
# 1) صفحة رئيسية بسيطة
# =========================
def home(request):
    return HttpResponse("<h1>Smart Store Recommendation API (Genetic Algorithm)</h1>")


# =========================
# 2) API: المنتجات
# =========================
@api_view(['GET'])
def get_products(request):
    return Response(products_df.to_dict(orient="records"))


# =========================
# 3) API: المستخدمين
# =========================
@api_view(['GET'])
def users_list(request):
    return Response(users_df.to_dict(orient="records"))


# =========================
# 4) API: تسجيل السلوك
# =========================
@api_view(['POST'])
def log_behavior(request):
    data = request.data
    print("Behavior Logged:", data)
    return Response({"status": "ok"})


# =========================
# 5) الخوارزمية الجينية
# =========================

def build_population(pop_size, length, products_df):
    all_ids = products_df['product_id'].tolist()
    return [random.sample(all_ids, length) for _ in range(pop_size)]


def fitness_function(chromosome, user_id, products_df, ratings_df, behavior_df):
    score = 0

    user_behavior = behavior_df[behavior_df['user_id'] == user_id]
    user_ratings = ratings_df[ratings_df['user_id'] == user_id]

    # الفئات المفضلة
    if not user_behavior.empty:
        merged = user_behavior.merge(products_df, on='product_id', how='left')
        fav_cats = merged['category'].value_counts().to_dict()
    else:
        fav_cats = {}

    seen_products = set(user_behavior['product_id'].tolist())

    for pid in chromosome:
        row = products_df[products_df['product_id'] == pid]
        if row.empty:
            continue

        category = row.iloc[0]['category']
        price = row.iloc[0]['price']

        # 1) مكافأة الفئات المفضلة
        if category in fav_cats:
            score += 2 * fav_cats[category]

        # 2) مكافأة المنتجات الجديدة
        if pid not in seen_products:
            score += 1.5

        # 3) مكافأة التقييمات
        r = user_ratings[user_ratings['product_id'].astype(str) == str(pid)]
        if not r.empty:
            score += r.iloc[0]['rating']

        # 4)   للسعر العالي
        if price > products_df['price'].mean():
            score -= 0.5

    return score


def selection(population, fitnesses, k=3):
    selected = random.sample(list(zip(population, fitnesses)), k)
    selected.sort(key=lambda x: x[1], reverse=True)
    return selected[0][0]


def crossover(p1, p2):
    cut = random.randint(1, len(p1) - 2)
    child = p1[:cut] + [x for x in p2 if x not in p1[:cut]]
    return child[:len(p1)]


def mutate(chromosome, products_df, rate=0.1):
    all_ids = products_df['product_id'].tolist()
    for i in range(len(chromosome)):
        if random.random() < rate:
            chromosome[i] = random.choice(all_ids)
    return chromosome


def run_genetic_algorithm(user_id, products_df, users_df, ratings_df, behavior_df,
                          pop_size=8, length=5, generations=10):


    population = build_population(pop_size, length, products_df)

    for _ in range(generations):
        fitnesses = [
            fitness_function(ch, user_id, products_df, ratings_df, behavior_df)
            for ch in population
        ]

        new_population = []

        # elitism
        best_idx = int(np.argmax(fitnesses))
        new_population.append(population[best_idx])

        while len(new_population) < pop_size:
            p1 = selection(population, fitnesses)
            p2 = selection(population, fitnesses)
            child = crossover(p1, p2)
            child = mutate(child, products_df)
            new_population.append(child)

        population = new_population

    final_fitnesses = [
        fitness_function(ch, user_id, products_df, ratings_df, behavior_df)
        for ch in population
    ]
    best_idx = int(np.argmax(final_fitnesses))
    return population[best_idx]


# =========================
# 6) API: التوصيات
# =========================
@api_view(['GET'])
def get_recommendations(request, user_id):

    # لو المستخدم غير موجود يرجع منتجات عشوائية
    if user_id not in users_df['user_id'].values:
        return Response(products_df.sample(5).to_dict(orient="records"))

    best = run_genetic_algorithm(
        user_id, products_df, users_df, ratings_df, behavior_df
    )

    rec_df = products_df[products_df['product_id'].isin(best)]
    return Response(rec_df.to_dict(orient="records"))
