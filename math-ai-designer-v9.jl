# ====================================================================
# ІНТЕРАКТИВНИЙ КОНСТРУКТОР-АНАЛІЗАТОР НЕЙРОМЕРЕЖ З НУЛЯ (Julia-скрипт)
# ====================================================================
# Ця програма є повноцінною навчальною та експериментальною ШІ-лабораторією.
# Вона дозволяє користувачеві з нуля проектувати архітектуру нейромережі,
# вибирати математичні параметри, тренувати модель на різних математичних
# датасетах, аналізувати криву навчання та досліджувати "мозок" ШІ
# через ASCII-візуалізацію ваг та аналіз важливості ознак (Feature Importance).

using Random
using LinearAlgebra

# Глобальні параметри для множини Жюліа
julia_cr = -0.7
julia_ci = 0.27015

# ====================================================================
# 1. МАТЕМАТИЧНЕ ШІ-ЯДРО (Універсальні функції активації та Loss)
# ====================================================================

# Функції активації прихованого шару
sigmoid(x) = 1.0 ./ (1.0 .+ exp.(.-x))
sigmoid_derivative(a) = a .* (1.0 .- a)

tanh_act(x) = tanh.(x)
tanh_derivative(a) = 1.0 .- a.^2

relu(x) = max.(0.0, x)
relu_derivative(a) = Float64.(a .> 0.0)

# Чисельно стабільний Softmax для вихідного шару
function softmax(x::Matrix{Float64})
    max_val = maximum(x, dims=1)
    exp_x = exp.(x .- max_val)
    return exp_x ./ sum(exp_x, dims=1)
end

# Структура ШІ-моделі
mutable struct CustomizableNeuralNetwork
    W1::Matrix{Float64}         # Ваги першого шару (Hidden x Input)
    b1::Vector{Float64}         # Зсуви першого шару
    W2::Matrix{Float64}         # Ваги другого шару (Output x Hidden)
    b2::Vector{Float64}         # Зсуви другого шару
    act_hidden::Symbol          # :sigmoid, :tanh, :relu
    act_output::Symbol          # :sigmoid, :softmax, :linear
    loss_type::Symbol           # :mse, :binary_crossentropy, :categorical_crossentropy
end

# Ініціалізація Ксав'є (Xavier/Glorot) для стабільності градієнтів
function initialize_network(input_size::Int, hidden_size::Int, output_size::Int, 
                            act_hidden::Symbol, act_output::Symbol, loss_type::Symbol)
    Random.seed!(42) # Фіксуємо для відтворюваності
    
    limit1 = sqrt(6.0 / (input_size + hidden_size))
    limit2 = sqrt(6.0 / (hidden_size + output_size))
    
    W1 = (rand(hidden_size, input_size) .- 0.5) .* (2.0 * limit1)
    b1 = zeros(hidden_size)
    
    W2 = (rand(output_size, hidden_size) .- 0.5) .* (2.0 * limit2)
    b2 = zeros(output_size)
    
    return CustomizableNeuralNetwork(W1, b1, W2, b2, act_hidden, act_output, loss_type)
end

# Пряме поширення (Forward Pass)
function forward_pass(nn::CustomizableNeuralNetwork, X::Matrix{Float64})
    # Прихований шар
    z1 = nn.W1 * X .+ nn.b1
    a1 = if nn.act_hidden == :sigmoid
        sigmoid(z1)
    elseif nn.act_hidden == :tanh
        tanh_act(z1)
    elseif nn.act_hidden == :relu
        relu(z1)
    else
        z1
    end
    
    # Вихідний шар
    z2 = nn.W2 * a1 .+ nn.b2
    a2 = if nn.act_output == :sigmoid
        sigmoid(z2)
    elseif nn.act_output == :softmax
        softmax(z2)
    else
        z2 # Лінійна активація для регресії (MSE)
    end
    
    return a1, a2
end

# ====================================================================
# 2. АНАЛІТИЧНИЙ МОДУЛЬ (ASCII-Візуалізація та Математичний Аналіз)
# ====================================================================

# ASCII-графік навчання
function draw_learning_curve(losses::Vector{Float64}; width=55, height=8)
    n = length(losses)
    if n == 0 return end
    
    # Ресемплінг для відповідності ширині графіка
    step = max(1, n ÷ width)
    sampled = [losses[i] for i in 1:step:n]
    if length(sampled) > width
        sampled = sampled[1:width]
    end
    
    max_l = maximum(sampled)
    min_l = minimum(sampled)
    range_l = max_l - min_l == 0 ? 1.0 : max_l - min_l
    
    println("\n📊 ГРАФІК ЗБІЖНОСТІ ПОМИЛКИ НАВЧАННЯ (Loss Convergence Plot):")
    println("      " * "—"^width)
    for h in height:-1:1
        threshold = min_l + (h / height) * range_l
        val_str = string(round(threshold, digits=4))
        val_str = length(val_str) > 6 ? val_str[1:6] : rpad(val_str, 6)
        print(" " * val_str * " |")
        for val in sampled
            print(val >= threshold ? "█" : " ")
        end
        println("|")
    end
    println("      " * "—"^width)
    println("      0" * " "^(width-13) * "Епохи -> " * lpad(n, 4))
end

# ASCII-Теплокарта матриці ваг першого шару W1 (Hidden x Input)
function draw_weights_heatmap(W::Matrix{Float64})
    rows, cols = size(W)
    println("\n🧠 ТЕПЛОКАРТА МАТРИЦІ ВАГ ПЕРШОГО ШАРУ W1 (Приховані нейрони x Вхідні ознаки):")
    println("Символи: '█' (сильний + зв'язок), '▒' (середній), '░' (близький до 0), '·' (сильний - зв'язок)")
    
    print("        ")
    for c in 1:cols
        print(" Вх_$c ")
    end
    println()
    
    for r in 1:rows
        print("Нейрон_$r |")
        for c in 1:cols
            val = W[r, c]
            # Нормалізуємо для відображення відносно максимуму в матриці
            max_abs = maximum(abs.(W))
            ratio = val / (max_abs == 0.0 ? 1.0 : max_abs)
            
            char = if ratio > 0.6
                " ███ "
            elseif ratio > 0.15
                " ▒▒▒ "
            elseif ratio > -0.15
                " ░░░ "
            elseif ratio > -0.6
                " ░░· "
            else
                " ··· "
            end
            print(char)
        end
        println("|")
    end
end

# Аналіз важливості вхідних ознак (Feature Importance)
# Визначає сумарну абсолютну силу синаптичних зв'язків кожного входу з прихованим шаром
function analyze_feature_importance(W1::Matrix{Float64}, feature_names::Vector{String})
    rows, cols = size(W1)
    importance = zeros(cols)
    
    # Метод суми абсолютних ваг
    for c in 1:cols
        importance[c] = sum(abs.(W1[:, c]))
    end
    
    # Нормалізуємо у відсотки
    total = sum(importance)
    if total > 0.0
        importance = (importance ./ total) .* 100.0
    end
    
    println("\n🔍 АНАЛІЗ ВАЖЛИВОСТІ ВХІДНИХ ОЗНАК (Feature Importance):")
    println("Показує, які вхідні сигнали мають найбільший вплив на формування прихованих концепцій ШІ:")
    
    sorted_indices = sortperm(importance, rev=true)
    for idx in sorted_indices
        pct = importance[idx]
        bar_len = Int(round(pct / 4))
        bar = "█"^bar_len * "░"^(25 - bar_len)
        println("  • $(rpad(feature_names[idx], 18)) |$bar| $(round(pct, digits=1))%")
    end
end

# Індикатор впевненості
function draw_confidence_bar(prob::Float64; width=25)
    filled = Int(round(prob * width))
    empty = width - filled
    bar = "█"^filled * "░"^empty
    return "|$bar| ($(round(prob*100, digits=1))% впевненості)"
end

# ====================================================================
# 3. ДАТАСЕТИ-ПРЕСЕТИ ДЛЯ НАВЧАННЯ ТА ЕКСПЕРИМЕНТІВ
# ====================================================================

# Пресет 1: Класичний нелінійний XOR (2 входи, 1 вихід)
function get_xor_dataset()
    X = [0.0 0.0 1.0 1.0;
         0.0 1.0 0.0 1.0]
    y = [0.0 1.0 1.0 0.0]
    names = ["Вхід А", "Вхід В"]
    return X, y, names, :sigmoid, :sigmoid, :binary_crossentropy
end

# Пресет 2: Теорія Чисел - Прості числа 8-біт (8 входів, 1 вихід)
function is_prime(n::Int)
    if n <= 1 return false end
    for i in 2:Int(floor(sqrt(n)))
        if n % i == 0 return false end
    end
    return true
end

function get_prime_dataset()
    X = zeros(8, 255)
    y = zeros(1, 255)
    for i in 1:255
        X[:, i] = Float64.(digits(i, base=2, pad=8))
        y[1, i] = is_prime(i) ? 1.0 : 0.0
    end
    names = ["Біт 2^0 (LSD)", "Біт 2^1", "Біт 2^2", "Біт 2^3", "Біт 2^4", "Біт 2^5", "Біт 2^6", "Біт 2^7 (MSD)"]
    return X, y, names, :sigmoid, :sigmoid, :binary_crossentropy
end

# Пресет 3: Лінійна Алгебра - Визначник матриці 2х2 (4 входи, 1 вихід)
function get_determinant_dataset()
    Random.seed!(42)
    num_samples = 1000
    X = rand(4, num_samples) .* 2.0 .- 1.0 # елементи матриці від -1 до 1
    y = zeros(1, num_samples)
    for i in 1:num_samples
        # det [a b; c d] = a*d - b*c
        a, b, c, d = X[1, i], X[2, i], X[3, i], X[4, i]
        y[1, i] = a*d - b*c
    end
    # Нормалізація цілі в [0, 1] для стабільності
    min_y, max_y = -2.0, 2.0
    y_norm = (y .- min_y) ./ (max_y - min_y)
    names = ["Елемент a11", "Елемент a12", "Елемент a21", "Елемент a22"]
    return X, y_norm, names, :tanh, :sigmoid, :mse, min_y, max_y
end

# Пресет 4: Дискретна математика - Періоди Пізано Фібоначчі (6 входів, 1 вихід)
function get_fibonacci_parity_dataset()
    # Перші 60 чисел Фібоначчі (період парності Пізано для m=2 дорівнює 3)
    fib = zeros(Int, 60)
    fib[1] = 1
    fib[2] = 1
    for i in 3:60
        fib[i] = (fib[i-1] + fib[i-2]) % 2 # беремо відразу по модулю 2 (парність)
    end
    
    X = zeros(6, 60)
    y = zeros(1, 60)
    for i in 1:60
        X[:, i] = Float64.(digits(i, base=2, pad=6)) # 6-бітний індекс елемента
        y[1, i] = Float64(fib[i])                    # 1.0 - непарне, 0.0 - парне
    end
    names = ["Індекс Біт 2^0", "Індекс Біт 2^1", "Індекс Біт 2^2", "Індекс Біт 2^3", "Індекс Біт 2^4", "Індекс Біт 2^5"]
    return X, y, names, :sigmoid, :sigmoid, :binary_crossentropy
end


# Пресет 5: Лінійна алгебра - Вироджені матриці 2х2 (4 входи, 1 вихід, класифікація)
function get_degenerate_matrix_dataset()
    Random.seed!(42)
    num_samples = 1000
    X = zeros(4, num_samples)
    y = zeros(1, num_samples)
    
    for i in 1:num_samples
        if rand() < 0.5
            # Дегенерована матриця (вироджена)
            # Спосіб 1: Лінійна залежність рядків або стовпців
            a = rand() * 2.0 - 1.0
            b = rand() * 2.0 - 1.0
            k = rand() * 2.0 - 1.0 # випадковий множник
            X[:, i] = [a, b, k*a, k*b]
            y[1, i] = 1.0
        else
            # Звичайна матриця (невироджена)
            while true
                a, b, c, d = rand(4) .* 2.0 .- 1.0
                det_val = a*d - b*c
                if abs(det_val) > 0.15 # гарантуємо невиродженість
                    X[:, i] = [a, b, c, d]
                    break
                end
            end
            y[1, i] = 0.0
        end
    end
    names = ["Елемент a11", "Елемент a12", "Елемент a21", "Елемент a22"]
    return X, y, names, :tanh, :sigmoid, :binary_crossentropy
end

# Пресет 6: Теорія хаосу - Прогнозування хаотичних рядів (Логістичне відображення) (3 входи, 1 вихід, регресія)
function get_chaotic_series_dataset()
    Random.seed!(42)
    num_samples = 600
    r_param = 3.95
    # Генеруємо довгу послідовність
    series = zeros(num_samples + 5)
    series[1] = 0.4 # початкове значення
    for i in 2:length(series)
        series[i] = r_param * series[i-1] * (1.0 - series[i-1])
    end
    
    # Будуємо ковзне вікно шириною 3: [x(t-2), x(t-1), x(t)] -> x(t+1)
    X = zeros(3, num_samples)
    y = zeros(1, num_samples)
    for i in 1:num_samples
        X[1, i] = series[i]     # x(t-2)
        X[2, i] = series[i+1]   # x(t-1)
        X[3, i] = series[i+2]   # x(t)
        y[1, i] = series[i+3]   # x(t+1)
    end
    names = ["Значення x(t-2)", "Значення x(t-1)", "Значення x(t)"]
    return X, y, names, :tanh, :sigmoid, :mse, 0.0, 1.0
end



# Пресет 7: Теорія хаосу - Атрактор Лоренца (3 входи, 3 виходи, регресія)
# x_t, y_t, z_t -> x_t+1, y_t+1, z_t+1
function get_lorenz_dataset()
    Random.seed!(42)
    num_samples = 800
    # Параметри Лоренца (хаотичний режим)
    sigma = 10.0
    beta = 8/3
    rho = 28.0
    dt = 0.01
    
    # Симуляція методом Ейлера
    x_seq = zeros(num_samples + 1)
    y_seq = zeros(num_samples + 1)
    z_seq = zeros(num_samples + 1)
    
    # Початкові значення
    x_seq[1], y_seq[1], z_seq[1] = 1.0, 1.0, 20.0
    
    for t in 1:num_samples
        dx = sigma * (y_seq[t] - x_seq[t]) * dt
        dy = (x_seq[t] * (rho - z_seq[t]) - y_seq[t]) * dt
        dz = (x_seq[t] * y_seq[t] - beta * z_seq[t]) * dt
        
        x_seq[t+1] = x_seq[t] + dx
        y_seq[t+1] = y_seq[t] + dy
        z_seq[t+1] = z_seq[t] + dz
    end
    
    # Нормалізація в діапазон [0, 1] для стабільності
    min_x, max_x = minimum(x_seq), maximum(x_seq)
    min_y, max_y = minimum(y_seq), maximum(y_seq)
    min_z, max_z = minimum(z_seq), maximum(z_seq)
    
    x_norm = (x_seq .- min_x) ./ (max_x - min_x)
    y_norm = (y_seq .- min_y) ./ (max_y - min_y)
    z_norm = (z_seq .- min_z) ./ (max_z - min_z)
    
    # Входи: [x_norm(t), y_norm(t), z_norm(t)]
    # Виходи: [x_norm(t+1), y_norm(t+1), z_norm(t+1)]
    X = zeros(3, num_samples)
    y = zeros(3, num_samples)
    for t in 1:num_samples
        X[1, t] = x_norm[t]
        X[2, t] = y_norm[t]
        X[3, t] = z_norm[t]
        
        y[1, t] = x_norm[t+1]
        y[2, t] = y_norm[t+1]
        y[3, t] = z_norm[t+1]
    end
    
    names = ["Норм. x(t)", "Норм. y(t)", "Норм. z(t)"]
    return X, y, names, :tanh, :sigmoid, :mse, [min_x, min_y, min_z], [max_x, max_y, max_z]
end

# ASCII Візуалізатор атрактора Лоренца
function visualize_lorenz_ascii()
    num_points = 1200
    sigma, beta, rho = 10.0, 8/3, 28.0
    dt = 0.01
    
    x, y, z = 1.0, 1.0, 20.0
    pts = Tuple{Float64, Float64}[]
    
    for _ in 1:num_points
        dx = sigma * (y - x) * dt
        dy = (x * (rho - z) - y) * dt
        dz = (x * y - beta * z) * dt
        x += dx
        y += dy
        z += dz
        push!(pts, (x, z))
    end
    
    rows = 16
    cols = 60
    grid = fill(' ', rows, cols)
    
    xs = [p[1] for p in pts]
    zs = [p[2] for p in pts]
    
    min_x, max_x = minimum(xs), maximum(xs)
    min_z, max_z = minimum(zs), maximum(zs)
    
    for (px, pz) in pts
        r = round(Int, rows - (pz - min_z) / (max_z - min_z) * (rows - 1))
        c = round(Int, 1 + (px - min_x) / (max_x - min_x) * (cols - 1))
        r = clamp(r, 1, rows)
        c = clamp(c, 1, cols)
        grid[r, c] = '*'
    end
    
    println("\n🦋 АТИПОВИЙ ASCII-ПОРТРЕТ АТРАКТОРА ЛОРЕНЦА (Проекція X - Z):")
    println("╭" * "─"^cols * "╮")
    for r in 1:rows
        print("│")
        for c in 1:cols
            print(grid[r, c])
        end
        println("│")
    end
    println("╰" * "─"^cols * "╯")
end



# Пресет 8: Теорія хаосу - Атрактор Рьосслера (3 входи, 3 виходи, регресія)
# x_t, y_t, z_t -> x_t+1, y_t+1, z_t+1
function get_roessler_dataset()
    Random.seed!(42)
    num_samples = 1000
    # Параметри Рьосслера (хаотичний режим)
    a = 0.2
    b = 0.2
    c = 5.7
    dt = 0.05
    
    # Симуляція методом Ейлера
    x_seq = zeros(num_samples + 1)
    y_seq = zeros(num_samples + 1)
    z_seq = zeros(num_samples + 1)
    
    # Початкові значення
    x_seq[1], y_seq[1], z_seq[1] = 0.5, 0.5, 0.5
    
    for t in 1:num_samples
        dx = (-y_seq[t] - z_seq[t]) * dt
        dy = (x_seq[t] + a * y_seq[t]) * dt
        dz = (b + z_seq[t] * (x_seq[t] - c)) * dt
        
        x_seq[t+1] = x_seq[t] + dx
        y_seq[t+1] = y_seq[t] + dy
        z_seq[t+1] = z_seq[t] + dz
    end
    
    # Нормалізація в діапазон [0, 1] для стабільності
    min_x, max_x = minimum(x_seq), maximum(x_seq)
    min_y, max_y = minimum(y_seq), maximum(y_seq)
    min_z, max_z = minimum(z_seq), maximum(z_seq)
    
    x_norm = (x_seq .- min_x) ./ (max_x - min_x)
    y_norm = (y_seq .- min_y) ./ (max_y - min_y)
    z_norm = (z_seq .- min_z) ./ (max_z - min_z)
    
    # Входи: [x_norm(t), y_norm(t), z_norm(t)]
    # Виходи: [x_norm(t+1), y_norm(t+1), z_norm(t+1)]
    X = zeros(3, num_samples)
    y = zeros(3, num_samples)
    for t in 1:num_samples
        X[1, t] = x_norm[t]
        X[2, t] = y_norm[t]
        X[3, t] = z_norm[t]
        
        y[1, t] = x_norm[t+1]
        y[2, t] = y_norm[t+1]
        y[3, t] = z_norm[t+1]
    end
    
    names = ["Норм. x(t)", "Норм. y(t)", "Норм. z(t)"]
    return X, y, names, :tanh, :sigmoid, :mse, [min_x, min_y, min_z], [max_x, max_y, max_z]
end

# ASCII Візуалізатор атрактора Рьосслера
function visualize_roessler_ascii()
    num_points = 1500
    a, b, c = 0.2, 0.2, 5.7
    dt = 0.05
    
    x, y, z = 0.5, 0.5, 0.5
    pts = Tuple{Float64, Float64}[]
    
    for _ in 1:num_points
        dx = (-y - z) * dt
        dy = (x + a * y) * dt
        dz = (b + z * (x - c)) * dt
        x += dx
        y += dy
        z += dz
        push!(pts, (x, y)) # Проекція X - Y є красивою спіральною формою
    end
    
    rows = 16
    cols = 60
    grid = fill(' ', rows, cols)
    
    xs = [p[1] for p in pts]
    ys = [p[2] for p in pts]
    
    min_x, max_x = minimum(xs), maximum(xs)
    min_y, max_y = minimum(ys), maximum(ys)
    
    for (px, py) in pts
        r = round(Int, rows - (py - min_y) / (max_y - min_y) * (rows - 1))
        c = round(Int, 1 + (px - min_x) / (max_x - min_x) * (cols - 1))
        r = clamp(r, 1, rows)
        c = clamp(c, 1, cols)
        grid[r, c] = '*'
    end
    
    println("\n🌀 АТРАКТОР РЬОССЛЕРА (Проекція X - Y):")
    println("╭" * "─"^cols * "╮")
    for r in 1:rows
        print("│")
        for c in 1:cols
            print(grid[r, c])
        end
        println("│")
    end
    println("╰" * "─"^cols * "╯")
end

# Пресет 9: Фрактали - Множина Мандельброта (2 входи, 1 вихід, класифікація)
# Входи: x (реальна частина), y (уявна частина)
# Вихід: 1.0 - належить множині (не вилітає), 0.0 - не належить (вилітає)
function get_mandelbrot_dataset()
    Random.seed!(42)
    num_samples = 1200
    X = zeros(2, num_samples)
    y = zeros(1, num_samples)
    
    for i in 1:num_samples
        # Генеруємо випадкові координати у цікавому прямокутнику
        cx = rand() * 2.5 - 2.0   # [-2.0, 0.5]
        cy = rand() * 2.5 - 1.25  # [-1.25, 1.25]
        
        # Перевіряємо чи належить множині Мандельброта
        zx, zy = 0.0, 0.0
        is_inside = true
        max_iter = 100
        for iter in 1:max_iter
            # z = z^2 + c
            zx_new = zx*zx - zy*zy + cx
            zy_new = 2.0*zx*zy + cy
            zx, zy = zx_new, zy_new
            if zx*zx + zy*zy > 4.0
                is_inside = false
                break
            end
        end
        
        X[1, i] = cx
        X[2, i] = cy
        y[1, i] = is_inside ? 1.0 : 0.0
    end
    
    names = ["Координата X (Re)", "Координата Y (Im)"]
    return X, y, names, :tanh, :sigmoid, :binary_crossentropy
end

# ASCII Візуалізатор множини Мандельброта
function visualize_mandelbrot_ascii()
    rows = 16
    cols = 60
    grid = fill(' ', rows, cols)
    
    # Межі відображення
    min_x, max_x = -2.0, 0.5
    min_y, max_y = -1.25, 1.25
    
    max_iter = 80
    for r in 1:rows
        for c in 1:cols
            # Відображаємо рядок і стовпчик у комплексні координати
            cx = min_x + (c - 1) / (cols - 1) * (max_x - min_x)
            cy = min_y + (rows - r) / (rows - 1) * (max_y - min_y)
            
            zx, zy = 0.0, 0.0
            is_inside = true
            escaped_at = max_iter
            for iter in 1:max_iter
                zx_new = zx*zx - zy*zy + cx
                zy_new = 2.0*zx*zy + cy
                zx, zy = zx_new, zy_new
                if zx*zx + zy*zy > 4.0
                    is_inside = false
                    escaped_at = iter
                    break
                end
            end
            
            # Візуальні символи залежно від швидкості розбіжності
            if is_inside
                grid[r, c] = '#'
            else
                if escaped_at > 40
                    grid[r, c] = '*'
                elseif escaped_at > 20
                    grid[r, c] = '+'
                elseif escaped_at > 10
                    grid[r, c] = '-'
                elseif escaped_at > 5
                    grid[r, c] = '·'
                else
                    grid[r, c] = ' '
                end
            end
        end
    end
    
    println("\n❄ ПОРТРЕТ МНОЖИНИ МАНДЕЛЬБРОТА (ASCII MANDELBROT FRACTAL):")
    println("╭" * "─"^cols * "╮")
    for r in 1:rows
        print("│")
        for c in 1:cols
            print(grid[r, c])
        end
        println("│")
    end
    println("╰" * "─"^cols * "╯")
end



# Пресет 10: Фрактали - Множина Жюліа (2 входи, 1 вихід, класифікація)
# Входи: z0_x (реальна частина), z0_y (уявна частина)
# Вихід: 1.0 - належить множині (не вилітає), 0.0 - не належить (вилітає)
function get_julia_dataset(cr::Float64=julia_cr, ci::Float64=julia_ci)
    Random.seed!(42)
    num_samples = 1200
    X = zeros(2, num_samples)
    y = zeros(1, num_samples)
    
    for i in 1:num_samples
        # Генеруємо випадкові стартові координати z0 у прямокутнику
        zx = rand() * 3.0 - 1.5   # [-1.5, 1.5]
        zy = rand() * 2.0 - 1.0   # [-1.0, 1.0]
        
        # Перевіряємо чи належить множині Жюліа
        curr_zx, curr_zy = zx, zy
        is_inside = true
        max_iter = 100
        for iter in 1:max_iter
            # z = z^2 + c
            zx_new = curr_zx*curr_zx - curr_zy*curr_zy + cr
            zy_new = 2.0*curr_zx*curr_zy + ci
            curr_zx, curr_zy = zx_new, zy_new
            if curr_zx*curr_zx + curr_zy*curr_zy > 4.0
                is_inside = false
                break
            end
        end
        
        X[1, i] = zx
        X[2, i] = zy
        y[1, i] = is_inside ? 1.0 : 0.0
    end
    
    names = ["Старт Z0_X (Re)", "Старт Z0_Y (Im)"]
    return X, y, names, :tanh, :sigmoid, :binary_crossentropy
end

# ASCII Візуалізатор множини Жюліа
function visualize_julia_ascii(cr::Float64=julia_cr, ci::Float64=julia_ci)
    rows = 16
    cols = 60
    grid = fill(' ', rows, cols)
    
    # Межі відображення
    min_x, max_x = -1.5, 1.5
    min_y, max_y = -1.0, 1.0
    
    max_iter = 80
    for r in 1:rows
        for c in 1:cols
            zx = min_x + (c - 1) / (cols - 1) * (max_x - min_x)
            zy = min_y + (rows - r) / (rows - 1) * (max_y - min_y)
            
            is_inside = true
            escaped_at = max_iter
            for iter in 1:max_iter
                zx_new = zx*zx - zy*zy + cr
                zy_new = 2.0*zx*zy + ci
                zx, zy = zx_new, zy_new
                if zx*zx + zy*zy > 4.0
                    is_inside = false
                    escaped_at = iter
                    break
                end
            end
            
            # Візуальні символи залежно від швидкості розбіжності
            if is_inside
                grid[r, c] = '#'
            else
                if escaped_at > 40
                    grid[r, c] = '*'
                elseif escaped_at > 20
                    grid[r, c] = '+'
                elseif escaped_at > 10
                    grid[r, c] = '-'
                elseif escaped_at > 5
                    grid[r, c] = '·'
                else
                    grid[r, c] = ' '
                end
            end
        end
    end
    
    println("\n❄ ПОРТРЕТ МНОЖИНИ ЖЮЛІА (ASCII JULIA FRACTAL):")
    println("╭" * "─"^cols * "╮")
    for r in 1:rows
        print("│")
        for c in 1:cols
            print(grid[r, c])
        end
        println("│")
    end
    println("╰" * "─"^cols * "╯")
end


# ====================================================================
# 4. ДИНАМІЧНИЙ ПРОЦЕС ТРЕНУВАННЯ ШІ
# ====================================================================

function train_custom_ai!(nn::CustomizableNeuralNetwork, X::Matrix{Float64}, y::Matrix{Float64};
                          epochs=5000, lr_init=0.1, lr_decay=0.0001)
    m = size(X, 2)
    losses = Float64[]
    
    println("\n" * "═"^60)
    println("             ПРОЦЕС ТРЕНУВАННЯ НЕЙРОМЕРЕЖІ")
    println("═"^60)
    println("• Архітектура: Вхідний шар -> $(size(nn.W1, 1)) прихованих -> $(size(nn.W2, 1)) вихідний")
    println("• Активації:   Прихована: $(nn.act_hidden) | Вихідна: $(nn.act_output)")
    println("• Оптимізатор: Базовий градієнтний спуск з Learning Rate Decay")
    
    for epoch in 1:epochs
        # Пряме поширення (Forward pass)
        a1, a2 = forward_pass(nn, X)
        
        # Розрахунок помилки (Loss)
        epsilon = 1e-15
        loss = if nn.loss_type == :binary_crossentropy
            -sum(y .* log.(a2 .+ epsilon) .+ (1.0 .- y) .* log.(1.0 .- a2 .+ epsilon)) / m
        elseif nn.loss_type == :categorical_crossentropy
            -sum(y .* log.(a2 .+ epsilon)) / m
        else # :mse
            sum((a2 .- y).^2) / (2 * m)
        end
        push!(losses, loss)
        
        # Планувальник кроку навчання (Learning Rate Decay)
        lr = lr_init / (1.0 + lr_decay * epoch)
        
        # Зворотне поширення (Backpropagation)
        # Градієнт на вихідному шарі
        delta2 = if nn.loss_type == :mse
            if nn.act_output == :sigmoid
                (a2 .- y) .* sigmoid_derivative(a2)
            else
                (a2 .- y)
            end
        else # для BCE/CCE з Sigmoid/Softmax градієнт красивий та спрощений: a2 - y
            (a2 .- y)
        end
        
        # Помилка прихованого шару
        error_hidden = nn.W2' * delta2
        
        # Градієнт на прихованому шарі
        delta1 = if nn.act_hidden == :sigmoid
            error_hidden .* sigmoid_derivative(a1)
        elseif nn.act_hidden == :tanh
            error_hidden .* tanh_derivative(a1)
        elseif nn.act_hidden == :relu
            error_hidden .* relu_derivative(a1)
        else
            error_hidden
        end
        
        # Розрахунок градієнтів ваг та зсувів
        dW2 = (delta2 * a1') ./ m
        db2 = sum(delta2, dims=2) ./ m
        dW1 = (delta1 * X') ./ m
        db1 = sum(delta1, dims=2) ./ m
        
        # Градієнтний крок (оновлення ваг)
        nn.W2 .-= lr .* dW2
        nn.b2 .-= lr .* vec(db2)
        nn.W1 .-= lr .* dW1
        nn.b1 .-= lr .* vec(db1)
        
        # Логування ходу навчання
        if epoch % 1000 == 0 || epoch == 1
            println("  [Епоха $(lpad(epoch, 5))] Loss: $(round(loss, digits=6)) | LR: $(round(lr, digits=4))")
        end
    end
    
    println("✔ Навчання завершено успішно!")
    draw_learning_curve(losses)
end

# ====================================================================
# 5. ГОЛОВНИЙ ІНТЕРФЕЙС ТА УПРАВЛІННЯ ЛАБОРАТОРІЄЮ (CLI-Меню)
# ====================================================================

function interactive_designer_loop()
    # Ініціалізаційні змінні за замовчуванням
    X, y, feature_names = nothing, nothing, String[]
    act_hidden, act_output, loss_type = :sigmoid, :sigmoid, :binary_crossentropy
    min_val_y, max_val_y = 0.0, 1.0
    is_regression = false
    
    # Модель за замовчуванням (XOR)
    X, y, feature_names, act_hidden, act_output, loss_type = get_xor_dataset()
    nn_model = initialize_network(size(X, 1), 4, size(y, 1), act_hidden, act_output, loss_type)
    
    current_dataset_name = "Логічний XOR Gate"
    
    while true
        println("\n" * "█"*75)
        println("   ШІ-КОНСТРУКТОР ТА АНАЛІЗАТОР НЕЙРОМЕРЕЖ З НУЛЯ (MATH AI DESIGNER v6.0)")
        println("█"*75)
        println("  Поточний датасет:   [$current_dataset_name]")
        println("  Розмірність входів: [$(size(X, 1)) ознак(и)] | Прикладів у базі: [$(size(X, 2))]")
        println("  Поточна конфігурація ШІ-мозгу:")
        println("    - Структура:      Вхід ($(size(X, 1))) -> Прихований ($(size(nn_model.W1, 1))) -> Вихід ($(size(nn_model.W2, 1)))")
        println("    - Активації:      Прихована: [$act_hidden] | Вихідна: [$act_output]")
        println("    - Loss-функція:   [$loss_type]")
        println("-" * 75)
        println("Оберіть дію:")
        println("1. ОБРАТИ МАТЕМАТИЧНИЙ ДАТАСЕТ")
        println("2. СКОНФІГУРУВАТИ ВЛАСНУ АРХІТЕКТУРУ (Кількість нейронів та активацій)")
        println("3. ЗАПУСТИТИ НАВЧАННЯ ШІ (Епохи та кроки навчання)")
        println("4. АНАЛІЗУВАТИ ШІ: Візуалізувати теплокарту синапсів (W1)")
        println("5. АНАЛІЗУВАТИ ШІ: Дослідити важливість ознак (Feature Importance)")
        println("6. ТЕСТУВАТИ ШІ: Запустити випадковий математичний іспит для моделі")
        println("7. ТЕСТУВАТИ ШІ: ВВЕСТИ ВЛАСНИЙ ЗАПИТ (Ввести свої дані для прогнозу)")
        println("8. Вийти з конструктора")
        print("> Ваш вибір: ")
        
        choice = strip(readline())
        
        if choice == "1"
            println("\n--- ОБЕРІТЬ МАТЕМАТИЧНИЙ ДАТАСЕТ ДЛЯ ШІ ---")
            println("1. Логічний XOR Gate (Нелінійна комбінаторика, 2 входи)")
            println("2. Теорія чисел: Розпізнавання простих чисел за 8 бітами (1...255)")
            println("3. Лінійна алгебра: Прогнозування детермінанта матриці 2х2 (4 входи, регресія)")
            println("4. Дискретна математика: Періоди Пізано Фібоначчі на парність (6-біт)")
            println("5. Лінійна алгебра: Вироджені матриці 2х2 (4 входи, класифікація)")
            println("6. Теорія хаосу: Прогнозування хаотичних рядів (3 входи, регресія)")
            println("7. Теорія хаосу: Атрактор Лоренца (3 входи, 3 виходи, регресія)")
            println("8. Теорія хаосу: Атрактор Рьосслера (3 входи, 3 виходи, регресія)")
            println("9. Фрактали: Множина Мандельброта (2 входи, класифікація)")
            println("10. Фрактали: Множина Жюліа (2 входи, класифікація)")
            print("> Оберіть датасет (1-10): ")
            ds_choice = strip(readline())
            
            if ds_choice == "1"
                X, y, feature_names, act_hidden, act_output, loss_type = get_xor_dataset()
                current_dataset_name = "Логічний XOR Gate"
                is_regression = false
            elseif ds_choice == "2"
                X, y, feature_names, act_hidden, act_output, loss_type = get_prime_dataset()
                current_dataset_name = "Розпізнавання простих чисел (8-біт)"
                is_regression = false
            elseif ds_choice == "3"
                X, y, feature_names, act_hidden, act_output, loss_type, min_val_y, max_val_y = get_determinant_dataset()
                current_dataset_name = "Детермінант матриці 2х2 (Регресія)"
                is_regression = true
            elseif ds_choice == "4"
                X, y, feature_names, act_hidden, act_output, loss_type = get_fibonacci_parity_dataset()
                current_dataset_name = "Парність чисел Фібоначчі (Періоди Пізано)"
                is_regression = false
            elseif ds_choice == "5"
                X, y, feature_names, act_hidden, act_output, loss_type = get_degenerate_matrix_dataset()
                current_dataset_name = "Вироджені матриці 2х2 (Класифікація)"
                is_regression = false
            elseif ds_choice == "6"
                X, y, feature_names, act_hidden, act_output, loss_type, min_val_y, max_val_y = get_chaotic_series_dataset()
                current_dataset_name = "Хаотичний ряд (Логістичне відображення)"
                is_regression = true
            elseif ds_choice == "7"
                X, y, feature_names, act_hidden, act_output, loss_type, min_val_y, max_val_y = get_lorenz_dataset()
                current_dataset_name = "Атрактор Лоренца"
                is_regression = true
                visualize_lorenz_ascii()
            elseif ds_choice == "8"
                X, y, feature_names, act_hidden, act_output, loss_type, min_val_y, max_val_y = get_roessler_dataset()
                current_dataset_name = "Атрактор Рьосслера"
                is_regression = true
                visualize_roessler_ascii()
            elseif ds_choice == "9"
                X, y, feature_names, act_hidden, act_output, loss_type = get_mandelbrot_dataset()
                current_dataset_name = "Множина Мандельброта (Фрактал)"
                is_regression = false
                visualize_mandelbrot_ascii()
            elseif ds_choice == "10"
                println("\n--- НАЛАШТУВАННЯ МНОЖИНИ ЖЮЛІА ---")
                println("Поточна константа c = Re(c) + Im(c)*i: $julia_cr + $(julia_ci)i")
                print("Бажаєте змінити константу c? (yes/no) [За замовчуванням: no]: ")
                ans_julia = strip(lowercase(readline()))
                if ans_julia == "yes" || ans_julia == "y" || ans_julia == "так"
                    try
                        print("Реальна частина Re(c) [Поточна: $julia_cr]: ")
                        cr_str = strip(readline())
                        if !isempty(cr_str)
                            global julia_cr = parse(Float64, cr_str)
                        end
                        print("Уявна частина Im(c) [Поточна: $julia_ci]: ")
                        ci_str = strip(readline())
                        if !isempty(ci_str)
                            global julia_ci = parse(Float64, ci_str)
                        end
                        println("✅ Встановлено константу c = $julia_cr + $(julia_ci)i")
                    catch
                        println("❌ Помилка введення числових значень. Залишено попередні параметри.")
                    end
                end
                X, y, feature_names, act_hidden, act_output, loss_type = get_julia_dataset(julia_cr, julia_ci)
                current_dataset_name = "Множина Жюліа (c = $julia_cr + $(julia_ci)i)"
                is_regression = false
                visualize_julia_ascii(julia_cr, julia_ci)
            else
                println("❌ Невірний вибір датасету.")
                continue
            end
            
            # Скидаємо мережу під новий датасет за замовчуванням (hidden_size = 8)
            nn_model = initialize_network(size(X, 1), 8, size(y, 1), act_hidden, act_output, loss_type)
            println("✅ Датасет [$current_dataset_name] активовано. Створено нову нейромережу.")
            
        elseif choice == "2"
            println("\n--- СКОНФІГУРУВАТИ ВЛАСНУ АРХІТЕКТУРУ ШІ ---")
            try
                print("Вкажіть кількість нейронів у прихованому шарі [Поточна: $(size(nn_model.W1, 1))]: ")
                h_size = parse(Int, readline())
                if h_size < 1
                    println("❌ Має бути хоча б 1 нейрон.")
                    continue
                end
                
                println("Оберіть функцію активації для прихованого шару:")
                println("1. Sigmoid (класична нелінійність)")
                println("2. Tanh (гіперболічний тангенс, чудово для знакозмінних даних)")
                println("3. ReLU (сучасний лінійний випрямляч)")
                print("> Ваш вибір (1-3): ")
                act_choice = strip(readline())
                chosen_act = if act_choice == "1"
                    :sigmoid
                elseif act_choice == "2"
                    :tanh
                elseif act_choice == "3"
                    :relu
                else
                    println("❌ Буде встановлено Sigmoid за замовчуванням.")
                    :sigmoid
                end
                
                # Переналаштовуємо параметри
                act_hidden = chosen_act
                nn_model = initialize_network(size(X, 1), h_size, size(y, 1), act_hidden, act_output, loss_type)
                println("✅ Конфігурацію успішно оновлено! Нейромережа переініціалізована.")
            catch
                println("❌ Помилка введення числових значень.")
            end
            
        elseif choice == "3"
            println("\n--- ЗАПУСТИТИ НАВЧАННЯ ШІ ---")
            try
                print("Кількість епох навчання (рекомендовано 5000-15000) [За замовчуванням: 8000]: ")
                epochs_str = strip(readline())
                epochs_val = isempty(epochs_str) ? 8000 : parse(Int, epochs_str)
                
                print("Початковий крок навчання (learning rate) [За замовчуванням: 0.2]: ")
                lr_str = strip(readline())
                lr_val = isempty(lr_str) ? 0.2 : parse(Float64, lr_str)
                
                train_custom_ai!(nn_model, X, y, epochs=epochs_val, lr_init=lr_val, lr_decay=0.0001)
            catch e
                println("❌ Некоректні параметри навчання.")
            end
            
        elseif choice == "4"
            draw_weights_heatmap(nn_model.W1)
            
        elseif choice == "5"
            analyze_feature_importance(nn_model.W1, feature_names)
            
        elseif choice == "6"
            println("\n" * "═"^60)
            println("            ТЕСТУВАННЯ ТА МАТЕМАТИЧНИЙ ІСПИТ ШІ")
            println("═"^60)
            
            _, predictions = forward_pass(nn_model, X)
            m_samples = size(X, 2)
            
            if is_regression
                println("Тип тесту: Нелінійна Регресія (Прогнозування)")
                println("-"^60)
                for k in 1:4
                    idx = rand(1:m_samples)
                    if size(y, 1) == 1
                        pred_norm = predictions[1, idx]
                        pred_real = pred_norm * (max_val_y - min_val_y) + min_val_y
                        true_real = y[1, idx] * (max_val_y - min_val_y) + min_val_y
                        diff = abs(pred_real - true_real)
                        
                        println("Тест #$k:")
                        if current_dataset_name == "Детермінант матриці 2х2 (Регресія)"
                            println("  Матриця:   [$(round(X[1, idx], digits=2))  $(round(X[2, idx], digits=2)) ; $(round(X[3, idx], digits=2))  $(round(X[4, idx], digits=2))]")
                            println("  Реальний визначник: $(round(true_real, digits=4))")
                            println("  Прогноз ШІ-розуму:  $(round(pred_real, digits=4)) (Абсолютна похибка: $(round(diff, digits=4)))")
                        else
                            println("  Історія:   [$(round(X[1, idx], digits=4)) -> $(round(X[2, idx], digits=4)) -> $(round(X[3, idx], digits=4))]")
                            println("  Реальне наступне x(t+1): $(round(true_real, digits=4))")
                            println("  Прогноз ШІ-інтуїції:    $(round(pred_real, digits=4)) (Абсолютна похибка: $(round(diff, digits=4)))")
                        end
                    else
                        # Атрактор Лоренца (3 виходи)
                        pred_norm = predictions[:, idx]
                        pred_real = pred_norm .* (max_val_y .- min_val_y) .+ min_val_y
                        true_real = y[:, idx] .* (max_val_y .- min_val_y) .+ min_val_y
                        diff = abs.(pred_real .- true_real)
                        
                        println("Тест #$k:")
                        println("  Стан t:      x=$(round(X[1, idx]*(max_val_y[1]-min_val_y[1])+min_val_y[1], digits=2)), y=$(round(X[2, idx]*(max_val_y[2]-min_val_y[2])+min_val_y[2], digits=2)), z=$(round(X[3, idx]*(max_val_y[3]-min_val_y[3])+min_val_y[3], digits=2))")
                        println("  Реальний t+1: x=$(round(true_real[1], digits=2)), y=$(round(true_real[2], digits=2)), z=$(round(true_real[3], digits=2))")
                        println("  Прогноз ШІ:   x=$(round(pred_real[1], digits=2)), y=$(round(pred_real[2], digits=2)), z=$(round(pred_real[3], digits=2))")
                        println("  Похибки:      Δx=$(round(diff[1], digits=4)), Δy=$(round(diff[2], digits=4)), Δz=$(round(diff[3], digits=4))")
                    end
                    println()
                end
            else
                println("Тип тесту: Бінарна Класифікація (Логіка, Числа, Послідовності)")
                println("-"^60)
                correct = 0
                for i in 1:m_samples
                    pred_val = predictions[1, i] >= 0.5 ? 1.0 : 0.0
                    if pred_val == y[1, i]
                        correct += 1
                    end
                end
                accuracy = correct / m_samples * 100
                println("Загальна точність моделі на всій вибірці: $(round(accuracy, digits=2))%")
                println("-"^60)
                
                for k in 1:4
                    idx = rand(1:m_samples)
                    prob = predictions[1, idx]
                    pred_label = prob >= 0.5 ? 1.0 : 0.0
                    true_label = y[1, idx]
                    
                    status = (pred_label == true_label) ? "✅ ПРАВИЛЬНО" : "❌ ПОМИЛКА"
                    
                    println("Тест #$k:")
                    if current_dataset_name == "Логічний XOR Gate"
                        println("  Входи:     А=$(Int(X[1, idx])), B=$(Int(X[2, idx]))")
                        println("  Правильна відповідь: ", true_label == 1.0 ? "ТАК/АКТИВНО" : "НІ/ПАСИВНО")
                        println("  Прогноз ШІ-інтуїції: ", pred_label == 1.0 ? "ТАК/АКТИВНО" : "НІ/ПАСИВНО")
                    elseif current_dataset_name == "Розпізнавання простих чисел (8-біт)"
                        println("  Число:     $idx (Біти: $(join(reverse(Int.(X[:, idx])))))")
                        println("  Правильна відповідь: ", true_label == 1.0 ? "ТАК/АКТИВНО" : "НІ/ПАСИВНО")
                        println("  Прогноз ШІ-інтуїції: ", pred_label == 1.0 ? "ТАК/АКТИВНО" : "НІ/ПАСИВНО")
                    elseif current_dataset_name == "Вироджені матриці 2х2 (Класифікація)"
                        println("  Матриця:   [$(round(X[1, idx], digits=2))  $(round(X[2, idx], digits=2)) ; $(round(X[3, idx], digits=2))  $(round(X[4, idx], digits=2))]")
                        det_val = X[1, idx]*X[4, idx] - X[2, idx]*X[3, idx]
                        println("  Точний det: $(round(det_val, digits=4))")
                        println("  Правильна відповідь: ", true_label == 1.0 ? "ВИРОДЖЕНА (det = 0)" : "НЕВИРОДЖЕНА (det != 0)")
                        println("  Прогноз ШІ-інтуїції: ", pred_label == 1.0 ? "ВИРОДЖЕНА" : "НЕВИРОДЖЕНА")
                    elseif current_dataset_name == "Множина Мандельброта (Фрактал)"
                        println("  Координати c:  x=$(round(X[1, idx], digits=4)), y=$(round(X[2, idx], digits=4))")
                        println("  Правильна відповідь: ", true_label == 1.0 ? "НАЛЕЖИТЬ множині" : "НЕ НАЛЕЖИТЬ множині")
                        println("  Прогноз ШІ-інтуїції: ", pred_label == 1.0 ? "НАЛЕЖИТЬ множині" : "НЕ НАЛЕЖИТЬ множині")
                    elseif startswith(current_dataset_name, "Множина Жюліа")
                        println("  Початкова точка Z0:  x=$(round(X[1, idx], digits=4)), y=$(round(X[2, idx], digits=4))")
                        println("  Правильна відповідь: ", true_label == 1.0 ? "НАЛЕЖИТЬ множині" : "НЕ НАЛЕЖИТЬ множині")
                        println("  Прогноз ШІ-інтуїції: ", pred_label == 1.0 ? "НАЛЕЖИТЬ множині" : "НЕ НАЛЕЖИТЬ множині")
                    else # Фібоначчі
                        println("  Число Фібоначчі №$idx")
                        println("  Правильна відповідь: ", true_label == 1.0 ? "ТАК/АКТИВНО" : "НІ/ПАСИВНО")
                        println("  Прогноз ШІ-інтуїції: ", pred_label == 1.0 ? "ТАК/АКТИВНО" : "НІ/ПАСИВНО")
                    end
                    println("  Шкала впевненості:   " * draw_confidence_bar(prob) * "  [$status]")
                    println()
                end
            end
            println("═"^60)
            

        elseif choice == "7"
            println("\n" * "═"^60)
            println("            ВВЕДЕННЯ ВЛАСНОГО ЗАПИТУ ДЛЯ ШІ")
            println("═"^60)
            try
                if current_dataset_name == "Логічний XOR Gate"
                    print("Введіть перший вхід А (0 або 1): ")
                    val_a = parse(Float64, readline())
                    print("Введіть другий вхід B (0 або 1): ")
                    val_b = parse(Float64, readline())
                    
                    if (val_a != 0.0 && val_a != 1.0) || (val_b != 0.0 && val_b != 1.0)
                        println("❌ Помилка: Входи XOR мають бути строго 0 або 1.")
                        continue
                    end
                    
                    X_custom = reshape([val_a, val_b], 2, 1)
                    _, pred_custom = forward_pass(nn_model, X_custom)
                    prob = pred_custom[1, 1]
                    pred_label = prob >= 0.5 ? 1.0 : 0.0
                    true_label = (val_a != val_b) ? 1.0 : 0.0
                    
                    status = (pred_label == true_label) ? "✅ ПРАВИЛЬНО" : "❌ ПОМИЛКА"
                    
                    println("\nРезультат:")
                    println("  Ваші входи:  A=$(Int(val_a)), B=$(Int(val_b))")
                    println("  Точна логіка (XOR): ", true_label == 1.0 ? "ТАК (1)" : "НІ (0)")
                    println("  Прогноз ШІ-інтуїції: ", pred_label == 1.0 ? "ТАК (1)" : "НІ (0)")
                    println("  Шкала впевненості:   " * draw_confidence_bar(prob) * "  [$status]")
                    
                elseif current_dataset_name == "Розпізнавання простих чисел (8-біт)"
                    print("Введіть ціле число від 1 до 255: ")
                    val_num = parse(Int, readline())
                    if val_num < 1 || val_num > 255
                        println("❌ Помилка: Число за межами діапазону 1...255.")
                        continue
                    end
                    
                    bits_custom = Float64.(digits(val_num, base=2, pad=8))
                    X_custom = reshape(bits_custom, 8, 1)
                    _, pred_custom = forward_pass(nn_model, X_custom)
                    prob = pred_custom[1, 1]
                    pred_label = prob >= 0.5 ? 1.0 : 0.0
                    true_label = is_prime(val_num) ? 1.0 : 0.0
                    
                    status = (pred_label == true_label) ? "✅ ПРАВИЛЬНО" : "❌ ПОМИЛКА"
                    
                    println("\nРезультат:")
                    println("  Ваше число: $val_num (Бінарний код: $(join(reverse(Int.(bits_custom)))))")
                    println("  Статус простого:     ", true_label == 1.0 ? "ПРОСТЕ" : "СКЛАДЕНЕ")
                    println("  Прогноз ШІ-інтуїції: ", pred_label == 1.0 ? "ПРОСТЕ" : "СКЛАДЕНЕ")
                    println("  Шкала впевненості:   " * draw_confidence_bar(prob) * "  [$status]")
                    
                elseif current_dataset_name == "Детермінант матриці 2х2 (Регресія)"
                    println("Введіть елементи матриці 2х2:")
                    print("  a11: ")
                    a11 = parse(Float64, readline())
                    print("  a12: ")
                    a12 = parse(Float64, readline())
                    print("  a21: ")
                    a21 = parse(Float64, readline())
                    print("  a22: ")
                    a22 = parse(Float64, readline())
                    
                    X_custom = reshape([a11, a12, a21, a22], 4, 1)
                    _, pred_custom = forward_pass(nn_model, X_custom)
                    pred_norm = pred_custom[1, 1]
                    
                    pred_real = pred_norm * (max_val_y - min_val_y) + min_val_y
                    true_real = a11 * a22 - a12 * a21
                    diff = abs(pred_real - true_real)
                    
                    println("\nРезультат:")
                    println("  Матриця: [ $a11  $a12 ; $a21  $a22 ]")
                    println("  Точний det:       $(round(true_real, digits=4))")
                    println("  Прогноз ШІ-розуму: $(round(pred_real, digits=4)) (Абсолютна похибка: $(round(diff, digits=4)))")
                    
                elseif current_dataset_name == "Парність чисел Фібоначчі (Періоди Пізано)"
                    print("Введіть індекс числа Фібоначчі (1 до 60): ")
                    val_idx = parse(Int, readline())
                    if val_idx < 1 || val_idx > 60
                        println("❌ Помилка: Індекс має бути у діапазоні 1...60.")
                        continue
                    end
                    
                    bits_custom = Float64.(digits(val_idx, base=2, pad=6))
                    X_custom = reshape(bits_custom, 6, 1)
                    _, pred_custom = forward_pass(nn_model, X_custom)
                    prob = pred_custom[1, 1]
                    pred_label = prob >= 0.5 ? 1.0 : 0.0
                    
                    true_label = (val_idx % 3 == 0) ? 0.0 : 1.0
                    status = (pred_label == true_label) ? "✅ ПРАВИЛЬНО" : "❌ ПОМИЛКА"
                    
                    println("\nРезультат:")
                    println("  Індекс Фібоначчі №$val_idx (Бінарний індекс: $(join(reverse(Int.(bits_custom)))))")
                    println("  Правильна парність: ", true_label == 1.0 ? "НЕПАРНЕ" : "ПАРНЕ")
                    println("  Прогноз ШІ-інтуїції: ", pred_label == 1.0 ? "НЕПАРНЕ" : "ПАРНЕ")
                    println("  Шкала впевненості:   " * draw_confidence_bar(prob) * "  [$status]")
                    
                elseif current_dataset_name == "Вироджені матриці 2х2 (Класифікація)"
                    println("Введіть елементи матриці 2х2:")
                    print("  a11: ")
                    a11 = parse(Float64, readline())
                    print("  a12: ")
                    a12 = parse(Float64, readline())
                    print("  a21: ")
                    a21 = parse(Float64, readline())
                    print("  a22: ")
                    a22 = parse(Float64, readline())
                    
                    X_custom = reshape([a11, a12, a21, a22], 4, 1)
                    _, pred_custom = forward_pass(nn_model, X_custom)
                    prob = pred_custom[1, 1]
                    pred_label = prob >= 0.5 ? 1.0 : 0.0
                    
                    det_val = a11 * a22 - a12 * a21
                    true_label = (abs(det_val) < 1e-7) ? 1.0 : 0.0
                    status = (pred_label == true_label) ? "✅ ПРАВИЛЬНО" : "❌ ПОМИЛКА"
                    
                    println("\nРезультат:")
                    println("  Матриця: [ $a11  $a12 ; $a21  $a22 ]")
                    println("  Точний det: $(round(det_val, digits=4))")
                    println("  Реальний статус:      ", true_label == 1.0 ? "ВИРОДЖЕНА (det = 0)" : "НЕВИРОДЖЕНА")
                    println("  Прогноз ШІ-інтуїції:  ", pred_label == 1.0 ? "ВИРОДЖЕНА" : "НЕВИРОДЖЕНА")
                    println("  Шкала впевненості:   " * draw_confidence_bar(prob) * "  [$status]")
                    
                elseif current_dataset_name == "Хаотичний ряд (Логістичне відображення)"
                    println("Введіть 3 останні значення історії x (кожне в межах [0, 1]):")
                    print("  x(t-2): ")
                    xt2 = parse(Float64, readline())
                    print("  x(t-1): ")
                    xt1 = parse(Float64, readline())
                    print("  x(t):   ")
                    xt = parse(Float64, readline())
                    
                    if xt2 < 0 || xt2 > 1 || xt1 < 0 || xt1 > 1 || xt < 0 || xt > 1
                        println("❌ Помилка: Значення мають бути в діапазоні від 0.0 до 1.0.")
                        continue
                    end
                    
                    X_custom = reshape([xt2, xt1, xt], 3, 1)
                    _, pred_custom = forward_pass(nn_model, X_custom)
                    pred_norm = pred_custom[1, 1]
                    pred_real = pred_norm * (max_val_y - min_val_y) + min_val_y
                    
                    true_real = 3.95 * xt * (1.0 - xt)
                    diff = abs(pred_real - true_real)
                    
                    println("\nРезультат:")
                    println("  Введена історія: [ $xt2 -> $xt1 -> $xt ]")
                    println("  Точне x(t+1) за формулою: $(round(true_real, digits=4))")
                    println("  Прогноз ШІ-інтуїції:       $(round(pred_real, digits=4)) (Абсолютна похибка: $(round(diff, digits=4)))")
                    
                elseif current_dataset_name == "Атрактор Лоренца"
                    println("Введіть поточні координати у просторі атрактора Лоренца:")
                    print("  Координата X: ")
                    cx = parse(Float64, readline())
                    print("  Координата Y: ")
                    cy = parse(Float64, readline())
                    print("  Координата Z: ")
                    cz = parse(Float64, readline())
                    
                    cx_norm = (cx - min_val_y[1]) / (max_val_y[1] - min_val_y[1])
                    cy_norm = (cy - min_val_y[2]) / (max_val_y[2] - min_val_y[2])
                    cz_norm = (cz - min_val_y[3]) / (max_val_y[3] - min_val_y[3])
                    
                    X_custom = reshape([cx_norm, cy_norm, cz_norm], 3, 1)
                    _, pred_custom = forward_pass(nn_model, X_custom)
                    
                    pred_real = pred_custom[:, 1] .* (max_val_y .- min_val_y) .+ min_val_y
                    
                    sigma, beta, rho, dt = 10.0, 8/3, 28.0, 0.01
                    dx = sigma * (cy - cx) * dt
                    dy = (cx * (rho - cz) - cy) * dt
                    dz = (cx * cy - beta * cz) * dt
                    true_x = cx + dx
                    true_y = cy + dy
                    true_z = cz + dz
                    
                    diff = abs.(pred_real .- [true_x, true_y, true_z])
                    
                    println("\nРезультат:")
                    println("  Введені координати t:   x=$(round(cx, digits=2)), y=$(round(cy, digits=2)), z=$(round(cz, digits=2))")
                    println("  Точний крок t+1 (ODE):  x=$(round(true_x, digits=2)), y=$(round(true_y, digits=2)), z=$(round(true_z, digits=2))")
                    println("  Прогноз ШІ-розуму:      x=$(round(pred_real[1], digits=2)), y=$(round(pred_real[2], digits=2)), z=$(round(pred_real[3], digits=2))")
                    println("  Похибки прогнозу:       Δx=$(round(diff[1], digits=4)), Δy=$(round(diff[2], digits=4)), Δz=$(round(diff[3], digits=4))")
                    
                elseif current_dataset_name == "Атрактор Рьосслера"
                    println("Введіть поточні координати у просторі атрактора Рьосслера:")
                    print("  Координата X: ")
                    cx = parse(Float64, readline())
                    print("  Координата Y: ")
                    cy = parse(Float64, readline())
                    print("  Координата Z: ")
                    cz = parse(Float64, readline())
                    
                    cx_norm = (cx - min_val_y[1]) / (max_val_y[1] - min_val_y[1])
                    cy_norm = (cy - min_val_y[2]) / (max_val_y[2] - min_val_y[2])
                    cz_norm = (cz - min_val_y[3]) / (max_val_y[3] - min_val_y[3])
                    
                    X_custom = reshape([cx_norm, cy_norm, cz_norm], 3, 1)
                    _, pred_custom = forward_pass(nn_model, X_custom)
                    
                    pred_real = pred_custom[:, 1] .* (max_val_y .- min_val_y) .+ min_val_y
                    
                    a, b, c, dt = 0.2, 0.2, 5.7, 0.05
                    dx = (-cy - cz) * dt
                    dy = (cx + a * cy) * dt
                    dz = (b + cz * (cx - c)) * dt
                    true_x = cx + dx
                    true_y = cy + dy
                    true_z = cz + dz
                    
                    diff = abs.(pred_real .- [true_x, true_y, true_z])
                    
                    println("\nРезультат:")
                    println("  Введені координати t:   x=$(round(cx, digits=2)), y=$(round(cy, digits=2)), z=$(round(cz, digits=2))")
                    println("  Точний крок t+1 (ODE):  x=$(round(true_x, digits=2)), y=$(round(true_y, digits=2)), z=$(round(true_z, digits=2))")
                    println("  Прогноз ШІ-розуму:      x=$(round(pred_real[1], digits=2)), y=$(round(pred_real[2], digits=2)), z=$(round(pred_real[3], digits=2))")
                    println("  Похибки прогнозу:       Δx=$(round(diff[1], digits=4)), Δy=$(round(diff[2], digits=4)), Δz=$(round(diff[3], digits=4))")
                    
                elseif current_dataset_name == "Множина Мандельброта (Фрактал)"
                    println("Введіть комплексну координату c = x + iy для аналізу:")
                    print("  Дійсна частина X (Re): ")
                    cx = parse(Float64, readline())
                    print("  Уявна частина Y (Im):  ")
                    cy = parse(Float64, readline())
                    
                    X_custom = reshape([cx, cy], 2, 1)
                    _, pred_custom = forward_pass(nn_model, X_custom)
                    prob = pred_custom[1, 1]
                    pred_label = prob >= 0.5 ? 1.0 : 0.0
                    
                    zx, zy = 0.0, 0.0
                    is_inside = true
                    max_iter = 100
                    for iter in 1:max_iter
                        zx_new = zx*zx - zy*zy + cx
                        zy_new = 2.0*zx*zy + cy
                        zx, zy = zx_new, zy_new
                        if zx*zx + zy*zy > 4.0
                            is_inside = false
                            break
                        end
                    end
                    true_label = is_inside ? 1.0 : 0.0
                    status = (pred_label == true_label) ? "✅ ПРАВИЛЬНО" : "❌ ПОМИЛКА"
                    
                    println("\nРезультат:")
                    println("  Ваша точка c:       $cx + $(cy)i")
                    println("  Статус фракталу:    ", true_label == 1.0 ? "НАЛЕЖИТЬ множині" : "НЕ НАЛЕЖИТЬ множині")
                    println("  Прогноз ШІ-інтуїції: ", pred_label == 1.0 ? "НАЛЕЖИТЬ множині" : "НЕ НАЛЕЖИТЬ множині")
                    println("  Шкала впевненості:   " * draw_confidence_bar(prob) * "  [$status]")
                    
                elseif startswith(current_dataset_name, "Множина Жюліа")
                    println("Введіть комплексну стартову точку Z0 = x + iy для аналізу:")
                    print("  Дійсна частина X (Re): ")
                    zx = parse(Float64, readline())
                    print("  Уявна частина Y (Im):  ")
                    zy = parse(Float64, readline())
                    
                    X_custom = reshape([zx, zy], 2, 1)
                    _, pred_custom = forward_pass(nn_model, X_custom)
                    prob = pred_custom[1, 1]
                    pred_label = prob >= 0.5 ? 1.0 : 0.0
                    
                    curr_zx, curr_zy = zx, zy
                    is_inside = true
                    max_iter = 100
                    for iter in 1:max_iter
                        zx_new = curr_zx*curr_zx - curr_zy*curr_zy + cr
                        zy_new = 2.0*curr_zx*curr_zy + ci
                        curr_zx, curr_zy = zx_new, zy_new
                        if curr_zx*curr_zx + curr_zy*curr_zy > 4.0
                            is_inside = false
                            break
                        end
                    end
                    true_label = is_inside ? 1.0 : 0.0
                    status = (pred_label == true_label) ? "✅ ПРАВИЛЬНО" : "❌ ПОМИЛКА"
                    
                    println("\nРезультат:")
                    println("  Ваша точка Z0:      $zx + $(zy)i  (параметр c = $cr + $(ci)i)")
                    println("  Статус фракталу:    ", true_label == 1.0 ? "НАЛЕЖИТЬ множині" : "НЕ НАЛЕЖИТЬ множині")
                    println("  Прогноз ШІ-інтуїції: ", pred_label == 1.0 ? "НАЛЕЖИТЬ множині" : "НЕ НАЛЕЖИТЬ множині")
                    println("  Шкала впевненості:   " * draw_confidence_bar(prob) * "  [$status]")
                end
            catch e
                println("❌ Помилка: Введено некоректні дані.")
            end
            println("═"^60)

        elseif choice == "8"
            println("\nДякуємо за роботу з ШІ-Конструктором Math AI Designer! Успіхів у дослідженнях!")
            break
        else
            println("❌ Невірний вибір опції. Спробуйте ще раз.")
        end
    end
end

# Точка входу в програму
if abspath(PROGRAM_FILE) == @__FILE__
    interactive_designer_loop()
end
