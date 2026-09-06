# ====================================================================
# НЕЙРОМЕРЕЖА З НУЛЯ НА МОВІ JULIA (Рішення задачі XOR) - Версія 2.0
# ====================================================================
# Додано можливість динамічної зміни швидкості навчання (Learning Rate Decay)
# без використання сторонніх бібліотек.

using Random

# 1. Допоміжні математичні функції
# Функція активації Sigmoid та її похідна
sigmoid(x) = 1.0 ./ (1.0 .+ exp.(.-x))
sigmoid_derivative(a) = a .* (1.0 .- a) # де 'a' - це вже активоване значення sigmoid(x)

# 2. Архітектура та ініціалізація параметрів
mutable struct NeuralNetwork
    W1::Matrix{Float64} # Ваги між вхідним та прихованим шаром (hidden_size x input_size)
    b1::Vector{Float64} # Зсуви прихованого шару (hidden_size)
    W2::Matrix{Float64} # Ваги між прихованим та вихідним шаром (output_size x hidden_size)
    b2::Vector{Float64} # Зсуви вихідного шару (output_size)
end

function initialize_network(input_size, hidden_size, output_size)
    Random.seed!(42) # фіксуємо випадковість для відтворюваності
    
    # Ініціалізація Ксав'є (Xavier initialization) для стабільного навчання
    val1 = sqrt(2.0 / (input_size + hidden_size))
    val2 = sqrt(2.0 / (hidden_size + output_size))
    
    W1 = (rand(hidden_size, input_size) .- 0.5) .* (2.0 * val1)
    b1 = zeros(hidden_size)
    W2 = (rand(output_size, hidden_size) .- 0.5) .* (2.0 * val2)
    b2 = zeros(output_size)
    
    return NeuralNetwork(W1, b1, W2, b2)
end

# 3. Пряме поширення (Forward Pass)
function forward_pass(nn::NeuralNetwork, X::Matrix{Float64})
    # Вхідні дані X мають розмірність (input_size x batch_size)
    z1 = nn.W1 * X .+ nn.b1
    a1 = sigmoid(z1)
    z2 = nn.W2 * a1 .+ nn.b2
    a2 = sigmoid(z2)
    return a1, a2
end

# 4. Функція розрахунку поточної швидкості навчання (Learning Rate Scheduler)
function get_current_lr(lr_init, epoch, decay_type, decay_rate, step_size, step_factor)
    if decay_type == :none
        return lr_init
    elseif decay_type == :inverse
        # Зворотне згасання за часом (Inverse Time Decay): lr_init / (1 + decay_rate * epoch)
        return lr_init / (1.0 + decay_rate * epoch)
    elseif decay_type == :exponential
        # Експоненціальне згасання (Exponential Decay): lr_init * e^(-decay_rate * epoch)
        return lr_init * exp(-decay_rate * epoch)
    elseif decay_type == :step
        # Ступінчасте згасання (Step Decay): зменшується на step_factor кожні step_size епох
        num_steps = floor(epoch / step_size)
        return lr_init * (step_factor ^ num_steps)
    else
        return lr_init
    end
end

# 5. Навчання за допомогою Backpropagation (Зворотного поширення помилки)
function train!(nn::NeuralNetwork, X::Matrix{Float64}, y::Matrix{Float64}; 
                epochs=10000, 
                lr_init=0.5,                  # Початкова швидкість навчання
                decay_type=:inverse,          # Тип згасання: :none, :inverse, :exponential, :step
                decay_rate=0.0002,            # Коефіцієнт згасання (для :inverse та :exponential)
                step_size=2500,               # Крок зниження швидкості (для :step)
                step_factor=0.5)              # Множник зниження швидкості (для :step)
    
    m = size(X, 2) # Кількість прикладів у навчальній вибірці (batch_size)
    
    println("--- Початок навчання нейромережі (Версія 2.0 з LR Decay) ---")
    println("Конфігурація оптимізатора:")
    println("  - Початковий LR (lr_init):  $lr_init")
    println("  - Режим згасання (decay_type): $decay_type")
    if decay_type in (:inverse, :exponential)
        println("  - Коефіцієнт згасання (decay_rate): $decay_rate")
    elseif decay_type == :step
        println("  - Зменшення в $step_factor рази кожні $step_size епох")
    end
    println("-"^60)
    
    for epoch in 1:epochs
        # Пряме поширення
        a1, a2 = forward_pass(nn, X)
        
        # Обчислення похибки на виході (Mean Squared Error Loss)
        loss = sum((a2 .- y).^2) / m
        
        # Розрахунок поточної швидкості навчання для цієї епохи
        lr = get_current_lr(lr_init, epoch, decay_type, decay_rate, step_size, step_factor)
        
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
        
        # Оновлення параметрів (Градієнтний спуск з поточним lr)
        nn.W2 .-= lr .* dW2
        nn.b2 .-= lr .* vec(db2)
        nn.W1 .-= lr .* dW1
        nn.b1 .-= lr .* vec(db1)
        
        # Логування кожні 1000 епох
        if epoch % 1000 == 0 || epoch == 1
            println("Епоха $epoch: Помилка (Loss) = $(round(loss, digits=6)) | Поточний LR = $(round(lr, digits=6))")
        end
    end
    println("--- Навчання завершено --- \n")
end

# 6. Демонстрація роботи програми з різними режимами згасання швидкості навчання
X_train = [
    0.0 0.0 1.0 1.0;
    0.0 1.0 0.0 1.0
]
y_train = [0.0 1.0 1.0 0.0]

# --- Сценарій 1: Зворотне згасання за часом (:inverse) ---
println("=== СЦЕНАРІЙ 1: Зворотне згасання за часом (Inverse Time Decay) ===")
nn_inverse = initialize_network(2, 3, 1)
train!(nn_inverse, X_train, y_train, epochs=10000, lr_init=0.5, decay_type=:inverse, decay_rate=0.0001)

_, predictions_inverse = forward_pass(nn_inverse, X_train)
println("Результати для Сценарію 1:")
for i in 1:4
    println("  Вхід: $(X_train[:, i]) | Очікувано: $(y_train[1, i]) | Передбачено: $(round(predictions_inverse[1, i], digits=4))")
end
println("\n" * "="^60 * "\n")

# --- Сценарій 2: Ступінчасте згасання (:step) ---
println("=== СЦЕНАРІЙ 2: Ступінчасте згасання (Step Decay) ===")
nn_step = initialize_network(2, 3, 1)
# Починаємо з вищої швидкості навчання (lr_init=1.0) та зменшуємо її вдвічі кожні 2500 епох
train!(nn_step, X_train, y_train, epochs=10000, lr_init=1.0, decay_type=:step, step_size=2500, step_factor=0.5)

_, predictions_step = forward_pass(nn_step, X_train)
println("Результати для Сценарію 2:")
for i in 1:4
    println("  Вхід: $(X_train[:, i]) | Очікувано: $(y_train[1, i]) | Передбачено: $(round(predictions_step[1, i], digits=4))")
end
