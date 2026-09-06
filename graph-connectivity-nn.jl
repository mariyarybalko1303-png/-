# ====================================================================
# НЕЙРОМЕРЕЖА ДЛЯ ВИЗНАЧЕННЯ ЗВ'ЯЗНОСТІ ГРАФІВ (З НУЛЯ НА JULIA)
# ====================================================================
# Цей скрипт демонструє застосування глибокого навчання до задач
# дискретної математики та теорії графів. 
# Ми навчимо нейромережу визначати, чи є ненапрямлений граф зв'язним,
# використовуючи його матрицю суміжності як вхідні дані.

using Random

# --------------------------------------------------------------------
# 1. Допоміжні функції для дискретної математики та теорії графів
# --------------------------------------------------------------------

# Алгоритм пошуку в ширину (BFS) для точного визначення зв'язності графа.
# Використовується для автоматичної генерації міток (labels) для навчання.
function is_graph_connected(adj::Matrix{Float64})
    n = size(adj, 1)
    visited = zeros(Bool, n)
    
    # Починаємо обхід з першої вершини
    queue = [1]
    visited[1] = true
    head = 1
    
    while head <= length(queue)
        curr = queue[head]
        head += 1
        for neighbor in 1:n
            if adj[curr, neighbor] == 1.0 && !visited[neighbor]
                visited[neighbor] = true
                push!(queue, neighbor)
            end
        end
    end
    
    return all(visited)
end

# Генерація повного набору даних (dataset) для 4-вершинних графів.
# Для 4 вершин існує 6 потенційних ребер: (1,2), (1,3), (1,4), (2,3), (2,4), (3,4).
# Це дає нам 2^6 = 64 можливі комбінації ненапрямлених графів.
function generate_graph_dataset()
    X = Matrix{Float64}(undef, 16, 64) # 16 вхідних ознак (сплющена матриця суміжності 4x4)
    y = Matrix{Float64}(undef, 1, 64)  # 1 вихідна ознака (1 - зв'язний, 0 - незв'язний)
    
    # Список незалежних ребер у верхній трикутній матриці суміжності
    edges = [
        (1, 2), (1, 3), (1, 4),
        (2, 3), (2, 4),
        (3, 4)
    ]
    
    for i in 0:63
        adj = zeros(Float64, 4, 4)
        # Розподіляємо ребра відповідно до бінарного представлення числа i (від 0 до 63)
        for e_idx in 1:6
            if (i >> (e_idx - 1)) & 1 == 1
                u, v = edges[e_idx]
                adj[u, v] = 1.0
                adj[v, u] = 1.0 # граф ненапрямлений, тому матриця симетрична
            end
        end
        
        X[:, i+1] = vec(adj) # Сплющуємо матрицю 4x4 у вектор довжиною 16
        y[1, i+1] = is_graph_connected(adj) ? 1.0 : 0.0
    end
    
    return X, y
end

# --------------------------------------------------------------------
# 2. Математичний базис нейромережі
# --------------------------------------------------------------------

sigmoid(x) = 1.0 ./ (1.0 .+ exp.(.-x))
sigmoid_derivative(a) = a .* (1.0 .- a)

# --------------------------------------------------------------------
# 3. Структура нейромережі
# --------------------------------------------------------------------

mutable struct GraphNeuralNetwork
    W1::Matrix{Float64} # Ваги прихованого шару (hidden_size x 16)
    b1::Vector{Float64} # Зсуви прихованого шару (hidden_size)
    W2::Matrix{Float64} # Ваги вихідного шару (1 x hidden_size)
    b2::Vector{Float64} # Зсув вихідного шару (1)
end

function initialize_network(input_size, hidden_size, output_size)
    Random.seed!(123) # Фіксуємо випадковість
    
    # Ініціалізація Ксав'є
    val1 = sqrt(2.0 / (input_size + hidden_size))
    val2 = sqrt(2.0 / (hidden_size + output_size))
    
    W1 = (rand(hidden_size, input_size) .- 0.5) .* (2.0 * val1)
    b1 = zeros(hidden_size)
    W2 = (rand(output_size, hidden_size) .- 0.5) .* (2.0 * val2)
    b2 = zeros(output_size)
    
    return GraphNeuralNetwork(W1, b1, W2, b2)
end

function forward_pass(gnn::GraphNeuralNetwork, X::Matrix{Float64})
    z1 = gnn.W1 * X .+ gnn.b1
    a1 = sigmoid(z1)
    
    z2 = gnn.W2 * a1 .+ gnn.b2
    a2 = sigmoid(z2)
    
    return a1, a2
end

# --------------------------------------------------------------------
# 4. Процес навчання з планувальником швидкості навчання (LR Decay)
# --------------------------------------------------------------------

function train_gnn!(gnn::GraphNeuralNetwork, X::Matrix{Float64}, y::Matrix{Float64}; 
                    epochs=15000, lr_init=0.5, decay_rate=0.0001)
    m = size(X, 2)
    
    println("--- Початок навчання нейромережі на графах ---")
    println("Розмір вибірки: $m унікальних графів")
    println("Кількість зв'язних графів у вибірці: $(Int(sum(y))) з $m\n")
    
    for epoch in 1:epochs
        # Динамічний розрахунок швидкості навчання (Inverse time decay)
        lr = lr_init / (1.0 + decay_rate * epoch)
        
        # Прямий хід
        a1, a2 = forward_pass(gnn, X)
        
        # Розрахунок помилки (MSE Loss)
        loss = sum((a2 .- y).^2) / m
        
        # Зворотне поширення помилки (Backpropagation)
        error_output = a2 .- y
        delta2 = error_output .* sigmoid_derivative(a2)
        
        error_hidden = gnn.W2' * delta2
        delta1 = error_hidden .* sigmoid_derivative(a1)
        
        dW2 = (delta2 * a1') ./ m
        db2 = sum(delta2, dims=2) ./ m
        dW1 = (delta1 * X') ./ m
        db1 = sum(delta1, dims=2) ./ m
        
        # Оновлення ваг
        gnn.W2 .-= lr .* dW2
        gnn.b2 .-= lr .* vec(db2)
        gnn.W1 .-= lr .* dW1
        gnn.b1 .-= lr .* vec(db1)
        
        # Логування прогресу
        if epoch % 1500 == 0 || epoch == 1
            # Обчислюємо поточну точність (Accuracy)
            predictions_discrete = a2 .>= 0.5
            accuracy = sum(predictions_discrete .== y) / m * 100
            println("Епоха $epoch: Помилка (Loss) = $(round(loss, digits=6)) | Точність = $(round(accuracy, digits=2))% | LR = $(round(lr, digits=5))")
        end
    end
    println("\n--- Навчання успішно завершено! ---\n")
end

# --------------------------------------------------------------------
# 5. Запуск та демонстрація результатів
# --------------------------------------------------------------------

# 1. Генеруємо повний датасет 4-вершинних графів
X, y = generate_graph_dataset()

# Розділимо дані на навчальну (80% - 51 граф) та тестову (20% - 13 графів) вибірки
shuffled_indices = shuffle(1:64)
train_indices = shuffled_indices[1:51]
test_indices = shuffled_indices[52:64]

X_train, y_train = X[:, train_indices], y[:, train_indices]
X_test, y_test = X[:, test_indices], y[:, test_indices]

# 2. Ініціалізуємо модель
# Вхід: 16 (сплющена матриця 4x4), Прихований шар: 10 нейронів, Вихід: 1 (ймовірність зв'язності)
gnn_model = initialize_network(16, 10, 1)

# 3. Навчаємо модель
train_gnn!(gnn_model, X_train, y_train, epochs=15000, lr_init=0.8, decay_rate=0.0001)

# 4. Перевіряємо точність на тестовій вибірці (дані, які модель ніколи не бачила)
_, test_predictions = forward_pass(gnn_model, X_test)
test_predictions_discrete = test_predictions .>= 0.5
test_accuracy = sum(test_predictions_discrete .== y_test) / length(test_indices) * 100

println("====================================================")
println("РЕЗУЛЬТАТИ ТЕСТУВАННЯ НА НЕВИДИМИХ ДАНИХ (Test Set)")
println("====================================================")
println("Загальна точність на тестових графах: $(round(test_accuracy, digits=2))%\n")

println("Приклади розпізнавання тестових графів:")
for i in 1:min(5, length(test_indices))
    idx = test_indices[i]
    adj_matrix = reshape(X[:, idx], 4, 4)
    true_val = y[1, idx] == 1.0 ? "Зв'язний" : "Незв'язний"
    pred_prob = test_predictions[1, i]
    pred_val = pred_prob >= 0.5 ? "Зв'язний" : "Незв'язний"
    status = true_val == pred_val ? "✅ ВІРНО" : "❌ ПОМИЛКА"
    
    println("\nГраф #$i (індекс у базі: $idx):")
    println("Матриця суміжності:")
    for row in 1:4
        println("  ", Int.(adj_matrix[row, :]))
    end
    println("Реальний стан: $true_val | Передбачено мережею: $pred_val (Ймовірність: $(round(pred_prob * 100, digits=1))%) | $status")
end
