# ====================================================================
# НЕЙРОМЕРЕЖА З НУЛЯ ДЛЯ ДИСКРЕТНОЇ МАТЕМАТИКИ: ПОВНИЙ СУМАТОР (FULL ADDER)
# ====================================================================
# Цей скрипт демонструє застосування нейронних мереж до фундаментальної 
# задачі дискретної математики та математичної логіки — моделювання 
# роботи цифрового суматора, який виконує додавання трьох бінарних розрядів.
#
# Повний суматор має:
# - 3 входи: A, B та Carry-in (перенесення з попереднього розряду)
# - 2 виходи: Sum (сума) та Carry-out (перенесення в наступний розряд)
#
# Це класична нелінійна задача булевої алгебри, що вимагає апроксимації
# дискретних логічних функцій за допомогою безперервної сигмоїди.

using Random

# 1. Допоміжні математичні функції
sigmoid(x) = 1.0 ./ (1.0 .+ exp.(.-x))
sigmoid_derivative(a) = a .* (1.0 .- a)

# 2. Структура нейромережі
mutable struct DiscreteMathNN
    W1::Matrix{Float64} # Ваги: прихований шар (hidden_size x input_size)
    b1::Vector{Float64} # Зсуви прихованого шару
    W2::Matrix{Float64} # Ваги: вихідний шар (output_size x hidden_size)
    b2::Vector{Float64} # Зсуви вихідного шару
end

# Ініціалізація ваг за методом Ксав'є (Xavier)
function initialize_network(input_size, hidden_size, output_size)
    Random.seed!(101) # фіксований seed для стабільного результату навчання
    
    val1 = sqrt(2.0 / (input_size + hidden_size))
    val2 = sqrt(2.0 / (hidden_size + output_size))
    
    W1 = (rand(hidden_size, input_size) .- 0.5) .* (2.0 * val1)
    b1 = zeros(hidden_size)
    W2 = (rand(output_size, hidden_size) .- 0.5) .* (2.0 * val2)
    b2 = zeros(output_size)
    
    return DiscreteMathNN(W1, b1, W2, b2)
end

# Пряме поширення (Forward Pass)
function forward_pass(nn::DiscreteMathNN, X::Matrix{Float64})
    z1 = nn.W1 * X .+ nn.b1
    a1 = sigmoid(z1)
    z2 = nn.W2 * a1 .+ nn.b2
    a2 = sigmoid(z2)
    return a1, a2
end

# Функція згасання швидкості навчання (Learning Rate Decay)
function get_lr(lr_init, epoch, decay_rate)
    return lr_init / (1.0 + decay_rate * epoch)
end

# 3. Навчання моделі
function train!(nn::DiscreteMathNN, X::Matrix{Float64}, y::Matrix{Float64}; 
                epochs=25000, lr_init=0.3, decay_rate=0.0001)
    m = size(X, 2) # розмір вибірки (8 станів таблиці істинності)
    
    println("=== НАВЧАННЯ НЕЙРОМЕРЕЖІ ДЛЯ ПОВНОГО СУМАТОРА ===")
    println("Конфігурація: Вхід (3) -> Прихований шар (6) -> Вихід (2)")
    println("Початкова швидкість навчання (LR): $lr_init, згасання: $decay_rate\n")
    
    for epoch in 1:epochs
        # Пряме поширення
        a1, a2 = forward_pass(nn, X)
        
        # Розрахунок похибки (Mean Squared Error)
        loss = sum((a2 .- y).^2) / m
        
        # Отримання поточної адаптивної швидкості навчання
        lr = get_lr(lr_init, epoch, decay_rate)
        
        # Зворотне поширення (Backpropagation)
        error_output = a2 .- y
        delta2 = error_output .* sigmoid_derivative(a2)
        
        error_hidden = nn.W2' * delta2
        delta1 = error_hidden .* sigmoid_derivative(a1)
        
        # Обчислення градієнтів
        dW2 = (delta2 * a1') ./ m
        db2 = sum(delta2, dims=2) ./ m
        dW1 = (delta1 * X') ./ m
        db1 = sum(delta1, dims=2) ./ m
        
        # Оновлення ваг
        nn.W2 .-= lr .* dW2
        nn.b2 .-= lr .* vec(db2)
        nn.W1 .-= lr .* dW1
        nn.b1 .-= lr .* vec(db1)
        
        # Логування прогресу
        if epoch % 5000 == 0 || epoch == 1
            println("Епоха $(lpad(epoch, 5)): Loss (MSE) = $(round(loss, digits=6)) | Поточний LR = $(round(lr, digits=5))")
        end
    end
    println("\n=== НАВЧАННЯ ЗАВЕРШЕНО ===\n")
end

# 4. Вхідні дані: Таблиця істинності повного суматора
# Стовпчики матриці — це 8 можливих комбінацій вхідних сигналів: [A, B, Cin]'
X_train = [
    0.0  0.0  0.0  0.0  1.0  1.0  1.0  1.0; # Вхід A
    0.0  0.0  1.0  1.0  0.0  0.0  1.0  1.0; # Вхід B
    0.0  1.0  0.0  1.0  0.0  1.0  0.0  1.0  # Перенесення Cin
]

# Очікувані дискретні виходи: [Sum, Cout]'
y_train = [
    0.0  1.0  1.0  0.0  1.0  0.0  0.0  1.0; # Вихід Sum (S = A ⊕ B ⊕ Cin)
    0.0  0.0  0.0  1.0  0.0  1.0  1.0  1.0  # Вихід Cout (Cout = (A*B) + (Cin*(A ⊕ B)))
]

# Ініціалізація мережі: 
# 3 входи, 6 нейронів у прихованому шарі (для вивчення складних XOR-зв'язків), 2 виходи
nn_adder = initialize_network(3, 6, 2)

# Запуск навчання (25 000 епох для високої точності класифікації дискретних значень)
train!(nn_adder, X_train, y_train, epochs=25000, lr_init=0.4, decay_rate=0.00005)

# 5. Тестування та верифікація таблиці істинності
_, predictions = forward_pass(nn_adder, X_train)

# Функція для гарного форматування бінарних сигналів
bin_format(val) = val > 0.5 ? "1" : "0"

println("ТАБЛИЦЯ ІСТИННОСТІ ТА ПЕРЕДБАЧЕННЯ НЕЙРОМЕРЕЖІ:")
println("-"^75)
println("Входи: [A, B, Cin] | Очікувано: [Sum, Cout] | Прогноз мережі (Аналог -> Дискрет)")
println("-"^75)
for i in 1:8
    input_vals = Int.(X_train[:, i])
    targets = Int.(y_train[:, i])
    raw_preds = predictions[:, i]
    
    # Конвертуємо аналогові виходи сигмоїди [0..1] у дискретні значення {0, 1}
    binary_preds = [raw_preds[1] > 0.5 ? 1 : 0, raw_preds[2] > 0.5 ? 1 : 0]
    
    # Визначаємо, чи правильне передбачення
    status = (targets == binary_preds) ? "✅ УСПІХ" : "❌ ПОМИЛКА"
    
    # Красиве виведення результату
    println(
        "Вхід: $input_vals     | " *
        "Ціль: $targets         | " *
        "Raw: [$(round(raw_preds[1], digits=3)), $(round(raw_preds[2], digits=3))] " *
        "-> $binary_preds | $status"
    )
end
println("-"^75)
