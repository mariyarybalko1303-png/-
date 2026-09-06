# ====================================================================
# ІНТЕРАКТИВНИЙ АНАЛІЗАТОР ГРАФІВ НА МОВІ JULIA (Версія 2.0)
# ====================================================================
# Ця програма об'єднує класичні алгоритми дискретної математики:
# 1. Перевірка зв'язності графа за допомогою пошуку в ширину (BFS).
# 2. Пошук Ейлерового циклу за лінійний час (алгоритм Ієргальцера).
# 3. Пошук Гамільтового циклу за допомогою пошуку з поверненням (Backtracking).
# 4. Пошук найкоротшого шляху за допомогою алгоритму Дейкстри (Dijkstra).
# 5. Побудова мінімального кістякового дерева за допомогою алгоритму Пріма (Prim).
#
# Програма працює як консольний інтерактивний інструмент без зовнішніх залежностей.

using Random

# ====================================================================
# СТРУКТУРИ ТА ПРЕДСТАВЛЕННЯ ГРАФА
# ====================================================================

# Представлення ребра: (сусідня_вершина => вага_ребра)
const Edge = Pair{Int, Float64}
const Graph = Vector{Vector{Edge}}

# Створення неорієнтованого зваженого ребра (виправлено у версії 2.0)
function add_edge!(adj::Graph, u::Int, v::Int, w::Float64=1.0)
    push!(adj[u], v => w) # зберігаємо пару: сусідня_вершина => вага
    push!(adj[v], u => w)
end

# Перетворення зваженого графа на простий список суміжності без ваг (для Ейлера/Гамільтона)
function get_unweighted_adj(adj::Graph)
    n = length(adj)
    unweighted = [Int[] for _ in 1:n]
    for u in 1:n
        for edge in adj[u]
            push!(unweighted[u], edge.first) # edge.first - це сусідня вершина
        end
    end
    return [unique(list) for list in unweighted]
end

# ====================================================================
# АЛГОРИТМ 1: ЗВ'ЯЗНІСТЬ ГРАФА (BFS)
# ===================================================================

function is_connected(adj_simple::Vector{Vector{Int}}, n::Int)
    visited = zeros(Bool, n)
    
    start_node = -1
    for i in 1:n
        if !isempty(adj_simple[i])
            start_node = i
            break
        end
    end
    
    if start_node == -1
        return true # порожній граф вважається зв'язним
    end
    
    queue = [start_node]
    visited[start_node] = true
    
    while !isempty(queue)
        curr = popfirst!(queue)
        for neighbor in adj_simple[curr]
            if !visited[neighbor]
                visited[neighbor] = true
                push!(queue, neighbor)
            end
        end
    end
    
    for i in 1:n
        if !isempty(adj_simple[i]) && !visited[i]
            return false
        end
    end
    return true
end

# ====================================================================
# АЛГОРИТМ 2: ЕЙЛЕРОВИЙ ЦИКЛ (Алгоритм Ієргальцера)
# ====================================================================

function has_eulerian_cycle(adj_simple::Vector{Vector{Int}}, n::Int)
    for i in 1:n
        if length(adj_simple[i]) % 2 != 0
            return false
        end
    end
    return is_connected(adj_simple, n)
end

function find_eulerian_cycle(adj_simple::Vector{Vector{Int}})
    n = length(adj_simple)
    if !has_eulerian_cycle(adj_simple, n)
        return nothing
    end
    
    g = [Set{Int}(neighbors) for neighbors in adj_simple]
    curr_path = Int[]
    eulerian_cycle = Int[]
    
    start_node = 1
    for i in 1:n
        if !isempty(g[i])
            start_node = i
            break
        end
    end
    
    push!(curr_path, start_node)
    curr_v = start_node
    
    while !isempty(curr_path)
        if !isempty(g[curr_v])
            push!(curr_path, curr_v)
            next_v = first(g[curr_v])
            delete!(g[curr_v], next_v)
            delete!(g[next_v], curr_v)
            curr_v = next_v
        else
            push!(eulerian_cycle, curr_v)
            curr_v = pop!(curr_path)
        end
    end
    
    return reverse(eulerian_cycle)
end

# ====================================================================
# АЛГОРИТМ 3: ГАМІЛЬТОНІВ ЦИКЛ (Backtracking)
# ====================================================================

function is_safe_hamiltonian(v::Int, adj_simple::Vector{Vector{Int}}, path::Vector{Int}, pos::Int)
    # Перевірка наявності ребра між попередньою вершиною і новою
    if !(v in adj_simple[path[pos - 1]])
        return false
    end
    # Перевірка, чи не відвідували вершину раніше
    for i in 1:(pos - 1)
        if path[i] == v
            return false
        end
    end
    return true
end

function ham_cycle_util!(adj_simple::Vector{Vector{Int}}, path::Vector{Int}, pos::Int, n::Int)
    if pos == n + 1
        # Перевірка, чи є ребро від останньої вершини до стартової (вузол path[1])
        if path[n] in adj_simple[path[1]]
            return true
        else
            return false
        end
    end

    for v in 1:n
        if is_safe_hamiltonian(v, adj_simple, path, pos)
            path[pos] = v
            if ham_cycle_util!(adj_simple, path, pos + 1, n)
                return true
            end
            path[pos] = 0 # крок назад (backtrack)
        end
    end
    return false
end

function find_hamiltonian_cycle(adj_simple::Vector{Vector{Int}})
    n = length(adj_simple)
    path = zeros(Int, n)
    path[1] = 1 # фіксуємо стартову вершину
    
    if !ham_cycle_util!(adj_simple, path, 2, n)
        return nothing
    end
    
    # Замикаємо цикл для виведення
    push!(path, path[1])
    return path
end

# ====================================================================
# АЛГОРИТМ 4: АЛГОРИТМ ДЕЙКСТРИ (Shortest Path)
# ====================================================================

function dijkstra(adj::Graph, start_node::Int)
    n = length(adj)
    dist = fill(Inf, n)
    parent = fill(-1, n)
    visited = zeros(Bool, n)
    
    dist[start_node] = 0.0
    
    for _ in 1:n
        u = -1
        min_d = Inf
        for i in 1:n
            if !visited[i] && dist[i] < min_d
                min_d = dist[i]
                u = i
            end
        end
        
        if u == -1
            break
        end
        
        visited[u] = true
        
        for edge in adj[u]
            v = edge.first    # Сусідня вершина
            w = edge.second   # Вага ребра
            
            if !visited[v] && dist[u] + w < dist[v]
                dist[v] = dist[u] + w
                parent[v] = u
            end
        end
    end
    
    return dist, parent
end

function reconstruct_path(parent::Vector{Int}, start_node::Int, target_node::Int)
    path = Int[]
    curr = target_node
    while curr != -1
        push!(path, curr)
        if curr == start_node
            break
        end
        curr = parent[curr]
    end
    if isempty(path) || path[end] != start_node
        return Int[] # Шлях не існує
    end
    return reverse(path)
end

# ====================================================================
# АЛГОРИТМ 5: АЛГОРИТМ ПРІМА (Minimum Spanning Tree - MST)
# ====================================================================

"""
    prim_mst(adj::Graph)

Будує мінімальне кістякове дерево (MST) графа за допомогою алгоритму Пріма.
Повертає список ребер MST у форматі Tuple{Int, Int, Float64} (u, v, вага) та сумарну вагу дерева.
Якщо граф незв'язний, повертає `nothing`.
"""
function prim_mst(adj::Graph)
    n = length(adj)
    if n == 0
        return [], 0.0
    end
    
    in_mst = zeros(Bool, n)
    min_edge = fill(Inf, n)  # Мінімальна вага ребра для приєднання вершини до MST
    parent = fill(-1, n)     # Батьківська вершина для відновлення дерева
    
    # Починаємо з першої вершини
    min_edge[1] = 0.0
    
    mst_edges = Tuple{Int, Int, Float64}[]
    total_weight = 0.0
    
    for _ in 1:n
        # Знаходимо вершину з мінімальним min_edge серед тих, що ще не в MST
        u = -1
        min_w = Inf
        for i in 1:n
            if !in_mst[i] && min_edge[i] < min_w
                min_w = min_edge[i]
                u = i
            end
        end
        
        # Якщо граф незв'язний і залишилися невідвідані активні вершини
        if u == -1
            for i in 1:n
                if !isempty(adj[i]) && !in_mst[i]
                    return nothing # Побудова MST неможлива для незв'язного графа
                end
            end
            break
        end
        
        in_mst[u] = true
        total_weight += min_w
        
        # Якщо це не стартова вершина, додаємо ребро до MST
        if parent[u] != -1
            push!(mst_edges, (parent[u], u, min_w))
        end
        
        # Оновлюємо ваги суміжних ребер для невідвіданих вершин
        for edge in adj[u]
            v = edge.first      # Сусідня вершина
            w = edge.second     # Вага ребра
            
            if !in_mst[v] && w < min_edge[v]
                min_edge[v] = w
                parent[v] = u
            end
        end
    end
    
    return mst_edges, total_weight
end

# ====================================================================
# ІНТЕРФЕЙС КОРИСТУВАЧА ТА ШАБЛОНИ
# ====================================================================

function print_graph_info(adj::Graph)
    n = length(adj)
    total_edges = sum(length.(adj)) ÷ 2
    println("\nХарактеристики поточного графа:")
    println("• Кількість вершин (V): $n")
    println("• Кількість ребер  (E): $total_edges")
    println("• Ступені вершин:")
    for i in 1:n
        edge_strings = ["$(edge.first) (вага $(edge.second))" for edge in adj[i]]
        println("  Вершина $i (ступінь $(length(adj[i]))): " * join(edge_strings, ", "))
    end
end

# Створення шаблону: "Пісочний годинник" (Ейлеровий, не Гамільтонів)
function make_hourglass_graph()
    adj = [Vector{Edge}() for _ in 1:5]
    add_edge!(adj, 1, 2, 2.5)
    add_edge!(adj, 2, 3, 1.2)
    add_edge!(adj, 3, 4, 3.0)
    add_edge!(adj, 4, 1, 1.8)
    add_edge!(adj, 1, 3, 4.0)
    add_edge!(adj, 3, 5, 2.0)
    add_edge!(adj, 5, 1, 1.5)
    return adj
end

# Створення шаблону: "Кенігсберзькі мости" (Гамільтонів, не Ейлеровий)
function make_konigsberg_graph()
    adj = [Vector{Edge}() for _ in 1:4]
    add_edge!(adj, 1, 2, 1.0)
    add_edge!(adj, 1, 3, 4.5)
    add_edge!(adj, 1, 4, 2.0)
    add_edge!(adj, 2, 3, 2.3)
    add_edge!(adj, 2, 4, 5.0)
    return adj
end

# Ручне введення графа
function input_custom_graph()
    print("Введіть кількість вершин графа: ")
    n_str = readline()
    n = parse(Int, n_str)
    adj = [Vector{Edge}() for _ in 1:n]
    
    println("Введіть ребра у форматі: вершина1 вершина2 вага (наприклад: 1 2 3.5)")
    println("Введіть 'stop' або порожній рядок, щоб завершити введення.")
    
    while true
        print("Ребро: ")
        input = strip(readline())
        if input == "stop" || isempty(input)
            break
        end
        parts = split(input)
        if length(parts) < 2
            println("❌ Неправильний формат. Потрібно вказати хоча б дві вершини.")
            continue
        end
        try
            u = parse(Int, parts[1])
            v = parse(Int, parts[2])
            w = length(parts) >= 3 ? parse(Float64, parts[3]) : 1.0
            
            if u < 1 || u > n || v < 1 || v > n
                println("❌ Помилка: Вершини мають бути в межах від 1 до $n.")
                continue
            end
            add_edge!(adj, u, v, w)
            println("✅ Додано ребро $u <-> $v з вагою $w")
        catch e
            println("❌ Не вдалося розпізнати введення. Спробуйте ще раз.")
        end
    end
    return adj
end

# Головне меню аналізу конкретного графа
function analyze_graph_loop(adj::Graph)
    n = length(adj)
    adj_simple = get_unweighted_adj(adj)
    
    while true
        println("\n" * "="^50)
        println("        МЕНЮ АНАЛІЗУ ОБРАНОГО ГРАФА")
        println("="^50)
        println("1. Переглянути структуру графа та ступені вершин")
        println("2. Перевірити зв'язність графа (BFS)")
        println("3. Знайти Ейлеровий цикл (алгоритм Ієргальцера)")
        println("4. Знайти Гамільтонів цикл (бектрекінг)")
        println("5. Знайти найкоротший шлях між двома вершинами (Дейкстра)")
        println("6. Побудувати мінімальне кістякове дерево (алгоритм Пріма)")
        println("7. Повернутися до вибору графа")
        println("8. Вийти з програми")
        print("> Ваш вибір: ")
        
        choice = strip(readline())
        if choice == "1"
            print_graph_info(adj)
        elseif choice == "2"
            connected = is_connected(adj_simple, n)
            if connected
                println("\n✅ Граф є ЗВ'ЯЗНИМ. Існує шлях між будь-якою парою вершин.")
            else
                println("\n❌ Граф є НЕЗВ'ЯЗНИМ. У ньому є відокремлені компоненти.")
            end
        elseif choice == "3"
            cycle = find_eulerian_cycle(adj_simple)
            if cycle !== nothing
                println("\n✅ ЕЙЛЕРОВИЙ ЦИКЛ ІСНУЄ!")
                println("Маршрут: ", join(cycle, " -> "))
            else
                println("\n❌ Ейлерового циклу НЕМАЄ. Не всі вершини мають парний ступінь або граф незв'язний.")
            end
        elseif choice == "4"
            cycle = find_hamiltonian_cycle(adj_simple)
            if cycle !== nothing
                println("\n✅ ГАМІЛЬТОНІВ ЦИКЛ ІСНУЄ!")
                println("Маршрут: ", join(cycle, " -> "))
            else
                println("\n❌ Гамільтонового циклу НЕМАЄ (бектрекінг перебрав усі варіанти й не знайшов замкненого обходу).")
            end
        elseif choice == "5"
            try
                print("Вкажіть стартову вершину (1-$n): ")
                start_node = parse(Int, readline())
                print("Вкажіть кінцеву вершину (1-$n): ")
                target_node = parse(Int, readline())
                
                if start_node < 1 || start_node > n || target_node < 1 || target_node > n
                    println("❌ Помилка: Вершини мають бути в діапазоні від 1 до $n.")
                    continue
                end
                
                distances, parents = dijkstra(adj, start_node)
                path = reconstruct_path(parents, start_node, target_node)
                
                if distances[target_node] == Inf
                    println("\n❌ Шлях між вершиною $start_node та $target_node не існує.")
                else
                    println("\n✅ НАЙКОРОТШИЙ ШЛЯХ ЗНАЙДЕНО!")
                    println("• Загальна відстань (вага): ", distances[target_node])
                    println("• Маршрут: ", join(path, " -> "))
                end
            catch
                println("❌ Помилка введення даних.")
            end
        elseif choice == "6"
            result = prim_mst(adj)
            if result === nothing
                println("\n❌ Побудувати мінімальне кістякове дерево (MST) неможливо, оскільки граф незв'язний.")
            else
                edges, total_w = result
                println("\n✅ МІНІМАЛЬНЕ КІСТЯКОВЕ ДЕРЕВО (MST) ПОБУДОВАНО!")
                println("• Загальна вага MST: ", total_w)
                println("• Обрані ребра:")
                for (u, v, w) in edges
                    println("  Ребро $u <-> $v (вага: $w)")
                end
            end
        elseif choice == "7"
            break
        elseif choice == "8"
            println("Дякуємо за використання аналізатора графових алгоритмів. Бувайте!")
            exit(0)
        else
            println("❌ Невірний вибір. Спробуйте ще раз.")
        end
    end
end

# Головна точка входу програми
function main()
    while true
        println("\n" * "█"*60)
        println("      ІНТЕРАКТИВНИЙ АНАЛІЗАТОР ГРАФІВ НА JULIA (v2.0)")
        println("█"*60)
        println("Оберіть граф для аналізу:")
        println("1. Шаблонний граф: \"Пісочний годинник\" (Ейлеровий, не Гамільтонів)")
        println("2. Шаблонний граф: \"Кенігсберзькі мости\" (Гамільтонів, не Ейлеровий)")
        println("3. Створити та ввести власний граф вручну")
        println("4. Вийти з програми")
        print("> Ваш вибір: ")
        
        main_choice = strip(readline())
        
        if main_choice == \"1\"
            adj = make_hourglass_graph()
            analyze_graph_loop(adj)
        elseif main_choice == \"2\"
            adj = make_konigsberg_graph()
            analyze_graph_loop(adj)
        elseif main_choice == \"3\"
            adj = input_custom_graph()
            if !isempty(adj)
                analyze_graph_loop(adj)
            end
        elseif main_choice == \"4\"
            println("Дякуємо за використання аналізатора графових алгоритмів. Бувайте!")
            break
        else
            println("❌ Невірний вибір. Спробуйте ще раз.")
        end
    end
end

# Запуск програми, якщо файл запускається безпосередньо
if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
