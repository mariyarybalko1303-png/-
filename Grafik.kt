val data = mapOf(
    "x" to listOf(1, 2, 3, 4, 5),
    "y" to listOf(2, 5, 3, 8, 7)
)

letsPlot(data) + geomLine {
    x = "x"
    y = "y"
}
