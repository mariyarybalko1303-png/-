# ====================================================================
# ПОШУК ГАМІЛЬТОНОВИХ ЦИКЛІВ МЕТОДОМ БЕКТРЕКІНГУ (Backtracking)
# ====================================================================
# Цей скрипт реалізує класичний алгоритм дискретной математики
# для знаходження Гамільтонового циклу в неорієнтованому графі.
# Гамільтонів цикл — це замкнений шлях, який проходить через кожну
# ВЕРШИНУ графа рівно один раз і повертається в початкову точку.

using Random

# Структура для представлення результату пошуку
struct HamiltonianResult
    found::Bool
    path::Vector{Int}
end

"""
    is_safe(v::Int, adj::Vector{Vector{Int}}, path::Vector{Int}, pos::Int)

Перевіряє, чи можна додати вершину `v` на позицію `pos` у поточний шлях:
1. Чи є ребро між попередньою вершиною у шляху та вершиною `v`?
2. Чи не відвідували ми вже цю вершину `v`?
"""
function is_safe(v::Int, adj::Vector{Vector{Int}}, path::Vector{Int}, pos::Int)
    # 1. Перевіряємо, чи є ребро між попередньою вершиною у шляху і вершиною v
    prev_node = path[pos - 1]
    if !(v in adj[prev_node])
        return false
    end

    # 2. Перевіряємо, чи вершина v вже була додана до шляху
    for i in 1:(pos - 1)
        if path[i] == v
            return false
        end
    end

    return true
end

"""
    ham_cycle_util!(adj::Vector{Vector{Int}}, path::Vector{Int}, pos::Int, n::Int)

Рекурсивна допоміжна функція для розв'язання задачі Гамільтонового циклу
методом пошуку з поверненням (backtracking).
"""
function ham_cycle_util!(adj::Vector{Vector{Int}}, path::Vector{Int}, pos::Int, n::Int)
    # Базовий випадок: якщо всі вершини включені у шлях
    if pos == n + 1
        # Перевіряємо, чи є ребро від останньої вершини шляху назад до першої (стартової)
        first_node = path[1]
        last_node = path[n]
        if first_node in adj[last_node]
            return true
        end
        return false
    end

    # Перебираємо всі можливі вершини для поточної позиції `pos`
    # (для оптимізації дивимося лише на сусідів попередньої вершини)
    prev_node = path[pos - 1]
    for next_v in adj[prev_node]
        if is_safe(next_v, adj, path, pos)
            path[pos] = next_v

            # Рекурсивно намагаємося побудувати шлях далі
            if ham_cycle_util!(adj, path, pos + 1, n)
                return true
            end

            # Якщо додавання вершини next_v не привело до розв'язку,
            # виконуємо бектрекінг (відкочуємо зміни)
            path[pos] = 0
        end
    end

    return false
end

"""
    find_hamiltonian_cycle(adj::Vector{Vector{Int}})

Головна функція для запуску алгоритму бектрекінгу.
Повертає об'єкт HamiltonianResult.
"""
function find_hamiltonian_cycle(adj::Vector{Vector{Int}})
    n = length(adj)
    path = zeros(Int, n)
    
    # Починаємо з вершини 1. Будь-який Гамільтонів цикл має проходити через
    # усі вершини, тому вибір початкової точки не впливає на існування циклу.
    path[1] = 1
    
    if !ham_cycle_util!(adj, path, 2, n)
        return HamiltonianResult(false, Int[])
    end
    
    # Додаємо стартову вершину в кінець для демонстрації замкненості циклу
    push!(path, path[1])
    return HamiltonianResult(true, path)
end

# ====================================================================
# ДЕМОНСТРАЦІЯ ТА ТЕСТУВАННЯ
# ====================================================================

# Граф 1: Форма "пісочного годинника" (Ейлеровий, але НЕ Гамільтонів)
# Вершини: 5. Очікується результат: Цикл не існує.
adj_graph1 = [
    [2, 4, 3, 5], # 1
    [1, 3],       # 2
    [2, 4, 1, 5], # 3
    [3, 1],       # 4
    [3, 1]        # 5
]

# Граф 2: Міст Кенігсберга (Гамільтонів, але НЕ Ейлеровий)
# Вершини: 4. Очікується результат: Знайдений цикл (наприклад, 1 -> 4 -> 2 -> 3 -> 1)
adj_graph2 = [
    [2, 3, 4],    # 1
    [1, 3, 4],    # 2
    [1, 2],       # 3
    [1, 2]        # 4
]

println("="^60)
println("ТЕСТУВАННЯ АЛГОРИТМУ ПОШУКУ ГАМІЛЬТОНОВИХ ЦИКЛІВ")
println("="^60)

# Тестуємо Граф 1
println("\n[Аналіз Графа 1 (форма пісочного годинника)]")
result1 = find_hamiltonian_cycle(adj_graph1)
if result1.found
    println("✅ Знайдено Гамільтонів цикл: ", join(result1.path, " -> "))
else
    println("❌ Гамільтонів цикл НЕ існує (математично доведено раніше).")
end

# Тестуємо Граф 2
println("\n[Аналіз Графа 2 (міст Кенігсберга)]")
result2 = find_hamiltonian_cycle(adj_graph2)
if result2.found
    println("✅ Знайдено Гамільтонів цикл: ", join(result2.path, " -> "))
else
    println("❌ Гамільтонів цикл НЕ існує.")
end
