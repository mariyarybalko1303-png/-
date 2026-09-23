fun squareNumbers(list: List<Int>): List<Int> {
    return list.map { it * it }
}

val numbers = listOf(1, 2, 3, 4, 5)
val squared = squareNumbers(numbers)
println("Результат обчислень: $squared")
