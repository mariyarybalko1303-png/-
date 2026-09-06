# ====================================================================
# ПОШУК ЕЙЛЕРОВИХ ЦИКЛІВ У ГРАФАХ (Алгоритм Ієргальцера / Hierholzer)
# ====================================================================
# Цей скрипт реалізує класичний алгоритм дискретної математики
# для перевірки існування та побудови Ейлерового циклу в неорієнтованому графі.
# Ейлеровий цикл — це замкнений шлях, який проходить через кожне ребро графа рівно один раз.

"""
    is_connected(adj::Vector{Vector{Int}}, n::Int)

Перевіряє, чи є неорієнтований граф зв'язним для всіх вершин, що мають ступінь > 0.
Використовує класичний алгоритм пошуку в ширину (BFS).
"""
function is_connected(adj::Vector{Vector{Int}}, n::Int)
    visited = zeros(Bool, n)
    
    # Знаходимо першу вершину з ненульовим ступенем для старту обходу
    start_node = -1
    for i in 1:n
        if !isempty(adj[i])
            start_node = i
            break
        end
    end
    
    # Якщо в графі взагалі немає ребер, він тривіально вважається зв'язним
    if start_node == -1
        return true
    end
    
    # BFS обхід
    queue = [start_node]
    visited[start_node] = true
    
    while !isempty(queue)
        curr = popfirst!(queue)
        for neighbor in adj[curr]
            if !visited[neighbor]
                visited[neighbor] = true
                push!(queue, neighbor)
            end
        end
    end
    
    # Перевіряємо, чи відвідали ми всі вершини, які мають бодай одне ребро
    for i in 1:n
        if !isempty(adj[i]) && !visited[i]
            return false
        end
    end
    
    return true
end

"""
    has_eulerian_cycle(adj::Vector{Vector{Int}}, n::Int)

Перевіряє критерії Ейлеровості для неорієнтованого графа:
1. Кожна вершина має парний ступінь.
2. Усі вершини з ненульовим ступенем належать до одного зв'язного компонента.
"""
function has_eulerian_cycle(adj::Vector{Vector{Int}}, n::Int)
    # Критерій 1: парність ступеня для кожної вершини
    for i in 1:n
        if length(adj[i]) % 2 != 0
            return false
        end
    end
    
    # Критерій 2: зв'язність
    return is_connected(adj, n)
end

"""
    find_eulerian_cycle(adj::Vector{Vector{Int}})

Знаходить Ейлеровий цикл за допомогою лінійного алгоритму Ієргальцера (Hierholzer).
Повертає вектор вершин, що утворюють цикл, або `nothing`, якщо цикл не існує.
Часова складність: O(V + E), де V — вершини, E — ребра.
"""
function find_eulerian_cycle(adj::Vector{Vector{Int}})
    n = length(adj)
    
    # Перевіряємо, чи граф взагалі підтримує існування Ейлерового циклу
    if !has_eulerian_cycle(adj, n)
        return nothing
    end
    
    # Створюємо копію списку суміжності як Set{Int} для швидкого видалення ребер O(1)
    g = [Set{Int}(neighbors) for neighbors in adj]
    
    curr_path = Int[]       # Стек для тимчасового збереження шляху
    eulerian_cycle = Int[]  # Фінальний порядок вершин в Ейлеровому циклі
    
    # Знаходимо стартову вершину (перша вершина, що має ребра)
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
        # Якщо у поточної вершини є невідвідані суміжні ребра
        if !isempty(g[curr_v])
            # Зберігаємо вершину в стек
            push!(curr_path, curr_v)
            
            # Вибираємо будь-якого сусіда
            next_v = first(g[curr_v])
            
            # Видаляємо неорієнтоване ребро (в обидва боки)
            delete!(g[curr_v], next_v)
            delete!(g[next_v], curr_v)
            
            # Переходимо до наступної вершини
            curr_v = next_v
        else
            # Якщо вершина тупикова (немає невідвіданих ребер), додаємо її до циклу
            # і повертаємося назад (backtrack)
            push!(eulerian_cycle, curr_v)
            curr_v = pop!(curr_path)
        end
    end
    
    # Оскільки ми збирали шлях з кінця, реверсуємо результат
    return reverse(eulerian_cycle)
end

# ====================================================================
# ДЕМОНСТРАЦІЯ ТА ТЕСТУВАННЯ
# ====================================================================

# Тест 1: Класичний Ейлеровий граф (форма конверта без даху або "пісочний годинник")
# Вершини: 5. Ребра: (1-2), (2-3), (3-4), (4-1), (1-3), (3-5), (5-1)
# Усі вершини мають парний ступінь: 1(4), 2(2), 3(4), 4(2), 5(2).
adj_eulerian = [
    [2, 4, 3, 5], # 1
    [1, 3],       # 2
    [2, 4, 1, 5], # 3
    [3, 1],       # 4
    [3, 1]        # 5
]

# Тест 2: Не-Ейлеровий граф (класичний міст Кегнігсберга / непарні ступені)
# Вершини: 4. Вершини з непарними ступенями.
adj_non_eulerian = [
    [2, 3, 4],    # 1 (ступінь 3)
    [1, 3, 4],    # 2 (ступінь 3)
    [1, 2],       # 3 (ступінь 2)
    [1, 2]        # 4 (ступінь 2)
]

println("="^60)
println("ТЕСТУВАННЯ АЛГОРИТМУ ПОШУКУ ЕЙЛЕРОВИХ ЦИКЛІВ")
println("="^60)

# Тестуємо Граф 1
println("\n[Аналіз Графа 1 (Очікується успіх)]")
cycle1 = find_eulerian_cycle(adj_eulerian)
if cycle1 !== nothing
    println("✅ Граф є Ейлеровим!")
    println("Знайдений Ейлеровий цикл: ", join(cycle1, " -> "))
else
    println("❌ Граф не є Ейлеровим.")
end

# Тестуємо Граф 2
println("\n[Аналіз Графа 2 (Очікується відхилення)]")
cycle2 = find_eulerian_cycle(adj_non_eulerian)
if cycle2 !== nothing
    println("✅ Граф є Ейлеровим!")
    println("Знайдений Ейлеровий цикл: ", join(cycle2, " -> "))
else
    println("❌ Граф не є Ейлеровим (не виконується теорема Ейлера про парні ступені).")
end
