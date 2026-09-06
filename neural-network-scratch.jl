# ====================================================================
# НЕЙРОМЕРЕЖА З НУЛЯ НА МОВІ JULIA (Рішення задачі XOR)
# ====================================================================
# Цей скрипт демонструє реалізацію повнозв'язної нейромережі
# без використання зовнішніх бібліотек машинного навчання.
# Використовується лише вбудована лінійна алгебра Julia.

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
    
    # Обчислення для прихованого шару
    z1 = nn.W1 * X .+ nn.b1
    a1 = sigmoid(z1)
    
    # Обчислення для вихідного шару
    z2 = nn.W2 * a1 .+ nn.b2
    a2 = sigmoid(z2)
    
    return a1, a2
end

# 4. Навчання за допомогою Backpropagation (Зворотного поширення помилки)
function train!(nn::NeuralNetwork, X::Matrix{Float64}, y::Matrix{Float64}; epochs=10000, lr=0.1)
    m = size(X, 2) # Кількість прикладів у навчальній вибірці (batch_size)
    
    println("--- Початок навчання нейромережі з нуля ---")
    
    for epoch in 1:epochs
        # Пряме поширення
        a1, a2 = forward_pass(nn, X)
        
        # Обчислення похибки на виході (Mean Squared Error Loss)
        loss = sum((a2 .- y).^2) / m
        
        # Зворотне поширення (Backpropagation)
        # Помилка на вихідному шарі
        error_output = a2 .- y
        delta2 = error_output .* sigmoid_derivative(a2)
        
        # Помилка на прихованому шарі
        error_hidden = nn.W2' * delta2
        delta1 = error_hidden .* sigmoid_derivative(a1)
        
        # Обчислення градієнтів
        dW2 = (delta2 * a1') ./ m
        db2 = sum(delta2, dims=2) ./ m
        dW1 = (delta1 * X') ./ m
        db1 = sum(delta1, dims=2) ./ m
        
        # Оновлення параметрів (Градієнтний спуск)
        nn.W2 .-= lr .* dW2
        nn.b2 .-= lr .* vec(db2)
        nn.W1 .-= lr .* dW1
        nn.b1 .-= lr .* vec(db1)
        
        # Логування кожні 1000 епох
        if epoch % 1000 == 0 || epoch == 1
            println("Епоха $epoch: Помилка (MSE Loss) = $(round(loss, digits=6))")
        end
    end
    println("--- Навчання завершено --- \n")
end

# 5. Демонстрація роботи програми
# Вхідні дані для XOR: 4 приклади, кожен має 2 ознаки
# Розмірність: (input_size x batch_size) -> (2 x 4)
X_train = [
    0.0 0.0 1.0 1.0;
    0.0 1.0 0.0 1.0
]

# Очікувані виходи XOR
# Розмірність: (output_size x batch_size) -> (1 x 4)
y_train = [0.0 1.0 1.0 0.0]

# Створення моделі: 2 входи, 3 приховані нейрони, 1 вихідний нейрон
nn = initialize_network(2, 3, 1)

# Навчання мережі
train!(nn, X_train, y_train, epochs=10000, lr=0.2)

# Тестування результатів
_, predictions = forward_pass(nn, X_train)

println("Результати передбачень для XOR:")
for i in 1:4
    input_val = X_train[:, i]
    target_val = y_train[1, i]
    pred_val = predictions[1, i]
    println("Вхід: $(input_val) | Очікувано: $target_val | Передбачено: $(round(pred_val, digits=4))")
end
