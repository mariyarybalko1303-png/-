using Random

# 1. Генерація синтетичних даних для навчання
# Створимо залежність виду: y = 2 * X + 1 + випадковий шум
Random.seed!(42) # фіксуємо випадковість для відтворюваності

X = rand(100) .* 10                 # 100 випадкових точок у діапазоні [0, 10]
y = 2.0 .* X .+ 1.0 .+ randn(100) .* 0.5 # цільова змінна з додаванням шуму

# 2. Функція передбачення: h(x) = w * x + b
# Крапка перед операторами (.* та .+) означає "broadcasting" — 
# операція застосовується до кожного елемента вектора автоматично.
predict(X, w, b) = w .* X .+ b

# 3. Функція помилки (Mean Squared Error - MSE)
function compute_loss(X, y, w, b)
    predictions = predict(X, w, b)
    return sum((predictions .- y).^2) / (2 * length(y))
end

# 4. Градієнтний спуск для оптимізації параметрів w (вага) та b (зсув)
function train_linear_regression(X, y; epochs=500, lr=0.01)
    m = length(y)
    
    # Ініціалізуємо параметри нулями
    w = 0.0
    b = 0.0
    
    println("--- Початок навчання лінійної регресії ---")
    
    for epoch in 1:epochs
        predictions = predict(X, w, b)
        errors = predictions .- y
        
        # Обчислення часткових похідних (градієнтів)
        dw = sum(errors .* X) / m
        db = sum(errors) / m
        
        # Оновлення параметрів у напрямку, протилежному градієнту
        w -= lr * dw
        b -= lr * db
        
        # Виводимо проміжний прогрес кожні 100 епох
        if epoch % 100 == 0 || epoch == 1
            loss = compute_loss(X, y, w, b)
            println("Епоха $epoch: w = $(round(w, digits=4)), b = $(round(b, digits=4)), Помилка (Loss) = $(round(loss, digits=4))")
        end
    end
    
    return w, b
end

# 5. Запуск алгоритму навчання
final_w, final_b = train_linear_regression(X, y, epochs=500, lr=0.01)

println("\n--- Результати навчання ---")
println("Справжня формула:  y = 2.0 * x + 1.0")
println("Знайдена формула: y = $(round(final_w, digits=3)) * x + $(round(final_b, digits=3))")